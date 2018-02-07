from django.apps import AppConfig
from app.clustering.Main import Main
import time


class MyAppConfig(AppConfig):
    name = 'app'
    hasRun = False

    def ready(self):
        #WARNING: NOT SAFE TO INTERACT WITH DATABASE HERE !
        #WARNING: THIS CODE IS EXECUTED TWICE
        pass
