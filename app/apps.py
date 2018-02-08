from django.apps import AppConfig
import time


class MyAppConfig(AppConfig):
    name = 'app'
    hasRun = False

    def ready(self):
        #WARNING: NOT SAFE TO INTERACT WITH DATABASE HERE !
        #WARNING: THIS CODE IS EXECUTED TWICE
        pass
