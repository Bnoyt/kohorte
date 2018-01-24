# -*- coding: utf-8 -*-

# libraries
import networkx as nx

# dependencies
import parameters as param
import ProjectController
import errors as err
import Nodes


class GenericModification():
    def apply_to_graph(self, project_graph):
        pass

class NewPost(GenericModification):
    def __init__(self, database_id, noeud, tags, size, parent, value):
        super().__init__()
        self.database_id = database_id
        self.noeud = noeud
        self.parent = parent
        self.tags = list(tags)
        self.size = size
        if value == -1:
            self.value = param.default_post_value
        else:
            self.value = value

        if size < 0:
            raise err.ForbidenModificationRequest("The new post was requested with a size of + " + str(size)
                                              + " The size of a post cannot be negative")

    def list_rep(self):
        return ["np", self.database_id, self.noeud, self.parent, self.size] + self.tags

    def apply_to_graph(self, project_graph):
        if self.database_id in project_graph._databasePostIDMap:
            raise err.NodeAlreadyExists(
                "Could not create the following post node : " + self.__str__() + " This node already exists",
                project_graph._databasePostIDMap[self.database_id], self.database_id)
        new_node = Nodes.PostNode(project_graph.get_unique_id(), self.size, self.database_id, value=self.value)
        project_graph._databasePostIDMap[self.database_id] = new_node
        project_graph._baseGraph.add_node(new_node)
        if self.parent != -1:
            try:
                parentNode = project_graph._databasePostIDMap[self.parent]
            except KeyError:
                raise err.NodeMissing("Error while creating nodes : missing parent post", Nodes.PostNode, self.parent)
            project_graph._baseGraph.add_edge(new_node, parentNode, key="parent_post",
                                              default_weight=param.default_edge_weight_parent)
        for tag in self.tags:
            try:
                tag_node = project_graph._tagSlugMap[tag]
            except KeyError:
                raise err.NodeMissing("Error while creating post : could not find the following tag : " + tag,
                                      Nodes.TagNode, tag)
            project_graph._baseGraph.add_edge(new_node, tag_node, key=("tagged_with", 0),
                                              default_weight=param.default_edge_weight_tag)


class NewRecommendationLink(GenericModification):
    def __init__(self, n1, n2, weight = 1.0):
        self.n1_id = n1
        self.n2_id = n2
        self.weight = weight

    def list_rep(self):
        return ["nr", self.n1, self.n2, self.weight]

    def apply_to_graph(self, project_graph):
        if not (self.n1_id in project_graph._databasePostIDMap):
            raise err.NodeMissing("Could not find parent while creating new node", node_id=self.p1)
        if not (self.n2_id in project_graph._databasePostIDMap):
            raise err.inconsistent_graph(type=err.inconsistent_graph.node_missing, node_id=self.p2)
        n1 = project_graph._databasePostIDMap[self.n1_id]
        n2 = project_graph._databasePostIDMap[self.n2_id]
        k = 0
        while (("group_recommended", k) in project_graph._baseGraph[n1][n2]):
            k += 1
        project_graph._baseGraph.add_edge(n1, n2, key=("group_recommended", k), default_weight=self.weight)
        return

class PostRemoval(GenericModification):
    def __init__(self, database_id):
        self.database_id = database_id

    def apply_to_graph(self, project_graph):
        if not (self.database_id in project_graph._databasePostIDMap):
            raise err.inconsistent_graph(type=err.inconsistent_graph.node_missing, node_id=self.database_id)
        node = project_graph._databasePostIDMap[self.database_id]
        del project_graph._databasePostIDMap[self.database_id]
        # TODO : delete this node properly
        try:
            project_graph._baseGraph.remove_node(node)
        except nx.NetworkXError:
            raise err.inconsistent_graph(type=err.inconsistent_graph.graph_idMap_inconsistency, node=node,
                                         node_id=project_graph._databasePostIDMap)

