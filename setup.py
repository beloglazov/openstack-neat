"""
The OpenStack Neat Project
==========================
"""

import distribute_setup
distribute_setup.use_setuptools()

from setuptools import setup, find_packages


setup(
    name='openstack-neat',
    version='0.1',
    description='The OpenStack Neat Project',
    long_description=__doc__,
    author='Anton Beloglazov',
    author_email='anton.beloglazov@gmail.com',
    url='https://github.com/beloglazov/openstack-neat',
    platforms='any',

    packages=find_packages(),
    tests_require=['pyqcy'],
)
