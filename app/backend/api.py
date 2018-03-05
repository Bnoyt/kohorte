# -*- coding: utf-8 -*-
from app.backend.phantom import PhantomClassFactory, PhantomMethodFactory
import app.backend.network as net

GraphModifier = PhantomClassFactory('GraphModifier',
                                    PhantomMethodFactory('network_callback',
                                                         net.DistantFunc.distant_call))