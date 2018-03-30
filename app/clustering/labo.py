# -*- coding: utf-8 -*-

import app.clustering.parameters as param
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


def run():
    path = Path("./app/clustering/memory/3/logs/2018-03-29/17.29.54.690802/initial_graph.pkl")
    with path.open('rb') as pickle_file:
        pickle_graph = pickle.load(pickle_file)

    g = pickle_graph.base_graph

    node_colors = [param.node_colors[node.class_rep()] for node in g.nodes]

    lyt = nx.spring_layout(g, k=0.5)

    nx.draw_networkx(g, lyt, with_labels=False, node_color=node_colors)
    plt.show()
