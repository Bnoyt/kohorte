# -*- coding: utf-8 -*-
import pathlib

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

from app.backend.network import MessageHandler
from app.clustering.parameters import memory_path
import app.models as models

# Reference :
# https://docs.djangoproject.com/en/dev/howto/custom-management-commands/#howto-custom-management-commands

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('authorname', help='The name of the author')
        parser.add_argument('question', help='The question for this project', type=str)
        

    def handle(self, *args, **options):
        try:
            question = options['question']
            authorname = options['authorname']
            description = options['description']
            
            #Database Initialisation
            usermatch = User.objects.all().filter(username=authorname)
            if len(usermatch) == 1:
                new_project = models.Question(label=question, auteur=usermatch[0])
                new_project.save()
                self.stdout.write("Created new project with id " + str(new_project.id) + "\n")
		new_noeud_base = models.Noeud(type_noeud=1, label=question, question=new_project)
                new_noeud_base.save()
                self.stdout.write("Created new node with id " + str(new_noeud_base.id) + "\n")
                new_post_base = models.Post(titre=question, auteur=usermatch[0], question=new_project, contenu=description, noeud=new_noeud_base)
		new_post_base.save()
                self.stdout.write("Created new post with id " + str(new_post_base.id) + "\n")
            else:
                raise ValueError("Unknown username for author or multiple users\n")
            #FileSystem Initialisation
            root = 
            
        except Exception as e:
            self.stderr.write(e)
        else:
            #Starting Backend thread for the new project
            msg = {'type': 'command', 'method_name': '_init_project', 'args': (new_project.id,)}
            MessageHandler.send_python(msg)
        
