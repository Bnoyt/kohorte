# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from app.com.network import MessageHandler

# Reference :
# https://docs.djangoproject.com/en/dev/howto/custom-management-commands/#howto-custom-management-commands

class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        msg = {'type': 'command',
               'method_name': 'stop_backend'}
        MessageHandler.send_python(msg)

