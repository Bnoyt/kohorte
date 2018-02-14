# -*- coding: utf-8 -*-

# libraries
import networkx as nx

# dependencies
import app.clustering.parameters as param
import app.clustering.errors as err
import app.clustering.Nodes as Nodes
#import datetime UNUSED IN THIS CODE


class GenericModification():
    def __init__(self):
        self.creation_time = param.now()

    def time_since_creation(self):
        return (self.creation_time - param.now())

    def apply_to_graph(self, project_graph):
        pass


class NewPost(GenericModification):
    def __init__(self, database_id, noeud, tags, size, parent):
        super().__init__()
        self.database_id = database_id
        self.noeud = noeud
        self.parent = parent
        self.tags = list(tags)
        self.size = size
        if size < 0:
            raise err.ForbidenModificationRequest("The new post was requested with a size of + " + str(size)
                                                  + " The size of a post cannot be negative")

    def list_rep(self):
        return ["np", self.database_id, self.noeud, self.parent, self.size] + self.tags

    def apply_to_graph(self, project_graph):
        if self.database_id in project_graph.databasePostIDMap:
            raise err.NodeAlreadyExists(
                "Could not create the following post node : " + self.__str__() + " This node already exists",
                project_graph.databasePostIDMap[self.database_id], self.database_id)
        new_node = Nodes.PostNode(self.database_id, self.size)
        project_graph.databasePostIDMap[self.database_id] = new_node
        project_graph.baseGraph.add_node(new_node)

        try:
            home_noeud = project_graph.databaseNoeudIDMap[self.noeud]
        except KeyError:
            raise err.NodeMissing("Error while creating nodes : could not find home Noeud", Nodes.NoeudNode, self.noeud)
        project_graph.baseGraph.add_edge(new_node, home_noeud, key=param.belongs_to,
                                         default_weight=param.default_node_belonging_weight)

        if self.parent != -1:
            try:
                parent_node = project_graph.databasePostIDMap[self.parent]
            except KeyError:
                raise err.NodeMissing("Error while creating nodes : missing parent post", Nodes.PostNode, self.parent)
            project_graph.baseGraph.add_edge(new_node, parent_node, key=param.parent_post,
                                             default_weight=param.default_edge_weight_parent)
        for tag in self.tags:
            try:
                tag_node = project_graph.databaseTagIDMap[tag]
            except KeyError:
                raise err.NodeMissing("Error while creating post : could not find the following tag : " + tag,
                                      Nodes.TagNode, tag)
            project_graph.baseGraph.add_edge(new_node, tag_node, key=("tagged_with", 0),
                                             default_weight=param.default_edge_weight_tag)


class NewRecommendationLink(GenericModification):
    def __init__(self, n1, n2, author):
        super().__init__()
        self.n1_id = n1
        self.n2_id = n2
        self.author_id = author

    def list_rep(self):
        return ["nr", self.n1_id, self.n2_id, self.author_id]

    def apply_to_graph(self, project_graph):
        if not (self.n1_id in project_graph.databasePostIDMap):
            raise err.NodeMissing("Could not find node 1 while creating recommendation link", node_id=self.n1_id, node_type=Nodes.PostNode)
        if not (self.n2_id in project_graph.databasePostIDMap):
            raise err.NodeMissing("Could not find node 2 while creating recommendation link", node_id=self.n2_id, node_type=Nodes.PostNode)
        if not (self.author_id in project_graph.databaseUserIDMap):
            raise err.NodeMissing("Could not find author node while creating recommendation link", node_id=self.author_id, node_type=Nodes.UserNode)
        n1 = project_graph.databasePostIDMap[self.n1_id]
        n2 = project_graph.databasePostIDMap[self.n2_id]
        author = project_graph.databaseUserIDMap[self.author_id]
        k = 0
        while (param.group_recommended, k) in project_graph.baseGraph[n1][n2]:
            k += 1
        project_graph.baseGraph.add_edge(n1, n2, key=("group_recommended", k), default_weight=param.default_edge_weight_recommendation, reputation_weight=author.get_recomendation_weight(), author=author)


