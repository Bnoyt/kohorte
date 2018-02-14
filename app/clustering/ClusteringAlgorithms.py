# -*- coding: utf-8 -*-
"""
Created on Wed Nov 22 19:06:27 2017

@author: anatole
"""

#import packages
import random
import matplotlib.pyplot as plt
import queue
import datetime as dtt
import networkx as nx
import time as lib_time

#import perso
import app.clustering.Nodes as Nodes
import app.clustering.parameters as param
import app.clustering.errors as err
import app.clustering.ClusteringObjects as co

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

def full_graph_model_1():
    pass

# define procedures


class GenericProcedure:
    def __init__(self, the_graph):
        self.the_graph = the_graph
        self.name = "generic-procedure"
        self.period = dtt.timedelta(days=1)
        self.last_run_time = param.now()

    def next_run(self):
        return self.last_run_time + (self.period * self.the_graph.time_dilation)

    def run(self, log_channel, command_handler):
        pass


def get_procedure_table(the_graph):
    return [Procedure1(the_graph),
            Procedure2(the_graph)
            ]


class DoNothing(GenericProcedure):
    def __init__(self):
        super().__init__(None)

    def next_run(self):
        return param.never


class Procedure1(GenericProcedure):
    def __init__(self, the_graph):
        super().__init__(the_graph)
        self.name = "procedure1"
        self.period = param.p_procedure1

    def run(self, log_channel, command_handler):
        self.last_run_time = param.now()
        lib_time.sleep(2)


class Procedure2(GenericProcedure):
    def __init__(self, the_graph):
        super().__init__(the_graph)
        self.period = param.p_procedure2

    def run(self, log_channel, command_handler):
        self.last_run_time = param.now()
        lib_time.sleep(3)


'''filtering and preparation'''


def roots_and_leaves(mdg : nx.MultiDiGraph):
    """ A terme, renverra un subgraph (objet SubgraphView), constitué des racinnes et des feuilles.
    Cree de nouveaux edges de cle param.head_and_leaf_reduce
    Pour l'instant on cree juste un nouveau graphe"""
    ng = nx.Graph()
    roots = []
    for n in mdg.nodes:
        if isinstance(n, Nodes.NoeudNode):
            ng.add_node(n)
            if len(get_out_edges(mdg, n, param.parent_post)):
                roots.append(n)
    for e in mdg.edges(ng.nodes, keys=True, data=True):
        if e[2][0] == param.parent_post:
            ng.add_edge(e[0], e[1], length=1, default_weight=e[3]["default_weight"])
    for rn in roots:
        child_pile = list(ng[rn].keys())
        while len(child_pile) > 0:
            cn = child_pile.pop()
            grand_children = list(ng[cn].keys())
            grand_children.remove(rn)
            ilength = ng[rn][cn]["length"]
            idw = ng[rn][cn]["default_weight"]
            for gcn in grand_children:
                ng.add_edge(gcn, rn, length=ilength+1, default_weight= (ilength*idw + ng[cn][gcn]["default_weight"])/(ilength+1))
                child_pile.append(gcn)
            if len(grand_children) > 0:
                ng.remove_node(cn)
    return ng


def get_bridges(g):
    """returns the bridges. A bridge is an edge in a 1-edge biconnected component"""
    bico = nx.biconnected_components(g)
    bridges = set()
    for c in bico:
        if len(g.subgraph(c).edges) == 1:
            lc = list(c)
            bridges.add((lc[0],lc[1]))
    return bridges


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


