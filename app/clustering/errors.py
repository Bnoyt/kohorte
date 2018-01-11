# -*- coding: utf-8 -*-

class GraphError(Exception):
    def __init__(self, descriptor):
        super().__init__(descriptor)


class GraphNotLoaded(GraphError):
    def __init__(self, descriptor):
        super().__init__(descriptor)


class InconsistentGraph(GraphError):
    node_exists = 0
    node_missing = 1
    graph_idMap_inconsistency = 2

    def __init__(self, descriptor):
        super().__init__(descriptor)

def NodeAlreadyExists(InconsistentGraph):
    def __init__(self, descriptor, nodeDatabaseID):
        super().__init__(descriptor)
        self.nodeDatabaseID = nodeDatabaseID

def NodeMissing(InconsistentGraph):
    def __init__(self, descriptor, nodeDatabaseID):
        super().__init__(descriptor)
        self.nodeDatabaseID = nodeDatabaseID

def NodeDeleted(InconsistentGraph):
    def __init__(self, descriptor, nodeDatabaseID):
        super().__init__(descriptor)
        self.nodeDatabaseID = nodeDatabaseID

def InconsistentIDMap(InconsistentGraph):
    def __init__(self, descriptor, inconsistentIDs):
        super().__init__(descriptor)
        self.inconsistentIDs = inconsistentIDs


class InadequatePartition(GraphError):
    def __init__(self, descriptor):
        super().__init__(descriptor)


