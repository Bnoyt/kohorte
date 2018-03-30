# -*- coding: utf-8 -*-

#imports lib
import networkx as nx
import logging

# import dependencies
import app.clustering.GraphModifications as mods
import app.clustering.errors as errors
import app.clustering.DatabaseAccess as dba
import app.clustering.parameters as param


class ProjectGraph:
    def __init__(self, projectController, projectLogger, projectParam, pg=None):
        self.projectController = projectController
        self.projectLogger = projectLogger
        self.projectParam = projectParam

        self.branch_instructions = []

        self.LOGGER = logging.getLogger('agorado.machinerie.' + str(projectController.database_id) + '.ProjectGraph')

        if pg is None:

            self.baseGraph = nx.MultiDiGraph()

            self.databasePostIDMap = dict()
            self.databaseNoeudIDMap = dict()
            self.databaseUserIDMap = dict()
            self.databaseTagIDMap = dict()
            self.databaseCitationIDMap = dict()
            self.databaseVoteIDMap = dict()

        else:

            self.baseGraph = pg.baseGraph
            self.databasePostIDMap = pg.databasePostIDMap
            self.databaseNoeudIDMap = pg.databaseNoeudIDMap
            self.databaseUserIDMap = pg.databaseUserIDMap
            self.databaseTagIDMap = pg.databaseTagIDMap
            self.databaseCitationIDMap = pg.databaseCitationIDMap
            self.databaseVoteIDMap = pg.databaseVoteIDMap

    def load_from_database(self, database_access: dba.DatabaseAccess):

        iterables = database_access.get_database_iterable()

        self.baseGraph = nx.MultiDiGraph()

        self.databasePostIDMap = dict()
        self.databaseNoeudIDMap = dict()
        self.databaseUserIDMap = dict()
        self.databaseTagIDMap = dict()
        self.databaseCitationIDMap = dict()
        self.databaseVoteIDMap = dict()

        incoherences = 0

        for node in iterables["post"]:
            self.baseGraph.add_node(node)
            self.databasePostIDMap[node.database_id] = node

        for node in iterables["noeud"]:
            self.baseGraph.add_node(node)
            self.databaseNoeudIDMap[node.database_id] = node

        for node in iterables["tag"]:
            self.baseGraph.add_node(node)
            self.databaseTagIDMap[node.database_id] = node

        for node in iterables["citation"]:
            self.baseGraph.add_node(node)
            self.databaseCitationIDMap[node.database_id] = node

        for node in iterables["user"]:
            self.baseGraph.add_node(node)
            self.databaseUserIDMap[node.database_id] = node

        for edge in iterables["tag_post"]:
            try:
                n0 = self.databaseTagIDMap[edge[0]]
                n1 = self.databasePostIDMap[edge[1]]
                k = 0
                edge_key = param.tagged_with
                while n1 in self.baseGraph[n0] and (edge_key, k) in self.baseGraph[n0][n1]:
                    k += 1
                self.baseGraph.add_edge(n0, n1, key=(edge_key, k),
                                        default_weight=self.projectParam.default_edge_weight[edge_key])
            except KeyError:
                self.LOGGER.debug("failed while loading a (tag to post) edge from "+str(edge[0])+" to "+str(edge[1]))
                incoherences += 1

        for edge in iterables["post_noeud"]:
            try:
                n0 = self.databasePostIDMap[edge[0]]
                n1 = self.databaseNoeudIDMap[edge[1]]
                self.baseGraph.add_edge(n0, n1, key=(param.belongs_to, 0), 
                                        default_weight=self.projectParam.default_edge_weight[param.belongs_to])
            except KeyError:
                self.LOGGER.debug("failed while loading a (post tp noeud) edge from "+str(edge[0])+" to "+str(edge[1]))
                incoherences += 1

        for edge in iterables["post_uses_citation"]:
            try:
                n0 = self.databasePostIDMap[edge[0]]
                n1 = self.databaseCitationIDMap[edge[1]]
                k = 0
                edge_key = param.belongs_to
                while self.baseGraph.has_edge(n0, n1, key=(edge_key, k)):
                    k += 1
                self.baseGraph.add_edge(n0, n1, key=(edge_key, k),
                                        default_weight=self.projectParam.default_edge_weight[edge_key])
            except KeyError as error:
                self.LOGGER.debug("failed while loading a (post uses citation) edge from "+str(edge[0])+" to "+str(edge[1]))
                incoherences += 1

        for edge in iterables["citation_source_post"]:
            try:
                n0 = self.databaseCitationIDMap[edge[0]]
                n1 = self.databasePostIDMap[edge[1]]
                k = 0
                edge_key = param.source_citation
                while self.baseGraph.has_edge(n0, n1, key=(edge_key, k)):
                    k += 1
                self.baseGraph.add_edge(n0, n1, key=(edge_key, k),
                                        default_weight=self.projectParam.default_edge_weight[edge_key])
            except KeyError:
                self.LOGGER.debug("failed while loading a (citation source post) edge from "+str(edge[0])+" to "+str(edge[1]))
                incoherences += 1

        for edge in iterables["raporteur_citation"]:
            try:
                n0 = self.databaseCitationIDMap[edge[0]]
                n1 = self.databaseUserIDMap[edge[1]]
                k = 0
                edge_key = param.raporteur_citation
                while self.baseGraph.has_edge(n0, n1, key=(edge_key, k)):
                    k += 1
                self.baseGraph.add_edge(n0, n1, key=(edge_key, k),
                                        default_weight=self.projectParam.default_edge_weight[edge_key])
            except KeyError:
                self.LOGGER.debug("failed while loading a (raporteur citation) edge from "+str(edge[0])+" to "+str(edge[1]))
                incoherences += 1

        for edge in iterables["aretes_reflexion"]:
            try:
                n0 = self.databaseNoeudIDMap[edge[0]]
                n1 = self.databaseNoeudIDMap[edge[1]]
                k = 0
                edge_key = param.parent_noeud
                while self.baseGraph.has_edge(n0, n1, key=(edge_key, k)):
                    k += 1
                self.baseGraph.add_edge(n0, n1, key=(edge_key, k),
                                        default_weight=self.projectParam.default_edge_weight[edge_key])
            except KeyError:
                self.LOGGER.debug("failed while loading a (arrete reflexion) edge from "+str(edge[0])+" to "+str(edge[1]))
                incoherences += 1

        for edge in iterables["vote"]:
            try:
                n0 = self.databaseUserIDMap[edge[0]]
                n1 = self.databasePostIDMap[edge[1]]
                d = edge[2]
                k = 0
                edge_key = param.user_vote
                while self.baseGraph.has_edge(n0, n1, key=(edge_key, k)):
                    k += 1
                self.baseGraph.add_edge(n0, n1, key=(edge_key, k),
                                        default_weight=self.projectParam.default_edge_weight[edge_key],
                                        vote_type=d["vote_type"])
            except KeyError:
                self.LOGGER.debug("failed while loading a (tag to post) edge from "+str(edge[0])+" to "+str(edge[1]))
                incoherences += 1

        for edge in iterables["auteur_post"]:
            try:
                n0 = self.databasePostIDMap[edge[0]]
                n1 = self.databaseUserIDMap[edge[1]]
                edge_key = param.auteur_of_post
                self.baseGraph.add_edge(n0, n1, key=(edge_key, 0),
                                        default_weight=self.projectParam.default_edge_weight[edge_key])
            except KeyError:
                self.LOGGER.debug("failed while loading a (auteur of post) edge from "+str(edge[0])+" to "+str(edge[1]))
                incoherences += 1

        for edge in iterables["suivi_noeud"]:
            try:
                n0 = self.databaseUserIDMap[edge[0]]
                n1 = self.databaseNoeudIDMap[edge[1]]
                edge_key = param.parent_noeud
                self.baseGraph.add_edge(n0, n1, key=(edge_key, 0),
                                        default_weight=self.projectParam.default_edge_weight[edge_key])
            except KeyError:
                self.LOGGER.debug("failed while loading a (suivi noeud) edge from "+str(edge[0])+" to "+str(edge[1]))
                incoherences += 1

        if incoherences:
            info = str(incoherences) + " issues encountered and silenced while loading graph." + \
                   " The graph is probably incorrect."
            self.LOGGER.warning(info)

        self.LOGGER.info("Graph successfully loaded")

    def apply_modification(self, modif: mods.GenericModification):
        try:
            modif.apply_to_graph(self)
        except errors.InconsistentGraph:
            pass

    def get_pickle_graph(self):
        return PickleGraph(self)


class PickleGraph:

    def __init__(self, pg: ProjectGraph):
        self.base_graph = pg.baseGraph
        self.databasePostIDMap = pg.databasePostIDMap
        self.databaseNoeudIDMap = pg.databaseNoeudIDMap
        self.databaseUserIDMap = pg.databaseUserIDMap
        self.databaseTagIDMap = pg.databaseTagIDMap
        self.databaseCitationIDMap = pg.databaseCitationIDMap
        self.databaseVoteIDMap = pg.databaseVoteIDMap


class PickleAnalysis:

    def __init__(self, pg: ProjectGraph):
        pass