def get_central_tags_eigenvectors(g : nx.Graph, num_wanted):
    """ returns a set of tags to be used as seeds for a clustering algorithms.
    The tags are chosen to convey a lot of information, and eigenvector clustering is used to quantify how interesting
    a post node is. The argument g can be a graph of a single noeud, or a graph of the whole graph,
    Howevr if it's of the whole graph it risks identifying ideas which cover the whole node you want to split,
    and that would just be dumb. So, like, it's up to you but I designed it with "just one noeud" in mind.
    And yes there's a reason why I'm using the french word for "noeud".
    Tag nodes must only link to post nodes. """
    centrality = nx.eigenvector_centrality(g, max_iter=param.eigen_num_iter)
    tags = []
    total_centrality = 0

    for n in g.nodes():
        if isinstance(n, Nodes.TagNode):
            tags.append(n)
        if isinstance(n, Nodes.PostNode):
            total_centrality += centrality[n]

    cover = {}
    weight_modifier = {}

    for t in tags:
        t_cover = 0
        for pn in g[t].keys():
            t_cover += centrality[pn]
        cover[t] = t_cover
        weight_modifier[t] = 1.0

    def information(tn):
        """ roughly corresponds to the amount of information the tag brings us.
        Same as the weight of all posts the tag links to, unless the tag covers more than half the posts
        posts are given more or less important depending on their centrality"""
        return min(cover[tn]/total_centrality, 1 - (cover[tn]/total_centrality)) * weight_modifier[tn]

    tag_graph = nx.Graph()
    tag_graph.add_nodes_from(tags)
    for t in tags:
        for n in nx.neighbors(g, t):
            for t2 in nx.neighbors(g, n):
                if t != t2 and isinstance(t2, Nodes.TagNode):
                    if t2 in tag_graph[t]:
                        tag_graph[t][t2]["shared_nodes"] += centrality[n]/2
                    else:
                        tag_graph.add_edge(t, t2, shared_nodes=centrality[n]/2)

    for t1 in tags:
        for t2 in nx.neighbors(tag_graph, t1):
            both = tag_graph[t1][t2]["shared_nodes"]
            just1 = cover[t1] - both
            just2 = cover[t2] - both
            neither = total_centrality - just1 - just2 - both
            inf_both = (just1 + just2 + both + neither - max(just1, just2, both, neither)) / total_centrality
            tag_graph[t1][t2]["difference"] = inf_both/(information(t1) + information(t2))

    # The difference attribute quantifies whther these tags give the same information
    # it ranges between 0.5 and 1
    # 0.5 difference corresponds to tags which are exactly overlapping (or complementary)
    # The highest value it can get is 1, corresponding for example to small enough disjointed sets
    # It can also correspond to other fonky things, such as nested sets where the small one is small enough
    # Basically, a high difference means the tags represent different things. And that's cool, we want tags which
    # represent different things.
    # By the way, notice how tags are interchangable with their complementary in all this ?
    # It's a direct consequence of working with information, so I think it's a good idea to keep it.
    # The interpretation is that if tag2 is complementary of tag1, then they're two words to indicate the same division
    # Liekwise, if a tag covers the whole node, it doesn't teach us much.

    def diff_key(e):
        return (e[2]["difference"] - 0.5) * (information(e[0]) + information(e[1]))

    tag_edges = list(tag_graph.edges(data=True))
    tag_edges.sort(key=diff_key)

    for e in tag_edges:
        if e[0] in tags and e[1] in tags:
            if information(e[0]) < information(e[1]):
                a = e[0]
                b = e[1]
            else:
                a = e[1]
                b = e[0]
            weight_modifier[b] += ((e[2]["difference"] * (information(a)/information(b) + 1)) - 1) \
                                * param.tag_weight_transmition

            tags.remove(a)

            # a tag is discarded this way because it is estimated that the information it carries is too also conveyed
            # by another tag. As a result, the weight of that other tag is increased to represent the fact that it also
            # carries the information of that first tag. I am not sure on the formula for weight modifier
            # devising the right formula would take a bit more theoretical thinking

            if len(tags) <= num_wanted:
                break

    # This should be really resilient:
    # If there are too few tags, it just returns all the tags it has
    # If the tags are totally unrelated, it just returns the tags with highest information

    tags.sort(key=information)

    return tags[-num_wanted:]


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
    return list(nx.connected_components(g.subgraph(points)))


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


# A finir

