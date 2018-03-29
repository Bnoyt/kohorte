
import datetime as dtt
import time

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

# Indicator_keys

# activity indicators
num_of_posts = "num_of_posts"
num_of_tags = "num_of_tags"
num_of_tag_use = "num_of_tag_use"
num_of_users = "num_of_users"
num_of_votes = "num_of_votes"
num_of_citations = "num_of_citations"
num_of_cit_use = "num_of_cit_use"
num_of_characters = "num_of_characters"

# advancement indicators
depth_value = "depth_value"  # sum for all posts (depth of post)

# encouragement to split

num_of_group_recom = "num_of_group_recom"

# path to the clustering memory
memory_path = "./app/clustering/memory/"

type_arete_label = "dependance"
type_suivi_branch_label = "auto pendant branch"

ghost_user_id = 8
branch_notification_text = " a été créé à partir de "
nf_type_branch_key = "branch"

upvote_vote_key = "upvote"

forbidden_titles = ["test", "titre"]
never = dtt.datetime(year=2078, month=1, day=1, hour=1, minute=1, second=1)

node_colors = {
    "bn": "black",
    "pn": "blue",
    "nn": "red",
    "un": "purple",
    "sn": "white",
    "tn": "green",
    "cn": "pink"
}


def now():
    return dtt.datetime.fromtimestamp(time.time())

