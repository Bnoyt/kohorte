# -*- coding: utf-8 -*-

# import libraries
import random as rnd

# import dependencies
import app.clustering.parameters as param


class BaseNode:

    ClassInt = 0

    def __init__(self, database_id):
        self.database_id = database_id
        self.randomised_id = rnd.randrange(self.database_id)
        self.deleted = False

    def __eq__(self, other):
        if isinstance(other, BaseNode):
            return self.database_id == other.database_id and type(self) == type(other)
        else:
            raise NotImplemented()

    def __lt__(self, other):
        if self.__eq__(other):
            return False
            # Ce test renvoie aussi NotImplemented si other n'est pas du bon type
        return (self.randomised_id, self.ClassInt, self.database_id) < (other.randomised_id, self.ClassInt, other.database_id)
        # Les noeuds sont compares par leur randomised_id et non par leur database_id.
        # Ceci sert à ajouter de l'aleatoire dans l'ordre des noeuds,
        # ainsi si jamais on range les noeuds dans une structure de type arbre binaire de recherche,
        #  on ne risque pas d'être dans un cas particulier indesirable

    def __le__(self, other):
        if self.__eq__(other) :
            return True
        return (self.randomised_id, self.ClassInt, self.database_id) < (other.randomised_id, self.ClassInt, other.database_id)

    def __gt__(self, other):
        if self.__eq__(other):
            return False
        return (self.randomised_id, self.ClassInt, self.database_id) > (other.randomised_id, self.ClassInt, other.database_id)

    def __ge__(self, other):
        if self.__eq__(other):
            return True
        return (self.randomised_id, self.ClassInt, self.database_id) > (other.randomised_id, self.ClassInt, other.database_id)

    def __repr__(self):
        return "<supergraph.tg_node>"

    def __str__(self):
        return "(" + self.database_id + ") generic_node"

    def __hash__(self):
        return self.database_id


class PostNode(BaseNode):
    """Noeud correspondant a un post"""
    def __init__(self, database_id, size, **kwargs):
        super().__init__(database_id)
        self.size = size
        if "value" in kwargs:
            self.value = kwargs["value"]
        else:
            self.value = param.post_node_default_value
        self.deleted = False

    def __str__(self):
        return "(" + str(self.database_id) + ") post node : " + str(self.value)


class NoeudNode(BaseNode):
    """Noeud correspondant a un Noeud du graphe de reflexion"""
    def __init__(self, database_id):
        super().__init__(database_id)

    def __str__(self):
        return "(" + str(self.database_id) + ") noeud node"


class UserNode(BaseNode):
    def __init__(self, database_id):
        super().__init__(database_id)

    def __str__(self):
        return "(" + str(self.database_id) + ") utilisateur node"

    def get_recomendation_weight(self):
        """returns the reputation_weight value for any recomendation link which the author publishes"""
        pass


class SourceNode(BaseNode):
    def __init__(self, database_id):
        super().__init__(database_id)
        self.is_wikipedia = True
        self.reliability = 5

    def __str__(self):
        return "(" + str(self.database_id) + ") source node : " + "wikipedia"


class TagNode(BaseNode):
    def __init__(self, database_id, slug):
        super().__init__(database_id)
        self.slug = slug

    def __str__(self):
        return "(" + str(self.database_id) + ") tag node : " + self.slug


class QuoteNode(BaseNode):
    def __init__(self, database_id):
        super().__init__(database_id)

    def __str__(self):
        return "(" + str(self.database_id) + ") tag node"

