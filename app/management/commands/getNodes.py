from django.core.management.base import BaseCommand, CommandError
from app.models import Noeud

# Reference :
# https://docs.djangoproject.com/en/dev/howto/custom-management-commands/#howto-custom-management-commands

class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        strIds = ''.join([str(noeud.id) + '\n' for noeud in Noeud.objects.all()])
        self.stdout.write("The nodes are :\n" + strIds)


