# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from app.backend.network import MessageHandler

# Reference :
# https://docs.djangoproject.com/en/dev/howto/custom-management-commands/#howto-custom-management-commands

class Command(BaseCommand):

    def handle(self, *args, **options):
        msg = {'type': 'command',
               'method_name': 'list_projects'}
        project_list = MessageHandler.send_recv_python(msg)
        out = ['Project list :']
        for project in project_list:
            out.append('\t%s %s' % (project[0],
                                  ('[RUNNING]' if project[1] == 1 else '')))
        self.stdout.write('\n'.join(out))
