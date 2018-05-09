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
        parser.add_argument('-d', '--desc', default=None, dest='description', help='Description of the project to precise the question')
        

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
            else:
                raise ValueError("Unknown username for author or multiple users\n")
            new_noeud_base = models.Noeud(type_noeud=1, label=question, question=new_project)
            new_noeud_base.save()
            self.stdout.write("Created new node with id " + str(new_noeud_base.id) + "\n")
            if description:
                utilisateur = models.Utilisateur.objects.get(user=usermatch[0])
                new_post_base = models.Post(titre=question, auteur=utilisateur,
                                            question=new_project,
                                            contenu=description,
                                            noeud=new_noeud_base)
                new_post_base.save()
                self.stdout.write("Created new post with id " + str(new_post_base.id) + "\n")
            #FileSystem Initialisation
            root = pathlib.Path(memory_path)
            if not root.exists():
                raise IOError('Memory Root folder does not exist - Check your files setup, %s might be missing' % memory_path)
            project_path = root / str(new_project.id)
            project_path.mkdir()

            with (project_path / "control.txt").open('w') as control_file:
                control_file.writelines("project " + str(new_project.id))
                control_file.writelines(str(new_project.id))
                control_file.write("true")
            (project_path / "logs").mkdir()
            
        except Exception as e:
            self.stderr.write(str(e))
        else:
            #Starting Backend thread for the new project
            msg = {'type': 'command', 'method_name': '_init_project', 'args': (new_project.id,)}
            MessageHandler.send_python(msg)
        
