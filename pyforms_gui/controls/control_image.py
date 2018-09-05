# !/usr/bin/python
# -*- coding: utf-8 -*-
 
import logging
 
from confapp import conf
 
logger = logging.getLogger(__name__)
 
from pyforms_gui.controls.control_base import ControlBase
from pyforms_gui.utils import tools
 
try:
    import cv2
except:
    logger.debug("OpenCV not available")
 
import OpenGL.GL  as GL
import OpenGL.GLU as GLU
        
from AnyQt           import QtCore, QtOpenGL, uic
from AnyQt.QtWidgets import QWidget
 
from AnyQt import _api
 
if _api.USED_API == _api.QT_API_PYQT5:
    try:
        from AnyQt.QtOpenGL import QGLWidget
    except:
        logger.debug("No OpenGL library available")
 
    import platform
    if platform.system() == 'Darwin':
        from pyforms_gui.controls.control_player.VideoQt5GLWidget import VideoQt5GLWidget as VideoGLWidget
    else:
        from pyforms_gui.controls.control_player.VideoGLWidget import VideoGLWidget
 
elif _api.USED_API == _api.QT_API_PYQT4:
    try:
        from PyQt4.QtOpenGL import QGLWidget
    except:
        logger.debug("No OpenGL library available")
 
    from pyforms_gui.controls.control_player.VideoGLWidget import VideoGLWidget
 
import numpy as np
 
class ControlImage(ControlBase):
    _imageWidget = None
 
    def init_form(self):
        control_path = tools.getFileInSameDirectory(__file__, "image.ui")
        self._form = uic.loadUi(control_path)
        self._imageWidget = VideoGLWidget()
        self._form.imageLayout.addWidget(self._imageWidget)
        super().init_form()
 
    def save_form(self, data, path=None):
        if type(self.value) is np.ndarray: data['value'] = self._value
