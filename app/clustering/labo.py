# -*- coding: utf-8 -*-

import app.clustering.ProjectController as pc
import app.clustering.GraphModifier
import app.clustering.Nodes
import app.clustering.parameters as param
import networkx as nx
import pickle
from pathlib import Path

project1 = pc.ProjectController("example", False)

project1.load_graph()

gm = GraphModifier.GraphModifier.get(1)

project1.theGraph.baseGraph.add_node(Nodes.NoeudNode(17))
usr = Nodes.UserNode(8)
project1.theGraph.baseGraph.add_node(usr)
project1.theGraph.databaseUserIDMap[8] = usr
usr = Nodes.UserNode(12)
project1.theGraph.baseGraph.add_node(usr)
project1.theGraph.databaseUserIDMap[12] = usr

gm.create_tag(5, "awesome")
gm.create_tag(7, "rocket")

gm.create_post(database_id=6, noeud=17, tag_list=[5, 7], quote_list=[], author=12, size=83, parent=-1)

gm.create_tag(19, "quizzascious")

gm.create_post(database_id=21, noeud=17, tag_list=[5, 19], quote_list=[], author=8, size=83, parent=6)

project1.apply_modifications()

gm.create_post(database_id=20, noeud=17, tag_list=[19, 5, 7], quote_list=[], author=12, size=283, parent=21)

gm.add_vote(post=20, user=8, vote=55, vote_type="votey_vote")

project1.apply_modifications()

"""
path = Path(param.memory_path) / "graph_test.pkl"
g = nx.Graph()
g.add_node(5)
print(g.nodes())

with path.open('wb')as d:
    pickle.dump(g, d)

with path.open('rb') as d:
    g2 = pickle.load(d)

print(g2.nodes)
"""