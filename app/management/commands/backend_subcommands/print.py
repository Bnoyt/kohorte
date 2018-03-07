# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from app.backend.network import MessageHandler

# Reference :
# https://docs.djangoproject.com/en/dev/howto/custom-management-commands/#howto-custom-management-commands

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('echo', help='The string to be printed by the backend')

    def handle(self, *args, **options):
        echo = options['echo']
        msg = {'type': 'command',
               'method_name': 'print',
               'args': (echo,)}
        MessageHandler.send_python(msg)
