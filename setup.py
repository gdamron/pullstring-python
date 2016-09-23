#!/usr/bin/env python

from setuptools import setup, find_packages

with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='pullstring-python',
    version='1.0.1',
    description='Python SDK to access the PullString Web API',
    long_description=readme,
    author='PullString',
    author_email='support@pullstring.com',
    url='https://github.com/pullstring/pullstring-python',
    license=license,
    packages=['pullstring'],
)
