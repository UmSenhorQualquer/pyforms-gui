# !/usr/bin/python
# -*- coding: utf-8 -*-

from confapp      import conf

from AnyQt           import QtCore, uic
from AnyQt.QtWidgets import QMenu, QAction
from AnyQt.QtGui     import QIcon, QKeySequence

class ControlBase(object):
    """
    All the Controls inherit from this Control, therefore you can find its functions and properties in all the other controls listed below.

    """

    def __init__(self, *args, **kwargs):
        """
        :param str label: Control label. Default = ''.
        :param str helptext: Text shown when the mouse is over the control. Default = None.
        :param str default: Initial value of the control. Default = None.

        :param bool visible: Flag to set the control visible or hidden. Default = True.
        :param bool enabled: Flag to set the control enabled or Disabled. Default = True.
        :param bool readonly: Flag to set the control readonly. Default = False.
        :param function changed_event: Function to call whenever the control value is updated. Default = None.  

        """

        self._form       = None  # Qt widget
        self._parent     = None  # Parent window
        self._popup_menu = None

        self._help          = kwargs.get('helptext', None)
        self._value         = kwargs.get('default',  None)
        self._label         = kwargs.get('label', args[0] if len(args)>0 else '')
        self._style         = kwargs.get('style', None)

        self.init_form()

        self.changed_event  = kwargs.get('changed_event', self.changed_event)
        self.enabled        = kwargs.get('enabled', True)
        self.readonly       = kwargs.get('readonly', False)
        if not kwargs.get('visible', True):  self.hide()


    def __repr__(self): return str(self._value)

    ##########################################################################
    ############ Funcions ####################################################
    ##########################################################################

    def init_form(self):
        """
        Load the control UI and initiate all the events.
        """     
        if self.help: self.form.setToolTip(self.help)

        if self._style: self.form.setStyleSheet(self._style)
   


    def load_form(self, data, path=None):
        """
        Loads the value of the control.

        :param dict data: It is a dictionary with the required information to load the control. 
        :param str path: Optional parameter that can be used to save the data.  
        """
        if 'value' in data:
            self.value = data['value']

    def save_form(self, data, path=None):
        """
        Save a value of the control to a dictionary.  

        :param dict data: Dictionary where the control value should be saved.  
        :param str path: Optional parameter that can be used to load the data.  
        """
        data['value'] = self.value
        return data

    def show(self):
        """
        Show the control
        """
        if self.form is None:
            return
        elif self.form==self:
            super(ControlBase,self).show()
        else:
            self.form.show()

    def hide(self):
        """
        Hide the control
        """
        if self.form is None:
            return
        elif self.form==self:
            super(ControlBase,self).hide()
        else:
            self.form.hide()


    def __create_popup_menu(self):
        if not self._popup_menu:
            self.form.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
            self.form.customContextMenuRequested.connect(self._open_popup_menu)
            self._popup_menu = QMenu(self.parent)
            self._popup_menu.aboutToShow.connect( self.about_to_show_contextmenu_event)

    def add_popup_submenu(self, label, submenu=None):
        """
        It returns a new sub popup menu. If submenu is open the menu is added to the main popup menu.

        :param str label: Label of the option  
        :param QMenu submenu: Parent submenu to which the option should be added. If no value is set, then the option will be added to the main popup menu.  
        """
        self.__create_popup_menu()
        menu = submenu if submenu else self._popup_menu
        submenu = QMenu(label, menu)
        menu.addMenu(submenu)
        return submenu

    def add_popup_menu_option(self, label, function_action=None, key=None, icon=None, menu=None):
        """
        Add an option to the Control popup menu.  

        :param str label: Label of the option  
        :param function function_action: The function that should be executed when the menu is selected.  
        :param str key: Short key.  
        :param QIcon or str icon: Icon.  
        :param QMenu submenu: Parent submenu to which the option should be added. If no value is set, then the option will be added to the main popup menu.  
        
        .. code:: python

            control.add_popup_menu_option('option 0', function_action=self._do_something)
            submenu1 = control.add_popup_submenu('menu 1')
            submenu2 = control.add_popup_submenu('menu 2', submenu=submenu1)
            control.add_popup_menu_option('option 1', function_action=self._do_something, key='Control+Q', submenu=submenu2)
        """
        self.__create_popup_menu()

        menu = menu if menu else self._popup_menu

        if label == "-":
            return menu.addSeparator()
        else:
            action = QAction(label, self.form)
            if icon is not None:
                action.setIconVisibleInMenu(True)
                action.setIcon(icon if isinstance(icon, QIcon) else QIcon(icon) )
            if key != None:
                action.setShortcut(QKeySequence(key))
            if function_action:
                action.triggered.connect(function_action)
                menu.addAction(action)
            return action


    ##########################################################################
    ############ Events ######################################################
    ##########################################################################

    def changed_event(self):
        """
        Function called when ever the Control value is changed. The event function should return True if the data was saved with success.

        """
        return True

    def about_to_show_contextmenu_event(self):
        """
        Function called before the Control popup menu is opened.
        """
        pass

    def _open_popup_menu(self, position):
        if self._popup_menu:
            self._popup_menu.exec_(self.form.mapToGlobal(position))

    ##########################################################################
    ############ Properties ##################################################
    ##########################################################################

    ##########################################################################
    # Set the Control enabled or disabled

    @property
    def enabled(self):
        """
        Returns or set if the control is enable or disable.
        """
        return self.form.isEnabled()

    @enabled.setter
    def enabled(self, value):
        self.form.setEnabled(value)

    ##########################################################################
    # Return or update the value of the Control

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
        if oldvalue != value:
            self.changed_event()

    
    @property
    def name(self): 
        """
        This property returns or set the name of the control.
        """
        return self.form.objectName()

    @name.setter
    def name(self, value):
        self.form.setObjectName(value)

    ##########################################################################
    # Return or update the label of the Control

    @property
    def label(self):
        """
        Returns or sets the label of the control.
        """
        return self._label

    @label.setter
    def label(self, value):
        self._label = value

    ##########################################################################
    # Parent window

    @property
    def parent(self):
        """
        Returns or set the parent basewidget where the Control is.
        """
        return self._parent

    @parent.setter
    def parent(self, value):
        self._parent = value

    @property
    def visible(self):
        """
        Return the control visibility.
        """
        return self.form.isVisible()

    @property
    def help(self):
        """
        Returns or set the tip box of the control.
        """
        return self._help if self._help else ''

    @property
    def error(self): return None

    @error.setter
    def error(self, value):
        pass

    @property
    def label_visible(self): return None

    @label_visible.setter
    def label_visible(self, value):
        pass

    @property
    def readonly(self):
        """
        Set and return the control readonly state.
        """
        return None

    @readonly.setter
    def readonly(self, value):
        pass

    @property
    def css(self): return None

    @css.setter
    def css(self, value):
        pass


    ##########################################################################
    ############ Properties just for the GUI version #########################
    ##########################################################################

    ##########################################################################
    # Return the QT widget

    @property
    def form(self):
        """
        Returns the QWidget of the control.
        """
        return self._form
