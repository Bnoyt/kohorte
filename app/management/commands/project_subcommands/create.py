# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from app.backend.network import MessageHandler

import app.models as models
from django.contrib.auth.models import User

# Reference :
# https://docs.djangoproject.com/en/dev/howto/custom-management-commands/#howto-custom-management-commands

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('authorname', help='The name of the author')
        parser.add_argument('question', help='The question for this project', type=str)
        

    def handle(self, *args, **options):
        question = options['question']
        authorname = options['authorname']
        
        
        #INIT FILE SYSTEM HERE
        if authorname:
            usermatch = User.objects.all().filter(username=authorname)
            if len(usermatch) == 1:
                new_project = models.Question(label=question, auteur=usermatch[0])
                new_project.save()
                self.stdout.write("Created new project with id " + str(new_project.id) + "\n")
                msg = {'type': 'command', 'method_name': '_init_project', 'args': (new_project.id,)}
                MessageHandler.send_python(msg)
            else:
                self.stderr.write("Unknown username for author or multiple users\n")