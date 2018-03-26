# -*- coding: utf-8 -*-

# import libraries
import networkx as nx
import pickle
from pathlib import Path
import time as lib_time
import queue
from threading import Thread
import traceback
import logging

# import dependances
import app.clustering.errors as errors
import app.clustering.ProjectGraph as prg
import app.clustering.ProjectLogger as prl
from app.clustering.GraphModifier import GraphModifier
import app.clustering.parameters as param
import app.clustering.ClusteringAlgorithms as ClusterAlg
import app.clustering.DatabaseAccess as DbAccess
from app.backend.network import MessageHandler


class ProjectController(Thread):
    """Chaque projet qui tourne sera géré par une unique instance de cette classe"""

    # the_graph contient le supergraphe, de type networkx : multiDiGraph
    # graph_loaded est un boolean indiquant si le supergraph est actuelement chargé

    def __init__(self, database_id, command_queue):
        super().__init__()
        self.name = 'BACKEND_project#%s' % database_id
        self.database_id = database_id

        self.LOGGER = logging.getLogger('agorado.machinerie.' + str(database_id))

        self.projectParam = param.Parameter()

        self.path = Path(param.memory_path) / str(database_id)
        try:
            with (self.path / "control.txt").open('r') as control_file:
                self.name = control_file.readline()[0:-1]
                database_id_in_file = int(control_file.readline()[:-1])
                if database_id_in_file != self.database_id:
                    raise errors.LoadingError("Incompatible control file format : id not valid")
                self.database_id = int(control_file.readline()[:-1])
                # TODO : go check if this id is indeed in the database
                self.clean_shutdown = bool(control_file.readline()[0:-1])
                self.register_instructions = (control_file.readline()[0:-1]).split(";")

                self.projectLogger = prl.ProjectLogger(self.path)

                self.memory_free = False

        except (IOError, errors.LoadingError):
                self.LOGGER.exception("error while accessing memory : ", exc_info=True)
                self.LOGGER.warning("Could not access project memory tree. Launching project in no-saving mode.")
                self.memory_free = True
                self.projectLogger = prl.ProjectLogger(self.path, active=False)
                self.register_instructions = []
                self.clean_shutdown = False

        self.graphLoaded = False
        self.graphIsLoading = False
        self.theGraph = None
        self.database_access = DbAccess.DatabaseAccess(self.database_id)

        self.modification_queue = queue.Queue()

        self._command_queue = command_queue
        self._end_of_cycle = []

        self.procedure_table = None
        self.dummy_procedure = None

        self.open_algo_log_file = self.projectLogger.log_nothing()
        self.open_modif_log_file = self.projectLogger.log_nothing()

        self.running_algorithm = False
        self._shutdown_requested = False

        # NE PAS APPELER self.run : C'EST AU THREAD DEMARRANT CELUI-LA D'APPELER
        # self.strat() SUR UN OBJECT THREAD !!!!!!!

    def get_graph_modifier(self):
        return GraphModifier(self.modification_queue)

    def clear_all_modifications(self):
        while not self.modification_queue.empty():
            self.modification_queue.get()

    def unload_graph(self):
        # TODO all the unloading procedure
        self.graphLoaded = False
        self.theGraph = None
        self.procedure_table = None

    def load_graph(self, use_memory=False):
        if self.graphLoaded:
            self.unload_graph()
        self.theGraph = prg.ProjectGraph(self, self.projectLogger, self.projectParam)
        self.graphIsLoading = True
        self.clear_all_modifications()

        try:

            self.theGraph.load_from_database(self.database_access)

            self.graphIsLoading = False
            self.graphLoaded = True

            self.apply_modifications(expect_errors=True)

        except (errors.DatabaseError, errors.GraphError, nx.NetworkXError) as err:
            self.graphIsLoading = False
            self.theGraph = None
            info = "Error while loading graph from database for project %s: " % self.database_id
            self.LOGGER.exception(info, exc_info=(err.__class__, err, err.__traceback__))
            return

        self.procedure_table = ClusterAlg.get_procedure_table(self)
        self.dummy_procedure = ClusterAlg.DoNothing(self)

        dl = self.projectLogger.log_nothing()
        try:
            log_location = self.projectLogger.register_graph_loading()
            dl = (log_location / "initial_graph.pkl").open('wb')
            pickle.dump(self.theGraph.get_pickle_graph(), dl)
        except IOError:
            self.LOGGER.exception(msg="error while initiating project logger : ", exc_info=False)
            self.LOGGER.warning("Could not initialize the logger for this graph. " +
                                "Modifications and algorithms will not be saved")
            self.projectLogger.active = False
        finally:
            dl.close()

    def apply_modifications(self, expect_errors=False):
        if self.graphLoaded:
            while not self.modification_queue.empty():
                self.theGraph.apply_modification(self.modification_queue.get())
        else:
            self.clear_all_modifications()

    def modify_config_file(self, clean_shutdown=False, register_instructions=[]):
        with (self.path / "control.txt").open('r') as control_file:
            control_file.write(self.name)
            control_file.write(str(self.database_id))
            control_file.write(str(clean_shutdown))
            reg_i = ""
            for inst in register_instructions:
                reg_i += inst
                reg_i += ";"
            control_file.write(reg_i)

    def update_priority(self):
        pass

    def update_suggestions(self):
        pass

    def branch(self):
        while len(self.theGraph.branch_instructions) > 0:
            inst = self.theGraph.branch_instructions.get(0)

    def abandon_memory(self):
        self.memory_free = True
        self.projectLogger = prl.ProjectLogger(self.path, active=False)
        self.register_instructions = []
        self.clean_shutdown = False

    def rebind_memory(self, new_path_string):
        new_path = Path(new_path_string)
        if not new_path.exists():
            self.LOGGER.error("Error : could not rebind path, " + str(new_path_string) + " does not exist")
            return False
        self.path = new_path
        try:
            with (self.path / "control.txt").open('r') as control_file:
                self.name = control_file.readline()[0:-1]
                database_id_in_file = int(control_file.readline()[:-1])
                if database_id_in_file != self.database_id:
                    raise errors.LoadingError("Incompatible control file format : name not valid")
                self.database_id = int(control_file.readline()[:-1])
                # TODO : go check if this id is indeed in the database
                self.clean_shutdown = bool(control_file.readline()[0:-1])
                self.register_instructions = (control_file.readline()[0:-1]).split(";")

                self.projectLogger = prl.ProjectLogger(self.path)

                self.memory_free = False

        except (IOError, errors.LoadingError):
            self.LOGGER.exception(self, exc_info=False)
            info = "Memory rebind failed. Project %s continuing in no-saving mode." % self.database_id
            self.LOGGER.warning(info)
            self.abandon_memory()

    def interuptible_sleep(self, duration):
        """sleeps for approximately duration seconds, but stops if a shutdown is required."""
        for i in range(int(duration//10 + 1)):
            if self.shutdown_req():
                return
            else:
                lib_time.sleep(10)

    def run(self):
        try:

            self.load_graph(use_memory=self.clean_shutdown)

            self.LOGGER.info("Backend %s successfully initiated. Begining algorithmic analysis." % self.database_id)

            while not self.shutdown_req():

                if not self.graphLoaded:
                    self.interuptible_sleep(param.idle_execution_period.total_seconds())
                    if self.shutdown_req():
                        break
                    self.load_graph()
                else:

                    try:

                        self.running_algorithm = True

                        run_time = param.now()

                        chosen_procedure = self.dummy_procedure

                        for proc in self.procedure_table:
                            if proc.next_run() < chosen_procedure.next_run():
                                chosen_procedure = proc

                        nr = chosen_procedure.next_run()

                        if nr > run_time:
                            if nr < param.never:
                                self.interuptible_sleep((nr - run_time).total_seconds())
                            else:
                                self.interuptible_sleep(param.idle_execution_period.total_seconds())

                        if self.shutdown_req():
                            break

                        self.apply_modifications()

                        if self.shutdown_req():
                            break

                        if len(self.register_instructions) > 0 and self.register_instructions[-1] == chosen_procedure.name:
                            self.register_instructions.pop()
                            self.open_algo_log_file = self.projectLogger.log_algorithm(chosen_procedure.name)

                        chosen_procedure.run(self.open_algo_log_file)

                        self.open_algo_log_file.close() # probably not necessary, but I put it here just in case
                        self.open_algo_log_file = self.projectLogger.log_nothing()

                        if self.shutdown_req():
                            break

                        self.branch()

                        self.update_priority()

                        self.update_suggestions()

                        self.running_algorithm = True
                        self.handle_commands()

                    except (errors.GraphError, nx.NetworkXError):
                        # There are two possibilities for how a GraphError can be caught here
                        # possibility 1 : a procedure below decided that things were out of control and the graph needed
                        # to be reloaded so it raised a CatastrophicGraphFailure
                        # possibility 1 : another GraphError subclass wasn't caught below. This shouldn't happen,
                        # and if it does this implies a fault in my code
                        # Similarily, all NetworkXError should be caught below
                        # In any case, generic GraphError are only caught in ProjectControler.py
                        self.unload_graph()
                        self.load_graph()
                    finally:
                        self.open_algo_log_file.close()
                        self.running_algorithm = True

            # TODO : clean shutdown code
            self.LOGGER.info("shutting down")
        except Exception as err:
            info = "An error occured while running. THREAD STOPPED !\nCould not execute proper cleanup"
            self.LOGGER.exception(info, exc_info=(err.__class__, err, err.__traceback__))
            pass

    def _handle_command(self, msg):
        MessageHandler.handle_json(msg, self)
        pass

    def handle_commands(self):
        try:
            while True:
                msg = self._command_queue.get_nowait()
                self._handle_command(msg)
        except queue.Empty:
            pass
        if self.running_algorithm:
            try:
                while True:
                    msg = self._end_of_cycle.pop()
                    self._handle_command(msg)
            except IndexError:
                pass

    def shutdown_req(self):
        self.handle_commands()
        return self._shutdown_requested

    def shutdown(self):
        self._shutdown_requested = True

    def change_parameter(self, *args, **kwargs):
        if "dict" in kwargs:
            pass
        else:
            try:
                var_name = kwargs["name"]
            except KeyError:
                self.LOGGER.warning("Could not change parameter : you must specify a parameter name")
                return
            try:
                value = kwargs["value"]
            except KeyError:
                self.LOGGER.warning("Could not change parameter : you must specify a parameter value")
                return

            try:
                vars(self.projectParam)[var_name] = value
            except ValueError:
                info = "could not change parameter " + str(var_name) + " to value " + str(value)
                self.LOGGER.exception(msg= info, exc_info=True)

    def change_memory_path(self, *args):
        if self.running_algorithm:
            self._end_of_cycle.append({'method_name': '_resolve_rebind_memory', 'args': args})
        else:
            if len(args) == 0 or args[0] == 'default':
                new_path = param.memory_path
            elif args[0] == 'current':
                new_path = self.path
            elif args[0] == 'none':
                self.abandon_memory()
                return
            else:
                new_path = args[0]
            self.rebind_memory(new_path)

    def reload_graph(self, use_memory=False, **kwargs):
        if self.running_algorithm:
            self._end_of_cycle.append({'method_name': '_resolve_reload_graph', 'kwargs': kwargs})
        else:
            self.unload_graph()
            self.load_graph(use_memory)
