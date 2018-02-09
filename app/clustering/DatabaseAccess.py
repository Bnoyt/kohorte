# -*- coding: utf-8 -*-

# import libraries
import networkx as nx

# import dependencies
import app.models as models
import app.clustering.parameters as param


class DatabaseAccess:
    def __init__(self, project_id):
        self.project_id = project_id

    def load_database_to_graph(self):
        pass

    def get_local_graph_explorer(self):
        pass

    def branch(self, instr):
        instr.prep_for_branch()
        start_node = get_database_object(instr.start_node.database_id)
        roots = [get_database_object(nx_root_node.database_id) for nx_root_node in instr.roots]
        for root_node in roots:
            change_database_field()


class BranchInstruction:
    def __init__(self, the_graph, start_noeud, moving_posts, temp_title_post):
        self.the_graph = the_graph
        self.start_noeud = start_noeud
        self.moving_posts = moving_posts
        self.temp_title_post = temp_title_post

        self.parent = None
        self.roots = None

    def prep_for_branch(self):
        parent = dict()
        for n in self.moving_posts:
            parent[n] = n
        for n in self.moving_posts:
            for e in self.the_graph.out_edges(n, keys=True, data=False):
                if e[2][0] == param.parent_post:
                    if e[1] in parent:
                        parent[e[0]] = e[1]
                    break
        roots = []
        for i in parent.items():
            if i[0] == i[1]:
                roots.append(i[0])
        self.parent = parent
        self.roots = roots



def get_database_object(a):
    pass
    # a placeholder function for all django database queries

def change_database_field():
    pass
# another placeholder function