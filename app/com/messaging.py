# -*- coding: utf-8 -*-
import socket
import sys
import json
from collections import Mapping
import traceback

from app.com.config import ERROR_HANDLING, SERVER_PORT


class MessageHandler:
    @staticmethod
    def send_json(msg):
        connexion = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        connexion.connect(('localhost', SERVER_PORT))
        try:
            connexion.sendall(msg.encode())
        except Exception as err:
            sys.stdout.write('An error occured while sending the following messaeg:\n%s' % msg)
            sys.stdout.write('The traceback is as follows:')
            traceback.print_tb(err.__traceback__)
            sys.sdtout.write(err)
            sys.stdout.flush()
        finally:
            connexion.close()
        pass

    @staticmethod
    def send_python(msg):
        try:
            msg = json.dumps(msg)
        except Exception as err:
            if not ERROR_HANDLING:
                raise
            pass
        else:
            connexion = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            connexion.connect(('localhost', SERVER_PORT))
            try:
                connexion.sendall(msg.encode())
            except Exception as err:
                sys.stdout.write('An error occured while sending the following message:\n%s' % msg)
                sys.stdout.write('The traceback is as follows:')
                traceback.print_tb(err.__traceback__)
                sys.stdout.write(err)
                sys.stdout.flush()
            finally:
                connexion.close()
        pass

    @staticmethod
    def handle_json(json_msg, klass):
        action = MessageHandler.decode_json(json_msg)
        MessageHandler.handle_decoded(action, klass)

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
            func(*args, **kwargs)
            return
        if args is not None:
            func(*args)
            return
        if kwargs is not None:
            func(**kwargs)
            return
        if args is None and kwargs is None:
            func()
            return


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
        MessageHandler.handle_decoded(action, destination)
        pass

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
