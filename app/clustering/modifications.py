class modification_interface():
    pass

class graph_modification():
    def __init__(self):
        pass

class create_post(graph_modification):
    def __init__(self, sql_id, parent = -1, **args):
        super().__init__()
        self.sql_id = sql_id
        self.parent = parent

        if("size" in args):
            self.size = args["size"]
        else:
            self.size = -1

        if("value" in args):
            self.value = args["value"]
        else:
            self.value = -1


class recommend_link(graph_modification):
    def __init__(self, n1, n2, weight = 1.0):
        self.n1_id = n1
        self.n2_id = n2
        self.weight = weight

class remove_post(graph_modification):
    def __init__(self, sql_id):
        self.sql_id = sql_id

class edit_post(graph_modification):
    def __init__(self, sql_id, new_size):
        self.sql_id = sql_id
        self.new_size = new_size