class ViolentPostRemoval(GenericModification):
    def __init__(self, database_id):
        super().__init__()
        self.database_id = database_id

    def list_rep(self):
        return ["vr", self.database_id]

    def apply_to_graph(self, project_graph):
        if not (self.database_id in project_graph.databasePostIDMap):
            raise err.NodeMissing("Exception reached while violently removing node this node : "
                                  + str(self.database_id) + "this node does not exist", node_id=self.database_id)
        node = project_graph.databasePostIDMap[self.database_id]
        del project_graph.databasePostIDMap[self.database_id]
        # TODO : delete this node properly
        try:
            project_graph.baseGraph.remove_node(node)
        except nx.NetworkXError:
            raise err.InconsistentGraph("networkx error raised while removing node")


class PostDeletion(GenericModification):
    def __init__(self, database_id):
        super().__init__()
        self.database_id = database_id

    def list_rep(self):
        return ["pd", self.database_id]

    def apply_to_graph(self, project_graph):
        if not (self.database_id in project_graph.databasePostIDMap):
            raise err.NodeMissing("Exception reached while deleting this node : " + str(self.database_id)
                                  + ". could not find node", node_type=Nodes.PostNode, node_id=self.database_id)
        node = project_graph.databasePostIDMap[self.database_id]
        if node.deleted:
            raise err.NodeDeleted("Error encounterd while trying to delete a node : node already deleted",
                                  self.database_id)
        node.deleted = True


class PostModification(GenericModification):
    def __init__(self, database_id, new_size=-1, new_tags=None):
        super().__init__()
        self.database_id = database_id
        self.new_size = new_size
        self.modify_tags = (new_tags is not None)
        if self.modify_tags:
            self.new_tags = set(new_tags)
        else:
            self.new_tags = set()

    def list_rep(self):
        return ["pm", self.database_id, self.new_size] + self.new_tags

    def apply_to_graph(self, project_graph):
        if not (self.database_id in project_graph.databasePostIDMap):
            raise err.NodeMissing("Exception reached while modifiying this node : " + str(self.database_id)
                                  + ". node missing", node_type=Nodes.PostNode, node_id=self.database_id)
        node = project_graph.databasePostIDMap[self.database_id]
        if node.deleted:
            raise err.NodeDeleted("Error encounterd while trying to selfy a node : node has been deleted",
                                  self.database_id)
        if self.new_size != -1:
            node.size = self.new_size
        if self.modify_tags:
            current_tags = set()
            for edge in project_graph.baseGraph.out_edges(node):
                for i in project_graph.baseGraph[node][edge[1]].items():
                    if i[0][0] == param.tagged_with:
                        current_tags.add(edge[1])
            for t in current_tags.difference(self.new_tags):
                project_graph.baseGraph.remove_edge(node, t, key=(param.tagged_with, 0))
            for t in self.new_tags.difference(current_tags):
                project_graph.baseGraph.add_edge(node, t, key=(param.tagged_with, 0))


class NewTag(GenericModification):
    def __init__(self, database_id, slug):
        super().__init__()
        self.database_id = database_id
        self.slug = slug

    def list_rep(self):
        return ["nt", self.database_id, self.slug]

    def apply_to_graph(self, project_graph):
        if self.database_id in project_graph.databaseTagIDMap:
            raise err.NodeAlreadyExists("Error while creating this tag : " + self.slug + " Tag already exists",
                                        project_graph.tagSlugMap[self.slug], self.slug)
        new_node = Nodes.TagNode(self.database_id, self.slug)
        project_graph.databaseTagIDMap[self.database_id] = new_node
        project_graph.baseGraph.add_node(new_node)


class TagOnPost(GenericModification):
    def __init__(self, post, tag):
        super().__init__()
        self.post_database_id = post
        self.tag_database_id = tag

    def list_rep(self):
        return ["tp", self.post_database_id, self.tag_database_id]

    def apply_to_graph(self, project_graph):
        if not (self.post_database_id in project_graph.databasePostIDMap):
            raise err.NodeMissing("Error while tagging a post : post does not exist", Nodes.PostNode,
                                  self.post_database_id)
        if not (self.tag_database_id in project_graph.databaseTagIDMap):
            raise err.NodeMissing("Error while tagging a post : tag does not exist", Nodes.TagNode, self.tag_database_id)
        post_node = project_graph.databasePostIDMap[self.post_database_id]
        tag_node = project_graph.databaseTagIDMap[self.tag_database_id]
        if (param.tagged_with, 0) in project_graph.baseGraph[post_node][tag_node]:
            raise err.EdgeAlreadyExists("Error while tagging a post : post already has this tag", post_node, tag_node,
                                        self.post_database_id, self.tag_database_id, (param.tagged_with, 0))
        project_graph.baseGraph.add_edge(post_node, tag_node, key=(param.tagged_with, 0),
                                         default_weight=param.default_edge_weight_tag)


