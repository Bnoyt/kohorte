# -*- coding: utf-8 -*-

#imports lib
import networkx as nx
import queue

#import dependencies
import ProjectController
import GraphModifications as mods
import errors as err
import Nodes
import parameters as param


class ProjectGraph:
    def __init__(self, projectController, projectLogger):
        self._projectController = projectController
        self._projectLogger = projectLogger
        self._baseGraph = nx.MultiDiGraph()

        self._databasePostIDMap = dict()
        self._databaseNoeudIDMap = dict()
        self._databaseUserIDMap = dict()
        self._databaseSlugIDMap = dict()

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

    # Clés utilisées pour les arrêtes :
    # parent_post : post enfant -> post parent
    # tagged_with : post -> tg utilise sur le post
    # group_recommended -> post -> post | suggestion d'un utilisateur de grouper ces posts

