# -*- coding: utf-8 -*-

#imports lib
import networkx as nx
import queue

#import dependencies
import ProjectController
import GraphModifier as mods
import errors as err
import Nodes
import parameters as param


class ProjectGraph:
    def __init__(self, projectController, projectLogger):
        self._projectController = projectController
        self._projectLogger = projectLogger
        self._baseGraph = nx.multiDiGraph()
        self._databasePostIDMap = dict()
        self._databaseNoeudIDMap = dict()
        self._tagSlugMap = dict()
        self._uniqueIDCounter = 0

    def getUniqueID(self):
        self._uniqueIDCounter += 1
        return self._uniqueIDCounter
    
    def apply_modif(self, modif):

        if isinstance(modif, mods.NewPost):
            if (modif.databaseID in self._databasePostIDMap):
                raise err.NodeAlreadyExists("Could not create the following post node : " + modif.__str__() + " This node already exists", self._databasePostIDMap[modif.databaseID], modif.databaseID)
            new_node = Nodes.PostNode(self.getUniqueID, modif.size, modif.databaseID, value=modif.value)
            self._databasePostIDMap[modif.databaseID] = new_node
            self._baseGraph.add_node(new_node)
            if (modif.parent != -1):
                try:
                    parentNode = self._databasePostIDMap[modif.parent]
                except KeyError:
                    raise err.NodeMissing("Error while creating nodes : missing parent post", Nodes.PostNode, modif.parent)
                self._baseGraph.add_edge(new_node, parentNode, key="parent_post", default_weight=param.default_edge_weight_parent)
            for tag in modif.tags:
                try:
                    tag_node = self._tagSlugMap[tag]
                except KeyError:
                    raise err.NodeMissing("Error while creating post : could not find the following tag : " + tag, Nodes.TagNode, tag)
                self._baseGraph.add_edge(new_node, tag_node, key=("tagged_with", 0), default_weight=param.default_edge_weight_tag)


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
            if modif.slug in self._tagSlugMap:
                raise err.NodeAlreadyExists("Error while creating this tag : " + modif.slug + " Tag already exists", self._tagSlugMap[modif.slug], modif.slug)
            newNode = Nodes.TagNode(self.getUniqueID(), modif.slug)
            self._tagSlugMap[modif.slug] = newNode
            self._baseGraph.add_node(newNode)
            return

        if isinstance(modif, mods.TagOnPost):
            if not (modif.post_database_id in self._databasePostIDMap):
                raise err.NodeMissing("Error while tagging a post : post does not exist", Nodes.PostNode, modif.post_database_id)
            if not (modif.tag_slug in self._tagSlugMap):
                raise err.NodeMissing("Error while tagging a post : tag does not exist", Nodes.TagNode, modif.tag_slug)
            post_node = self._databasePostIDMap[modif.post_database_id]
            tag_node = self._tagSlugMap[modif.tag_slug]
            if ("tagged_with", 0) in self._baseGraph[post_node][tag_node]:
                raise err.EdgeAlreadyExists("Error while tagging a post : post already has this tag", post_node, tag_node, modif.post_database_id, modif.tag_slug, ("tagged_with", 0))
            self._baseGraph.add_edge(post_node, tag_node, key=("tagged_with", 0), default_weight=param.default_edge_weight_tag)
            return

        if isinstance(modif, mods.TagFromPost):
            if not (modif.post_database_id in self._databasePostIDMap):
                raise err.NodeMissing("Error while removing tag from a post : post does not exist", Nodes.PostNode, modif.post_database_id)
            if not (modif.tag_slug in self._tagSlugMap):
                raise err.NodeMissing("Error while removing tag from a post : tag does not exist", Nodes.TagNode, modif.tag_slug)
            post_node = self._databasePostIDMap[modif.post_database_id]
            tag_node = self._tagSlugMap[modif.tag_slug]
            if not ("tagged_with", 0) in self._baseGraph[post_node][tag_node]:
                raise err.EdgeDoesNotExist("Error while removing tag from a post : post does not have this tag", post_node, tag_node, modif.post_database_id, modif.tag_slug, ("tagged_with", 0))
            self._baseGraph.remove_edge(post_node, tag_node, key=("tagged_with", 0))
            return

    def apply_modifications(self, modification_queue):
        pass

    # Clés utilisées pour les arrêtes :
    # parent_post : post enfant -> post parent
    # tagged_with : post -> tg utilise sur le post
    # group_recommended -> post -> post | suggestion d'un utilisateur de grouper ces posts

