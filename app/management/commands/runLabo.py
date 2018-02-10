from django.core.management.base import BaseCommand, CommandError
from app.clustering import labo

import traceback

class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        try:
            labo.run()
        except Exception as err:
            print('The following exception occured')
            traceback.print_tb(err.__traceback__)
            print(err)

    
