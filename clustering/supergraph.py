# -*- coding: utf-8 -*-
"""
Created on Wed Nov 22 17:14:39 2017

@author: anatole
"""
#import packages
import random as rnd

#import perso
import networkx as nx
import modifications as mods
import errors as err


class unique_id_generator:
    def __init__(self):
        self.id_counter = 0
    def get_id(self):
        self.id_counter += 1
        return(self.id_counter)

'''node types'''

class tg_node:
    def __init__(self, uig):
        self.unique_id = uig.get_id()
        self.randomised_id = rnd.randrange(self.unique_id)

    def __eq__(self, other):
        if(type(other) == tg_node):
            return(self.unique_id == other.unique_id)
        else:
            raise(NotImplemented)

    def __lt__(self, other):
        if(self.__eq__(other)):
            return(False)
            #Ce test renvoie aussi NotImplemented si other n'est pas du bon type
        return((self.randomised_id, self.unique_id) < (other.randomised_id, other.unique_id))
        #Les noeuds sont compares par leur randomised_id et non par leur unique_id. Ceci sert à ajouter de l'aleatoire dans l'ordre des noeuds,
        # ainsi si jamais on range les noeuds dans une structure de type arbre binaire de recherche, on ne risque pas d'être dans un cas particulier indesirable


    def __le__(self, other):
        if(self.__eq__(other)):
            return(True)
        return((self.randomised_id, self.unique_id) < (other.randomised_id, other.unique_id))

    def __gt__(self, other):
        if(self.__eq__(other)):
            return(False)
        return((self.randomised_id, self.unique_id) > (other.randomised_id, other.unique_id))

    def __ge__(self, other):
        if(self.__eq__(other)):
            return(True)
        return((self.randomised_id, self.unique_id) > (other.randomised_id, other.unique_id))

    def __repr__(self):
        return("<supergraph.tg_node>")

    def __str__(self):
        return("(" + self.unique_id + ") generic_node")

    def __hash__(self):
        return(self.unique_id)


class post_node(tg_node):
    def __init__(self, uig, size, value, sql_id):
        super().__init__(uig)
        self.size = size
        self.value = value
        self.sql_id = sql_id

    def __str__(self):
        return( "(" + str(self.unique_id) + ") post node : " + self.value)

class noeud_node:
    def __init__(self, uig, global_graph_id):
        super().__init__(uig)
        self.global_graph_id = global_graph_id

    def __str__(self):
        return( "(" + str(self.unique_id) + ") noeud node : ")

class utilisateur_node:
    def __init__(self, uig):
        super().__init__(uig)
        self.karma = 0
        self.username = "bob"

    def __str__(self):
        return ("(" + str(self.unique_id) + ") utilisateur node : " + self.username)

class source_node:
    def __init__(self, uig):
        super().__init__(uig)
        self.is_wikipedia = True
        self.reliability = 5

    def __str__(self):
        return ("(" + str(self.unique_id) + ") source node : " + "wikipedia")

class tag_node:
    def __init__(self, uig, slug):
        super().__init__(uig)
        self.jocularity = 1717
        self.slug = slug

    def __str__(self):
        return ("(" + str(self.unique_id) + ") tag node : " + self.slug)

'''new exceptions'''



'''graph modification classes'''




def write_to_graph(modif, g : nx.MultiDiGraph, uig : unique_id_generator, sql_id_map):

    if(type(modif) == mods.create_post):
        if (modif.sql_id in sql_id_map):
            raise err.inconsistent_graph(type=err.inconsistent_graph.node_exists, node_id=modif.sql_id)
        new_node = post_node(uig, modif.size, modif.value, modif.sql_id)
        sql_id_map[modif.sql_id] = new_node
        g.add_node(new_node)
        if (modif.parent != -1):
            try:
                parent_node = sql_id_map[modif.parent]
            except KeyError:
                raise err.inconsistent_graph(type=err.inconsistent_graph.node_missing, node_id=modif.parent, details="missing parent post")
            g.add_edge(new_node, parent_node, key="parent_post")
        return

    if(type(modif) == mods.recommend_link):
        if not (modif.p1 in sql_id_map):
            raise err.inconsistent_graph(type=err.inconsistent_graph.node_missing, node_id=modif.p1)
        if not (modif.p2 in sql_id_map):
            raise err.inconsistent_graph(type=err.inconsistent_graph.node_missing, node_id=modif.p2)
        n1 = sql_id_map[modif.n1_id]
        n2 = sql_id_map[modif.n2_id]
        k = 0
        while(("group_recommended", k) in g[n1][n2]):
            k += 1
        g.add_edge(n1, n2, key=("group_recommended", k), weight=modif.weight)
        return

    if( type(modif) == mods.remove_post ):
        if not (modif.sql_id in sql_id_map):
            raise err.inconsistent_graph(type=err.inconsistent_graph.node_missing, node_id=modif.sql_id)
        node = sql_id_map[modif.sql_id]
        del sql_id_map[modif.sql_id]
        #TODO : call a method in graph_master which removes this post from all eventual locations (specific to remove_post)
        try:
            g.remove_node(node)
        except nx.NetworkXError:
            raise err.inconsistent_graph(type=err.inconsistent_graph.graph_idMap_inconsistency, node=node, node_id=sql_id_map)

    if(type(modif) == mods.edit_post):
        if not (modif.sql_id in sql_id_map):
            raise err.inconsistent_graph(type=err.inconsistent_graph.node_missing, node_id=modif.sql_id)
        node = sql_id_map[modif.sql_id]
        node.size = modif.new_size
    



def update_graph(the_graph, update_list, uig, sql_id_map):
    for modif in update_list:
        try:
            write_to_graph(modif, the_graph, uig, sql_id_map)
        except err.inconsistent_graph_exception:
            pass
            #TODO : write some log and remember that a problem occured. After the problems become too problematic, the graph is rebooted


'''
The edge identification Keys are of the form (string, int), where the string is a type identifier and the int is for multiple edges of the same type
Here are these id string used as keys for the MultiGraph

parent_post
group_recommended

Non-oriented edges are always stored as oriented edges from the smallest to the largest node (using built-in node comparaison)

'''