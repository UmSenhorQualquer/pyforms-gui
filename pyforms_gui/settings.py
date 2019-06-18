# !/usr/bin/python
# -*- coding: utf-8 -*-

import os

PYFORMS_MAIN_WINDOW_ICON_PATH = None

PYFORMS_MAINWINDOW_MARGIN = 7

PYFORMS_CONTROL_CODE_EDITOR_DEFAULT_FONT_SIZE = '12'
PYFORMS_CONTROL_EVENTS_GRAPH_DEFAULT_SCALE = 1

PYFORMS_QUALITY_TESTS_PATH = None

PYFORMS_STYLESHEET = None
PYFORMS_STYLESHEET_DARWIN = None
PYFORMS_STYLESHEET_LINUX = None
PYFORMS_STYLESHEET_WINDOWS = None

PYFORMS_CONTROLPLAYER_FONT = 9

# In a normal loading, there may be errors that show up which are not important.
# This happens because plugins_finder will search for classes on plugins which are not present because they are not needed.
# However, if plugin is not loaded at all, this will show all related errors.
# See pyforms_gui.utils.plugins_finder.find_class()
PYFORMS_SILENT_PLUGINS_FINDER = True

PYFORMS_QSCINTILLA_ENABLED 	= True
PYFORMS_MATPLOTLIB_ENABLED 	= True
PYFORMS_WEB_ENABLED 		= True
PYFORMS_GL_ENABLED 			= True
PYFORMS_VISVIS_ENABLED 		= True


PYFORMS_DIALOGS_OPTIONS = None
PYFORMS_COLORDIALOGS_OPTIONS = None

#from AnyQt.QtWidgets import QColorDialog, QFileDialog
#PYFORMS_DIALOGS_OPTIONS = QFileDialog.DontUseNativeDialog
#PYFORMS_COLORDIALOGS_OPTIONS = QColorDialog.DontUseNativeDialog

import logging
PYFORMS_LOG_HANDLER_LEVEL = logging.INFO
PYFORMS_LOG_FORMAT = '[%(levelname)-7s] %(name)-60s %(message)s'