class PostDeletion(GenericModification):
    def __init__(self, database_id):
        self.database_id = database_id

    def apply_to_graph(self, project_graph):
        if not (self.database_id in project_graph._databasePostIDMap):
            raise err.inconsistent_graph(type=err.inconsistent_graph.node_missing, node_id=self.database_id)
        node = project_graph._databasePostIDMap[self.database_id]
        if node.deleted:
            raise err.NodeDeleted("Error encounterd while trying to delete a node : node already deleted",
                                  self.database_id)
        node.deleted = True

class PostModification(GenericModification):
    def __init__(self, database_id, newSize):
        self.database_id = database_id
        self.new_size = newSize

    def apply_to_graph(self, project_graph):
        if not (self.database_id in project_graph._databasePostIDMap):
            raise err.inconsistent_graph(type=err.inconsistent_graph.node_missing, node_id=self.database_id)
        node = project_graph._databasePostIDMap[self.database_id]
        if node.deleted:
            raise err.NodeDeleted("Error encounterd while trying to selfy a node : node has been deleted",
                                  self.database_id)
        node.size = self.new_size

class NewTag(GenericModification):
    def __init__(self, slug):
        self.slug = slug

    def apply_to_graph(self, project_graph):
        if self.slug in project_graph._tagSlugMap:
            raise err.NodeAlreadyExists("Error while creating this tag : " + self.slug + " Tag already exists",
                                        project_graph._tagSlugMap[self.slug], self.slug)
        newNode = Nodes.TagNode(project_graph.getUniqueID(), self.slug)
        project_graph._tagSlugMap[self.slug] = newNode
        project_graph._baseGraph.add_node(newNode)

class TagOnPost(GenericModification):
    def __init__(self, post_database_id, tag_slug):
        self.post_database_id = post_database_id
        self.tag_slug = tag_slug

    def apply_to_graph(self, project_graph):
        if not (self.post_database_id in project_graph._databasePostIDMap):
            raise err.NodeMissing("Error while tagging a post : post does not exist", Nodes.PostNode,
                                  self.post_database_id)
        if not (self.tag_slug in project_graph._tagSlugMap):
            raise err.NodeMissing("Error while tagging a post : tag does not exist", Nodes.TagNode, self.tag_slug)
        post_node = project_graph._databasePostIDMap[self.post_database_id]
        tag_node = project_graph._tagSlugMap[self.tag_slug]
        if ("tagged_with", 0) in project_graph._baseGraph[post_node][tag_node]:
            raise err.EdgeAlreadyExists("Error while tagging a post : post already has this tag", post_node, tag_node,
                                        self.post_database_id, self.tag_slug, ("tagged_with", 0))
        project_graph._baseGraph.add_edge(post_node, tag_node, key=("tagged_with", 0),
                                          default_weight=param.default_edge_weight_tag)

class TagFromPost(GenericModification):
    def __init__(self, post_database_id, tag_slug):
        self.post_database_id = post_database_id
        self.tag_slug = tag_slug

    def apply_to_graph(self, project_graph):
        if not (self.post_database_id in project_graph._databasePostIDMap):
            raise err.NodeMissing("Error while removing tag from a post : post does not exist", Nodes.PostNode,
                                  self.post_database_id)
        if not (self.tag_slug in project_graph._tagSlugMap):
            raise err.NodeMissing("Error while removing tag from a post : tag does not exist", Nodes.TagNode,
                                  self.tag_slug)
        post_node = project_graph._databasePostIDMap[self.post_database_id]
        tag_node = project_graph._tagSlugMap[self.tag_slug]
        if not ("tagged_with", 0) in project_graph._baseGraph[post_node][tag_node]:
            raise err.EdgeDoesNotExist("Error while removing tag from a post : post does not have this tag", post_node,
                                       tag_node, self.post_database_id, self.tag_slug, ("tagged_with", 0))
        project_graph._baseGraph.remove_edge(post_node, tag_node, key=("tagged_with", 0))

class UserCreation(GenericModification):
    pass