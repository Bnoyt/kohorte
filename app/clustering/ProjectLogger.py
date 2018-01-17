# -*- coding: utf-8 -*-

# import lib
import csv
import datetime

# import dependencies
import parameters as param

class ProjectLogger:
    def __init__(self, name):
        self.name = name
        self.path = param.memory_path + name + "/logs/"
        self.graph_is_loaded = False
        self.loaded_graph_path = ""

    def register_graph_loading(self):
        self.loaded_graph_path = self.path + str(datetime.date.today()) + "/"

    def log_modifs_to_loaded_graph(self):
        if not self.graph_is_loaded:
            pass
        file_name = self.loaded_graph_path + "mods/" + str(datetime.time.now()) # datetime.time.now() doesn't exist, I'll replace it with something that works eventually
        log_file = open(file_name, 'w')
        return ModifLogChannel(log_file)

    def log_algorithm(self, algo_name):
        pass



class ModifLogChannel:
    def __init__(self, log_file):
        self.log_file = log_file
        self.writer = csv.writer(log_file, delimiter=',')

    def __del__(self):
        self.log_file.close()

    def register(self, modif):
        self.writer.writerow(modif.list_rep())

class AlgorithmLogChannel:
    def __init__(self, log_file):
        self.log_file = log_file
        self.writer = csv.writer(log_file, delimiter=',')

    def __del__(self):
        self.log_file.close()

    def register(self, node_unique_id, new_group_id):
        self.writer.writerow([node_unique_id, new_group_id])