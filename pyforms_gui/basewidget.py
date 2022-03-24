#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
import AnyQt

from AnyQt.QtWidgets import QFrame
from AnyQt.QtWidgets import QVBoxLayout
from AnyQt.QtWidgets import QTabWidget
from AnyQt.QtWidgets import QSplitter
from AnyQt.QtWidgets import QHBoxLayout
from AnyQt.QtWidgets import QSpacerItem
from AnyQt.QtWidgets import QSizePolicy
from AnyQt.QtWidgets import QLabel
from AnyQt.QtGui import QFont
from AnyQt.QtWidgets import QFileDialog
from AnyQt import QtCore, _api

from pyforms_gui.controls.control_base import ControlBase

from AnyQt.QtWidgets import QMessageBox, QInputDialog

from .organizers import *


class BaseWidget(QFrame):
    """
    The class implements the most basic widget or window.
    """

    def __init__(self, *args, **kwargs):
        title = kwargs.get('title', args[0] if len(args) > 0 else '')

        parent_win = kwargs.get('parent_win', kwargs.get('parent_widget', None))
        win_flag = kwargs.get('win_flag', None)

        self._parent_widget = parent_win

        if parent_win is not None and win_flag is None:
            win_flag = QtCore.Qt.Dialog

        QFrame.__init__(self) if parent_win is None else QFrame.__init__(self, parent_win, win_flag)

        layout = QVBoxLayout()
        self.setLayout(layout)
        
        if _api.USED_API == _api.QT_API_PYQT5:
            layout.setContentsMargins(0, 0, 0, 0)
        elif _api.USED_API == _api.QT_API_PYQT4:
            layout.setMargin(0)

        self.title = title

        self.title = title
        self.has_progress = False

        self.toolbar = []
        self._mainmenu = []
        self._splitters = []
        self.vlayouts = []
        self.hlayouts = []
        self._tabs = []
        self._formset = None
        self._formLoaded = False
        self.uid = id(self)

        self.setAccessibleName('BaseWidget')

    ##########################################################################
    ############ FUNCTIONS  ##################################################
    ##########################################################################

    def init_form(self):
        """
        Generate the module Form
        """
        if not self._formLoaded:

            allparams = self.controls
            for key, param in allparams.items():
                param.parent = self
                param.name = key

            if self._formset is not None:
                control = self.generate_panel(self._formset)
                self.layout().addWidget(control)
            else:
                for key, param in allparams.items():
                    self.layout().addWidget(param.form)
            self._formLoaded = True

    def set_margin(self, margin):
        if _api.USED_API == _api.QT_API_PYQT5:
            self.layout().setContentsMargins(margin,margin,margin,margin)
        elif _api.USED_API == _api.QT_API_PYQT4:
            self.layout().setMargin(margin)

    def generate_tabs(self, formsetdict):
        """
        Generate QTabWidget for the module form
        @param formset: Tab form configuration
        @type formset: dict
        """
        tabs = QTabWidget(self)
        for key, item in sorted(formsetdict.items()):
            ctrl = self.generate_panel(item)
            tabs.addTab(ctrl, key[key.find(':') + 1:])
        return tabs

    def generate_panel(self, formset):
        """
        Generate a panel for the module form with all the controls
        formset format example: [('_video', '_arenas', '_run'), {"Player":['_threshold', "_player", "=", "_results", "_query"], "Background image":[(' ', '_selectBackground', '_paintBackground'), '_image']}, "_progress"]
        tuple: will display the controls in the same horizontal line
        list: will display the controls in the same vertical line
        dict: will display the controls in a tab widget
        '||': will split the controls in a horizontal line
        '=': will split the controls in a vertical line
        @param formset: Form configuration
        @type formset: list
        """
        control = None
        if '=' in formset or isinstance( formset, hsplitter):
            control = QSplitter(QtCore.Qt.Vertical)
            index = list(formset).index('=')
            first_panel = self.generate_panel(formset[0:index])
            second_panel = self.generate_panel(formset[index+1:])
            control.addWidget(first_panel)
            control.addWidget(second_panel)
            self._splitters.append(control)
            return control
        elif '||' in formset or isinstance( formset, vsplitter):
            control = QSplitter(QtCore.Qt.Horizontal)
            index = list(formset).index('||')
            first_panel = self.generate_panel(formset[0:index])
            second_panel = self.generate_panel(formset[index+1:])
            control.addWidget(first_panel)
            control.addWidget(second_panel)

            if isinstance(formset, vsplitter):
                sizes = [formset.left_width, formset.right_width]
                control.setSizes(sizes)
            self._splitters.append(control)
            return control
        control = QFrame(self)
        layout = None
        if isinstance(formset, (tuple, no_columns)):
            layout = QHBoxLayout()
            self.hlayouts.append(layout)
            for row in formset:
                if isinstance(row, (list, tuple, vsplitter, hsplitter, no_columns, segment)):
                    panel = self.generate_panel(row)
                    layout.addWidget(panel)
                elif row == " ":
                    spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
                    layout.addItem(spacer)
                elif type(row) is dict:
                    c = self.generate_tabs(row)
                    layout.addWidget(c)
                    self._tabs.append(c)
                else:
                    self._handle_text(layout, row)
        elif isinstance(formset, (list, segment)):
            layout = QVBoxLayout()
            self.vlayouts.append(layout)
            for row in formset:
                if isinstance(row, (list, tuple, vsplitter, hsplitter, segment, no_columns) ):
                    panel = self.generate_panel(row)
                    layout.addWidget(panel)
                elif row == " ":
                    spacer = QSpacerItem(
                        20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
                    layout.addItem(spacer)
                elif type(row) is dict: 
                    c = self.generate_tabs(row)
                    layout.addWidget(c)
                    self._tabs.append(c)
                else:
                    self._handle_text(layout, row)

        if _api.USED_API == _api.QT_API_PYQT5:
            layout.setContentsMargins(0, 0, 0, 0)
        elif _api.USED_API == _api.QT_API_PYQT4:
            layout.setMargin(0)
            
        control.setLayout(layout)
        return control

    def _handle_text(self, layout, row):
        param = self.controls.get(row, None)
        if param is None:
            label = QLabel()
            label.setOpenExternalLinks(True)
            label.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)

            if row.startswith('info:'):
                label.setText(row[5:])
                font = QFont()
                font.setPointSize(10)
                label.setFont(font)
                label.setAccessibleName('info')
            elif row.startswith('h1:'):
                label.setText(row[3:])
                font = QFont()
                font.setPointSize(17)
                font.setBold(True)
                label.setFont(font)
                label.setAccessibleName('h1')
            elif row.startswith('h2:'):
                label.setText(row[3:])
                font = QFont()
                font.setPointSize(16)
                font.setBold(True)
                label.setFont(font)
                label.setAccessibleName('h2')
            elif row.startswith('h3:'):
                label.setText(row[3:])
                font = QFont()
                font.setPointSize(15)
                font.setBold(True)
                label.setFont(font)
                label.setAccessibleName('h3')
            elif row.startswith('h4:'):
                label.setText(row[3:])
                font = QFont()
                font.setPointSize(14)
                font.setBold(True)
                label.setFont(font)
                label.setAccessibleName('h4')
            elif row.startswith('h5:'):
                label.setText(row[3:])
                font = QFont()
                font.setPointSize(12)
                font.setBold(True)
                label.setFont(font)
                label.setAccessibleName('h5')
            else:
                label.setText(row)
                label.setAccessibleName('msg')
            label.setToolTip(label.text())
            layout.addWidget(label)
        else:
            param.parent = self
            param.name = row
            layout.addWidget(param.form)

    def show(self):
        self.init_form()
        super(BaseWidget, self).show()

    def save_form(self, data={}, path=None):
        allparams = self.controls

        if hasattr(self, 'load_order'):
            for name in self.load_order:
                param = allparams[name]
                data[name] = {}
                param.save_form(data[name])
        else:
            for name, param in allparams.items():
                data[name] = {}
                param.save_form(data[name])
        return data

    def load_form(self, data, path=None):
        allparams = self.controls

        if hasattr(self, 'load_order'):
            for name in self.load_order:
                param = allparams[name]
                if name in data:
                    param.load_form(data[name])
        else:
            for name, param in allparams.items():
                if name in data:
                    param.load_form(data[name])
                # self.init_form()

    def save_window(self):
        allparams = self.controls
        data = {}
        self.save_form(data)

        filename, _ = QFileDialog.getSaveFileName(self, 'Select file')
        if filename:
            with open(filename, 'w') as output_file:
                json.dump(data, output_file, indent = 4)

    def load_form_filename(self, filename):
        with open(filename, 'r') as pkl_file:
            project_data = json.load(pkl_file)
        data = dict(project_data)
        self.load_form(data)

    def load_window(self):
        filename, _ = QFileDialog.getOpenFileNames(self, 'Select file')
        self.load_form_filename(str(filename[0]))

    def close(self):
        super(BaseWidget, self).close()

    def input_text(self, msg, title='', default=None):
        text, ok = QInputDialog.getText(self, title, msg, text=default)
        if ok:
            return str(text)
        else:
            return None

    def input_double(self, msg, title='', default=0, min=-2147483647, max=2147483647, decimals=1):
        text, ok = QInputDialog.getDouble(self, title, msg, value=default, min=min, max=max, decimals=decimals)
        if ok:
            return float(text)
        else:
            return None
        
    def input_int(self, msg, title='', default=0, min=-2147483647, max=2147483647):
        text, ok = QInputDialog.getInt(self, title, msg, value=default, min=min, max=max)
        if ok:
            return int(text)
        else:
            return None

    def question(self, msg, title=None, buttons=['no', 'yes']):
        btns = None
        for btn in buttons:
            if btn.lower() == 'cancel':
                b = QMessageBox.Cancel
            elif btn.lower() == 'no':
                b = QMessageBox.No
            elif btn.lower() == 'yes':
                b = QMessageBox.Yes
            elif btn.lower() == 'no_all':
                b = QMessageBox.NoToAll
            elif btn.lower() == 'yes_all':
                b = QMessageBox.YesToAll

            if btns is None: 
                btns = b
            else:
                btns |= b

        m = QMessageBox(QMessageBox.Question, title, msg, btns)
        reply = m.exec_()

        if reply == QMessageBox.Cancel:
            return 'cancel'
        elif reply == QMessageBox.No:
            return 'no'
        elif reply == QMessageBox.Yes:
            return 'yes'
        elif reply == QMessageBox.NoToAll:
            return 'no_all'
        elif reply == QMessageBox.YesToAll:
            return 'yes_all'

        return None

    def message(self, msg, title=None, msg_type=None):
        if msg_type == 'success':
            m = QMessageBox(QMessageBox.NoIcon, title, msg) 
        elif msg_type == 'info':
            m = QMessageBox(QMessageBox.Information, title, msg)    
        elif msg_type == 'warning':
            m = QMessageBox(QMessageBox.Warning, title, msg) 
        elif msg_type == 'error':
            m = QMessageBox(QMessageBox.Critical, title, msg)
        elif msg_type == 'about':
            m = QMessageBox(QMessageBox.Question, title, msg) 
        elif msg_type == 'aboutQt':
            m = QMessageBox(QMessageBox.Question, title, msg)
        else:
            m = QMessageBox(QMessageBox.NoIcon, title, msg)

        m.exec_()

    def success(self,   msg, title=None):   self.message(msg, title, msg_type='success')
    def info(self,      msg, title=None):   self.message(msg, title, msg_type='info')
    def warning(self,   msg, title=None):   self.message(msg, title, msg_type='warning');
    def alert(self,     msg, title=None):   self.message(msg, title, msg_type='error')
    def critical(self,  msg, title=None):   self.message(msg, title, msg_type='error')
    def about(self,     msg, title=None):   self.message(msg, title, msg_type='about')
    def aboutQt(self,   msg, title=None):   self.message(msg, title, msg_type='aboutQt')

    def message_popup(self, msg, title='', buttons=None, handler=None, msg_type='success'):
        pass

    def success_popup(self, msg, title='', buttons=None, handler=None):
        return self.message_popup(msg, title, buttons, handler, msg_type='success')

    def info_popup(self, msg, title='', buttons=None, handler=None):
        return self.message_popup(msg, title, buttons, handler, msg_type='info')

    def warning_popup(self, msg, title='', buttons=None, handler=None):
        return self.message_popup(msg, title, buttons, handler, msg_type='warning')

    def alert_popup(self, msg, title='', buttons=None, handler=None):
        return self.message_popup(msg, title, buttons, handler, msg_type='alert')

    ##########################################################################
    ############ GUI functions ###############################################
    ##########################################################################

    def set_margin(self, margin):
        if AnyQt.USED_API == 'pyqt5':
            self.layout().setContentsMargins(margin, margin, margin, margin)
        else:
            self.layout().setMargin(margin)

    ##########################################################################
    ############ EVENTS ######################################################
    ##########################################################################

    def before_close_event(self):
        """ 
        Do something before closing widget 
        Note that the window will be closed anyway    
        """
        pass

    ##########################################################################
    ############ Properties ##################################################
    ##########################################################################

    @property
    def controls(self):
        """
        Return all the form controls from the the module
        """
        result = {}
        for name, var in vars(self).items():
            try:
                if isinstance(var, ControlBase):
                    result[name] = var
            except:
                pass
        return result

    ############################################################################
    ############ GUI Properties ################################################
    ############################################################################

    @property
    def form_has_loaded(self):
        return self._formLoaded

    @property 
    def form(self): 
        return self 
    
    @property
    def visible(self):
        return self.isVisible()

    @property
    def mainmenu(self):
        return self._mainmenu

    @mainmenu.setter
    def mainmenu(self, value):
        self._mainmenu = value

    @property
    def controls(self):
        """
        Return all the form controls from the the module
        """
        result = {}
        for name, var in vars(self).items():
            try:
                if isinstance(var, ControlBase):
                    result[name] = var
            except:
                pass
        return result

    ############################################################################
    ############ GUI Properties ################################################
    ############################################################################

    @property
    def form_has_loaded(self):
        return self._formLoaded

    @property
    def parent_widget(self):
        return self._parent_widget

    @property
    def form(self):
        return self

    @property
    def title(self):
        return self.windowTitle()

    @title.setter
    def title(self, value):
        self.setWindowTitle(value)

    @property
    def formset(self):
        return self._formset

    @formset.setter
    def formset(self, value):
        self._formset = value

    @property
    def uid(self):
        return self._uid

    @uid.setter
    def uid(self, value):
        self._uid = value

    @property
    def visible(self):
        return self.isVisible()

    ##########################################################################
    ############ PRIVATE FUNCTIONS ###########################################
    ##########################################################################
    
    def closeEvent(self, event):
        self.before_close_event()
        super(BaseWidget, self).closeEvent(event)
