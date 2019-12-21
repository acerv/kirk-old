"""
.. module:: setup
   :platform: Multiplatform
   :synopsis: installer module
.. moduleauthor:: Andrea Cervesato <andrea.cervesato@mailbox.org>
"""
from setuptools import setup, find_packages
from kirk import __version__

setup(
    name='kirk',
    version=__version__,
    description='Jenkins Remote Launcher',
    author='Andrea Cervesato',
    author_email='andrea.cervesato@mailbox.org',
    license='GPLv2',
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
    install_requires=[
        'python-jenkins',
        'pyyaml',
        'pykwalify',
        'keyring',
        'keyrings.alt',
        'click',
        'colorama',
    ],
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'kirk=cmd.main:client',
        ],
    },
)
