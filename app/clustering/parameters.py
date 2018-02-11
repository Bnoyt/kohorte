import datetime as dtt
import time

# port of the Main Backend Server
SERVER_PORT = 65533

# Command keys

shutdown_command = "shutdown"

# path to the clustering memory
memory_path = "./app/clustering/memory/"

# Project controler decision parameters

idle_execution_period = dtt.timedelta(seconds=3)

p_procedure1 = dtt.timedelta(seconds=5)
p_procedure2 = dtt.timedelta(seconds=12)

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


never = dtt.datetime(year=2078, month=1, day=1, hour=1, minute=1, second=1)

def now():
    return dtt.datetime.fromtimestamp(time.time())


#print("Parameters successfully imported")
