# -*- coding: utf-8 -*-

#imports lib
import networkx as nx
import queue

# import dependencies
import GraphModifications as mods
import errors as err


class ProjectGraph:
    def __init__(self, projectController, projectLogger):
        self.projectController = projectController
        self.projectLogger = projectLogger
        self.baseGraph = nx.MultiDiGraph()

        self.databasePostIDMap = dict()
        self.databaseNoeudIDMap = dict()
        self.databaseUserIDMap = dict()
        self.databaseTagIDMap = dict()

        self._uniqueIDCounter = 0

    def get_unique_id(self):
        self._uniqueIDCounter += 1
        return self._uniqueIDCounter

    def apply_modif(self, modif: mods.GenericModification):
        try:
            modif.apply_to_graph(self)
        except err.InconsistentGraph:
            pass

    def apply_modifications(self, modification_queue):
        pass


print("ProjectGraph successfully imported")

    # Clés utilisées pour les arrêtes :
    # parent_post : post enfant -> post parent
    # tagged_with : post -> tg utilise sur le post
    # group_recommended -> post -> post | suggestion d'un utilisateur de grouper ces posts

