# -*- coding: utf-8 -*-

#import libraries
import networkx as nx
import queue
import pickle

#import dependances
import parameters
import supergraph as spg
import spg_algorithms
import errors as err
import ProjectGraph as pg
import ProjectLogger as pl
import GraphModifier as gm
import parameters as param


class ProjectController:
    '''Chaque projet qui tourne sera géré par une unique instance de cette classe'''

    #the_graph contient le supergraphe, de type networkx : multiDiGraph
    #graph_loaded est un boolean indiquant si le supergraph est actuelement chargé

    def __init__(self, name):
        self.name = name
        self.path = param.memory_path + name
        with open(self.path + "control.txt", 'r') as control_file:
            name_in_file = control_file.readline()[0:-1]
            if name_in_file != self.name:
                raise err.LoadingError()
            self.clean_shutdown = bool(control_file.readline()[0:-1])
            self.avenger = control_file.readline()
        self.graphLoaded = False
        self.graphIsLoading = False
        self.projectLogger = pl.ProjectLogger(name)
        self.graphModifier = gm.GraphModifier(name)


    def unload_graph(self):
        if not self.graphLoaded:
            raise err.graph_not_loaded
        #TODO all the unloading procedure
        self.graph_loaded = False

    def load_graph(self):
        if self.graphLoaded:
            self.unload_graph()
        self.theGraph = pg.ProjectGraph(self, self.projectLogger)
        self.graphIsLoading = True
        self.graphModifier.clear_all_modifications()
        #TODO : access appropriate databases and load the graph
        modifications_while_loading = self.graphModifier.pull_all_modifications()
        self.graphIsLoading = False
        self.graphLoaded = True
        if not modifications_while_loading.empty():
            self.theGraph.apply_modifications(modifications_while_loading)
        log_location = self.projectLogger.register_graph_loading()
        with (log_location / "initial_graph.pkl").open('w') as dl:
            pickle.dump(self.theGraph, dl)



    def apply_modifications(self, expectErrors=False):
        if(self.graphLoaded):
            self.theGraph.apply_modifications(self.graphModifier.pull_all_modifications(), expectErrors)
        else:
            raise err.graph_not_loaded()