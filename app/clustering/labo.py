# -*- coding: utf-8 -*-

import app.clustering.parameters as param
# import app.clustering.ClusteringAlgorithms as algos
import matplotlib.pyplot as plt
from pathlib import Path
import pickle
import networkx as nx

class A:

    def getter_factory(var_name):
        def getter(self):
            return vars(self)[var_name]
        return getter

    def setter_factory(var_name):
        def setter(self, value):
            vars(self)[var_name] = str(value)
        return setter

    t = property(getter_factory('__t'), setter_factory('__t'))
    g = property(getter_factory('__g'), setter_factory('__g'))

    # def _registerVariables(self, var_names, setter_factory):
    #     for var_name in var_names:
    #         vars(type(self))[var_name] = property(lambda self: vars(self)['__' + var_name], setter_factory('__' + var_name))


def node_members(mdg, node):
    """ returns a subgraph with all the objects within a given node """
    posts = []
    for e in get_in_edges(mdg, node, base_key=param.belongs_to):
        posts.append(e[0])
    tags = set()
    citations = set()
    for p in posts:
        for e in get_out_edges(mdg, p, param.tagged_with):
            tags.add(e[1])
        for e in get_in_edges(mdg, p, param.source_citation):
            citations.add(e[0])
        for e in get_out_edges(mdg, p, param.uses_citation):
            citations.add(e[1])

    return mdg.subgraph(posts + list(tags) + list(citations))


def get_in_edges(g, node, base_key):
    '''Returns one in_edge verifying a given charcteristics, or None if no such edge exists'''
    res = []
    for e in g.in_edges(node, data=True, keys=True):
        if e[2][0] == base_key:
            res.append(e)
    return res


def get_out_edges(g, node, base_key):
    '''Returns one in_edge verifying a given charcteristics, or None if no such edge exists'''
    res = []
    for e in g.out_edges(node, data=True, keys=True):
        if e[2][0] == base_key:
            res.append(e)
    return res


def run():

    path = Path("./app/clustering/memory/3/logs/2018-04-05/07.31.45.830392/initial_graph.pkl")
    with path.open('rb') as pickle_file:
        pickle_graph = pickle.load(pickle_file)

    g = pickle_graph.base_graph

    node_colors = [param.node_colors[node.class_rep()] for node in g.nodes]

    lyt = nx.spring_layout(g, k=0.5)

    c_path = Path("./app/clustering/memory/algorithm_result.pkl")
    with c_path.open('rb') as pickle_file:
        components = pickle.load(pickle_file)

    print(len(components))

    c = 0
    colors = ["red", "pink", "black", ]
    for comp in components:
        sbg = g.subgraph(comp)
        nx.draw_networkx_nodes(sbg, lyt, with_labels=False, node_color=colors[c], node_size=500)
        c = (c + 1) % len(colors)

    nx.draw_networkx(g, lyt, with_labels=False, node_color=node_colors, node_size=200)

    noeud_sbg = node_members(g, pickle_graph.databaseNoeudIDMap[10])
    nx.draw_networkx_nodes(noeud_sbg, lyt, with_labels=False, node_color="black", node_size=30)

    plt.show()
