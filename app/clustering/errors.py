# -*- coding: utf-8 -*-
import Nodes


class ForbidenModificationRequest(Exception):
    def __init__(self, descriptor):
        super().__init__(descriptor)


class LoadingError(Exception):
    pass


class LogMemoryError(Exception):
    pass


class GraphError(Exception):
    def __init__(self, descriptor):
        super().__init__(descriptor)


class GraphNotLoaded(GraphError):
    def __init__(self, descriptor):
        super().__init__(descriptor)


class InconsistentGraph(GraphError):
    def __init__(self, descriptor):
        super().__init__(descriptor)


class NodeAlreadyExists(InconsistentGraph):
    def __init__(self, descriptor, existing_node, node_id):
        super().__init__(descriptor)
        self.existing_node = existing_node
        self.node_type = type(existing_node)
        self.node_id = node_id


class NodeMissing(InconsistentGraph):
    def __init__(self, descriptor, node_type, node_id):
        super().__init__(descriptor)
        self.node_type = node_type
        self.node_id = node_id


class UserNodeMissing(NodeMissing):
    def __init__(self, descriptor, node_id):
        super().__init__(descriptor, Nodes.PostNode, node_id)


class NodeDeleted(InconsistentGraph):
    def __init__(self, descriptor, nodeDatabaseID):
        super().__init__(descriptor)
        self.nodeDatabaseID = nodeDatabaseID


class InconsistentIDMap(InconsistentGraph):
    def __init__(self, descriptor, inconsistentIDs):
        super().__init__(descriptor)
        self.inconsistentIDs = inconsistentIDs


class EdgeAlreadyExists(InconsistentGraph):
    def __init__(self, descriptor, n1, n2, n1_id, n2_id, edge_key):
        super().__init__(descriptor)
        self.n1 = n1
        self.n1_type = type(n1)
        self.n1_id = n1_id
        self.n2 = n2
        self.n2_type = type(n2)
        self.n2_id = n2_id
        self.edge_key = edge_key


class EdgeDoesNotExist(InconsistentGraph):
    def __init__(self, descriptor, n1_id, n2_id, edge_key, n1=None, n2=None):
        super().__init__(descriptor)
        self.n1 = n1
        self.n1_type = type(n1)
        self.n1_id = n1_id
        self.n2 = n2
        self.n2_type = type(n2)
        self.n2_id = n2_id
        self.edge_key = edge_key


class InadequatePartition(GraphError):
    def __init__(self, descriptor):
        super().__init__(descriptor)


