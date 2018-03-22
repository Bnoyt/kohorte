# -*- coding: utf-8 -*-

# import libraries
from collections.abc import Iterable
from collections.abc import Iterator
import django.core.exceptions as dj_err

# import dependencies
import app.models as models
from notify.signals import notify
import app.clustering.parameters as param
import app.clustering.Nodes as Nodes
import app.clustering.errors as err


class DatabaseAccess:
    def __init__(self, project_id):
        self.project_id = project_id

    def get_local_graph_explorer(self):
        pass

    def test(self):
        pass

    def change_importance(self, post_id, new_importance):
        try:
            post_object = models.Post.objects.get(id=post_id)
            if post_object.question.id != self.project_id:
                raise KeyError
            post_object.importance = new_importance
            post_object.save()
        except (models.Post.DoesNotExist, KeyError) as err:
            pass
            # TODO : corriger des bugs ?

    def create_suggestion(self, user_id, noeud_id, pertinence):
        try:
            user_object = models.Utilisateur.objects.get(id=user_id)
            noeud_object = models.Noeud.objects.get(id=noeud_id)
            sugg = models.Suggestion(userVise=user_object, objet=noeud_object, pertinence=pertinence)
            sugg.save()
        except (models.Post.DoesNotExist, KeyError) as err:
            pass
            # TODO : corriger des bugs ?

    def branch(self, instr):
        question = models.Question.objects.get(id=self.project_id)
        type_arete_unique = models.TypeArete.objects.get(label=param.type_arete_label)

        start_noeud = models.Noeud.objects.get(id=instr.start_noeud)
        moving_posts = models.Post.objects.filter(id__in=instr.moving_posts)
        title = models.Post.objects.get(id=instr.temp_title_post).titre
        if len(title) < 3 or title in param.forbidden_titles:
            title = "(titre a choisir)"

        going_users = models.Utilisateur.objects.filter(id__in=instr.going_users)
        leaving_users = models.Utilisateur.objects.filter(id__in=instr.leaving_users)

        new_noeud = models.Noeud(type_noeud='0', label=title, question=question)
        new_noeud.save()

        new_arete = models.AreteReflexion(ideeSource=start_noeud, ideeDest=new_noeud, typeArete=type_arete_unique)
        new_arete.save()

        for post_to_move in moving_posts:
            post_to_move.noeud = new_noeud
            post_to_move.save()

        for user in leaving_users:
            follow_rels = models.RelationUserSuivi.objects.filter(noeud=start_noeud).filter(user=user)
            for r in follow_rels:
                r.delete()

        type_suivi = models.TypeSuivi.objects.get(label=param.type_suivi_branch_label)

        for user in going_users:
            follow_rel = models.RelationUserSuivi(noeud=new_noeud, user=user, type_suivi=type_suivi)
            follow_rel.save()

        ghost_user = models.Utilisateur.objects.get(id=param.ghost_user_id)

        notify.send(sender=ghost_user, recipient_list=[utilis.user for utilis in going_users], verb=param.branch_notification_text,
                    target=start_noeud, object=new_noeud, nf_type=param.nf_type_branch_key, actor=ghost_user)

    def get_database_iterable(self):

        try:

            question = models.Question.objects.get(id=self.project_id)


            iterables = {
                "tag": GraphElementSet(models.Tag.objects.filter(question=question), TagNodeIterator),

                "noeud": GraphElementSet(models.Noeud.objects.filter(question=question), NoeudNodeIterator),

                "citation": GraphElementSet(models.Citation.objects.filter(
                                                        post__in=models.Post.objects.filter(question=question)),
                                            CitationNodeIterator),

                "user": GraphElementSet(models.Utilisateur.objects.all(), UserNodeIterator),
                # TODO : chopper les bons utilisateurs

                "post": GraphElementSet(models.Post.objects.filter(question=question),
                                        PostNodeIterator),

                "tag_post": GraphElementSet(models.Post.objects.filter(question=question),
                                            TagPostIterator),

                "post_noeud": GraphElementSet(models.Post.objects.filter(question=question),
                                              PostNoeudIterator),

                "post_uses_citation": GraphElementSet(models.Post.objects.filter(question=question),
                                                              PostUsesCitationIterator),

                "post_source_citation": GraphElementSet(models.Citation.objects.filter(
                                                                    post__in=models.Post.objects.filter(question=question)),
                                                        CitationSourceIterator),

                "raporteur_citation": GraphElementSet(models.Citation.objects.filter(
                                                        post__in=models.Post.objects.filter(question=question)),
                                                      CitationRapporteurIterator),

                "aretes_reflexion": GraphElementSet(models.AreteReflexion.objects.filter(
                                                        ideeSource__in=models.Noeud.objects.filter(question=question)),
                                                     AreteReflexionIterator),

                "vote": GraphElementSet(models.Vote.objects.filter(
                                            post__in=models.Post.objects.filter(question=question)),
                                        VoteIterator),

                "auteur_post": GraphElementSet(models.Post.objects.filter(question=question),
                                               AuteurPostIterator),

                "suivi_noeud": GraphElementSet(models.RelationUserSuivi.objects.filter(
                                                    noeud__in=models.Noeud.objects.filter(question=question)),
                                               SuiviNoeudIterator)
            }
        except dj_err.ObjectDoesNotExist as exe:
            raise err.LoadingError("Error while accessing database : innexistant access attempt")

        return iterables


