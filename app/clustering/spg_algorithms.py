# -*- coding: utf-8 -*-
"""
Created on Wed Nov 22 19:06:27 2017

@author: anatole
"""

#import packages
import random
import matplotlib.pyplot as plt
import queue

#import perso
import networkx as nx
import app.clustering.parameters as param
import app.clustering.errors as err

color_sample = ['blue', 'green', 'yellow', 'pink', 'purple', 'orange', 'red']

def graph_model_1(n, ideas, reduction):
    """each node belongs to some ideas, more one than the rest. Random links based on shared ideas"""
    pnodes = [[]]*n
    colors = dict()
    for i in range(n):
        pnodes[i] = [0]*ideas
        for j in range(1, 5):
            k = random.randrange(ideas)
            pnodes[i][k] = random.random()/(j**3)
            if j == 1:
                colors[i] = color_sample[ k % len(color_sample) ]
    res_graph = nx.Graph()
    res_graph.add_nodes_from(range(n))
    for i in range(n):
        for j in range(n):
            p = 0
            for k in range(ideas):
                p = max(p, pnodes[i][k]*pnodes[j][k])
            if p*reduction > random.random():
                res_graph.add_edge(i, j)
    for i in range(n-1, -1, -1):
        if len(res_graph[i]) == 0:
            res_graph.remove_node(i)
            del(colors[i])
    return (res_graph, colors)

class generic_exception(BaseException):
    description = ""
    def __init__(self, s):
        description = s

'''filtering and preparation'''

def get_bridges(g):
    """returns the bridges. A bridge is an edge in a 1-edge biconnected component"""
    bico = nx.biconnected_components(g)
    bridges = set()
    for c in bico:
        if len(g.subgraph(c).edges) == 1:
            lc = list(c)
            bridges.add((lc[0],lc[1]))
    return(bridges)

# networkx shell
def get_biconnection_components(g, bridges):
    """return the connected components after bridges have been removed"""
    core_edges = set(g.edges)
    for e in bridges:
        try:
            core_edges.remove(e)
        except KeyError:
            core_edges.remove((e[1], e[0]))
    return nx.connected_components(g.edge_subgraph(core_edges))

'''seed and core identification'''

def get_triangles(g):
    """returns a list of all trangles in G"""
    triangle_list = []
    cleared = set()
    for bnode in list(g.nodes()):
        cleared.add(bnode)
        d1 = list(g[bnode])
        d2 = []
        for n in d1:
            if n not in cleared:
                d2.append(n)
        for i in range(len(d2)):
            for j in range(i+1, len(d2)):
                if d2[j] in g[d2[i]]:
                    triangle_list.append((bnode, d2[i], d2[j]))
    return triangle_list

# networkx shell
def fuse_to_cores(g, points):
    return(list(nx.connected_components(g.subgraph(points))))

def local_clustering_coeffs(g):
    """returns a dictionary with the clustering coefficient for each node"""
    num_possible_edges = dict()
    num_edges = dict()
    for n in g.nodes:
        l = len(g[n])
        num_possible_edges[n] = l*(l-1)
        num_edges[n]= 0
    for e in g.edges:
        close_nodes = set(g[e[0]])
        close_nodes.intersection(g[e[1]])
        for n in close_nodes:
            num_edges[n] += 1
    result = dict()
    for n in g.nodes:
        if(num_possible_edges[n] > 0):
            result[n] = num_edges[n]/num_possible_edges[n]
        else:
            result[n]= 0
    return result

'''Core expansion'''

def appr_page_rank(g, starting_points, tele_prob, precision):
    #returns a pagerank vector of all the points, stored as a dictionnary
    n = len(g.nodes)
    p = dict()
    r = dict()
    to_push = queue.Queue()
    for (node, prob) in starting_points:
        r[node] = prob
        if prob > precision*g.degree(node):
            to_push.put(node)
    if to_push.empty():
        raise generic_exception("precision is too low, approximate page rank failed")
    while not to_push.empty():
        u = to_push.get()
        try:
            ru = r[u]
        except KeyError:
            ru = 0
        try:
            pu = p[u]
        except KeyError:
            pu = 0
        du = g.degree(u)
        nhbrs = g.neighbors(u)
        for v in nhbrs:
            try:
                rv= r[v]
            except KeyError:
                rv = 0
            not_yet_in_list = ( rv <= precision*g.degree(v) )
            r[v] = rv + (1-tele_prob)*ru/(2*du)
            if not_yet_in_list and rv > precision*g.degree(v):
                to_push.put(v)
        p[u] = pu + tele_prob*ru
        r[u] = (1-tele_prob)*ru/2
        if r[u] > precision*g.degree(u):
            to_push.put(u)
    print(len(p) - len(starting_points))
    return p

