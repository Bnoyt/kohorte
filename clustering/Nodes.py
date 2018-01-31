# -*- coding: utf-8 -*-

# import libraries
import random as rnd

# import dependencies
import parameters as param


class BaseNode:
    def __init__(self, uniqueID):
        self.uniqueID = uniqueID
        self.randomisedID = rnd.randrange(self.uniqueID)
        self.deleted = False

    def __eq__(self, other):
        if type(other) == BaseNode:
            return self.uniqueID == other.uniqueID
        else:
            raise NotImplemented()

    def __lt__(self, other):
        if self.__eq__(other):
            return False
            # Ce test renvoie aussi NotImplemented si other n'est pas du bon type
        return (self.randomisedID, self.uniqueID) < (other.randomisedID, other.uniqueID)
        # Les noeuds sont compares par leur randomisedID et non par leur uniqueID.
        # Ceci sert à ajouter de l'aleatoire dans l'ordre des noeuds,
        # ainsi si jamais on range les noeuds dans une structure de type arbre binaire de recherche,
        #  on ne risque pas d'être dans un cas particulier indesirable

    def __le__(self, other):
        if self.__eq__(other) :
            return True
        return (self.randomisedID, self.uniqueID) < (other.randomisedID, other.uniqueID)

    def __gt__(self, other):
        if self.__eq__(other):
            return False
        return (self.randomisedID, self.uniqueID) > (other.randomisedID, other.uniqueID)

    def __ge__(self, other):
        if self.__eq__(other):
            return True
        return (self.randomisedID, self.uniqueID) > (other.randomisedID, other.uniqueID)

    def __repr__(self):
        return "<supergraph.tg_node>"

    def __str__(self):
        return "(" + self.uniqueID + ") generic_node"

    def __hash__(self):
        return(self.uniqueID)


class PostNode(BaseNode):
    """Noeud correspondant a un post"""
    def __init__(self, uniqueID, size, sql_id, **kwargs):
        super().__init__(uniqueID)
        self.size = size
        if "value" in kwargs:
            self.value = kwargs["value"]
        else:
            self.value = param.post_node_default_value
        self.sql_id = sql_id
        self.deleted = False

    def __str__(self):
        return "(" + str(self.uniqueID) + ") post node : " + self.value


class NoeudNode(BaseNode):
    """Noeud correspondant a un Noeud du graphe de reflexion"""
    def __init__(self, uniqueID, global_graph_id):
        super().__init__(uniqueID)
        self.global_graph_id = global_graph_id

    def __str__(self):
        return "(" + str(self.uniqueID) + ") noeud node : "


class UserNode(BaseNode):
    def __init__(self, uniqueID):
        super().__init__(uniqueID)
        self.karma = 0
        self.username = "bob"

    def __str__(self):
        return "(" + str(self.uniqueID) + ") utilisateur node : " + self.username

    def get_recomendation_weight(self):
        """returns the reputation_weight value for any recomendation link which the author publishes"""
        pass


class SourceNode(BaseNode):
    def __init__(self, uniqueID):
        super().__init__(uniqueID)
        self.is_wikipedia = True
        self.reliability = 5

    def __str__(self):
        return "(" + str(self.uniqueID) + ") source node : " + "wikipedia"


class TagNode(BaseNode):
    def __init__(self, uniqueID, slug):
        super().__init__(uniqueID)
        self.slug = slug

    def __str__(self):
        return "(" + str(self.uniqueID) + ") tag node : " + self.slug
