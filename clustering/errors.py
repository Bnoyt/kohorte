


class inconsistent_graph(Exception):
    node_exists = 0
    node_missing = 1
    graph_idMap_inconsistency = 2

    def __init__(self, **args):
        super().__init__()
        if "type" in args:
            self.type = args["type"]
            del args["type"]
        else:
            self.type = "unspecified"

        self.info = args
