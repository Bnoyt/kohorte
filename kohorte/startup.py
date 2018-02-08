# -*- coding: utf-8 -*-
import time

from app.clustering.Main import Main
from app.com.api import GraphModifier

def run():
    #TODO: put startup code here
    t = Main('startup')
    t.daemon = True
    t.start()
    time.sleep(0.2)
    GraphModifier.testcall(1,2,3)
    gm = GraphModifier()
    gm.jappelleunefinciont_random('argument_1', 'argument_2')
    print(gm is GraphModifier)
    pass