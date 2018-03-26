
import datetime as dtt
import time

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


def now():
    return dtt.datetime.fromtimestamp(time.time())

