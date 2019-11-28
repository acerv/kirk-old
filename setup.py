"""
.. module:: setup
   :platform: Multiplatform
   :synopsis: installer module
   :license: GPLv2
.. moduleauthor:: Andrea Cervesato <andrea.cervesato@mailbox.org>
"""

from setuptools import setup, find_packages

setup(
    name='kirk',
    version='1.0',
    description='Jenkins Remote Launcher',
    author='Andrea Cervesato',
    author_email='andrea.cervesato@mailbox.org',
    license='GPLv2',
    scripts=['kirk/main.py'],
    url='https://github.com/acerv/kirk',
    classifiers=[
        'Natural Language :: English',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Software Development :: Testing',
    ],
    packages=find_packages(),
    install_requires=[
        'python-jenkins',
        'pyyaml',
        'pykwalify',
        'click',
        'keyrings.alt',
    ],
    tests_require=[
        'pytest',
        'pytest-mock'
    ],
    test_suite="tests",
    entry_points={
        'console_scripts': [
            'kirk=kirk.main:client',
        ],
    },
)
