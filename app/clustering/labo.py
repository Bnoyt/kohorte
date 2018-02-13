# -*- coding: utf-8 -*-


import app.clustering.ProjectController as pc
import app.clustering.GraphModifier
import app.clustering.Nodes as nd
import app.clustering.parameters as param
import app.clustering.ClusteringAlgorithms as ca
import app.clustering.DatabaseAccess as dba


import networkx as nx
import pickle
from pathlib import Path
import queue
import time


def run():
    print("on tourne")
    access = dba.DatabaseAccess(2)


