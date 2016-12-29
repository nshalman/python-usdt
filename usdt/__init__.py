# -*- coding: utf-8 -*-

"""
libusdt bindings for Python
"""

from __future__ import print_function
import os
from ctypes import cdll, c_char_p, c_int, c_void_p, cast, POINTER

__author__ = 'Nahum Shalman'
__email__ = 'nshalman@omniti.com'
__version__ = '0.1.4'

HAVE_USDT = False
FAKE_DTRACE = False

try:
    HERE = os.path.dirname(os.path.realpath(__file__))
    _LIBUSDT = cdll.LoadLibrary(HERE + "/libusdt.so")
    HAVE_USDT = True
except OSError:
    # Didn't find the library, probably not supported
    pass

if HAVE_USDT:
    _LIBUSDT.usdt_create_provider.argtypes = [c_char_p, c_char_p]
    _LIBUSDT.usdt_create_probe.argtypes = [c_char_p, c_char_p, c_int, c_void_p]

    _LIBUSDT.usdt_create_provider.restype = POINTER(c_void_p)
    _LIBUSDT.usdt_create_probe.restype = POINTER(c_void_p)

    class Probe(object):
        """ a USDT probe """

        def __init__(self, func, name, arg_desc):
            self._LIBUSDT = _LIBUSDT
            self.length = len(arg_desc)
            args = (c_char_p * self.length)()
            for i in range(self.length):
                args[i] = arg_desc[i]
            self.probedef = self._LIBUSDT.usdt_create_probe(func,
                                                            name, self.length, args)

        def fire(self, args):
            """ fire the probe """
            if len(args) == self.length:
                c_args = (c_void_p * self.length)()
                for i in range(self.length):
                    c_args[i] = cast(args[i], c_void_p)
                self._LIBUSDT.usdt_fire_probedef(self.probedef, self.length, c_args)

        def __del__(self):
            self._LIBUSDT.usdt_probe_release(self.probedef)
            del self._LIBUSDT
            del self.length
            del self.probedef

    class Provider(object):
        """ a USDT provider """

        def __init__(self, provider="python-dtrace", module="default_module"):
            self._LIBUSDT = _LIBUSDT
            self.provider = self._LIBUSDT.usdt_create_provider(provider, module)
            self.probes = []

        def add_probe(self, probe):
            """ add a probe to this provider """
            self.probes.append(probe)
            self._LIBUSDT.usdt_provider_add_probe(self.provider, probe.probedef)

        def enable(self):
            """ enable the provider """
            return(self._LIBUSDT.usdt_provider_enable(self.provider))

        def __del__(self):
            for probe in self.probes:
                del probe
            del self.probes
            self._LIBUSDT.usdt_provider_disable(self.provider)
            self._LIBUSDT.usdt_provider_free(self.provider)
            del self.provider
            del self._LIBUSDT
else:
    from sys import stderr

    class Probe(object):
        """ a fake USDT probe """

        def __init__(self, name, func, arg_desc):
            self.name = name
            self.func = func
            self.provider = None
            self.arg_desc = arg_desc

        def fire(self, args):
            """ send probe info to stderr if requested """
            if FAKE_DTRACE and self.provider and self.provider.enabled:
                print(self.provider.provider, self.provider.module,
                      self.name, self.func, args,
                      file=stderr)

        def __del__(self):
            pass

    class Provider(object):
        """ a fake USDT provider """
        probes = []

        def __init__(self, provider="python-dtrace", module="default_module"):
            self.provider = provider
            self.module = module
            self.enabled = False

        def add_probe(self, probe):
            """ add a probe to this provider """
            self.probes.append(probe)
            probe.provider = self

        def enable(self):
            """ enable this (fake) provider """
            self.enabled = True

        def __del__(self):
            pass
