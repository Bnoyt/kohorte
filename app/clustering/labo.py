# -*- coding: utf-8 -*-


import app.clustering.ProjectController as pc
import app.clustering.GraphModifier
import app.clustering.Nodes as nd
import app.clustering.parameters as param
import app.clustering.ClusteringAlgorithms as ca


import networkx as nx
import pickle
from pathlib import Path
import queue
import time


def run():
    print("on tourne")

    g = nx.Graph()

    ns = {1 : nd.TagNode(1, "tag1"), 2 : nd.TagNode(2, "tag2"), 5 : nd.PostNode(5, 50), 6 : nd.PostNode(6, 50),
                      7 : nd.PostNode(7, 50), 8 : nd.PostNode(8, 50)}

    g.add_nodes_from(ns.values())

    g.add_edges_from([(ns[1], ns[5]), (ns[1], ns[6]), (ns[2], ns[5]), (ns[2], ns[7]), (ns[2], ns[8]), (ns[6], ns[5]),
                      (ns[7], ns[5]), (ns[7], ns[8]), (ns[8], ns[6])])

    print(ca.get_central_tags_eigenvectors(g, num_wanted=1)[0].database_id)

