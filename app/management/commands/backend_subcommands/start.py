# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from app.com.network import MessageHandler

import app.models

# Reference :
# https://docs.djangoproject.com/en/dev/howto/custom-management-commands/#howto-custom-management-commands

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('project_id', type=int)

    def handle(self, *args, **kwargs):
        if args[0] in [int(p.id) for p in app.models.Question.objects.all()]:
            msg = {'type': 'command',
                   'method_name': 'start_project',
                   'args':[args[0]]}
            MessageHandler.send_python(msg)
        else:
            err = 'No project with id %s' % args[0]
            raise IndexError(err)
