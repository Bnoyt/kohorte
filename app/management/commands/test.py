from django.core.management.base import BaseCommand, CommandError
from kohorte.startup import SUPERVARIABLE

# Reference :
# https://docs.djangoproject.com/en/dev/howto/custom-management-commands/#howto-custom-management-commands

class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        self.stdout.write("The command has been successfully registered")
        try:
            self.stout.write("The variable SUPERVARIABLE was found to be %s" % SUPERVARIABLE)
        except Exception as e:
            self.stderr.write("The variable SUPERVARIABLE was not found")
            self.stderr.write(str(e))


