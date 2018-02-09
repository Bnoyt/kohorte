# -*- coding: utf-8 -*-


import app.clustering.ProjectController as pc
import app.clustering.GraphModifier
import app.clustering.Nodes
import app.clustering.parameters as param


import networkx as nx
import pickle
from pathlib import Path
import queue
import time


def run():
    print("on tourne")
    command_queue = queue.Queue()
    # project1 = pc.ProjectController("example", command_queue)
    # project1.run()