def sweep(g, ordered_nodes):
    if len(ordered_nodes) == 0:
        raise(generic_exception("performing a sweep with an empty pagerank vector"))
    vmax = nx.volume(g, g.nodes)
    vsweep = nx.degree(g, ordered_nodes[0])
    cut = vsweep
    best_cut = 0
    best_conductance = cut/(min(vsweep, vmax-vsweep))
    for i in range(1, len(ordered_nodes)):
        vsweep += nx.degree(g, ordered_nodes[i])
        cut = cut - 2*nx.cut_size(g, ordered_nodes[0:i], ordered_nodes[i:i+1]) + nx.degree(g, ordered_nodes[i])
        if cut/(min(vsweep, vmax-vsweep)) < best_conductance:
            best_cut = i
            best_conductance = cut/(min(vsweep, vmax-vsweep))
    return( ordered_nodes[0:best_cut+1])

def ec_ppr(g, core_list, divide_by_degree=False):
    comps = []
    for c in core_list:
        v = nx.volume(g, c)
        s = [(node, nx.degree(g,node)/v) for node in c]
        aprv = appr_page_rank(g, s, param.ppr_tp_prob, param.ppr_precision)
        def sort_key(node):
            if divide_by_degree:
                return(aprv[node]/nx.degree(g, node))
            else:
                return(aprv[node])
        ordered_nodes = sorted(aprv.keys(), key = sort_key)
        comps.append(sweep(g, ordered_nodes))
    return(comps)


def ec_balanced(g, core_list):
    #expands by adding the most connected node to the corresponding component, while trying to keep the components balanced
    flow = dict()
    num_c = len(core_list)
    destination = dict()
    comp_count = [len(c) for c in core_list]
    total_count = 0
    for count in comp_count:
        total_count += count
    for node in g.nodes:
        d = -1
        for ic in range(num_c):
            if node in core_list[ic]:
                d = ic
        if d == -1:
            flow[node] = [0]*num_c
            for ic in range(num_c):
                flow[node][ic] = nx.cut_size(g, core_list[ic], [node])
        destination[node] = d

    priorities = [[] for ic in range(num_c)]

    def relocate(t, i, ic):
        x = t[i]
        while(i > 0 and flow[x][ic] < flow[t[i-1]][ic]):
            t[i] = t[i-1]
            i -= 1
        while(i < len(t)-1 and flow[x][ic] > flow[t[i + 1]][ic]):
            t[i] = t[i + 1]
            i += 1
        t[i] = x

    for node in flow.keys():
        for ic in range(num_c):
            priorities[ic].append(node)
            relocate(priorities[ic], (len(priorities[ic]) - 1), ic)
            #Ceci tourne en quadratique. Des optimisations sont possibles

    while len(flow) > 0:
        e = -1
        e_value = 0
        for ic in range(num_c):
            n_value = flow[priorities[ic][-1]][ic]*(total_count - comp_count[ic])
            if n_value > e_value:
                e = ic
                e_value = n_value
        if e == -1:
            break
        node = priorities[e].pop()
        for ic in range(num_c):
            if ic != e:
                priorities[ic].remove(node)
        del flow[node]
        destination[node] = e
        for n2 in g[node]:
            if destination[n2] == -1:
                flow[n2][e] += 1 #or weight of the node -> n2 edge. Code to be modified
                i = priorities[e].index(n2)
                relocate(priorities[e], i, e)
        comp_count[e] += 1
        total_count += 1

    comps = [[] for ic in range(num_c + 1)]
    for pair in destination.items():
        if pair[1] != -1:
            comps[pair[1]].append(pair[0])
        else:
            comps[-1].append(pair[0])
    return(comps)

def ec_closest(g, core_list):
    """expands cores by assigning nodes to the closest core"""
    num_of_cores = len(core_list)
    distance = dict()
    for node in g.nodes:
        distance[node] = dict()
    for i in range(num_of_cores):
        core = core_list[i]
        to_explore = []
        for node in core:
            distance[node][i] = 0
            to_explore.append(node)
        while len(to_explore) > 0:
            n1 = to_explore.pop()
            for n2 in list(g[n1]):
                if not (i in distance[n2]):
                    distance[n2][i] = distance[n1][i] + 1
                    to_explore.append(n2)
    components = [[]]*num_of_cores
    for k in range(num_of_cores):
        components[k] = []
    for node in g.nodes:
        n_dist = distance[node]
        m = -1
        for k in range(1, num_of_cores):
            if k in n_dist and (m == -1 or n_dist[m] > n_dist[k]) :
                m = k
        if m >= 0:
            components[m].append(node)
    return(components)

'''Edge improvment'''