class BranchInstruction:
    def __init__(self, start_noeud, moving_posts, going_users, leaving_users, temp_title_post):
        self.start_noeud = start_noeud
        self.moving_posts = moving_posts
        self.temp_title_post = temp_title_post
        self.going_users = going_users
        self.leaving_users = leaving_users


class GraphElementSet(Iterable):
    def __init__(self, query_set, iterator_type):
        self.query_set = query_set
        self.iterator_type = iterator_type

    def __iter__(self):
        return self.iterator_type(iter(self.query_set))


class GraphElementIterator(Iterator):
    def __init__(self, qs_iterator):
        self.qs_iterator = qs_iterator

    def __iter__(self):
        return self

    def __next__(self):
        return self.next()

    def next(self):
        pass


class TagNodeIterator(GraphElementIterator):
    def next(self):
        next_tag = next(self.qs_iterator)
        return Nodes.TagNode(database_id=next_tag.id, slug=next_tag.label)


class PostNodeIterator(GraphElementIterator):
    def next(self):
        next_post = next(self.qs_iterator)
        return Nodes.PostNode(database_id=next_post.id, size=next_post.size())


class NoeudNodeIterator(GraphElementIterator):
    def next(self):
        return Nodes.NoeudNode(next(self.qs_iterator).id)


class CitationNodeIterator(GraphElementIterator):
    def next(self):
        return Nodes.CitationNode(next(self.qs_iterator).id)


class UserNodeIterator(GraphElementIterator):
    def next(self):
        return Nodes.UserNode(next(self.qs_iterator).id)


class TagPostIterator(GraphElementIterator):
    def __init__(self, qs_iterator):
        super().__init__(qs_iterator)
        self.current_post = None
        self.tag_qs_iterator = None

    def next(self):
        if self.current_post is None:
            self.current_post = next(self.qs_iterator)
            self.tag_qs_iterator = iter(self.current_post.tags.all())
        next_tag = None
        while next_tag is None:
            try:
                next_tag = next(self.tag_qs_iterator)
            except StopIteration:
                self.current_post = next(self.qs_iterator)
                self.tag_qs_iterator = iter(self.current_post.tags.all())
        return self.current_post.id, next_tag.id


class PostNoeudIterator(GraphElementIterator):
    def next(self):
        next_post = next(self.qs_iterator)
        return next_post.id, next_post.noeud.id


class VoteIterator(GraphElementIterator):
    def next(self):
        next_vote = next(self.qs_iterator)
        return next_vote.voteur, next_vote.post, {"vote_type": next_vote.typeVote.label}


class PostUsesCitationIterator(GraphElementIterator):
    def __init__(self, qs_iterator):
        super().__init__(qs_iterator)
        self.current_post = None
        self.tag_qs_iterator = None

    def next(self):
        if self.current_post is None:
            self.current_post = next(self.qs_iterator)
            self.tag_qs_iterator = iter(self.current_post.citations.all())
        next_citation = None
        while next_citation is None:
            try:
                next_citation = next(self.tag_qs_iterator)
            except StopIteration:
                self.current_post = next(self.qs_iterator)
                self.tag_qs_iterator = iter(self.current_post.tags.all())
        return self.current_post.id, next_citation.id


class CitationSourceIterator(GraphElementIterator):
    def next(self):
        next_citation = next(self.qs_iterator)
        return next_citation.id, next_citation.post.id


class CitationRapporteurIterator(GraphElementIterator):
    def next(self):
        next_citation = next(self.qs_iterator)
        return next_citation.id, next_citation.rapporteur.id


class AreteReflexionIterator(GraphElementIterator):
    def next(self):
        next_arete = next(self.qs_iterator)
        return next_arete.ideeSource, next_arete.ideeDest


class AuteurPostIterator(GraphElementIterator):
    def next(self):
        next_post = next(self.qs_iterator)
        return next_post.id, next_post.auteur.id


class SuiviNoeudIterator(GraphElementIterator):
    def next(self):
        next_suivi = next(self.qs_iterator)
        return next_suivi.user, next_suivi.noeud




class Navigator:
    def __init__(self):
        pass

    def get_edges(self):
        pass


class PostNavigator(Navigator):

    def get_parent(self):
        pass

    def get_children(self):
        pass

    def get_noeud(self):
        pass

    def get_citations(self):
        pass

    def get_tags(self):
        pass


class TagNavigator(Navigator):

    def get_posts(self):
        pass
