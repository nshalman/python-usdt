#!/usr/bin/env python

"""
Tools for logging that leverage USDT
"""

from usdt import Probe, Provider
import logging

_LEVELS = [logging.CRITICAL, logging.ERROR, logging.WARNING, logging.INFO, logging.DEBUG, logging.NOTSET]
_DESC = {
    logging.CRITICAL: "critical",
    logging.ERROR: "error",
    logging.WARNING: "warning",
    logging.INFO: "info",
    logging.DEBUG: "debug",
    logging.NOTSET: "notset",
}


class DtraceHandler(logging.Handler):
    """ Handler to fire USDT probes with log messages """

    def __init__(self):
        logging.Handler.__init__(self)

        self.provider = Provider("python", "dtrace-logger")

        self.probes = {}
        for key in _DESC.keys():
            self.probes[key] = Probe("logging", _DESC[key], ["int", "char *"])
            self.provider.add_probe(self.probes[key])
        self.provider.enable()

    def emit(self, record):
        """ Fire the appropriate USDT probe for this record's log level """
        probe = None
        for level in _LEVELS:
            if record.levelno >= level:
                probe = self.probes[level]
                break
        if not probe:
            probe = self.probes[logging.NOTSET]
        probe.fire([record.levelno, self.format(record)])
