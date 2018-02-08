# -*- coding: utf-8 -*-
from app.com.phantom import PhantomClassFactory, PhantomMethodFactory

GraphModifier = PhantomClassFactory('GraphModifier',
                                    PhantomMethodFactory('network_callback', print))