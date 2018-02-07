import socket
import time
import traceback

from django.core.management.base import BaseCommand, CommandError
from app.clustering.parameters import SERVER_PORT

# Reference :
# https://docs.djangoproject.com/en/dev/howto/custom-management-commands/#howto-custom-management-commands

class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        try:
            print('Establishing connection ...')
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(('localhost', SERVER_PORT))
            print('Sending data ...')
            sock.sendall(b'This is test command communicating with backend Main thread')
            sock.close()
        except Exception as err:
            print('The following exception occured')
            traceback.print_tb(err.__traceback__)
            print(err)
