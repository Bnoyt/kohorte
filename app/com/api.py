# -*- coding: utf-8 -*-
from app.com.phantom import PhantomClassFactory, PhantomMethodFactory
from app.com.network import DistantFunc

GraphModifier = PhantomClassFactory('GraphModifier',
                                    PhantomMethodFactory('network_callback',
                                                         DistantFunc.distant_call))