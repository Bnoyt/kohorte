# -*- coding: utf-8 -*-

#imports lib
import networkx as nx
import queue

#import dependencies
import ProjectController
import modifications as mods
import errors as err
import Nodes
import parameters as param


class ProjectGraph:
    def __init__(self, projectController):
        self._projectController = projectController
        self._baseGraph = nx.multiDiGraph()
        self._databasePostIDMap = dict()
        self._databaseNoeudIDMap = dict()
        self._uniqueIDCounter = 0

    def getUniqueID(self):
        self._uniqueIDCounter += 1
        return self._uniqueIDCounter
    
    def apply_modif(self, modif):

        if isinstance(modif, mods.NewPost):
            if (modif.databaseID in self._databasePostIDMap):
                raise err.NodeAlreadyExists("Could not create the following node : " + modif.__str__() + " This node already exists", modif.databaseID)
            newNode = Nodes.PostNode(self.getUniqueID, modif.size, modif.databaseID, value=modif.value)
            self._databasePostIDMap[modif.databaseID] = newNode
            self._baseGraph.add_node(newNode)
            if (modif.parent != -1):
                try:
                    parentNode = self._databasePostIDMap[modif.parent]
                except KeyError:
                    raise err.NodeMissing("Error while creating nodes : missing parent post", modif.parent)
                self._baseGraph.add_edge(newNode, parentNode, key="parent_post", default_weight=param.default_edge_weight_parent)
            return

        if isinstance(modif, mods.NewRecommendationLink):
            if not (modif.n1_id in self._databasePostIDMap):
                raise err.inconsistent_graph(type=err.inconsistent_graph.node_missing, node_id=modif.p1)
            if not (modif.n2_id in self._databasePostIDMap):
                raise err.inconsistent_graph(type=err.inconsistent_graph.node_missing, node_id=modif.p2)
            n1 = self._databasePostIDMap[modif.n1_id]
            n2 = self._databasePostIDMap[modif.n2_id]
            k = 0
            while (("group_recommended", k) in self._baseGraph[n1][n2]):
                k += 1
            self._baseGraph.add_edge(n1, n2, key=("group_recommended", k), default_weight=modif.weight)
            return

        if isinstance(modif, mods.PostRemoval):
            if not (modif.databaseID in self._databasePostIDMap):
                raise err.inconsistent_graph(type=err.inconsistent_graph.node_missing, node_id=modif.databaseID)
            node = self._databasePostIDMap[modif.databaseID]
            del self._databasePostIDMap[modif.databaseID]
            # TODO : delete this node properly
            try:
                self._baseGraph.remove_node(node)
            except nx.NetworkXError:
                raise err.inconsistent_graph(type=err.inconsistent_graph.graph_idMap_inconsistency, node=node,
                                             node_id=self._databasePostIDMap)
            return
        if isinstance(modif, mods.PostDeletion):
            if not (modif.databaseID in self._databasePostIDMap):
                raise err.inconsistent_graph(type=err.inconsistent_graph.node_missing, node_id=modif.databaseID)
            node = self._databasePostIDMap[modif.databaseID]
            if node.deleted:
                raise err.NodeDeleted("Error encounterd while trying to delete a node : node already deleted", modif.databaseID)
            node.deleted = True
            return


        if isinstance(modif, mods.PostModification):
            if not (modif.databaseID in self._databasePostIDMap):
                raise err.inconsistent_graph(type=err.inconsistent_graph.node_missing, node_id=modif.databaseID)
            node = self._databasePostIDMap[modif.databaseID]
            if node.deleted:
                raise err.NodeDeleted("Error encounterd while trying to modify a node : node has been deleted", modif.databaseID)
            node.size = modif.new_size
            return

        if isinstance(modif, mods.NewTag):
            pass

