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

    a_user, a_post = access.test()


    branch_order=dba.BranchInstruction(the_graph=None, start_noeud=14,
                                       moving_posts=[post.id for post in a_post[0:2]],
                                       going_users=[7],
                                       leaving_users=[7],
                                       temp_title_post=a_post[1].id)

    access.branch(branch_order)