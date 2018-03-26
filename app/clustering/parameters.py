import datetime as dtt
from app.clustering.Keys import *

def getter_factory(var_name):
    def getter(self):
        return vars(self)[var_name]

    return getter


def nn_integer_pf(var_name):
    def setter(self, value):
        v = int(value)
        if v >= 0:
            vars(self)[var_name] = v
        else:
            raise ValueError('the value for ' + var_name + ' must be non-negative')

    return property(getter_factory(var_name), setter)


def zero_to_one_pf(var_name):
    def setter(self, value):
        v = float(value)
        if 0.0 <= v <= 1.0:
            vars(self)[var_name] = v
        else:
            raise ValueError('the value for ' + var_name + ' must be between 0 and 1')

    return property(getter_factory(var_name), setter)


def duration_pf(var_name):
    def setter(self, value):
        if type(value) == dtt.timedelta:
            vars(self)[var_name] = value
        else:
            v = int(value)
            if 0 < v:
                vars(self)[var_name] = dtt.timedelta(seconds=v)
            else:
                raise ValueError('the value for ' + var_name + ' must be a positive number of seconds')

    return property(getter_factory(var_name), setter)


def float_pf(var_name):
    def setter(self, value):
        vars(self)[var_name] = float(value)

    return property(getter_factory(var_name), setter)


class Parameter:

    time_dilation = float_pf('__time_dilation')

    p_global_analysis = duration_pf('__p_global_analysis')
    p_attempt_split = duration_pf('__p_attempt_split')

    def __init__(self):
        assertions = {}
        type_read = {}


        # Project controler decision parameters

        idle_execution_period = dtt.timedelta(seconds=3)
        self.time_dilation = 1.0

        self.p_global_analysis = dtt.timedelta(minutes=2)
        self.p_attempt_split = dtt.timedelta(minutes=2)

        p_procedure1 = dtt.timedelta(seconds=2)
        p_procedure2 = dtt.timedelta(seconds=120)
        p_full_analysis = dtt.timedelta(hours=1)


        indic_oppose_split_below = {
            num_of_posts: 3
        }

        indic_encourage_split_above = {
            num_of_posts: 27
        }

        indic_value_reference = {
            num_of_posts: 12,
            num_of_tags: 5,
            num_of_tag_use: 15,
            num_of_users: 20,
            num_of_citations: 6,
            num_of_cit_use: 14,
            num_of_characters: 500,

            depth_value: 25,

            num_of_group_recom: 8
        }

        indic_weight_osb = {
            num_of_posts: 1.0
        }

        indic_weight_esa = {
            num_of_posts: 1.0
        }

        indic_weight_ref = {
            num_of_posts: 1.0
        }

        indic_weight_project_cmp = {
            num_of_posts: 3.0
        }

        # Algorithms
        # personalised page rank : teleport probability
        ppr_tp_prob = 0.99
        ppr_precision = 0.00000000001

        # heuristic algorithm parameters
        max_number_of_iterations = 1000000

        # Eigenvector centrality

        # number of iterations for calculation
        eigen_num_iter = 100

        # adjustment of how much other tags are taken into account for the weight of a given tag.
        # Advised between 0 and 1, but could theoretically be any nonnegative number
        tag_weight_transmition = 0.5

        # uphill conductance maximisation

        # a small, nonnegative number to reduce the importance of balance in the conductance edge_improvement algorithm
        # if it is 0, there is no balance dampening
        conductance_balance_dampener = 0

        # Default node caracteristics
        post_node_default_value = 10.0

        # edge keys

        parent_noeud = "parent_noeud"  # parend -> enfant (représente la dépendance)
        belongs_to = "belongs_to"  # post -> noeud
        tagged_with = "tagged_with"  # post -> tag
        parent_post = "parent_post"  # post enfant -> post parent
        auteur_of_post = "auteur_of_post"  # post -> user
        group_recommended = "group_recommended"  # post -> post (orientation not sepcified)
        user_vote = "user_vote"  # user -> vote
        uses_citation = "uses_citation"  # post -> citation
        source_citation = "source citation"  # citation -> post
        raporteur_citation = "raporteur_citation"  # citation -> utilisateur

        head_and_leaf_reduce = "hnl_reduce"

        # Default edge weights

        def_w = {
            belongs_to:         1.0,
            tagged_with:        1.5,
            parent_post:        3.0,
            group_recommended:  2.0,
            user_vote:          0.3,
            uses_citation:      2.2,
            raporteur_citation: 3.0,
        }

        default_edge_weight_parent = 3.0
        default_edge_weight_tag = 1.5
        default_edge_weight_recommendation = 2.0
        default_edge_weight_vote = 0.3
        default_node_belonging_weight = 1.0


# branching



#print("Parameters successfully imported")
