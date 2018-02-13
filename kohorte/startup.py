# -*- coding: utf-8 -*-
import time

from app.com.network import Main

def run():
    #TODO: put startup code here
    t = Main('startup')
    t.daemon = True
    t.start()
    time.sleep(0.2)
    pass