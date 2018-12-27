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
    raise Exception('OpenCV is not available. ControlImage will not be working')
 
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
        super(ControlImage, self).init_form()
 
    def save_form(self, data, path=None):
        if type(self.value) is np.ndarray: data['value'] = self._value


    @property
    def value(self):
        """
        This property returns or set what the control should manage or store.
        """
        return self._value

    @value.setter
    def value(self, value):
        oldvalue = self._value
        self._value = value
        self._imageWidget.paint([value])
        if  (type(oldvalue) is np.ndarray and type(value) is np.ndarray and oldvalue.any()!=value.any()) or \
            (type(oldvalue) is np.ndarray and type(value) is not np.ndarray) or \
            (type(oldvalue) is not np.ndarray and type(value) is np.ndarray):
            self.changed_event()

    ##########################################################################
    ############ EVENTS ######################################################
    ##########################################################################
    
    @property
    def double_click_event(self):
        return self._imageWidget.onDoubleClick

    @double_click_event.setter
    def double_click_event(self, value):
        self._imageWidget.onDoubleClick = value

    @property
    def click_event(self):
        return self._imageWidget.onClick

    @click_event.setter
    def click_event(self, value):
        self._imageWidget.onClick = value

    @property
    def drag_event(self):
        return self._imageWidget.onDrag

    @drag_event.setter
    def drag_event(self, value):
        self._imageWidget.onDrag = value

    @property
    def end_drag_event(self):
        return self._imageWidget.onEndDrag

    @end_drag_event.setter
    def end_drag_event(self, value):
        self._imageWidget.onEndDrag = value

    @property
    def key_release_event(self): return self._imageWidget.on_key_release

    @key_release_event.setter
    def key_release_event(self, value): self._imageWidget.on_key_release = value
