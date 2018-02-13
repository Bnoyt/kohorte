import traceback

from django.core.management.base import BaseCommand, CommandError
from app.com.network import MessageHandler

# Reference :
# https://docs.djangoproject.com/en/dev/howto/custom-management-commands/#howto-custom-management-commands

class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        try:
            msg = {'type': 'command', 'args':[b'Test command communicating']}
            MessageHandler.send_python(msg)
        except Exception as err:
            print('The following exception occured')
            traceback.print_tb(err.__traceback__)
            print(err)
