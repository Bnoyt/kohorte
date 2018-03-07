# -*- coding: utf-8 -*-
import time

from app.backend.main import Main
from app.backend.config import MAIN_AS_DAEMON

def run():
    #TODO: put startup code here
    t = Main('BACKEND_main')
    t.daemon = MAIN_AS_DAEMON
    t.start()
    time.sleep(0.2)
    pass