# -*- coding: utf-8 -*-
from app.com.phantom import PhantomClassFactory, PhantomMethodFactory
import app.com.network as net

GraphModifier = PhantomClassFactory('GraphModifier',
                                    PhantomMethodFactory('network_callback',
                                                         net.DistantFunc.distant_call))