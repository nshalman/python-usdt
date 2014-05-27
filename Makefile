.PHONY: clean-pyc clean-build docs clean

help:
	@echo "clean-build - remove build artifacts"
	@echo "clean-pyc - remove Python file artifacts"
	@echo "lint - check style with flake8"
	@echo "test - run tests quickly with the default Python"
	@echo "test-all - run tests on every Python version with tox"
	@echo "coverage - check code coverage quickly with the default Python"
	@echo "docs - generate Sphinx HTML documentation, including API docs"
	@echo "release - package and upload a release"
	@echo "dist - package"

clean: clean-build clean-pyc
	rm -fr htmlcov/

clean-build:
	rm -fr build/
	rm -fr dist/
	rm -fr *.egg-info

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +

lint:
	flake8 usdt tests

test: usdt/libusdt.so
	sudo python setup.py test

test-all:
	tox

coverage:
	coverage run --source usdt setup.py test
	coverage report -m
	coverage html
	open htmlcov/index.html

docs:
	rm -f docs/usdt.rst
	rm -f docs/modules.rst
	sphinx-apidoc -o docs/ usdt
	$(MAKE) -C docs clean
	$(MAKE) -C docs html
	open docs/_build/html/index.html

release: clean usdt/libusdt/usdt.h
	python setup.py sdist upload

dist: clean usdt/libusdt/usdt.h
	python setup.py sdist
	ls -l dist

usdt/libusdt/usdt.h:
	git submodule init
	git submodule update

build: clean usdt/libusdt/usdt.h
	python setup.py build

usdt/libusdt.so: build
	cp build/lib/usdt/libusdt.so $@
