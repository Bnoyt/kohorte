# -*- coding: utf-8 -*-


class UnionFind:

    def __init__(self, container=None):
        self._rep = dict()
        if container is not None:
            for o in container:
                self._rep[o] = o

    def add(self, o):
        self._rep[o] = o

    def remove(self, o):
        target = self._rep[o]
        for x in self._rep:
            if self._rep[x] == o:
                if target == o:
                    self._rep[x] = x
                else:
                    self._rep[x] = target
        del self._rep[o]

    def union(self, a, b):
        ra = self.find(a)
        rb = self.find(b)
        self._rep[ra] = rb

    def find(self, o):
        x = o
        t = []
        while self._rep[x] != x:
            t.append(x)
            x = self._rep[x]
        for y in t:
            self._rep[y] = x
        return x

    def together(self, a, b):
        return self.find(a) == self.find(b)