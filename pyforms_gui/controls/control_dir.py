#!/usr/bin/python
# -*- coding: utf-8 -*-

from confapp import conf

from pyforms_gui.controls.control_base import ControlBase

import pyforms_gui.utils.tools as tools


from AnyQt           import uic, _api
from AnyQt.QtWidgets import QFileDialog


class ControlDir(ControlBase):

    def init_form(self):
        control_path = tools.getFileInSameDirectory(__file__, "fileInput.ui")
        self._form = uic.loadUi(control_path)
        self._form.pushButton.clicked.connect(self.click)
        self.form.label.setText(self._label)
        self.form.lineEdit.editingFinished.connect(self.finishEditing)
        self._form.pushButton.setIcon(conf.PYFORMS_ICON_FILE_OPEN)
        super(ControlDir, self).init_form()


    def click(self):
        if conf.PYFORMS_DIALOGS_OPTIONS:
            value = QFileDialog.getExistingDirectory(self.parent, self._label, options=conf.PYFORMS_DIALOGS_OPTIONS)
        else:
            value = QFileDialog.getExistingDirectory(self.parent, self._label)

        if value and len(value)>0: 
            self.value = value

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