class TagFromPost(GenericModification):
    def __init__(self, post, tag):
        super().__init__()
        self.post_database_id = post
        self.tag_database_id = tag

    def list_rep(self):
        return ["tr", self.post_database_id, self.tag_database_id]

    def apply_to_graph(self, project_graph):
        if not (self.post_database_id in project_graph.databasePostIDMap):
            raise err.NodeMissing("Error while removing tag from a post : post does not exist", Nodes.PostNode,
                                  self.post_database_id)
        if not (self.tag_database_id in project_graph.databaseTagIDMap):
            raise err.NodeMissing("Error while removing tag from a post : tag does not exist", Nodes.TagNode,
                                  self.tag_database_id)
        post_node = project_graph.databasePostIDMap[self.post_database_id]
        tag_node = project_graph.databaseTagIDMap[self.tag_database_id]
        if not ("tagged_with", 0) in project_graph.baseGraph[post_node][tag_node]:
            raise err.EdgeDoesNotExist("Error while removing tag from a post : post does not have this tag", post_node,
                                       tag_node, self.post_database_id, self.tag_database_id, ("tagged_with", 0))
        project_graph.baseGraph.remove_edge(post_node, tag_node, key=("tagged_with", 0))


class NewVote(GenericModification):
    """When a user votes for a post. pass the id of the post, of the user,
    of the vote itself in the database, and pass the vote_type"""
    def __init__(self, post, author, vote, vote_type):
        super().__init__()
        self.post_id = post
        self.author_id = author
        self.vote_id = vote
        self.vote_type = vote_type

    def list_rep(self):
        return ["nv", self.post_id, self.author_id] + [self.vote_type]
        # TODO : create a list_rep function for the vote type

    def apply_to_graph(self, project_graph):
        if self.post_id not in project_graph.databasePostIDMap:
            raise err.NodeMissing("Exception reached while registering vote : post missing")
        if self.author_id not in project_graph.databaseUserIDMap:
            raise err.UserNodeMissing("Exception reached while registering a vote. user missing", self.author_id)
        if self.vote_id in project_graph.databaseVoteIDMap:
            raise err.EdgeAlreadyExists("", n1_id=self.author_id, n2_id=self.post_id,
                                        edge_key=(param.user_vote, self.vote_type))
        post = project_graph.databasePostIDMap[self.post_id]
        author = project_graph.databaseUserIDMap[self.author_id]
        project_graph.baseGraph.add_edge(author, post, key=(param.user_vote, self.vote_type), vote_id=self.vote_id,
                                         default_weight=param.default_edge_weight_vote)
        project_graph.databaseVoteIDMap[self.vote_id] = (author, post, (param.user_vote, self.vote_type))


class VoteCancellation(GenericModification):
    def __init__(self, vote_id):
        super().__init__()
        self.vote_id = vote_id

    def list_rep(self):
        return ["vc", self.vote_id]

    def apply_to_graph(self, project_graph):
        try:
            t = project_graph.databaseVoteIDMap[self.vote_id]
        except KeyError:
            raise err.EdgeDoesNotExist("Exception reached while removing vote edge : edge does no exist (not registered in databaseVoteIDMap)",
                                       n1_id=None, n2_id=None, edge_key=t[3], n1=t[0], n2=t[1])
        if t[0] not in g:
            raise err.InconsistentGraph("Exception reached while removing edge : author node missing")
        if t[1] not in g:
            raise err.InconsistentGraph("Exception reached while removing edge : post node missing")
        if t[3] not in g[t[0]][t[1]]:
            raise err.EdgeDoesNotExist("Exception reached while removing vote edge : edge does no exist (not found on baseGraph)",
                                       n1_id=None, n2_id=None, edge_key=t[3], n1=t[0], n2=t[1])
        project_graph.baseGraph.remove_edge(*t)


#print("GraphModifications successfully imported")