def ei_uphill_general_conductance(g, comp_list, weight):
    """A local uphill algorithm to improve a given graph partition.
    comp_list must be a list of node... containers I think ? In any case they must form a perfect graph partition
    The partitions are modified by repeatidely moving a node from it's component to the component of an adjacent node.
    This process is repeated as long as it improves global conductance (see the code for more explanation)
    The return is a list of node list forming the new and improved components
    """

    to_remove = []
    for c in range(len(comp_list)):
        if len(comp_list[c]) == 0:
            to_remove.append(c)
    for c in to_remove:
        del comp_list[c]
    # no empty component

    num_c = len(comp_list)

    volume = [nx.volume(g, comp_list[c], weight=weight) for c in range(num_c)]
    cut_size = [[nx.cut_size(g, S=comp_list[c1], T=comp_list[c2], weight=weight) for c1 in range(num_c)] for c2 in range(num_c)]

    total_volume = nx.volume(g, g.nodes, weight=weight)

    def global_conductance():
        s = 0
        for c1 in range(num_c):
            for c2 in range(c1 + 1, num_c):
                s += cut_size[c1][c2]
        return s / (min(volume) + param.conductance_balance_dampener*total_volume)
    # global conductance is a measure for how good a partition is
    # I adapted it from the concept of conductance, which I found as I was researching clustering
    # I'm not sure exactly what it represents or how good it is, but I think it's worth something
    # It might create partitions which are too balanced,
    # which is why the conductance_balance_dampener is there if we need it

    belonging = {}

    for c in range(num_c):
        for n in comp_list[c]:
            belonging[n] = c

    def get_comp(nd):
        try:
            return belonging[nd]
        except KeyError:
            belonging[nd] = random.randint(0, num_c - 1)
            return belonging[nd]

    iter_clock = 1
    last_mod_date = {c : 0 for c in range(num_c)}

    # I heard python was an object-oriented language, so I'm gonna create objects
    class Motion:
        """each instance of this class represents a possible change to the components. The class also posseses
        a gain value, which represent the gain in conductance for applying this motion. The main purpose of this object
        is that it makes it easy to reevaluate gain values as the graph evolves.
        The last_mod_date variable keeps track of which comps are modified when, so that we know which gain values need
        to be recalculated"""

        def __init__(self, node, dest):
            self.node = node
            self.dest = dest
            self.last_update = 1
            self.gain = self.calc_gain()

        def apply(self):
            """actually make the change"""
            c1 = get_comp(self.node)
            c2 = self.dest
            if c1 == c2:
                return
            cut1 = 0
            cut2 = 0
            for n2 in nx.neighbors(g, self.node):
                if get_comp(n2) == c1:
                    cut1 += g[self.node][n2][weight]
                if get_comp(n2) == c2:
                    cut2 += g[self.node][n2][weight]
            deg = nx.degree(g, self.node)
            cut_size[c1][c2] += cut1 - cut2
            cut_size[c2][c1] += cut1 - cut2
            volume[c1] -= deg
            volume[c2] += deg
            belonging[self.node] = self.dest

        def calc_gain(self):
            self.last_update = iter_clock

            current_cnd = global_conductance()
            c1 = get_comp(self.node)
            c2 = self.dest
            if volume[c1] <= 1.0001*nx.degree(g, self.node, weight=weight):
                return -1
            if c1 == c2:
                return 0
            cut1 = 0
            cut2 = 0
            for n2 in nx.neighbors(g, self.node):
                if get_comp(n2) == c1:
                    cut1 += g[self.node][n2][weight]
                if get_comp(n2) == c2:
                    cut2 += g[self.node][n2][weight]
            deg = nx.degree(g, self.node)
            cut_size[c1][c2] += cut1 - cut2
            cut_size[c2][c1] += cut1 - cut2
            volume[c1] -= deg
            volume[c2] += deg
            new_cnd = global_conductance()
            cut_size[c1][c2] -= cut1 - cut2
            cut_size[c2][c1] -= cut1 - cut2
            volume[c1] += deg
            volume[c2] -= deg
            return new_cnd - current_cnd

        def get_gain(self):
            if last_mod_date[self.dest] >= self.last_update or last_mod_date[belonging[self]] >= self.last_update:
                self.gain = self.calc_gain()
            return self.gain

        def __eq__(self, other):
            if not isinstance(other, Motion):
                raise NotImplemented
            return self.node == other.node and self.dest == other.dest

        def __lt__(self, other):
            if not isinstance(other, Motion):
                raise NotImplemented
            return self.get_gain() < other.get_gain()

        def __le__(self, other):
            if not isinstance(other, Motion):
                raise NotImplemented
            return self.get_gain() <= other.get_gain()

        def __gt__(self, other):
            if not isinstance(other, Motion):
                raise NotImplemented
            return self.get_gain() > other.get_gain()

        def __ge__(self, other):
            if not isinstance(other, Motion):
                raise NotImplemented
            return self.get_gain() >= other.get_gain()

        # These comparaison operators do not follow standard requierements
        # for example, a <= b and a >= b does not imply a == b
        # but it doesn't matter, their only purpose here is to be used by the sorting algorithm

    motion_list = []
    for nd in g.nodes:
        possible_dests = set()
        for nd2 in nx.neighbors(g, nd):
            possible_dests.add(get_comp(nd2))
        for dest in list(possible_dests):
            motion_list.append(Motion(node=nd, dest=dest))
    motion_list.sort()

    # motion list is used as a priority queue. It holds all the possible motions, sorted by their gain
    # using an actual priority queue isn't possible, since the gain of some motions will change with each iteration
    # instead, we take advantage of the fact that python's sort algorithm is efficient for almost sorted lists
    # Thanks to that, we can sort in pretty much linear time (I think)
    # this puts our whole loop down there in O(number of motions)
    # it is probably possible to do something a lot more efficient for large graphs,
    # since each iteration only applies local changes.
    # But this will be ran on a single node, so not that large a graph
    # and honestly, it was hard enough to code as is
    # I'll optimize it if optimisation turns out to be necessary.

    while motion_list[-1].get_gain() > 0 and iter_clock < param.max_number_of_iterations:

        iter_clock += 1

        motion = motion_list.pop()
        last_mod_date[get_comp(motion.node)] = iter_clock
        last_mod_date[motion.dest] = iter_clock
        motion.apply()

        for nd2 in nx.neighbors(g, motion.node):
            if get_comp(nd2) != motion.dest:
                new_motion = Motion(nd2, motion.dest)
                if new_motion not in motion_list:
                    motion_list.append(new_motion)

        # new possible changes are added to the list.
        # Notice that old, no-longer interesting changes are not removed, so that even if a node looses contact
        # with a component the motion to that component is still in the list. This doesn't change the result of
        # the algorithm, since that motion will probably never get a high enough gain to be applied
        # it might slow things down a bit, but It's probably fine

        motion_list.sort()

    new_comps = [[] for c in range(num_c)]

    for nd in g.nodes:
        new_comps[get_comp(nd)].append(nd)

    return new_comps


'''Global'''


# stuff. eventually


'''navigation'''


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


def algo1(the_graph):
    pass


def algo2(the_graph):
    pass
