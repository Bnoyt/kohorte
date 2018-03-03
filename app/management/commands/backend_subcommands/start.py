# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from app.com.messaging import MessageHandler

import app.models

# Reference :
# https://docs.djangoproject.com/en/dev/howto/custom-management-commands/#howto-custom-management-commands

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('project_id', type=int)

    def handle(self, *args, **options):
        project_id = options['project_id']
        if project_id in [int(p.id) for p in app.models.Question.objects.all()]:
            msg = {'type': 'command',
                   'method_name': 'start_project',
                   'args':[project_id]}
            MessageHandler.send_python(msg)
        else:
            err = 'No project with id %s' % project_id
            raise CommandError(err)
