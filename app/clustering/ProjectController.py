# -*- coding: utf-8 -*-

# import libraries
import networkx as nx
import pickle
from pathlib import Path
import time as lib_time
import queue
from threading import Thread
import traceback

# import dependances
import app.clustering.errors as err
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
        self.database_id = database_id

        self.projectParam = ProjectParameters()

        self.path = Path(param.memory_path) / str(database_id)
        try:
            with (self.path / "control.txt").open('r') as control_file:
                self.name = control_file.readline()[0:-1]
                database_id_in_file = int(control_file.readline()[:-1])
                if database_id_in_file != self.database_id:
                    raise err.LoadingError("Incompatible control file format : name not valid")
                self.database_id = int(control_file.readline()[:-1])
                # TODO : go check if this id is indeed in the database
                self.clean_shutdown = bool(control_file.readline()[0:-1])
                self.register_instructions = (control_file.readline()[0:-1]).split(";")

                self.projectLogger = prl.ProjectLogger(self.path)

                self.memory_free = False

        except (IOError, err.LoadingError):
                print("Could not access project memory tree. Launching project in no-saving mode.")
                self.memory_free = True
                self.projectLogger = prl.ProjectLogger(self.path, active=False)
                self.register_instructions = []
                self.clean_shutdown = False

        self.graphLoaded = False
        self.graphIsLoading = False
        self.theGraph = None
        self.database_access = DbAccess.DatabaseAccess(self.database_id)

        self.modification_queue = queue.Queue()

        self.command_handler = CommandHandler(command_queue, self)

        self.procedure_table = None
        self.dummy_procedure = None

        self.open_algo_log_file = self.projectLogger.log_nothing()
        self.open_modif_log_file = self.projectLogger.log_nothing()

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
        self.theGraph = prg.ProjectGraph(self, self.projectLogger)
        self.graphIsLoading = True
        self.clear_all_modifications()

        try:

            self.theGraph.load_from_database(self.database_access)

            self.graphIsLoading = False
            self.graphLoaded = True

            self.apply_modifications(expect_errors=True)

        except (err.DatabaseError, err.GraphError, nx.NetworkXError) as error:
            self.graphIsLoading = False
            self.theGraph = None
            print("Error while loeading graph from database : ")
            traceback.print_tb(error.__traceback__)
            print(err)
            return

        self.procedure_table = ClusterAlg.get_procedure_table(self.theGraph)
        self.dummy_procedure = ClusterAlg.DoNothing()

        dl = self.projectLogger.log_nothing()
        try:
            log_location = self.projectLogger.register_graph_loading()
            dl = (log_location / "initial_graph.pkl").open('wb')
            pickle.dump(self.theGraph.get_pickle_graph(), dl)
        except IOError:
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

    def rebind_memory(self, new_path_string):
        new_path = Path(new_path_string)
        if not new_path.exists():
            print("Error : could not rebind path, " + str(new_path_string) + " does not exist")
            return False
        self.path = new_path
        try:
            with (self.path / "control.txt").open('r') as control_file:
                self.name = control_file.readline()[0:-1]
                database_id_in_file = int(control_file.readline()[:-1])
                if database_id_in_file != self.database_id:
                    raise err.LoadingError("Incompatible control file format : name not valid")
                self.database_id = int(control_file.readline()[:-1])
                # TODO : go check if this id is indeed in the database
                self.clean_shutdown = bool(control_file.readline()[0:-1])
                self.register_instructions = (control_file.readline()[0:-1]).split(";")

                self.projectLogger = prl.ProjectLogger(self.path)

                self.memory_free = False

        except (IOError, err.LoadingError):
                print("Rebind failed. Project continuing in no-saving mode")
                self.memory_free = True
                self.projectLogger = prl.ProjectLogger(self.path, active=False)
                self.register_instructions = []
                self.clean_shutdown = False

    def interuptible_sleep(self, duration):
        """sleeps for approximately duration seconds, but stops if a shutdown is required."""
        for i in range(int(duration//10 + 1)):
            if self.command_handler.shutdown_req():
                return
            else:
                lib_time.sleep(10)

    def run(self):

        self.load_graph(use_memory=self.clean_shutdown)

        print("Backend successfully initiated. Begining algorithmic analysis.")

        while not self.command_handler.shutdown_req():

            if not self.graphLoaded:
                self.interuptible_sleep(param.idle_execution_period.total_seconds())
                if self.command_handler.shutdown_req():
                    break
                self.load_graph()
            else:

                try:

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

                    if self.command_handler.shutdown_req():
                        break

                    self.apply_modifications()

                    if self.command_handler.shutdown_req():
                        break

                    if len(self.register_instructions) > 0 and self.register_instructions[-1] == chosen_procedure.name:
                        self.register_instructions.pop()
                        self.open_algo_log_file = self.projectLogger.log_algorithm(chosen_procedure.name)

                    chosen_procedure.run(self.open_algo_log_file, self.command_handler)

                    self.open_algo_log_file.close() # probably not necessary, but I put it here just in case
                    self.open_algo_log_file = self.projectLogger.log_nothing()

                    if self.command_handler.shutdown_req():
                        break

                    self.branch()

                    self.update_priority()

                    self.update_suggestions()


                except (err.GraphError, nx.NetworkXError):
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

        # TODO : clean shutdown code
        print("shutting down")


class CommandHandler:
    def __init__(self, command_queue, project_controler : ProjectController):
        self._command_queue = command_queue
        self._shutdown_requested = False
        self._end_of_cycle = []
        self.project_controler = project_controler

    def read_commands(self):
        while not self._command_queue.empty():
            instruction = self._command_queue.get()
            if instruction == param.shutdown_command:
                print("shutdown request aknowledged")
                self._shutdown_requested = True

    def shutdown_req(self):
        self.read_commands()
        return self._shutdown_requested

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
        pass

    # The following code is an example for making a difference between command
    # type and handling them at separated time
    def _command_name_here(self, *args, **kwargs):
        # this is invoked by handle_commands
        # the handling is then schedule to a different time because it
        # cannot be handled now
        self._end_of_cycle.append({'method_name': 'handling_method_name',
                                   'args': args,
                                   'kwargs': kwargs})

    def _shutdown(self):
        self._shutdown_requested = True

    def change_parameters(self, **kwargs):
        self._end_of_cycle.append({'method_name': '_resolve_change_parameters',
                                   'kwargs': kwargs})

    def _resolve_change_parameters(self, **kwargs):
        self.project_controler.projectParam.update_parameters(kwargs)

    def rebind_memory(self, *args):
        self._end_of_cycle.append({'method_name': '_resolve_rebind_memory',
                                   'args': args})

    def _resolve_rebind_memory(self, *args):
        if len(args) == 0:
            path = param.memory_path
        else:
            path = args[0]
        self.project_controler.rebind_memory(path)

    def reload_graph(self, **kwargs):
        self._end_of_cycle.append({'method_name': '_resolve_reload_graph',
                                   'kwargs': kwargs})

    def _resolve_reload_graph(self, use_memory=False):
        self.project_controler.unload_graph()
        self.project_controler.load_graph(use_memory)

    def _handle_category(self):
        for command in self._end_of_cycle:
            MessageHandler.handle_decoded(command, self)

    def _handling_method_name(self, *args, **kwargs):
        # Actually do something here
        pass
    # ------------------------------------------------------

    # Another idea for handling methods
    def _another_command_name_here(self, *args, **kwargs):
        # self.CONFIG or another variable is used to determine if the command
        # can be handled now
        if self.CONFIG['UNIQUE_KEY_FOR_THIS_COMMAND']:
            # now this command can be handled
            # do something
            pass
        else:
            # command is delayed
            self.delayed.put({'method_name':'_another_command_name_here',
                              'args': args,
                              'kwargs': kwargs})

    def schedule_delayed_commands(self):
        # ONLY USE THIS WHEN handle_commands HAS TERMINATED
        # OTHERISE, IT MIGHT CREATE AN INFINITE LOOP
        # MOREOVER, queue.queue EXPLICITELY DOESN'T SUPPORT MULTIPLE ACCESS FROM
        # THE SAME THREAD
        for command in self.delayed:
            self._command_queue.put(command)
    # END OF SECOND IDEA -------------------------------------------------------


class ProjectParameters:

    def __init__(self):
        from app.clustering.parameters import *
        self.modified = set()

    def write_to_file(self, csv_file):

        for key in self.modified:
            csv_file.writerow([key, self.__dict__[key]])

    def read_from_file(self, csv_file):

        key, value = csv_file.readrow()
        self.update_parameters({key: value})

    def update_parameters(self, kwargs):
        for key, value in kwargs.items():
            if key not in self.__dict__:
                print(key + " is not a valid parameter")
                return False

            if key not in self._type_read():
                return False

            if key in self._assertions:
                if not self._assertions[key](value):
                    print(str(value) + " is not a valid value for parameter " + key)
                    return False

            self.__dict__[key] = self._type_read[key](kwargs[key])
            self.modified.add(key)
