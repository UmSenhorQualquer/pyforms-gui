from pyforms.basewidget import BaseWidget
from pyforms_gui.controls.control_button import ControlButton
from pyforms_gui.controls.control_text import ControlText
from pyforms_gui.controls.control_number import ControlNumber
from pyforms_gui.controls.control_checkbox import ControlCheckBox

from confapp import conf
from AnyQt.QtGui import QColor
from AnyQt.QtWidgets import QColorDialog

class EventWindow(BaseWidget):

    def __init__(self, parent_win, event):
        BaseWidget.__init__(self, 'Edit frame', parent_win=parent_win)

        self.event = event
        self._widget = parent_win

        self.set_margin(5)

        self._applybtn = ControlButton('Apply', default=self.__apply_evt)
        self._label = ControlText('Label', default=event.title)
        self._begin = ControlNumber(
            'Begin',
            default=event.begin,
            minimum=0,
            maximum=100000000000000,
            changed_event=self.__begin_changed_event
        )
        self._end   = ControlNumber(
            'End',
            default=event.end,
            minimum=0,
            maximum=100000000000000,
            changed_event=self.__end_changed_event
        )
        self._color = ControlButton(str(event.color.name()), default=self.__pick_color_evt)
        self._lock  = ControlCheckBox('Locked', default=event.lock)

        self.formset = [
            '_label',
            ('_begin', '_end'),
            ('_color', '_lock'),
            '_applybtn'
        ]

    def update_form(self, event):
        self.event = event
        self._label.value = event.title
        self._end.value = int(event.end)
        self._begin.value = int(event.begin)
        self._lock.value = event.lock
        self._color.label = str(event.color.name())

    def __apply_evt(self):
        self.event.title = self._label.value
        self.event.end = self._end.value
        self.event.begin = self._begin.value
        self.event.lock = self._lock.value
        self.event.color = self._color.label
        self._widget.repaint()
        self.close()

    def __pick_color_evt(self):
        color = QColorDialog.getColor(
            initial = QColor(self._color.label),
            parent = self._widget,
            options = conf.PYFORMS_COLORDIALOGS_OPTIONS
        )
        if color:
            self._color.label = color.name()

    def __begin_changed_event(self):
        if not hasattr(self, '_updating') and self._begin.value >= self._end.value:
            self._updating = True
            self._begin.value = self._end.value - 1
            del self._updating

    def __end_changed_event(self):
        if not hasattr(self, '_updating') and self._end.value <= self._begin.value:
            self._updating = True
            self._end.value = self._begin.value + 1
            del self._updating

