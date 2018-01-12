# -*- coding: utf-8 -*-

#import libraries
import networkx as nx
import queue

#import dependances
import parameters
import supergraph as spg
import spg_algorithms
import errors as err
import ProjectGraph as pg
import ProjectLogger as pl


class ProjectController:
    '''Chaque projet qui tourne sera géré par une unique instance de cette classe'''

    #the_graph contient le supergraphe, de type networkx : multiDiGraph
    #graph_loaded est un boolean indiquant si le supergraph est actuelement chargé

    def __init__(self, name="untitled"):
        self.graphLoaded = False
        self.graphIsLoading = False
        self.pendingModifications =  queue.Queue()
        self.projectLogger = pl.ProjectLogger(name)
        self.name = self.projectLogger.name


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
        #TODO : access appropriate databases and load the graph
        self.graphIsLoading = False
        self.graphLoaded = True
        self.apply_modifications(expectErrors=True)

    def push_modification(self, modif):
        if self.graphIsLoading or self.graphLoaded:
            self.pendingModifications.put(modif)


    def apply_modifications(self, expectErrors=False):
        if(self.graphLoaded):
            modifList = self.pendingModifications.copy() #In case a modification is pushed while the graph is loading modifications
            self.pendingModifications = queue.Queue()
            self.theGraph.apply_modifications(modifList, expectErrors)
        else:
            raise err.graph_not_loaded()