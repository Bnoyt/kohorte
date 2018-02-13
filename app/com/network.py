# -*- coding: utf-8 -*-
import json
from threading import Thread
import queue
import socket
import select

import traceback

from app.com.config import SERVER_PORT, CONTROLLERS_AS_DAEMON
from app.clustering.ProjectController import ProjectController

class DistantFunc(Thread):
    @classmethod
    def distant_call(cls, method_name, *args, **kwargs):
        thread = cls(method_name, *args, **kwargs)
        thread.daemon = False
        thread.start()

    def __init__(self, method_name, *args, **kwargs):
        Thread.__init__(self)
        self.method_name = method_name
        self.args = args
        self.kwargs = kwargs

    def run(self):
        msg = {'type': 'method',
               'method_name': self.method_name,
               'args': self.args,
               'kwargs': self.kwargs}
        msg = json.dumps(msg)
        MessageHandler.send(msg)



class MessageHandler:
    @staticmethod
    def send_json(msg):
        connexion = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        connexion.connect(('localhost', SERVER_PORT))
        try:
            connexion.sendall(msg.encode())
        except Exception as err:
            print('An error occured while sending the following messaeg:\n%s' % msg)
            print('The traceback is as follows:')
            traceback.print_tb(err.__traceback__)
            print(err)
        finally:
            connexion.close()
        pass

    @staticmethod
    def send_python(msg):
        try:
            msg = json.dumps(msg)
        except Exception as err:
            pass
        else:
            connexion = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            connexion.connect(('localhost', SERVER_PORT))
            try:
                connexion.sendall(msg.encode())
            except Exception as err:
                print('An error occured while sending the following message:\n%s' % msg)
                print('The traceback is as follows:')
                traceback.print_tb(err.__traceback__)
                print(err)
            finally:
                connexion.close()
        pass

    @staticmethod
    def handle(msg, destinations):
        try:
            action = json.loads(msg)
            destination = action['type']
            method = action['method_name']
            destination.__getattribute__(method)(*action['args'], **action['kwargs'])
        except json.JSONDecodeError:
            #TODO: Handle Exceptions
            pass
        except AttributeError:
            #TODO: Handle Exceptions
            pass
        pass

class Main(Thread):

    def __init__(self, name):
        Thread.__init__(self)
        self.daemon = True
        self.name = name
        self.socks = []
        self.clients = []
        self.infos = {}
        self.destinations = {'command': self}
        self.command_queues = {}

    def _init_project(self):
        project_ids = []
        for project_id in project_ids:
            command_queue = queue.Queue()
            controller = ProjectController(
                    'project_controller_%s' % str(project_id), command_queue)
            self.destination[project_id] = controller.get_graph_modifier()
            self.command_queues[project_id] = command_queue
            controller.daemon = CONTROLLERS_AS_DAEMON
            controller.start()
        pass

    def _init_socket(self, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('localhost', port))
        self.socks.append(sock)


    def _get_clients(self, timeout):
        queries, wlist, xlist = select.select(self.socks, [], [], timeout)
        for connexion in queries:
            client, infos = queries.accept()
            if infos[0] == '127.0.0.1':
                self.clients.append(client)
                self.infos[client] = infos
            else:
                client.close()

    def _listen_clients(self, timeout):
        try:
            to_read, wlist, xlist = select.select(self.clients, [], [], timeout)
        except select.error:
            pass
        else:
            try:
                for client in to_read:
                    try:
                        msg = b""
                        part = client.recv(1024)
                        while part:
                            msg = msg + part
                            part = client.recv(1024)
                        if msg:
                            self._handle_message(msg)
                    except Exception as err:
                        #TODO: Handle Exceptions
                        pass
            finally:
                for client in to_read:
                    self.clients.remove(client)
                    del self.infos[client]
                    client.close()

    def _handle_message(self, msg):
        try:
            msg = msg.decode()
        except Exception as err:
            #TODO: Handle Exceptions
            pass
        else:
            MessageHandler.handle(msg, self.destinations)


    def run(self):
        self._init_socket(SERVER_PORT)
        self._init_project()
        while True:
            self._get_clients(0.05)
            self._listen_clients()
        pass

    def print(self, *args, **kwargs):
        print(*args, **kwargs)