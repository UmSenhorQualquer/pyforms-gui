#!/usr/bin/python
# -*- coding: utf-8 -*-

from confapp                      import conf
from pyforms_gui.controls.control_base import ControlBase

import pyforms_gui.utils.tools as tools


from AnyQt           import uic, _api
from AnyQt.QtWidgets import QFileDialog


class ControlFile(ControlBase):

    def __init__(self, *args, **kwargs):
        self.__exec_changed_event = True
        super(ControlFile, self).__init__(*args, **kwargs)
        self.use_save_dialog = kwargs.get('use_save_dialog', False)

        # used to avoid triggering the finnishEditing when the input loses the focus
        self._value_before_finishEditing = None

    def init_form(self):
        control_path = tools.getFileInSameDirectory(__file__, "fileInput.ui")
        self._form = uic.loadUi(control_path)
        self._form.label.setText(self._label)
        self._form.pushButton.clicked.connect(self.click)
        self.form.lineEdit.editingFinished.connect(self.finishEditing)
        self._form.pushButton.setIcon(conf.PYFORMS_ICON_FILE_OPEN)
        super().init_form()

    def finishEditing(self):
        """Function called when the lineEdit widget is edited"""
        if self.__exec_changed_event and self._value_before_finishEditing!=self.value:
            self._value_before_finishEditing = self.value
            self.changed_event()

    def click(self):
        if self.use_save_dialog:
            value = QFileDialog.getSaveFileName(self.parent, self._label, self.value)
        else:
            if conf.PYFORMS_DIALOGS_OPTIONS:
                value = QFileDialog.getOpenFileName(self.parent, self._label, self.value,
                                                    options=conf.PYFORMS_DIALOGS_OPTIONS)
            else:
                value = QFileDialog.getOpenFileName(self.parent, self._label, self.value)


        if _api.USED_API == _api.QT_API_PYQT5:
            value = str(value[0])
        elif _api.USED_API == _api.QT_API_PYQT4:
            value = str(value)

        if value and len(value)>0:
            self.value = value
            self._value_before_finishEditing = value


    @property
    def value(self):
        self._value = str(self._form.lineEdit.text())
        return self._value

    @value.setter
    def value(self, value):
        self.__exec_changed_event = False
        self._form.lineEdit.setText(value)
        self.__exec_changed_event = True
        ControlBase.value.fset(self, value)

    @property
    def label(self): return self.form.label.text()

    @label.setter
    def label(self, value):
        self.form.label.setText(value)
        ControlBase.label.fset(self, value)