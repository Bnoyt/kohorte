# -*- coding: utf-8 -*-
#from clustering.ProjectController import ProjectController
#j'ai commenté pour pouvoir travailler par ailleurs

def run():
    #TODO: put startup code here
    print('Startup code in startup.py')
    p = ProjectController('Startup Controller', False)
    ProjectController._ProjectController__projectControllers['Startup Controller'] = p
    print('Done executing startup code')
    pass
