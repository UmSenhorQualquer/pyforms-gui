# !/usr/bin/python3
# -*- coding: utf-8 -*-


import os, sys

if 'terminal_mode' in sys.argv:
	PYFORMS_MODE = 'TERMINAL'
else:
	PYFORMS_MODE = os.environ.get('PYFORMS_MODE', 'GUI')
