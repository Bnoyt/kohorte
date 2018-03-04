# -*- coding: utf-8 -*-
import json
from threading import Thread
import socket
import select
from collections import Mapping
from timeit import default_timer as timer
import traceback

from app.backend.config import (SERVER_PORT, ERROR_HANDLING, LOG_THREAD,
                            HEADER_SIZE, PACKET_SIZE)

class HeaderOverflowError(ConnectionError):
    pass


class DistantFunc(Thread):

    @classmethod
    def distant_call(cls, method_name, project_id, *args, **kwargs):
        thread = cls(method_name, project_id, *args, **kwargs)
        thread.daemon = False
        thread.start()

    def __init__(self, method_name, project_id, *args, **kwargs):
        Thread.__init__(self)
        self.method_name = method_name
        self.project_id = project_id
        self.args = args
        self.kwargs = kwargs

    def run(self):
        msg = {'type': self.project_id,
               'method_name': self.method_name}
        if self.args and len(self.args) > 0:
            msg['args'] = self.args
        if self.kwargs and len(self.kwargs) > 0:
            msg['kwargs'] = self.kwargs
        MessageHandler.send_python(msg)

class MessageHandler:
    #-- Base sending and receiving over socket
    @staticmethod
    def send_over(byts, connexion):
        length = bytes(str(len(byts)), 'utf-8').zfill(HEADER_SIZE)
        if len(length) > HEADER_SIZE:
            err = 'The length of the message (%s) cannot be represented on a %s bytes-long header' %(len(byts), HEADER_SIZE)
            raise HeaderOverflowError(err)
        connexion.sendall(length)
        connexion.sendall(byts)

    @staticmethod
    def recv_from(connexion):
        byts = bytes()
        header = connexion.recv(HEADER_SIZE)
        length = int(header.decode())
        while length > 0:
            packet = min(PACKET_SIZE, length)
            byts = byts + connexion.recv(packet)
            length -= packet
        return byts

    #-- Higher level sending methods. Use those.
    @staticmethod
    def send_json(msg):
        connexion = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        connexion.connect(('localhost', SERVER_PORT))
        try:
            MessageHandler.send_over(msg.encode(), connexion)
        except Exception as err:
            print('An error occured while sending the following message:\n%s' % msg)
            print('The traceback is as follows:')
            traceback.print_tb(err.__traceback__)
            print(err)
        finally:
            connexion.close()
        pass

    @staticmethod
    def send_python(msg):
        try:
            msg = json.dumps(msg, separators=(',', ':'))
        except Exception as err:
            if not ERROR_HANDLING:
                raise
            pass
        else:
            MessageHandler.send_json(msg)
        pass

    @staticmethod
    def send_recv_json(msg):
        connexion = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        connexion.connect(('localhost', SERVER_PORT))
        try:
            MessageHandler.send_over(msg.encode(), connexion)
            return MessageHandler.recv_from(connexion).decode()
        except Exception as err:
            print('An error occured while sending the following message:\n%s' % msg)
            print('The traceback is as follows:')
            traceback.print_tb(err.__traceback__)
            print(err)
        finally:
            connexion.close()
        pass

    def send_recv_python(msg):
        try:
            msg = json.dumps(msg, separators=(',', ':'))
            return json.loads(MessageHandler.send_recv_json(msg))
        except Exception as err:
            if not ERROR_HANDLING:
                raise
            pass
        pass

    #-- Handling methods for automatic function calls
    @staticmethod
    def handle_decoded(action, klass):
        try:
            method = action['method_name']
        except AttributeError:
            if not ERROR_HANDLING:
                raise
            else:
                #TODO: Error handling
                return
        try:
            args = action['args']
        except KeyError:
            args = None
        try:
            kwargs = action['kwargs']
        except KeyError:
            kwargs = None
        func = klass.__getattribute__(method)
        if args is not None and kwargs is not None:
            return func(*args, **kwargs)
        if args is not None:
            return func(*args)
        if kwargs is not None:
            return func(**kwargs)
        if args is None and kwargs is None:
            return func()

    @staticmethod
    def encode_python(python_msg):
        return json.dumps(python_msg, separators=(',', ':'))

    @staticmethod
    def decode_json(json_msg):
        try:
            action = json.loads(json_msg)
        except json.JSONDecodeError:
            if not ERROR_HANDLING:
                raise
             #TODO: Error handling
        if not isinstance(action, Mapping):
            if not ERROR_HANDLING:
                raise TypeError('The decoded json message is not a mapping')
            else:
                #TODO: Error handling
                return {}
        return action

    @staticmethod
    def handle_json(json_msg, klass):
        action = MessageHandler.decode_json(json_msg)
        return MessageHandler.handle_decoded(action, klass)

    @staticmethod
    def route_json(json_msg, destinations):
        action = MessageHandler.decode_json(json_msg)
        try:
            destination = destinations[action['type']]
        except AttributeError:
            if not ERROR_HANDLING:
                raise
            else:
                #TODO: Error handling
                return
        return MessageHandler.handle_decoded(action, destination)

class Server(Thread):

    def __init__(self, name):
        super().__init__()
        self.name = name
        self.socks = []
        self.clients = []
        self.infos = {}
        if LOG_THREAD:
            self.time = timer()

    def _init_socket(self, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('localhost', port))
        sock.listen(5)
        self.socks.append(sock)

    def _get_clients(self, timeout):
        queries, wlist, xlist = select.select(self.socks, [], [], timeout)
        for connexion in queries:
            client, infos = connexion.accept()
            if infos[0] == '127.0.0.1':
                self.clients.append(client)
                self.infos[client] = infos
            else:
                print('refused connexion from %s' % infos)
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
                        msg = MessageHandler.recv_from(client)
                        if msg:
                            self._handle_message(msg, client, self.infos[client])
                    except Exception as err:
                        #TODO: Handle Exceptions
                        if not ERROR_HANDLING:
                            raise
                        pass
            finally:
                for client in to_read:
                    client.close()
                    self.clients.remove(client)
                    del self.infos[client]
        if LOG_THREAD:
            if timer() - self.time > 5:
                self.time = timer()
                print('Thread %s is still alive' % self.name)
                print(self.socks)

    def _handle_message(self, msg, client, info):
        try:
            msg = msg.decode()
        except Exception as err:
            #TODO: Handle Exceptions
            pass
        else:
            self.handle_message(self, msg, client, info)

    def run(self):
        try:
            self.preinit()
            while True:
                self._get_clients(0.05)
                self._listen_clients(0.05)
        except Exception as err:
            print('The following exception occured in thread %s:\n' % self.name)
            traceback.print_tb(err.__traceback__)
            print(err)
        finally:
            print('Closing ports used by backend ...')
            for sock in self.socks:
                sock.close()
            print('Done.')
        pass

    def preinit(self):
        """Called at the start of the run method, before entering the main loop
Used for initializing the thread"""
        raise NotImplemented

    def handle_message(self, msg, client, info):
        """Handles the message received from clients. msg is of type str
For handling the message before byte decoding, see _handle_message"""
        pass


    pass
