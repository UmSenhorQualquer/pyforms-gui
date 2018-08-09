******************
The basic
******************

This page was based on the examples available at the github folder: `Tutorial - SimpleExamples <https://github.com/UmSenhorQualquer/pyforms/tree/master/tutorials/1.SimpleExamples>`_


Prepare the application class
==================================

Create the Python file that will store your applications. 

Example: **SimpleExample.py**


Import the library
____________________


Import the pyforms library, the BaseWidget and the Controls classes that you will need:

.. code:: python 
    
    import pyforms
    from   pyforms import BaseWidget
    from   pyforms.controls import ControlText
    from   pyforms.controls import ControlButton


Create your application class.
________________________________


This class should inherit from the class BaseWidget.


.. code:: python 
    
    class SimpleExample1(BaseWidget):
        
        def __init__(self):
            super(SimpleExample1,self).__init__('Simple example 1')

            #Definition of the forms fields
            self._firstname  = ControlText('First name', 'Default value')
            self._middlename = ControlText('Middle name')
            self._lastname   = ControlText('Lastname name')
            self._fullname   = ControlText('Full name')
            self._button     = ControlButton('Press this button')

    #Execute the application    
    if __name__ == "__main__": pyforms.start_app( SimpleExample1 )


If you run this file, it will produce the next window.

SimpleExample1

.. image:: /_static/imgs/getting-started-1.png


Add an action to the button
***************************

Create the action
===================

Create the class function that will work as the button action.

.. code:: python 
    
    def __buttonAction(self):
        """Button action event"""
        self._fullname.value = self._firstname.value +" "+ self._middlename.value +" "+self._lastname.value


Set the button action
======================

Configure the button to execute your function when pressed.  
Inside the class constructor add the code:

.. code:: python 
    
    #Define the button action
    self._button.value = self.__buttonAction

The final code should look like:

.. code:: python 
    
    import pyforms
    from   pyforms.basewidget import BaseWidget
    from   pyforms.controls import ControlText
    from   pyforms.controls import ControlButton

    class SimpleExample1(BaseWidget):
        
        def __init__(self):
            super(SimpleExample1,self).__init__('Simple example 1')

            #Definition of the forms fields
            self._firstname  = ControlText('First name', 'Default value')
            self._middlename = ControlText('Middle name')
            self._lastname   = ControlText('Lastname name')
            self._fullname   = ControlText('Full name')
            self._button     = ControlButton('Press this button')

            #Define the button action
            self._button.value = self.__buttonAction

        def __buttonAction(self):
            """Button action event"""
            self._fullname.value = self._firstname.value +" "+ self._middlename.value + \
            " "+ self._lastname.value

    #Execute the application
    if __name__ == "__main__": pyforms.start_app( SimpleExample1 )


The previous code produces the next window, after you had pressed the button:

.. image:: /_static/imgs/getting-started-2.png



Organize your form Controls
***************************

Use the BaseWidget.formset variable to organize the Controls inside the Window.  
`Find here more details about the formset variable <http://pyforms.readthedocs.org/en/latest/api-documentation/basewidget/#important-variables>`_


.. code:: python 
    
    ...

    class SimpleExample1(BaseWidget):
        
        def __init__(self):
            ...

            #Define the organization of the forms
            self.formset = [ ('_firstname','_middlename','_lastname'), '_button', '_fullname', ' ']
            #The ' ' is used to indicate that a empty space should be placed at the bottom of the window
            #If you remove the ' ' the forms will occupy the entire window

        ...


Result:

.. image:: /_static/imgs/getting-started-3.png

Try now:

.. code:: python 
    
    self.formset = [ {
            'Tab1':['_firstname','||','_middlename','||','_lastname'], 
            'Tab2':['_fullname']
        },
        '=',
        (' ','_button', ' ')
    ]
    #Use dictionaries for tabs
    #Use the sign '=' for a vertical splitter
    #Use the signs '||' for a horizontal splitter


## **Add a main menu**
***************************

To add a main menu to your application, first you need to define the functions that will work as the options actions.

.. code:: python 
    
    ...

    class SimpleExample1(BaseWidget):
        ...

        def __openEvent(self):
            ...

        def __saveEvent(self):
            ...

        def __editEvent(self):
            ...

        def __pastEvent(self):
            ...



After you just need to set the BaseWidget.mainmenu property inside your application class constructor as the example bellow.

.. code:: python 
    
    ...

    class SimpleExample1(BaseWidget):
        
        def __init__(self):
            ...
            self.mainmenu = [
                { 'File': [
                        {'Open': self.__openEvent},
                        '-',
                        {'Save': self.__saveEvent},
                        {'Save as': self.__saveAsEvent}
                    ]
                },
                { 'Edit': [
                        {'Copy': self.__editEvent},
                        {'Past': self.__pastEvent}
                    ]
                }
            ]

        ...


Add popup menu to the Controls
******************************

Create the functions that will work as the popup menu options actions, as you have than in the main menu chapter. After use the functions **add_popup_menu_option** or **add_popup_sub_menu_option** to add a popup menu or a popup submenu to your Control.

[Find here more details about the functions add_popup_menu_option and add_popup_sub_menu_option.](http://pyforms.readthedocs.org/en/latest/api-documentation/controls/#controlbase)

.. code:: python 
    
    ...

    class SimpleExample1(BaseWidget):
        
        def __init__(self):
            ...

            self._fullname.addPopupSubMenuOption('Path', 
                {
                    'Delete':           self.__dummyEvent, 
                    'Edit':             self.__dummyEvent,
                    'Interpolate':      self.__dummyEvent
                })
        ...


Result:

.. image:: /_static/imgs/getting-started-4.png


What next?
***********

Move to the `next chapter <http://pyforms.readthedocs.org/en/latest/getting-started/multiple-windows/>`_.
_____________________________________________________________________________________________________________

Find out what you can do with other Controls `here <http://pyforms.readthedocs.org/en/latest/api-documentation/controls/>`_.
____________________________________________________________________________________________________________________________


.. image:: /_static/imgs/Example1.png

.. image:: /_static/imgs/Example2.png

.. image:: /_static/imgs/Example3.png