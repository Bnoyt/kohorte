# -*- coding: utf-8 -*-

#libraries
import queue

#dependencies
import parameters as param
import ProjectController

class GraphModifier:
    def __init__(self, projectController):
        self._projectController = projectController

    def create_post(self, databaseID, noeud, tagList, size : int, parent=-1, value=-1):
        '''A utiliser quand un utilisateur publie un nouveau post
        Noeud est l'ID BDD du Noeud du graphe de reflexion sous lequel ce post a été créé
        parent est l'ID BDD du post auquel celui-ci est une reponse, ou -1 si le post n'est pas une reponse
        tagList doit etre une liste de tous les mots cles, donnes sous forme de strings netoyés (tels qu'ils sont soques dans la BDD)
         Ne pas passer de Tag en argument avant d`avoir creé ces mots-clés avec create_tag. '''
        self._projectController.push_modification(NewPost(databaseID=databaseID, noeud=noeud, tags=tagList,size=size, parent=parent, value=value))

    def create_tag(self, slug : str):
        '''La premiere fois qu'un mot-clé est utilisé et ajouté a la base de données, il doit être passé via cette fonction
        Le string qui reprsente le tag est crée en filtrant ce que l'utilisateur a rentré comme tag, et sera utilisé comme clé'''
        self._projectController.push_modification(NewTag(slug=slug))

    def create_recommendation_link(self, node1DatabaseID, node2DatabaseID, weight=1.0):
        '''Creation d'un lien de recommendation entre deux posts, via le boutton [recommender une fusion]'''
        self._projectController.push_modification(NewRecommendationLink(n1=node1DatabaseID, n2=node2DatabaseID, weight=weight))

    def remove_post(self, databaseID):
        '''Suprime toutes les données concernant ce post. Le graphe peut refuser de supprimer le post si il est trop important.
        Opération assez violente, a éviter de préférence. Plutot utiliser delete_post a la place'''
        self._projectController.push_modification(PostRemoval(databaseID=databaseID))

    def delete_post(self, databaseID):
        '''Marque un post comme supprimé, mais conserve les données liées à ce post.
        Il est impératif que les données du post soient également conservé dans la base de donnée'''
        self._projectController.push_modification(PostDeletion(databaseID=databaseID))

    def modifyPost(self, databaseID, newSize):
        '''Fonction a utiliser pour les modifications de post a posteriori par les utilisateurs (bouton EDIT)'''
        self._projectController.push_modification(PostModification(databaseID=databaseID, newSize=newSize))

    def add_tag_to_post(self, post_database_id, tag_slug : str):
        ''' Ajoute un nouveau lien entre un tag deja existant et un post deja existant '''
        self._projectController.push_modification(TagOnPost(post_database_id=post_database_id, tag_slug=tag_slug))

    def remove_tag_from_post(self, post_database_id, tag_slug):
        '''retire un lien entre un tag et un post. Ne suprime ni le tag, ni le post'''
        self._projectController.push_modification(TagFromPost(post_database_id=post_database_id, tag_slug=tag_slug))


#Cette exception est la seule a ne pas etre dans error.py
#Ainsi, le code coté django, qui importera cette classe, y a accés
class ForbidenModificationRequest(Exception):
    def __init__(self, descriptor):
        super().__init__(descriptor)


class NewPost:
    def __init__(self, databaseID, noeud, tags, size, parent, value):
        super().__init__()
        self.databaseID = databaseID
        self.parent = parent
        self.tags = tags
        self.size = size
        if value == -1:
            self.value = param.default_post_value
        else:
            self.value = value

        if size < 0:
            raise ForbidenModificationRequest("The new post was requested with a size of + " + str(size) + " The size of a post cannot be negative")

class NewRecommendationLink:
    def __init__(self, n1, n2, weight = 1.0):
        self.n1_id = n1
        self.n2_id = n2
        self.weight = weight

class PostRemoval:
    def __init__(self, databaseID):
        self.databaseID = databaseID

class PostDeletion:
    def __init__(self, databaseID):
        self.databaseID = databaseID

class PostModification:
    def __init__(self, databaseID, newSize):
        self.databaseID = databaseID
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