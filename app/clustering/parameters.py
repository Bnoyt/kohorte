import datetime as dtt
import time

#port of the Main Backend Server
SERVER_PORT = 65533

# path to the clustering memory
memory_path = "./memory/"

# Project controler decision parameters

lazyness = 1.0
p_procedure1 = dtt.timedelta(minutes=300)
p_procedure2 = dtt.timedelta(minutes=40)

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
group_recommended = "group_recommended"
user_vote = "user_vote"

head_and_leaf_reduce = "hnl_reduce"

def now():
    return dtt.datetime.fromtimestamp(time.time())


#print("Parameters successfully imported")
