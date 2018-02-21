# -*- coding: utf-8 -*-

#imports lib
import networkx as nx
import queue

# import dependencies
import app.clustering.GraphModifications as mods
import app.clustering.errors as err
import app.clustering.DatabaseAccess as dba
import app.clustering.parameters as param


class ProjectGraph:
    def __init__(self, projectController, projectLogger, pg=None, cfg=None):
        self.projectController = projectController
        self.projectLogger = projectLogger

        self.branch_instructions = []

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

        if cfg is None:

            self.time_dilation = 1.0

        else:

            self.time_dilation = cfg.time_dilation

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
                self.baseGraph.add_edge(n0, n1, key=(edge_key, k), default_weight=param.def_w[edge_key])
            except KeyError as error:
                incoherences += 1
                # print("KeyError while loading graph : " + str(error))

        for edge in iterables["post_noeud"]:
            try:
                n0 = self.databasePostIDMap[edge[0]]
                n1 = self.databaseNoeudIDMap[edge[1]]
                self.baseGraph.add_edge(n0, n1, key=(param.belongs_to, 0), default_weight=param.def_w[param.belongs_to])
            except KeyError as error:
                incoherences += 1
                # print("KeyError while loading graph : " + str(error))

        for edge in iterables["post_uses_citation"]:
            try:
                n0 = self.databasePostIDMap[edge[0]]
                n1 = self.databaseCitationIDMap[edge[1]]
                k = 0
                edge_key = param.belongs_to
                while (edge_key, k) in self.baseGraph[n0][n1]:
                    k += 1
                self.baseGraph.add_edge(n0, n1, key=(edge_key, k), default_weight=param.def_w[edge_key])
            except KeyError as error:
                incoherences += 1
                # print("KeyError while loading graph : " + str(error))

        for edge in iterables["post_source_citation"]:
            try:
                n0 = self.databasePostIDMap[edge[0]]
                n1 = self.databaseCitationIDMap[edge[1]]
                k = 0
                edge_key = param.source_citation
                while (edge_key, k) in self.baseGraph[n0][n1]:
                    k += 1
                self.baseGraph.add_edge(n0, n1, key=(edge_key, k), default_weight=param.def_w[edge_key])
            except KeyError as error:
                incoherences += 1
                # print("KeyError while loading graph : " + str(error))

        for edge in iterables["raporteur_citation"]:
            try:
                n0 = self.databaseCitationIDMap[edge[0]]
                n1 = self.databaseUserIDMap[edge[1]]
                k = 0
                edge_key = param.raporteur_citation
                while (edge_key, k) in self.baseGraph[n0][n1]:
                    k += 1
                self.baseGraph.add_edge(n0, n1, key=(edge_key, k), default_weight=param.def_w[edge_key])
            except KeyError as error:
                incoherences += 1
                # print("KeyError while loading graph : " + str(error))

        for edge in iterables["aretes_reflexion"]:
            try:
                n0 = self.databaseNoeudIDMap[edge[0]]
                n1 = self.databaseNoeudIDMap[edge[1]]
                k = 0
                edge_key = param.parent_noeud
                while (edge_key, k) in self.baseGraph[n0][n1]:
                    k += 1
                self.baseGraph.add_edge(n0, n1, key=(edge_key, k), default_weight=param.def_w[edge_key])
            except KeyError as error:
                incoherences += 1
                # print("KeyError while loading graph : " + str(error))

        for edge in iterables["vote"]:
            try:
                n0 = self.databaseUserIDMap[edge[0]]
                n1 = self.databasePostIDMap[edge[1]]
                d = edge[3]
                k = 0
                edge_key = param.user_vote
                while (edge_key, k) in self.baseGraph[n0][n1]:
                    k += 1
                self.baseGraph.add_edge(n0, n1, key=(edge_key, k), default_weight=param.def_w[edge_key],
                                        vote_type=d["vote_type"])
            except KeyError as error:
                incoherences += 1
                # print("KeyError while loading graph : " + str(error))

        for edge in iterables["auteur_post"]:
            try:
                n0 = self.databasePostIDMap[edge[0]]
                n1 = self.databaseUserIDMap[edge[1]]
                edge_key = param.auteur_of_post
                self.baseGraph.add_edge(n0, n1, key=(edge_key, 0), default_weight=param.def_w[edge_key])
            except KeyError as error:
                incoherences += 1
                # print("KeyError while loading graph : " + str(error))

        for edge in iterables["suivi_noeud"]:
            try:
                n0 = self.databaseUserIDMap[edge[0]]
                n1 = self.databaseNoeudIDMap[edge[1]]
                edge_key = param.parent_noeud
                self.baseGraph.add_edge(n0, n1, key=(edge_key, 0), default_weight=param.def_w[edge_key])
            except KeyError as error:
                incoherences += 1
                # print("KeyError while loading graph : " + str(error))

        print("Graph loaded. No critical issue encountered. " + str(incoherences)
              + " incoherences encounered and silenced.")

    def apply_modification(self, modif: mods.GenericModification):
        try:
            modif.apply_to_graph(self)
        except err.InconsistentGraph:
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


class CSVConfigs:

    def __init__(self, pg: ProjectGraph):

        self.time_dilation = pg.time_dilation

    def write_to_file(self, csv_file):

        csv_file.writerow(["time_dilation", self.time_dilation])

    def read_from_file(self, csv_file):

        self.time_dilation = csv_file.readrow()[1]
