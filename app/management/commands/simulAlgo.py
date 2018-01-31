# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from clustering.ProjectController import ProjectController

# Reference :
# https://docs.djangoproject.com/en/dev/howto/custom-management-commands/#howto-custom-management-commands

class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        p = ProjectController.get('Startup Controller')
        p.sleep(360)

