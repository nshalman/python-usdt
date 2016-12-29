#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

from setuptools import setup, find_packages
from setuptools.command.build_py import build_py as _build_py

readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

requirements = [
    # TODO: put package requirements here
]

test_requirements = [
    # TODO: put package test requirements here
]

class build_py_(_build_py):
    def run(self):
        ret = _build_py.run(self)
        import site
        site.addsitedir(self.build_lib)
        sys.path.insert(0, self.build_lib)
        from usdt import build_hooks
        build_hooks.post_build()
        return ret

setup(
    name='usdt',
    version='0.1.4',
    description='Python libusdt bindings',
    long_description=readme + '\n\n' + history,
    author='Nahum Shalman',
    author_email='nshalman@omniti.com',
    url='https://github.com/nshalman/python-usdt',
    packages=[
        'usdt',
    ],
    package_dir={'usdt':
                 'usdt'},
    include_package_data=True,
    install_requires=requirements,
    license="BSD",
    zip_safe=False,
    keywords='usdt',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
    ],
    test_suite='tests',
    tests_require=test_requirements,
    cmdclass={'build_py': build_py_}
)
