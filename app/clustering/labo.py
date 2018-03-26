# -*- coding: utf-8 -*-

from app.clustering.parameters import Parameter

class A:

    def getter_factory(var_name):
        def getter(self):
            return vars(self)[var_name]
        return getter

    def setter_factory(var_name):
        def setter(self, value):
            vars(self)[var_name] = str(value)
        return setter

    t = property(getter_factory('__t'), setter_factory('__t'))
    g = property(getter_factory('__g'), setter_factory('__g'))

    # def _registerVariables(self, var_names, setter_factory):
    #     for var_name in var_names:
    #         vars(type(self))[var_name] = property(lambda self: vars(self)['__' + var_name], setter_factory('__' + var_name))


def run():
    param = Parameter()
    print(param.default_edge_weight)
