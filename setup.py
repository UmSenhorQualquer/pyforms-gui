#!/usr/bin/python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import re

version = ''
license = ''
with open('pyforms_gui/__init__.py', 'r') as fd:
    content = fd.read()
    version = re.search(
        r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', content, re.MULTILINE).group(1)

    license = re.search(
        r'^__license__\s*=\s*[\'"]([^\'"]*)[\'"]', content, re.MULTILINE).group(1)

if not version: raise RuntimeError('Cannot find version information')
if not license: raise RuntimeError('Cannot find license information')

with open('README.md', 'r') as fd:
    long_description = fd.read()

setup(
    name='PyForms GUI',
    version=version,
    description="""Pyforms is a Python framework to develop GUI applications based on pyqt""",
    author='Ricardo Ribeiro, Luís Teixeira',
    author_email='ricardojvr@gmail.com, micboucinha@gmail.com',
    license=license,
    url='https://github.com/UmSenhorQualquer/pyforms-gui',
    
    long_description = long_description,
    long_description_content_type = 'text/markdown',
    python_requires='>=3',
    install_requires=[
        'anyqt',
        "pyqt5; python_version>='3'",
        "PyQtWebEngine",
        'pyopengl',
        "QScintilla; python_version>='3'",
        'visvis',
        'matplotlib',
        'python-dateutil',
        'numpy',
        'opencv-python==4.5.*',
        'confapp',
        'natsort',
        'coloredlogs'
    ],
    packages=find_packages(),
    package_data={'pyforms_gui': [
        'controls/uipics/*.png',
        'controls/*.ui', 
        'controls/control_player/*.ui',
        'controls/control_event_timeline/*.ui',
        'controls/control_event_timeline/events/*.ui']
    },


    classifiers=[
        'Development Status :: 5 - Production/Stable',
        
        'Topic :: Software Development :: Build Tools',
        
        'Programming Language :: Python :: 3',

        'Environment :: MacOS X',
        'Environment :: X11 Applications :: Qt',
        'Environment :: Win32 (MS Windows)',

        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Science/Research',
        
        'Natural Language :: English',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: Unix',

        'Topic :: Scientific/Engineering :: Human Machine Interfaces',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',
        
    ],

    keywords='terminal development pyforms'
)
