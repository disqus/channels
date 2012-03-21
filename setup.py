#!/usr/bin/env python

from setuptools import setup, find_packages

import os.path


def parse_reqs_file(filepath):
    reqs = []
    with open(filepath, 'r') as fp:
        for line in fp:
            if not line.startswith('-'):
                reqs.append(line)
    return reqs

root = os.path.dirname(__file__)

install_requires = parse_reqs_file(os.path.join(root, 'requirements.txt'))

tests_require = [
    'nose',
    'unittest2',
]

setup(
    name='channels',
    version='0.1',
    author='David Cramer',
    author_email='dcramer@gmail.com',
    url='http://github.com/disqus/channels',
    description='A modern forum powered by DISQUS',
    packages=find_packages(),
    zip_safe=False,
    install_requires=install_requires,
    tests_require=tests_require,
    extras_require={'test': tests_require},
    test_suite='nose.main',
    include_package_data=True,
    classifiers=[
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Operating System :: OS Independent',
        'Topic :: Software Development'
    ],
)