#A finir
def ei_uphill(g, comp_list):
    '''Les nodes sont passes sur des composantes voisines tan que ça reduit le poid total de la coupe.'''
    if(type(g) != nx.graph and type(g) != nx.multiGraph):
        raise err.inadequate_partition("g must be a non-oriented graph")
    '''
    mobile_nodes = kwargs.get("mobile_nodes", g.nodes)

    if "mobile_nodes" in kwargs:
        mobile_nodes = kwargs["mobile_nodes"]
    else:
        mobile_nodes = g.nodes

    if "weight" in args:
        weight = args["weight"]
    else:
        weight = "default_weight"

    if "iteration_limit" in args:
        iteration_limit = args["iteration_limit"]
    else:
        iteration_limit = param.max_number_of_iterations
    '''
    num_c = len(comp_list)
    if num_c < 2:
        raise err.inadequate_partition("The partition must have at least two different components")

    cut_size = [0]*num_c
    for i in range(num_c):
        cut_size[i] = nx.cut_size(g, comp_list[i], weight)
    node_queue = queue.PriorityQueue()
    belonging = dict()
    node_shift_gain = dict()
    for i in range(num_c):
        for n in comp_list[i]:
            if n in belonging:
                raise err.inadequate_partition("The components must not overlap")
            belonging[n] = i
    for n in mobile_nodes:
        shift_gains = [1] * num_c
        try:
            i0 = belonging[n]
        except KeyError:
            raise err.inadequate_partition("All nodes must belong to a component")
        for i in range(num_c):
            if(i != i0):
                shift_gains[i] = nx.cut_size(g, [n], comp_list[i])
        node_shift_gain[n] = shift_gains
        best_gain = min(shift_gains)
        node_queue.put((best_gain, n))

    num_iter = 0

    while num_iter < iteration_limit and node_queue.not_empty():
        n = queue.get()[1]
        if n[0] >= 0:
            break
        try:
            i = belonging[n]
        except KeyError:
            raise err.inadequate_partition("All nodes must belong to a component")
        j = (i+1)%num_c
        shift_gains = node_shift_gain[n]
        for j2 in range(num_c):
            if( j2 != i and shift_gains[j2] > shift_gains[j]):
                j = j2
        i_neighboors = []
        j_neighboors = []
        for m in nx.neighbors(g, n):
            if(belonging[m] == i):
                i_neighboors.append(m)
            if (belonging[m] == j):
                j_neighboors.append(m)
        belonging[n] = j
        for ni in i_neighboors:
            nsg_i = node_shift_gain[ni]
            node_queue.remove((max(nsg_i),ni))
            nsg_i[j] -= g[i][j][weight]

'''Global'''



'''Utility'''

def attr_list_gen(o, d):
    """generates a list from a dictionnary, to use as a weight, size, color... argument for nx functions"""
    sample = d.popitem()
    d[sample[0]] = sample[1]
    is_edge_list = type(sample[0]) == tuple
    if(type(o) == nx.Graph or type(o) == nx.graphviews.SubGraph):
        if(is_edge_list):
            lo = list(o.edges)
        else:
            lo = list(o.nodes)
    if(type(o) == set):
        lo = list(o)
    if(type(o) == list):
        lo = o
    lr = ['white']*len(lo)

    for i in range(len(lo)):
        try:
            lr[i] = d[lo[i]]
        except KeyError:
            if is_edge_list:
                try:
                    lr[i] = d[(lo[i][1], lo[i][0])]
                except KeyError:
                    lr[i] = 'black'
            else:
                lr[i] = 'black'
    return(lr)


def gen_and_compare(gen_algo, g_param, split_algo, s_param):
    """See a graph in it's initial phase and after the splitting"""
    #gen_algo(*g_param) returns (generated graph, color_map_by_idea)
    cpl = gen_algo(*g_param)
    g = cpl[0]
    g_colors = cpl[1]

    #draw the initial graph
    lyt = nx.spring_layout(g, 0.6)
    plt.subplot(121)
    nx.draw(g, lyt, node_size=80, node_color=attr_list_gen(g, g_colors))

    #gather the subgraphs

    split_results = split_algo(g, s_param)

    gc_list = []
    for c in split_results[0]:
        gc_list.append(g.subgraph(c))

    gcore_list = []
    for c in split_results[1]:
        gcore_list.append(g.subgraph(c))

    plt.subplot(122)
    clc = 0
    for gc in gc_list:
        nx.draw(gc, lyt, node_color=attr_list_gen(gc, g_colors), node_size=80, edge_color = color_sample[clc % len(color_sample)], width=1.2)
        clc += 1
    clc = 0
    for gc in gcore_list:
        nx.draw_networkx_edges(gc, lyt, width = 3, edge_color = color_sample[clc % len(color_sample)])
        nx.draw_networkx_nodes(gc, lyt, node_size=120, node_color=attr_list_gen(gc, g_colors))
        clc += 1

    plt.show()


#print("algorithms successfully imported")
