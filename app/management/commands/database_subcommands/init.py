# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand

# Reference :
# https://docs.djangoproject.com/en/dev/howto/custom-management-commands/#howto-custom-management-commands

class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        #TODO: database command
        pass