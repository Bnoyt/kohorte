# -*- coding: utf-8 -*-
class PhantomClassFactory(type):
    #Create a class such as:
    # - it cannot be instanciated (returns itself upon instanciation)
    # - any attribute or method call is rerouted to the source

    def __getattr__(cls, method_name):
        source = super().__getattribute__('__source__')
        return source(method_name)

    def __new__(metacls, name, source):
        return type.__new__(metacls, name, (),
                     {'__new__': (lambda *args, **kwargs: args[0]),
                      '__source__': source})

    def __init__(cls, name, source):
        #Automatically called by __new__ as per python specification
        #Placeholder to prevent crash due to incorrect number of arguments
        pass
    pass

class PhantomMethodFactory(type):

    def __new__(metacls, name, callback):
        #Defining method of the class
        def __init__(self, method_name):
            self.__method_name__ = method_name

        def __call__(self, *args, **kwargs):
            return self.__callback__(self.__method_name__, *args, **kwargs)

        #Creating and returning the class
        return type.__new__(metacls, name, (),
                            {'__callback__': callback,
                             '__init__': __init__,
                             '__call__': __call__})

    #Placeholder to prevent crash. No initialisation required
    def __init__(cls, name, callback):
        pass
    pass
