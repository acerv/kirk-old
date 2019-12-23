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
    license='LGPLv2',
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
        'python-jenkins <= 1.6.0',
        'pyyaml <= 5.2',
        'pykwalify <= 1.7.0',
        'keyring <= 20.0.0',
        'keyrings.alt <= 3.4.0',
        'click <= 7.0',
        'colorama <= 0.4.3',
    ],
    packages=['kirk'],
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'kirk=kirk.commands:command_kirk',
            'kirk-check=kirk.commands:command_check',
            'kirk-credential=kirk.commands:command_credential',
        ],
    },
)
