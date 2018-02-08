# -*- coding: utf-8 -*-

# import libraries
import networkx as nx
import pickle
from pathlib import Path

# import dependances
import app.clustering.errors as err
import app.clustering.ProjectGraph as pg
import app.clustering.ProjectLogger as pl
from app.clustering.GraphModifier import GraphModifier
import app.clustering.parameters as param
from threading import Thread as Thread



class ProjectController(Thread):
    """Chaque projet qui tourne sera géré par une unique instance de cette classe"""

    # the_graph contient le supergraphe, de type networkx : multiDiGraph
    # graph_loaded est un boolean indiquant si le supergraph est actuelement chargé

    def __init__(self, name, queue, boot=False):
        super().__init__()
        if boot:
            self.name = name
            self.path = Path(param.memory_path) / name
            if self.path.exists():
                raise err.LoadingError("could not create new project : project already exists")
            self.path.mkdir()
        else:
            self.name = name
            self.path = Path(param.memory_path) / name
            with (self.path / "control.txt").open('r') as control_file:
                try:
                    name_in_file = control_file.readline()[0:-1]
                    if name_in_file != self.name:
                        raise err.LoadingError("Incompatible control file format : name not valid")
                    self.database_id = int(control_file.readline()[:-1])
                    # TODO : go check if this id is indeed in the database
                    self.clean_shutdown = bool(control_file.readline()[0:-1])
                    self.register_instructions = (control_file.readline()[0:-1]).split(";")

                except IOError:
                    raise err.LoadingError()
        self.graphLoaded = False
        self.graphIsLoading = False
        self.graphShouldBeLoaded = False
        self.projectLogger = pl.ProjectLogger(self.name)
        self.theGraph = None

        self.procedure_table = None
        self.dummy_procedure = None

    def unload_graph(self):
        # TODO all the unloading procedure
        self.graphLoaded = False
        self.theGraph = None
        self.procedure_table = None

    def load_graph(self):
        self.graphShouldBeLoaded = True
        if self.graphLoaded:
            self.unload_graph()
        self.theGraph = pg.ProjectGraph(self, self.projectLogger)
        self.graphIsLoading = True
        self.graphModifier.clear_all_modifications()
        try:
            pass
            # TODO : access appropriate databases and load the graph
        except (err.GraphError, nx.NetworkXError):
            self.graphIsLoading = False
            self.theGraph = None
            return

        modifications_while_loading = self.graphModifier.pull_all_modifications()
        self.graphIsLoading = False
        self.graphLoaded = True
        self.procedure_table = ClusteringAlgorithms.get_procedure_table(self.theGraph)
        self.dummy_procedure = ClusteringAlgorithms.DoNothing()
        if not modifications_while_loading.empty():
            self.theGraph.apply_modifications(modifications_while_loading)
        try:
            log_location = self.projectLogger.register_graph_loading()
            with (log_location / "initial_graph.pkl").open('wb') as dl:
                pickle.dump(self.theGraph.get_pickle_graph(), dl)
        except IOError:
            self.projectLogger.active = False

    def apply_modifications(self, expect_errors=False):
        if self.graphLoaded:
            self.theGraph.apply_modifications(self.graphModifier.pull_all_modifications(),
                                              self.projectLogger.log_modifs_to_loaded_graph(), expect_errors)
        else:
            raise err.GraphNotLoaded()

    def update_priority(self):
        pass

    def update_suggestions(self):
        pass

    def run(self):

        if not self.graphLoaded:
            if self.graphShouldBeLoaded:
                self.load_graph()
            else:
                return

        try:

            run_time = param.now()

            self.apply_modifications()

            chosen_procedure = self.dummy_procedure

            for proc in self.procedure_table:
                if proc.priority(run_time) > chosen_procedure.priority(run_time):
                    chosen_procedure = proc

            if self.register_instructions[-1] == chosen_procedure.name:
                log_channel = self.projectLogger.log_algorithm(chosen_procedure.name)
            else:
                log_channel = self.projectLogger.log_nothing()

            chosen_procedure.run(log_channel)

            self.update_priority()

            self.update_suggestions()

        except (err.GraphError, nx.NetworkXError):
            # There are two possibilities for how a GraphError can be caught here
            # possibility 1 : a procedure below decided that things were out of control and the graph needed to be
            # reloaded so it raised a CatastrophicGraphFailure
            # possibility 1 : another GraphError subclass wasn't caught below. This shouldn't happen,
            # and if it does this implies a fault in my code
            # Similarily, all NetworkXError should be caught below
            # In any case, generic GraphError are only caught in ProjectControler.py
            self.unload_graph()
            self.load_graph()


#print("Project controller successfully imported")
