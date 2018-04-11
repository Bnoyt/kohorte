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


def nn_float_pf(var_name):
    def setter(self, value):
        v = float(value)
        if v >= 0:
            vars(self)[var_name] = v
        else:
            raise ValueError('the value for ' + var_name + ' must be non-negative')

    return property(getter_factory(var_name), setter)


def non_mutable_pf(var_name):
    def setter(self, value):
        raise ValueError('You are not authorized to change the variable ' + var_name)

    return property(getter_factory(var_name), setter)


class Parameter:

    time_dilation = float_pf('__time_dilation')
    idle_execution_period = duration_pf('__idle_execution_period')

    p_global_analysis = duration_pf('__p_global_analysis')
    p_attempt_split = duration_pf('__p_attempt_split')
    p_procedure_1 = duration_pf('__p_procedure_1')
    p_procedure_2 = duration_pf('__p_procedure_2')

    indic_oppose_split_below = non_mutable_pf('_indic_oppose_split_below')
    indic_encourage_split_above = non_mutable_pf('_indic_encourage_split_above')
    indic_value_reference = non_mutable_pf('_indic_value_reference')
    indic_weight_osb = non_mutable_pf('_indic_weight_osb')
    indic_weight_esa = non_mutable_pf('_indic_weight_esa')
    indic_weight_ref = non_mutable_pf('_indic_weight_ref')
    indic_weight_project_cmp = non_mutable_pf('_indic_weight_project_cmp')

    typical_number_of_comps = nn_integer_pf('__typical_number_of_comps')
    minimal_indicator_ratio = nn_float_pf('__minimal_indicator_ratio')

    ppr_tp_prob = zero_to_one_pf('__ppr_tp_prob')
    ppr_precision = zero_to_one_pf('__ppr_precision')

    max_number_of_iterations = nn_integer_pf('__max_number_of_iterations')

    eigen_num_iter = nn_integer_pf('__eigen_num_iter')
    tag_weight_transmition = zero_to_one_pf('__tag_weight_transmition')

    conductance_balance_dampener = nn_float_pf('__conductance_balance_dampener')
    post_node_default_value = nn_float_pf('__post_node_default_value')

    default_edge_weight = non_mutable_pf('_default_edge_weight')

    def __init__(self):

        # Project controler decision parameters

        self.idle_execution_period = dtt.timedelta(seconds=50)
        self.time_dilation = 1.0

        self.p_global_analysis = dtt.timedelta(minutes=2)
        self.p_attempt_split = dtt.timedelta(minutes=5)
        self.p_procedure1 = dtt.timedelta(seconds=2)
        self.p_procedure2 = dtt.timedelta(seconds=120)

        self._indic_oppose_split_below = {
            num_of_posts: 5,
            num_of_tags: 2,
            num_of_tag_use: 5,
            num_of_users: 4,
            num_of_citations: 1,
            num_of_cit_use: 5,
            num_of_characters: 50,

            depth_value: 10,

            num_of_group_recom: 2
        }

        self._indic_encourage_split_above = {
            num_of_posts: 25,
            num_of_tags: 10,
            num_of_tag_use: 40,
            num_of_users: 40,
            num_of_citations: 10,
            num_of_cit_use: 20,
            num_of_characters: 2500,

            depth_value: 40,

            num_of_group_recom: 25
        }

        self._indic_value_reference = {
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

        self._indic_weight_osb = {
            num_of_posts: 3.0,
            num_of_tags: 1.0,
            num_of_tag_use: 2.0,
            num_of_users: 0.6,
            num_of_citations: 1.0,
            num_of_cit_use: 1.0,
            num_of_characters: 1.0,

            depth_value: 2.5,

            num_of_group_recom: 3.5
        }

        self._indic_weight_esa = {
            num_of_posts: 3.0,
            num_of_tags: 1.0,
            num_of_tag_use: 2.0,
            num_of_users: 0.6,
            num_of_citations: 1.0,
            num_of_cit_use: 1.0,
            num_of_characters: 1.0,

            depth_value: 2.5,

            num_of_group_recom: 3.5
        }

        self._indic_weight_ref = {
            num_of_posts: 3.0,
            num_of_tags: 1.0,
            num_of_tag_use: 2.0,
            num_of_users: 0.6,
            num_of_citations: 1.0,
            num_of_cit_use: 1.0,
            num_of_characters: 1.0,

            depth_value: 2.5,

            num_of_group_recom: 3.5
        }

        self._indic_weight_project_cmp = {
            num_of_posts: 3.0,
            num_of_tags: 1.0,
            num_of_tag_use: 2.0,
            num_of_users: 0.6,
            num_of_citations: 1.0,
            num_of_cit_use: 1.0,
            num_of_characters: 1.0,

            depth_value: 2.5,

            num_of_group_recom: 3.5
        }

        self.typical_number_of_comps = 4
        self.minimal_indicator_ratio = 0.001

        # Algorithms
        # personalised page rank : teleport probability
        self.ppr_tp_prob = 0.99
        self.ppr_precision = 0.00000000001

        # heuristic algorithm parameters
        self.max_number_of_iterations = 1000000

        # Eigenvector centrality

        # number of iterations for calculation
        self.eigen_num_iter = 100

        # adjustment of how much other tags are taken into account for the weight of a given tag.
        # Advised between 0 and 1, but could theoretically be any nonnegative number
        self.tag_weight_transmition = 0.5

        # uphill conductance maximisation

        # a small, nonnegative number to reduce the importance of balance in the conductance edge_improvement algorithm
        # if it is 0, there is no balance dampening
        self.conductance_balance_dampener = 0

        # Default node caracteristics
        self.post_node_default_value = 10.0

        # Default edge weights

        self._default_edge_weight = {
            belongs_to:         1.0,
            tagged_with:        1.5,
            parent_post:        3.0,
            group_recommended:  2.0,
            user_vote:          0.3,
            uses_citation:      2.2,
            source_citation:    4.0,
            raporteur_citation: 3.0,
            parent_noeud:       2.5,
            auteur_of_post:     3.0
        }

    def read_from_file(self, file_path):
        pass

    def write_to_file(self, file_path):
        pass


default = Parameter()