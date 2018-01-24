# -*- coding: utf-8 -*-

# import libraries
import networkx as nx
import queue
import pickle

# import dependances
import spg_algorithms
import errors as err
import ProjectGraph as pg
import ProjectLogger as pl
import GraphModifications as gm
import parameters as param
from pathlib import Path

class ProjectController:
    """Chaque projet qui tourne sera géré par une unique instance de cette classe"""

    # the_graph contient le supergraphe, de type networkx : multiDiGraph
    # graph_loaded est un boolean indiquant si le supergraph est actuelement chargé

    def __init__(self, name, boot=False):
        if boot:
            self.name = name
            self.path = Path(param.memory_path) / name
            if self.path.exists():
                raise err.LoadingError()
            self.path.mkdir()
        else:
            self.name = name
            self.path = param.memory_path + name
            with open(self.path + "control.txt", 'r') as control_file:
                try:
                    name_in_file = control_file.readline()[0:-1]
                    if name_in_file != self.name:
                        raise err.LoadingError()
                    self.database_id = int(control_file.readline()[:-1])
                    # TODO : go check if this id is indeed in the database
                    self.clean_shutdown = bool(control_file.readline()[0:-1])
                    self.avenger = control_file.readline()
                except IOError:
                    raise err.LoadingError()
        self.graphLoaded = False
        self.graphIsLoading = False
        self.projectLogger = pl.ProjectLogger(name)
        self.graphModifier = gm.GraphModifier(name)
        self.theGraph = None

    def unload_graph(self):
        if not self.graphLoaded:
            raise err.GraphNotLoaded()
        # TODO all the unloading procedure
        self.graphLoaded = False

    def load_graph(self):
        if self.graphLoaded:
            self.unload_graph()
        self.theGraph = pg.ProjectGraph(self, self.projectLogger)
        self.graphIsLoading = True
        self.graphModifier.clear_all_modifications()
        # TODO : access appropriate databases and load the graph
        modifications_while_loading = self.graphModifier.pull_all_modifications()
        self.graphIsLoading = False
        self.graphLoaded = True
        if not modifications_while_loading.empty():
            self.theGraph.apply_modifications(modifications_while_loading)
        log_location = self.projectLogger.register_graph_loading()
        with (log_location / "initial_graph.pkl").open('w') as dl:
            pickle.dump(self.theGraph, dl)

    def apply_modifications(self, expect_errors=False):
        if self.graphLoaded:
            self.theGraph.apply_modifications(self.graphModifier.pull_all_modifications(), expect_errors)
        else:
            raise err.GraphNotLoaded()