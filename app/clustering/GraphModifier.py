# -*- coding: utf-8 -*-

# libraries
import queue

# dependencies
import parameters as param
import ProjectController


class GraphModifier:

    __modifier_reference = dict()

    @staticmethod
    def get_graph_modifier(cls, project_name):
        try:
            return cls.__modifier_reference[project_name]
        except KeyError:
            raise ForbidenModificationRequest("The project named " + project_name + " does not exist")

    def __init__(self, name):
        self.name = name
        self.__modifier_reference[name] = self
        self._pendingModifications = queue.Queue()

    def _push_modification(self, modif):
        self._pendingModifications.put(modif)

    def pull_all_modifications(self):
        pass

    def clear_all_modifications(self):
        pass

    def create_post(self, database_id, noeud, tag_list, size: int, parent=-1, value=-1):
        """A utiliser quand un utilisateur publie un nouveau post
        Noeud est l'ID BDD du Noeud du graphe de reflexion sous lequel ce post a été créé
        parent est l'ID BDD du post auquel celui-ci est une reponse, ou -1 si le post n'est pas une reponse
        tag_list doit etre une liste de tous les mots cles, donnes sous forme de strings netoyés (tels qu'ils sont soques dans la BDD)
        Ne pas passer de Tag en argument avant d`avoir creé ces mots-clés avec create_tag. """
        self._push_modification(NewPost(database_id=database_id, noeud=noeud, tags=tag_list, size=size, parent=parent, value=value))

    def create_tag(self, slug : str):
        """La premiere fois qu'un mot-clé est utilisé et ajouté a la base de données, il doit être passé via cette fonction
        Le string qui reprsente le tag est crée en filtrant ce que l'utilisateur a rentré comme tag, et sera utilisé comme clé"""
        self._push_modification(NewTag(slug=slug))

    def create_recommendation_link(self, node1_database_id, node2_database_id, weight=1.0):
        """Creation d'un lien de recommendation entre deux posts, via le boutton [recommender une fusion]"""
        self._push_modification(NewRecommendationLink(n1=node1_database_id, n2=node2_database_id, weight=weight))

    def remove_post(self, database_id):
        """Suprime toutes les données concernant ce post. Le graphe peut refuser de supprimer le post si il est trop important.
        Opération assez violente, a éviter de préférence. Plutot utiliser delete_post a la place"""
        self._push_modification(PostRemoval(database_id=database_id))

    def delete_post(self, database_id):
        """Marque un post comme supprimé, mais conserve les données liées à ce post.
        Il est impératif que les données du post soient également conservé dans la base de donnée"""
        self._push_modification(PostDeletion(database_id=database_id))

    def modify_post(self, database_id, newSize):
        """Fonction a utiliser pour les modifications de post a posteriori par les utilisateurs (bouton EDIT)"""
        self._push_modification(PostModification(database_id=database_id, newSize=newSize))

    def add_tag_to_post(self, post_database_id, tag_slug : str):
        """ Ajoute un nouveau lien entre un tag deja existant et un post deja existant """
        self._push_modification(TagOnPost(post_database_id=post_database_id, tag_slug=tag_slug))

    def remove_tag_from_post(self, post_database_id, tag_slug):
        """retire un lien entre un tag et un post. Ne suprime ni le tag, ni le post"""
        self._push_modification(TagFromPost(post_database_id=post_database_id, tag_slug=tag_slug))

    def read_modification_from_list(self, l):
        try:
            if l[0] == "np":
                return NewPost(l[1], l[2], l[5:], l[3], l[4])
            if l[0] == "nr":
                return NewRecommendationLink(l[1], l[2], l[3])
        except IndexError:
            raise ForbidenModificationRequest("Error while creating modification from this list : " + str(l)
                                              + "list does not have enough elements")

    def push_modification_from_list(self, l):
        self._push_modification(self.read_modification_from_list(l))


# Cette exception est la seule a ne pas etre dans error.py
# Ainsi, le code coté django, qui importera cette classe, y a accés
class ForbidenModificationRequest(Exception):
    def __init__(self, descriptor):
        super().__init__(descriptor)


class NewPost:
    def __init__(self, database_id, noeud, tags, size, parent, value):
        super().__init__()
        self.database_id = database_id
        self.noeud = noeud
        self.parent = parent
        self.tags = list(tags)
        self.size = size
        if value == -1:
            self.value = param.default_post_value
        else:
            self.value = value

        if size < 0:
            raise ForbidenModificationRequest("The new post was requested with a size of + " + str(size)
                                              + " The size of a post cannot be negative")

    def list_rep(self):
        return ["np", self.database_id, self.noeud, self.parent, self.size] + self.tags


class NewRecommendationLink:
    def __init__(self, n1, n2, weight = 1.0):
        self.n1_id = n1
        self.n2_id = n2
        self.weight = weight

    def list_rep(self):
        return ["nr", self.n1, self.n2, self.weight]

class PostRemoval:
    def __init__(self, database_id):
        self.database_id = database_id

class PostDeletion:
    def __init__(self, database_id):
        self.database_id = database_id

class PostModification:
    def __init__(self, database_id, newSize):
        self.database_id = database_id
        self.new_size = newSize

class NewTag:
    def __init__(self, slug):
        self.slug = slug

class TagOnPost:
    def __init__(self, post_database_id, tag_slug):
        self.post_database_id = post_database_id
        self.tag_slug = tag_slug

class TagFromPost:
    def __init__(self, post_database_id, tag_slug):
        self.post_database_id = post_database_id
        self.tag_slug = tag_slug