# -*- coding: utf-8 -*-
import time

from app.com.network import Main
from app.com.config import MAIN_AS_DAEMON

def run():
    #TODO: put startup code here
    t = Main('backend - Main')
    t.daemon = MAIN_AS_DAEMON
    t.start()
    time.sleep(0.2)
    pass