# -*- coding: utf-8 -*-
from threading import Thread
import json
import socket

import traceback

from app.com.config import SERVER_PORT

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
        Sender.send(msg)



class Sender:
    #Sends the function call to the Main server
    #via a thread
    @staticmethod
    def send(msg):
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

class Router:
    #Responsible for routing message to the appropriate Project
    pass