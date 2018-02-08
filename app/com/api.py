# -*- coding: utf-8 -*-
"""
Created on Wed Feb  7 17:06:53 2018
"""

#class GraphModifier:
#
#    def __getattribute__(self, name):
#        return 'ERROR'

class ClassMethodInterceptor(type):

    def __getattr__(cls, name):
        return lambda *args, **kwargs: \
                   cls.static_method_missing(name, *args, **kwargs)

    def static_method_missing(cls, method_name, *args, **kwargs):
        e = "type object 'static.%s' has no attribute '%s'" \
            % (cls.__name__, method_name)
        print(e)
        return 5

GraphModifier = ClassMethodInterceptor('GraphModifier', tuple(), {})