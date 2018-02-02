import datetime
import time

# path to the clustering memory
memory_path = "./memory/"


# personalised page rank : teleport probability
ppr_tp_prob = 0.99
ppr_precision = 0.00000000001

# heuristic algorithm parameters
max_number_of_iterations = 1000000

# Default node caracteristics
post_node_default_value = 10.0

# Defaule edge caracteristics
default_edge_weight_parent = 3.0
default_edge_weight_tag = 1.5
default_edge_weight_recommendation = 2.0
default_edge_weight_vote = 0.3

# edge keys
tagged_with = "tagged_with"
parent_post = "parent_post"
group_recommended = "group recommended"
user_vote = "user_vote"

def now():
    return datetime.datetime.fromtimestamp(time.time())


print("Parameters successfully imported")
