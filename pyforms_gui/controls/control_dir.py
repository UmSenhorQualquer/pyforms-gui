#!/usr/bin/python
# -*- coding: utf-8 -*-

from confapp import conf

from pyforms_gui.controls.control_base import ControlBase

import pyforms_gui.utils.tools as tools


from AnyQt           import uic
from AnyQt.QtWidgets import QFileDialog


class ControlDir(ControlBase):

    def init_form(self):
        control_path = tools.getFileInSameDirectory(__file__, "fileInput.ui")
        self._form = uic.loadUi(control_path)
        self._form.pushButton.clicked.connect(self.click)
        self.form.lineEdit.editingFinished.connect(self.finishEditing)
        self._form.pushButton.setIcon(conf.PYFORMS_ICON_FILE_OPEN)
        super().init_form()


    def click(self):
        value = QFileDialog.getExistingDirectory(self.parent, self._label, self.value)

        if _api.USED_API == _api.QT_API_PYQT5:
            value = value[0]
        elif _api.USED_API == _api.QT_API_PYQT4:
            value = str(value)

        if value and len(value)>0: self.value = value

    def finishEditing(self):
        """Function called when the lineEdit widget is edited"""
        self.changed_event()


    @property
    def value(self):
        self._value = str(self._form.lineEdit.text())
        return self._value

    @value.setter
    def value(self, value):
        self._form.lineEdit.setText(value)
        ControlBase.value.fset(self, value)

    @property
    def label(self): return self.form.label.text()

    @label.setter
    def label(self, value):
        self.form.label.setText(value)
        ControlBase.label.fset(self, value)
