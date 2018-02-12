# -*- coding: utf-8 -*-

# import libraries
from collections.abc import Iterable
from collections.abc import Iterator

# import dependencies
import app.models as models
from notify.signals import notify
import app.clustering.parameters as param
import app.clustering.Nodes as Nodes


class DatabaseAccess:
    def __init__(self, project_id):
        self.project_id = project_id

    def load_database_to_graph(self):
        pass

    def get_local_graph_explorer(self):
        pass

    def test(self):
        return models.Tag.objects.all()

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

        question = models.Question.objects.get(id=self.project_id)

        tag_iterable = TagNodeSet(models.Tag.objects.filter(question=question))
        noeud_iterable = NoeudNodeSet(models.Noeud.objects.filter(question=question))
        citation_iterable = CitationNodeIterator()


class BranchInstruction:
    def __init__(self, start_noeud, moving_posts, going_users, leaving_users, temp_title_post):
        self.start_noeud = start_noeud
        self.moving_posts = moving_posts
        self.temp_title_post = temp_title_post
        self.going_users = going_users
        self.leaving_users = leaving_users


class GraphElementSet(Iterable):
    def __init__(self, query_set):
        self.query_set = query_set
        self.iterator_type = GraphElementIterator

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


class TagNodeSet(GraphElementSet):
    def __init__(self, query_set):
        super().__init__(query_set)
        self.iterator_type = TagNodeIterator


class TagNodeIterator(GraphElementIterator):
    def next(self):
        next_tag = next(self.qs_iterator)
        return Nodes.TagNode(database_id=next_tag.id, slug=next_tag.label)


class NoeudNodeSet(GraphElementSet):
    def __init__(self, query_set):
        super().__init__(query_set)
        self.iterator_type = NodeIterator


class NoeudNodeIterator(GraphElementIterator):
    def next(self):
        next_noeud = next(self.qs_iterator)
        return Nodes.NoeudNode(next_noeud.id)


class CitationNodeSet(GraphElementSet):
    def __init__(self, query_set):
        super().__init__(query_set)
        self.iterator_type = NodeIterator


class CitationNodeIterator(GraphElementIterator):
    def next(self):
        pass


class NodeSet(GraphElementSet):
    def __init__(self, query_set):
        super().__init__(query_set)
        self.iterator_type = NodeIterator


class NodeIterator(GraphElementIterator):
    def next(self):
        pass


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

def get_database_object(a):
    pass
    # a placeholder function for all django database queries

def change_database_field():
    pass
# another placeholder function