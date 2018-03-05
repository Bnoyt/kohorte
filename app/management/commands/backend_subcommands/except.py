# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from app.backend.network import MessageHandler

# Reference :
# https://docs.djangoproject.com/en/dev/howto/custom-management-commands/#howto-custom-management-commands

class Command(BaseCommand):


    def handle(self, *args, **options):
        msg = {'type': 'command',
               'method_name': 'exception'}
        MessageHandler.send_python(msg)
