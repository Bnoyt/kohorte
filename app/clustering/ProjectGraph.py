# -*- coding: utf-8 -*-

#imports lib
import networkx as nx
import queue

# import dependencies
import GraphModifications as mods
import errors as err


class ProjectGraph:
    def __init__(self, projectController, projectLogger, pg=None):
        self.projectController = projectController
        self.projectLogger = projectLogger
        self.baseGraph = nx.MultiDiGraph()

        if pg is None:

            self.databasePostIDMap = dict()
            self.databaseNoeudIDMap = dict()
            self.databaseUserIDMap = dict()
            self.databaseTagIDMap = dict()
            self.databaseVoteIDMap = dict()

            self._uniqueIDCounter = 0

        else:

            self.base_graph = pg.baseGraph
            self.databasePostIDMap = pg.databasePostIDMap
            self.databaseNoeudIDMap = pg.databaseNoeudIDMap
            self.databaseUserIDMap = pg.databaseUserIDMap
            self.databaseTagIDMap = pg.databaseTagIDMap
            self.databaseVoteIDMap = pg.databaseVoteIDMap


    def get_unique_id(self):
        self._uniqueIDCounter += 1
        return self._uniqueIDCounter

    def apply_modif(self, modif: mods.GenericModification):
        try:
            modif.apply_to_graph(self)
        except err.InconsistentGraph:
            pass

    def apply_modifications(self, modification_queue, logger, expect_errors):
        while not modification_queue.empty():
            modif = modification_queue.get()
            logger.register(modif)
            modif.apply_to_graph(self)

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


print("ProjectGraph successfully imported")

    # Clés utilisées pour les arrêtes :
    # parent_post : post enfant -> post parent
    # tagged_with : post -> tg utilise sur le post
    # group_recommended -> post -> post | suggestion d'un utilisateur de grouper ces posts

