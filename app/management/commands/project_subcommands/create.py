# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from app.backend.network import MessageHandler

# Reference :
# https://docs.djangoproject.com/en/dev/howto/custom-management-commands/#howto-custom-management-commands

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('question', help='The question for this project')

    def handle(self, *args, **options):
        question = options['question']
        
        #INIT FILE SYSTEM HERE
        
        msg = {'type': 'command',
               'method_name': 'init_project',
               'args': (question,)}
        MessageHandler.send_python(msg)