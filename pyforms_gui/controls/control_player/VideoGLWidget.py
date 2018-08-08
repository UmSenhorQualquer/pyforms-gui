#!/usr/bin/python
# -*- coding: utf-8 -*-

""" pyforms_gui.controls.ControlPlayer.VideoGLWidget

"""

from pyforms_gui.controls.control_player.AbstractGLWidget import AbstractGLWidget
from AnyQt.QtOpenGL import QGLWidget

class VideoGLWidget(AbstractGLWidget, QGLWidget): pass