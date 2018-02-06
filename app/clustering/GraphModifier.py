# -*- coding: utf-8 -*-

# libraries
import queue

# dependencies
import GraphModifications as gm
import errors as err


class GraphModifier:

    __modifier_reference = dict()

    @staticmethod
    def get(project_database_id):
        try:
            return GraphModifier.__modifier_reference[project_database_id]
        except KeyError:
            raise KeyError("The project named " + project_database_id + " does not exist")

    def __init__(self, database_id):
        self.database_id = database_id
        self.__modifier_reference[database_id] = self
        self._pendingModifications = queue.Queue()

    def _push_modification(self, modif):
        self._pendingModifications.put(modif)

    def pull_all_modifications(self):
        rt = self._pendingModifications
        self._pendingModifications = queue.Queue()
        return rt


    def clear_all_modifications(self):
        self._pendingModifications = queue.Queue()

    def create_post(self, database_id, noeud, tag_list, quote_list, author, size: int, parent=-1, value=-1):
        """A utiliser quand un utilisateur publie un nouveau post
        Noeud est l'ID BDD du Noeud du graphe de reflexion sous lequel ce post a été créé
        parent est l'ID BDD du post auquel celui-ci est une reponse, ou -1 si le post n'est pas une reponse
        tag_list doit etre une liste de tous les mots cles, donnes sous forme de strings netoyés (tels qu'ils sont soques dans la BDD)
        Ne pas passer de Tag en argument avant d`avoir creé ces mots-clés avec create_tag. """
        self._push_modification(gm.NewPost(database_id=database_id, noeud=noeud, tags=tag_list, size=size, parent=parent))

    def create_tag(self, database_id, slug):
        """La premiere fois qu'un mot-clé est utilisé et ajouté a la base de données, il doit être passé via cette fonction
        Le string qui reprsente le tag est crée en filtrant ce que l'utilisateur a rentré comme tag, et sera utilisé comme clé"""
        self._push_modification(gm.NewTag(database_id, slug))

    def create_quote(self, origin_post, user):
        """Utiliser quand un utilisateur clique sur le bouton "citer" et enregistre une citation"""
        pass

    def forget_quote(self, quote):
        pass

    def create_recommendation_link(self, node1, node2, author):
        """Creation d'un lien de recommendation entre deux posts, via le boutton [recommender une fusion]"""
        self._push_modification(gm.NewRecommendationLink(n1=node1, n2=node2, author=author))

    def violently_remove_post(self, database_id):
        """Suprime toutes les données concernant ce post. Le graphe peut refuser de supprimer le post si il est trop important.
        Opération assez violente, a éviter de préférence. Plutot utiliser delete_post a la place"""
        self._push_modification(gm.ViolentPostRemoval(database_id=database_id))

    def mark_post_deleted(self, database_id):
        """Marque un post comme supprimé, mais conserve les données liées à ce post.
        Il est impératif que les données du post soient également conservé dans la base de donnée"""
        self._push_modification(gm.PostDeletion(database_id=database_id))

    def modify_post(self, database_id, new_size=-1, new_tags=None, new_quotes=None):
        """FPermet de modifier un post. Cette opération est pensée pour accompagner un bouton "EDIT".
        new_size donne le nouveau nombre de caractères du post (compté comme pour create_post).
        new_tags indique la nouvelle liste de tags du post. Ce n'est pas une list de tags à ajouter,
        c'est une nouvelle liste de tags qui **remplace l'ancienne liste**.
        Si ces arguments sont laissé à leurs valeurs par défault (-1 et None respectivement), ils ne seront pas modifiés."""
        self._push_modification(gm.PostModification(database_id=database_id, new_size=new_size, new_tags=new_tags))

    def add_tag_to_post(self, post_database_id, tag_slug : str):
        """ Ajoute un nouveau lien entre un tag deja existant et un post deja existant """
        self._push_modification(gm.TagOnPost(post=post_database_id, tag=tag_slug))

    def remove_tag_from_post(self, post, tag):
        """retire un lien entre un tag et un post. Ne suprime ni le tag, ni le post"""
        self._push_modification(gm.TagFromPost(post=post, tag=tag))

    def add_vote(self, post, user, vote, vote_type):
        """Utliser quand un utilisateur vote pour un post"""
        self._push_modification(gm.NewVote(post=post, author=user, vote=vote, vote_type=vote_type))





    def read_modification_from_list(self, l):
        try:
            if l[0] == "np":
                return gm.NewPost(l[1], l[2], l[5:], l[3], l[4])
            if l[0] == "nr":
                return gm.NewRecommendationLink(l[1], l[2], l[3])
            if l[0] == "vr":
                return gm.ViolentPostRemoval(l[1])
            if l[0] == "pd":
                return gm.PostDeletion(l[1])
        except IndexError:
            raise err.ForbidenModificationRequest("Error while creating modification from this list : " + str(l)
                                              + "list does not have enough elements")

    def push_modification_from_list(self, l):
        self._push_modification(self.read_modification_from_list(l))


print("GraphModifier successfully imported")
