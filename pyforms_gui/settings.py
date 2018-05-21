# !/usr/bin/python
# -*- coding: utf-8 -*-

import os
from AnyQt.QtGui import QIcon, QPixmap
from AnyQt.QtWidgets import QStyle, qApp


def path(filename):
	"""	
	:param filename: 
	:return: 
	"""
	return os.path.join(os.path.dirname(__file__), filename)


PYFORMS_ICON_VIDEOPLAYER_PAUSE_PLAY = QIcon()
PYFORMS_ICON_VIDEOPLAYER_PAUSE_PLAY.addPixmap(qApp.style().standardPixmap(QStyle.SP_MediaPlay), mode=QIcon.Normal,
                                              state=QIcon.Off)
PYFORMS_ICON_VIDEOPLAYER_PAUSE_PLAY.addPixmap(qApp.style().standardPixmap(QStyle.SP_MediaPause), mode=QIcon.Normal,
                                              state=QIcon.On)

PYFORMS_ICON_CODEEDITOR_SAVE = QIcon(qApp.style().standardPixmap(QStyle.SP_DialogSaveButton))
PYFORMS_ICON_CODEEDITOR_DISCART = QIcon(qApp.style().standardPixmap(QStyle.SP_DialogDiscardButton))

PYFORMS_PIXMAP_EVENTTIMELINE_ZOOM_IN = QPixmap(path(os.path.join("Controls", "uipics", "zoom_in.png")))
PYFORMS_PIXMAP_EVENTTIMELINE_ZOOM_OUT = QPixmap(path(os.path.join("Controls", "uipics", "zoom_in.png")))

PYFORMS_ICON_EVENTTIMELINE_IMPORT = QIcon(path(os.path.join("Controls", "uipics", "page_white_get.png")))
PYFORMS_ICON_EVENTTIMELINE_EXPORT = QIcon(path(os.path.join("Controls", "uipics", "page_white_put.png")))
PYFORMS_ICON_EVENTTIMELINE_GRAPH = QIcon(path(os.path.join("Controls", "uipics", "graph.png")))
PYFORMS_ICON_EVENTTIMELINE_TIMELINE = QIcon(path(os.path.join("Controls", "uipics", "timeline.png")))
PYFORMS_ICON_EVENTTIMELINE_REFRESH = QIcon(path(os.path.join("Controls", "uipics", "refresh.png")))
PYFORMS_ICON_EVENTTIMELINE_ADD = QIcon(path(os.path.join("Controls", "uipics", "add.png")))
PYFORMS_ICON_EVENTTIMELINE_REMOVE = QIcon(path(os.path.join("Controls", "uipics", "remove.png")))

PYFORMS_ICON_FILE_OPEN = QIcon()

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

