# -*- coding: utf-8 -*-
"""
Created on Thu Feb  8 11:43:26 2018
"""


class phantomClass(type):
    #Create a class such as:
    # - it cannot be instanciated (returns itself upon instanciation)
    # - any attribute or method call is rerouted to the source

    def __getattr__(cls, name):
        source = super().__getattribute__('__source__')
        return source(cls, name)

    def __new__(cls, name, source):
        return type.__new__(cls, name, (),
                     {'__new__': (lambda *args, **kwargs: args[0]),
                      '__source__': source})

    def __init__(cls, name, deferred):
        pass
    pass