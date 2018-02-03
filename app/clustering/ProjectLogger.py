# -*- coding: utf-8 -*-

# import lib
import csv
import datetime
from pathlib import Path

# import dependencies
import parameters as param
import errors as err


class ProjectLogger:
    def __init__(self, name : str):
        self.name = name
        self.path = Path(param.memory_path) / name / "logs"
        if not self.path.exists():
            raise err.LoadingError("Could not find project log directory for project " + name)
        self.graph_is_loaded = False
        self.loaded_graph_path = Path()
        self.active = True

    def register_graph_loading(self):
        self.active = True
        p = self.path / str(param.now().date())
        if not p.exists():
            p.mkdir()
        self.loaded_graph_path = p / current_time_string()
        self.loaded_graph_path.mkdir()
        return self.loaded_graph_path

    def log_modifs_to_loaded_graph(self):
        if not self.active:
            return DummyLogChannel()
        if not self.graph_is_loaded:
            raise err.GraphNotLoaded("Exception reached while logging modifications to loaded graph : graph not loaded")
        file_path = self.loaded_graph_path / "modifications.csv"
        try:
            log_file = file_path.open('ab')
            return ModifLogChannel(log_file)
        except OSError:
            self.active = False
            return DummyLogChannel()

    def log_algorithm(self, algo_name):
        if not self.active:
            return DummyLogChannel()
        file_path = self.loaded_graph_path / (current_time_string() + "-" + algo_name)
        try:
            log_file = file_path.open('wb')
            return AlgorithmLogChannel(log_file)
        except OSError:
            self.active = False
            return DummyLogChannel()

    def log_nothing(self):
        return DummyLogChannel()


class LogChannel:
    def __init__(self, log_file):
        self.log_file = log_file
        self.writer = csv.writer(log_file, delimiter=',')

    def __del__(self):
        self.log_file.close()


class ModifLogChannel(LogChannel):
    def register(self, modif):
        self.writer.writerow([param.now().timestamp()] + modif.list_rep())


class AlgorithmLogChannel(LogChannel):
    def register(self, node_unique_id, new_group_id):
        self.writer.writerow([node_unique_id, new_group_id])


class DummyLogChannel:
    def __init__(self):
        pass

    def register(self, a=None, b=None, c=None):
        pass

def current_time_string():
    return str(param.now().time()).replace(":", ".")
