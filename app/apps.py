from django.apps import AppConfig
from app.clustering.ProjectController import ProjectController


class MyAppConfig(AppConfig):
    name = 'app'
    hasRun = False

    def ready(self):
        #WARNING: NOT SAFE TO INTERACT WITH DATABASE HERE !
        if not MyAppConfig.hasRun:
            p = ProjectController('startup', False)
            ProjectController._ProjectController__projectControllers['startup'] = p
            MyAppConfig.hasRun = True
        pass
