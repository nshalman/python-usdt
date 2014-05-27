#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_usdt
----------------------------------

Tests for `usdt` module.
"""

import os
import sys
import logging
import unittest
import subprocess

import usdt

from usdt.tracer import fbt
from usdt.log import DtraceHandler

if not os.geteuid() == 0:
    sys.exit('Please run with sudo (for launching DTrace).')

class DtraceTest(unittest.TestCase):
    def setUp(self):
        begin_probe = ':::BEGIN { printf("initialized\\n"); }'

        cmd = ['dtrace', '-Z', '-q', '-n', begin_probe]
        for glob in self.dtrace_globs:
            cmd += ['-n', glob]
        self.dtrace = subprocess.Popen(cmd, stdout=subprocess.PIPE)

        # wait for dtrace to print first line of output (based on the :::BEGIN
        #  probe) to indicate that it's readuy
        self.assertTrue(self.get_next_message().endswith('initialized\n'))

    def get_next_message(self):
        return self.dtrace.stdout.readline()

    def tearDown(self):
        self.dtrace.terminate()


class ProbeTest(DtraceTest):
    dtrace_globs = [
        '::hello:int { printf("%d\\n", arg1); }',
        '::hello:name { printf("%s\\n", copyinstr(arg0)); }'
    ]

    def test_probe(self):
        test_prov = usdt.Provider("python", "provmod")
        test_probe = usdt.Probe("hello", "name", ["char *"])
        test_prov.add_probe(test_probe)
        test_prov.enable()

        test_probe.fire(["Hello World"])
        self.assertEqual(self.get_next_message(), 'Hello World\n')

    def test_probe_2(self):
        test_prov = usdt.Provider("python", "provmod")
        int_probe = usdt.Probe("hello", "int", ["char *", "int"])
        test_prov.add_probe(int_probe)
        test_prov.enable()

        int_probe.fire(["Number Test", 5])
        self.assertEqual(self.get_next_message(), '5\n')


class FunctionBoundaryTracerTest(DtraceTest):
    dtrace_globs = [
        ':fbt:: { printf("%s:%s:%s:%s %s\\n", probeprov, probemod, probefunc, probename, copyinstr(arg0)); }'
    ]

    def test_fbt(self):
        @fbt
        def hello(arg1, arg2):
            return True

        hello(1, 2)
        self.assertTrue(self.get_next_message().endswith('hello:entry 1, 2\n'))
        self.assertTrue(self.get_next_message().endswith('hello:return True\n'))

    @fbt
    def hello2(self, arg1, arg2):
        return True

    def test_fbt_2(self):
        """Same as test_fbt, but tracing a class method."""
        self.hello2(1, 2)
        the_message = self.get_next_message()
        self.assertTrue('hello2:entry test_fbt_2 (' in the_message)
        self.assertTrue(the_message.endswith('FunctionBoundaryTracerTest), 1, 2\n'))
        self.assertTrue(self.get_next_message().endswith('hello2:return True\n'))


class LoggingTest(DtraceTest):
    dtrace_globs = [
        '::logging: { printf("%s:%s:%s:%s %d %s\\n", probeprov, probemod, probefunc, probename, arg0, copyinstr(arg1)); }'
    ]

    def get_probename(self, logline):
        probeprov, probemod, probefunc, more = logline.split(':')
        probename, arg0, arg1 = more.split(' ', 2)
        return probename

    def test_logging(self):
        logger = logging.getLogger()
        logger.setLevel(logging.NOTSET)

        dtrace_handler = DtraceHandler()
        dtrace_handler.setLevel(logging.NOTSET)

        logger.addHandler(dtrace_handler)

        logger.debug("debug message")
        logger.info("info message")
        logger.warning("warning message")
        logger.error("error message")
        logger.critical("critical message")
        logger.log(logging.NOTSET + 1, "notset message")

        self.assertEqual(self.get_probename(self.get_next_message()), 'debug')
        self.assertEqual(self.get_probename(self.get_next_message()), 'info')
        self.assertEqual(self.get_probename(self.get_next_message()), 'warning')
        self.assertEqual(self.get_probename(self.get_next_message()), 'error')
        self.assertEqual(self.get_probename(self.get_next_message()), 'critical')
        self.assertEqual(self.get_probename(self.get_next_message()), 'notset')


if __name__ == '__main__':
    unittest.main()
