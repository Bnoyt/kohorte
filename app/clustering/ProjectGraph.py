# -*- coding: utf-8 -*-

#imports lib
import networkx as nx
import queue

# import dependencies
import app.clustering.GraphModifications as mods
import app.clustering.errors as err


class ProjectGraph:
    def __init__(self, projectController, projectLogger, pg=None):
        self.projectController = projectController
        self.projectLogger = projectLogger

        if pg is None:

            self.baseGraph = nx.MultiDiGraph()

            self.databasePostIDMap = dict()
            self.databaseNoeudIDMap = dict()
            self.databaseUserIDMap = dict()
            self.databaseTagIDMap = dict()
            self.databaseVoteIDMap = dict()

            self.time_dilation = 1.0


        else:

            self.baseGraph = pg.baseGraph
            self.databasePostIDMap = pg.databasePostIDMap
            self.databaseNoeudIDMap = pg.databaseNoeudIDMap
            self.databaseUserIDMap = pg.databaseUserIDMap
            self.databaseTagIDMap = pg.databaseTagIDMap
            self.databaseVoteIDMap = pg.databaseVoteIDMap

            self.time_dilation = pg.time_dilation

    def apply_modification(self, modif: mods.GenericModification):
        try:
            modif.apply_to_graph(self)
        except err.InconsistentGraph:
            pass

    def get_pickle_graph(self):
        return PickleGraph(self)


class PickleGraph:

    def __init__(self, pg : ProjectGraph):
        self.base_graph = pg.baseGraph
        self.databasePostIDMap = pg.databasePostIDMap
        self.databaseNoeudIDMap = pg.databaseNoeudIDMap
        self.databaseUserIDMap = pg.databaseUserIDMap
        self.databaseTagIDMap = pg.databaseTagIDMap
        self.databaseVoteIDMap = pg.databaseVoteIDMap

        self.time_dilation = pg.time_dilation

#print("ProjectGraph successfully imported")

    # Clés utilisées pour les arrêtes :
    # parent_post : post enfant -> post parent
    # tagged_with : post -> tg utilise sur le post
    # group_recommended -> post -> post | suggestion d'un utilisateur de grouper ces posts

