# -*- coding: utf-8 -*-

# import persos
import parameters
import supergraph as spg
import spg_algorithms
import errors

# import packages
import networkx as nx
import queue


class running_project:

    # the_graph contient le supergraphe, de type networkx : multiDiGraph
    # graph_loaded est un boolean indiquant si le supergraph est actuelement chargé


    def __init__(self):
        self.graph_loaded = False
        self.modifications =  queue()


    def load_graph(self):
        self.the_graph = nx.multiDiGraph()
        #TODO : access appropriate databases and load the graph

    def push_modification(self, modif):
        if self.graph_loaded:
            self.modifications.put(modif)

    def read_modifications(self):
        if(self.graph_loaded):
            spg.update_graph(self.the_graph, self.modifications)
        else:
            raise errors.graph_not_loaded()

