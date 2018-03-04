# -*- coding: utf-8 -*-
import sys
from threading import Thread
import queue


from app.backend.config import SERVER_PORT, CONTROLLERS_AS_DAEMON, ERROR_HANDLING
from app.backend.network import MessageHandler, Server
from app.clustering.ProjectController import ProjectController



class Main(Server):

    def __init__(self, name):
        super().__init__(name)
        self.destinations = {'command': self}
        self.command_queues = {}

    def _init_projects(self):
        import app.models
        project_ids = [int(p.id) for p in app.models.Question.objects.all()]

        for project_id in project_ids:
            command_queue = queue.Queue()
            controller = ProjectController(project_id, command_queue)
            self.destination[project_id] = controller.get_graph_modifier()
            self.command_queues[project_id] = command_queue
            controller.daemon = CONTROLLERS_AS_DAEMON
            controller.start()
            sys.stdout.write('[BACKEND] Started backend thread for project %s' % project_id)
            sys.stdout.flush()
        pass

    def handle_message(self, msg, client, info):
        output = MessageHandler.route_json(msg, self.destinations)
        if output:
            json = MessageHandler.encode_python(output)
            MessageHandler.send_over(json, client)

    def preinit(self):
        self._init_socket(SERVER_PORT)
        self._init_projects()

    def print(self, *args, **kwargs):
        #sys.stdout.write(*args, **kwargs)
        print(*args, **kwargs)
        #sys.stdout.flush()

    def exception(self):
        raise SystemError