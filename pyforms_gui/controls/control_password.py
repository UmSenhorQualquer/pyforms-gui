#!/usr/bin/python
# -*- coding: utf-8 -*-

from pyforms_gui.controls.control_text import ControlText
from AnyQt.QtWidgets import QLineEdit

class ControlPassword(ControlText):

    def init_form(self):
        super(ControlPassword, self).init_form()
        
        self.form.label.setAccessibleName('ControlPassword-label')
        self.form.lineEdit.setEchoMode(QLineEdit.Password)