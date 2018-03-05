# -*- coding: utf-8 -*-
import queue


from app.backend.config import SERVER_PORT, CONTROLLERS_AS_DAEMON, ERROR_HANDLING
from app.backend.network import MessageHandler, Server
from app.clustering.ProjectController import ProjectController



class Main(Server):

    def __init__(self, name):
        super().__init__(name)
        self.destinations = {'command': self}
        self.command_queues = {}
        self.controllers = {}

    def _init_projects(self):
        import app.models
        project_ids = [int(p.id) for p in app.models.Question.objects.all()]
        self.print('The list of projects is as follows : %s' % project_ids)

        for project_id in project_ids:
            command_queue = queue.Queue()
            self.print('Creating thread for project %s' % project_id)
            controller = ProjectController(project_id, command_queue)
            self.controllers[project_id] = controller
            self.destinations[project_id] = controller.get_graph_modifier()
            self.command_queues[project_id] = command_queue
            controller.daemon = CONTROLLERS_AS_DAEMON
            self.print('Starting thread for project %s' % project_id)
            controller.start()
            self.print('Started ProjectController thread for project %s' % project_id)
        pass

    def handle_message(self, msg, client, info):
        output = MessageHandler.route_json(msg, self.destinations, self.print)
        if output:
            json = MessageHandler.encode_python(output, self.print)
            MessageHandler.send_over(json.encode(), client)

    def preinit(self):
        self.print('Starting main backend thread %s' % self.name)
        self._init_projects()
        self._init_socket(SERVER_PORT)
        self.print('Done starting main backend thread %s' % self.name)

    def exception(self):
        raise SystemError

    def list_projects(self):
        import app.models
        project_ids = [int(p.id) for p in app.models.Question.objects.all()]
        started = list(self.controllers.keys())
        return [(project_id, (1 if project_id in started else 0))
                for project_id in project_ids]