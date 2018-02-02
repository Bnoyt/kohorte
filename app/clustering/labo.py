# -*- coding: utf-8 -*-

import ProjectController as pc
import parameters as param
import networkx as nx
import pickle
from pathlib import Path

project1 = pc.ProjectController("example", False)

project1.load_graph()

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