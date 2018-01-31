from django.core.management.base import BaseCommand, CommandError

# Reference :
# https://docs.djangoproject.com/en/dev/howto/custom-management-commands/#howto-custom-management-commands

class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        self.stdout.write("The command has been successfully registered")

    
