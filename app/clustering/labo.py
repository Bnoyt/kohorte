#import packages
import networkx as nx
import matplotlib.pyplot as plt
import queue

#import perso
import supergraph as spg
import spg_algorithms as alg

n = 120
ideas = 6
reduction = 0.4
edge_req = 5

def split_algo(g, a):
    core_points = []
    for t in alg.get_triangles(g):
        core_points.append(t[0])
        core_points.append(t[1])
        core_points.append(t[2])
    cores = alg.fuse_to_cores(g, core_points)
    comps = alg.ec_ppr(g, cores)
    return(comps, cores)


alg.gen_and_compare(alg.graph_model_1, (n, ideas, reduction), split_algo, 0)
