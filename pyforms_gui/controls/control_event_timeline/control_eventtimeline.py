#!/usr/bin/python
# -*- coding: utf-8 -*-

import csv, os
from confapp import conf
from AnyQt import QtCore, _api
from AnyQt.QtWidgets import QWidget, QScrollArea, QFileDialog, QMessageBox, QPushButton, QLabel, QSlider, QHBoxLayout, QVBoxLayout
from pyforms_gui.controls.control_base import ControlBase
from pyforms_gui.controls.control_event_timeline.utils.import_window import ImportWindow
from pyforms_gui.controls.control_event_timeline.timeline_widget import TimelineWidget
from pyforms_gui.controls.control_event_timeline.events.win_track import TimelinePopupWindow
from pyforms_gui.controls.control_event_timeline.graphs.graph import Graph
from pyforms_gui.controls.control_event_timeline.graphs.win_graph_to_event import Graph2Event
from pyforms_gui.controls.control_event_timeline.graphs.win_graph_properties  import GraphsProperties
from pyforms_gui.controls.control_event_timeline.graphs.win_events_generator import GraphsEventsGenerator
import traceback


class ControlEventTimeline(ControlBase, QWidget):
    """
        Timeline events editor

        **Short keys:**

            - **Control + Left**: Move event to the left.
            - **Control + Right**: Move event to the right.
            - **Delete**: Delete an event.
            - **L**: Lock an event.
            - **Control + Up**: Move an event up.
            - **Control + Down**: Move an event down.
            - **Shift + Control + Left**: Move an event end time to the left.
            - **Shift + Control + Right**: Move an event end to the right.
            - **Shift + Left**: Move an event beginning to the left.
            - **Shift + Right**: Move an event beginning to the right.
            - **S**: First press, mark the beginning of an event, Second press, create an event ending in the current cursor time.
            - **A**: Move the cursor to the left.
            - **D**: Move the cursor to the right.
            - **Q**: Select the previous event in the selected row.
            - **E**: Select the next event in the selected row.
    """

    def __init__(self, label="", default=0, max=100):
        QWidget.__init__(self)
        ControlBase.__init__(self, label, default)
        self._max = 100
        self._graphs_prop_win     = GraphsProperties(self._time, self)
        self._graphsgenerator_win = GraphsEventsGenerator(self._time)
        self._graph2event_win     = Graph2Event(self._time)

        ###############################################################################################
        ######## EVENTS ACTIONS #######################################################################
        ###############################################################################################

        # Popup menus that only show when clicking on a TIMELINEDELTA object
        event_remove_action = self.add_popup_menu_option(
            "Remove event", self.__removeSelected, key='Delete',
            icon=conf.ANNOTATOR_ICON_DELETE
        )
        separator_action = self.add_popup_menu_option("-")
        self._events_actions = [event_remove_action, separator_action]
        for action in self._events_actions: action.setVisible(False)

        ###############################################################################################
        ######## TRACKS ACTIONS #######################################################################
        ###############################################################################################

        # General right click popup menus
        track_properties_action = self.add_popup_menu_option(
            "Row properties",
            self.__open_track_properties_evt,
            icon=conf.ANNOTATOR_ICON_INFO
        )

        track_insert_action = self.add_popup_menu_option(
            "Insert row",
            self.__add_track_evt,
            icon=conf.ANNOTATOR_ICON_ADD
        )

        track_remove_action = self.add_popup_menu_option(
            "Remove row",
            self.__remove_current_track_evt,
            icon=conf.ANNOTATOR_ICON_DELETE
        )

        track_moveup_action = self.add_popup_menu_option(
            "Move up",
            self.__move_track_up_evt,
            icon=conf.PYFORMS_ICON_EVENTTIMELINE_IMPORT
        )

        track_movedown_action = self.add_popup_menu_option(
            "Move down",
            self.__move_track_down_evt,
            icon=conf.PYFORMS_ICON_EVENTTIMELINE_EXPORT
        )

        separator_action = self.add_popup_menu_option("-")

        self._tracks_actions = [
            track_properties_action, track_insert_action,
            track_remove_action, track_moveup_action,
            track_movedown_action, separator_action
        ]
        for action in self._tracks_actions: action.setVisible(False)



        ###############################################################################################
        ######## GRAPHS ACTIONS #######################################################################
        ###############################################################################################

        self.add_popup_menu_option("Graphs", self.open_graphs_properties, icon=conf.PYFORMS_ICON_EVENTTIMELINE_GRAPH)
        self.add_popup_menu_option("Apply a function to the graphs", self.__generate_graphs_events,
                                   icon=conf.PYFORMS_ICON_EVENTTIMELINE_GRAPH)
        self.add_popup_menu_option("Convert graph to events", self.__graph2event_event,
                                   icon=conf.PYFORMS_ICON_EVENTTIMELINE_GRAPH)
        
        self.add_popup_menu_option("-")
        
        self.add_popup_menu_option("Auto adjust rows", self.__auto_adjust_tracks_evt,
                                   icon=conf.PYFORMS_ICON_EVENTTIMELINE_REFRESH)

        self.add_popup_menu_option(
            "Remove everything",
            self.clean,
            icon=conf.ANNOTATOR_ICON_DELETE
        )

        self._importwin = None # import window.

    def __repr__(self):
        return "Timeline "+str(self.name)

    def init_form(self):
        # Get the current path of the file
        rootPath = os.path.dirname(__file__)

        vlayout = QVBoxLayout()
        hlayout = QHBoxLayout()

        if _api.USED_API == _api.QT_API_PYQT5:
            hlayout.setContentsMargins(0,0,0,0)
            vlayout.setContentsMargins(0,0,0,0)
        elif _api.USED_API == _api.QT_API_PYQT4:
            hlayout.setMargin(0)
            vlayout.setMargin(0)

        self.setLayout(vlayout)

        # Add scroll area
        scrollarea = QScrollArea()
        self._scrollArea = scrollarea
        scrollarea.setMinimumHeight(140)
        scrollarea.setWidgetResizable(True)
        scrollarea.keyPressEvent = self.__scrollAreaKeyPressEvent
        scrollarea.keyReleaseEvent = self.__scrollAreaKeyReleaseEvent

        vlayout.addWidget(scrollarea)

        # The timeline widget
        self._time = widget = TimelineWidget(self)
        widget._scroll = scrollarea
        scrollarea.setWidget(widget)

        # Timeline zoom slider
        slider = QSlider(QtCore.Qt.Horizontal)
        slider.setFocusPolicy(QtCore.Qt.NoFocus)
        slider.setMinimum(1)
        slider.setMaximum(100)
        slider.setValue(10)
        slider.setPageStep(1)
        slider.setTickPosition(QSlider.NoTicks)  # TicksBothSides
        slider.valueChanged.connect(self.__scaleSliderChange)

        slider_label_zoom_in = QLabel()
        slider_label_zoom_out = QLabel()
        slider_label_zoom_in.setPixmap(conf.PYFORMS_PIXMAP_EVENTTIMELINE_ZOOM_IN)
        slider_label_zoom_out.setPixmap(conf.PYFORMS_PIXMAP_EVENTTIMELINE_ZOOM_OUT)

        self._zoomLabel = QLabel("100%")
        hlayout.addWidget(self._zoomLabel)
        hlayout.addWidget(slider_label_zoom_out)
        hlayout.addWidget(slider)
        hlayout.addWidget(slider_label_zoom_in)

        # Import/Export Buttons
        btn_import = QPushButton("Import")

        btn_import.setIcon(conf.PYFORMS_ICON_EVENTTIMELINE_IMPORT)
        btn_import.clicked.connect(self.__open_import_win_evt)
        btn_export = QPushButton("Export")

        btn_export.setIcon(conf.PYFORMS_ICON_EVENTTIMELINE_EXPORT)
        btn_export.clicked.connect(self.__export)
        hlayout.addWidget(btn_import)
        hlayout.addWidget(btn_export)

        vlayout.addLayout(hlayout)


    ##########################################################################
    #### HELPERS/PUBLIC FUNCTIONS ############################################
    ##########################################################################

    def __add__(self, other):
        if isinstance(other, Graph):
            self._graphs_prop_win     += other
            self._graphsgenerator_win += other
            self._graph2event_win     += other
        return self

    def __sub__(self, other):
        if isinstance(other, int): 
            self._graphs_prop_win     -= other
            self._graphsgenerator_win -= other
            self._graph2event_win     -= other
        return self

    def add_event(self, begin, end, title='', row=0, track=None):
        """
        :param begin: Initial frame
        :param end: Last frame
        :param title: Event title
        :param row: Row to which the event should be added.
        """

        self._time.add_event(begin, end, title=title, track=track, row=row)
        self._time.repaint()

    def add_graph(self, name, data):
        """
        
        :param name: 
        :param data: 
        :return: 
        """
        self._time.add_graph(name, data)

    def add_track(self, title='', color=None):
        """
        Add a new track.
        :param str title: Title of the track.
        :param QColor color: Default color of the events in the track.
        :return: Return the added track.
        """
        return self._time.add_track(title=title, color=color)

    def get_track(self, title):
        """
        Get a track by its title
        :param str title: Title of the track.
        :return: Return the track with the matching title.
        """
        return self._time.get_track(title)


    def rename_graph(self, graph_index, newname):
        """
        Rename a graph by index.
        :param int graph_index: Index of the graph to rename.
        :param str newname: New name
        """
        self._time.graphs[graph_index].name = newname
        self._graphs_prop_win.rename_graph(graph_index, newname)
        self._graphsgenerator_win.rename_graph(graph_index, newname)
        self._graph2event_win.rename_graph(graph_index, newname)


    def import_graph_csv(self, filepath, separator=';', ignore_rows=0):
        """
        Import a new graph from a csv file.
        :param filename: 
        :param separator: 
        :param ignore_rows: 
        :return: 
        """
        with open(filepath, 'U') as csvfile:
            spamreader = csv.reader(csvfile, delimiter=separator)
            for i in range(ignore_rows): next(spamreader, None)
            name = os.path.basename(filepath).replace('.csv', '').replace('.CSV', '')
            chart = self._time.add_graph(name, spamreader)
            return chart

    def export_csv_file(self, filename):
        with open(filename, 'w') as csvfile:
            spamwriter = csv.writer(csvfile, dialect='excel')
            self._time.export_events_to_csvwriter(spamwriter)

    def import_csv_file(self, filename):
        with open(filename, 'r') as csvfile:
            spamreader = csv.reader(csvfile, dialect='excel')
            self._time.import_events_from_csvreader(spamreader)

    def import_csv(self, csvfile):
        """

        :param csvfile:
        """
        # If there are annotation in the timeline, show a warning
        if len(self._time._tracks) > 0:  # dict returns True if not empty
            message = ["You are about to import new data. ",
                       "If you proceed, current annotations will be erased. ",
                       "Make sure to export current annotations first to save.",
                       "\n",
                       "Are you sure you want to proceed?"]
            reply = QMessageBox.question(self,
                                         "Warning!",
                                         "".join(message),
                                         QMessageBox.Yes | QMessageBox.No,
                                         QMessageBox.No)

            if reply != QMessageBox.Yes:
                return

        self._time.import_events_from_csvreader(csvfile)

    def open_graphs_properties(self):
        """
        Opens the graphs properties.
        """
        self._graphs_prop_win.show()
        self._time.repaint()


    def open_import_graph_win(self, filepath, frame_col=0, val_col=1):
        """
        Open a window to import a graph from a csv file.
        :param str filepath: Path of the file to import.
        :param int frame_col: Column corresponding to the frames number in the csv file.
        :param int val_col: Column corresponding to the values in the csv file.
        """
        self.__open_import_win_evt()
        self._importwin.import_chart(filepath, frame_col, val_col)


    ##########################################################################
    #### EVENTS ##############################################################
    ##########################################################################

    def mouse_moveover_timeline_event(self, event):
        self._graphs_prop_win.mouse_moveover_timeline_event(event)



    @property
    def pointer_changed_event(self):
        return self._time._pointer.moveEvent

    @pointer_changed_event.setter
    def pointer_changed_event(self, value):
        self._time._pointer.moveEvent = value

    def __auto_adjust_tracks_evt(self):
        for i in range(len(self._time.tracks) - 1, -1, -1):
            track = self._time.tracks[i]
            if len(track) == 0:
                self._time -= track
            else:
                break

    def __add_track_evt(self):
        self._time.add_track()

    def __remove_track_from_bottom_evt(self):
        if len(self._time.tracks) > 0:
            track = self._time.tracks[-1]
            if len(track) == 0:
                self._time -= track

    def __move_track_up_evt(self):
        self._time.selected_row.move_up()

    def __move_track_down_evt(self):
        self._time.selected_row.move_down()

    def __generate_graphs_events(self):
        self._graphsgenerator_win.show()

    def __graph2event_event(self):
        self._graph2event_win.show()

    ##########################################################################
    #### PROPERTIES ##########################################################
    ##########################################################################

    @property
    def timeline_widget(self):
        return self._time

    @property
    def value(self):
        return self._time.position

    @value.setter
    def value(self, value):
        ControlBase.value.fset(self, value)
        self._time.position = value

    @property
    def max(self):
        return self._time.minimumWidth()

    @max.setter
    def max(self, value):
        self._max = value
        self._time.setMinimumWidth(value)
        self.repaint()

    @property
    def form(self):
        return self

    @property
    def rows(self):
        return self._time.tracks

    @property
    def graphs(self): return self._time.graphs

    @property
    def key_release_event(self):
        return self._time.key_release_event
    @key_release_event.setter
    def key_release_event(self, value):
        self._time.key_release_event = value

    ##########################################################################
    #### PRIVATE FUNCTIONS ###################################################
    ##########################################################################

    def about_to_show_contextmenu_event(self):
        """
        Hide and show context menu options.
        """
        # Hide and show events actions.
        for action in self._events_actions:
            action.setVisible(
                True if self._time._selected is not None else False
            )
        # Hide and show tracks actions.
        for action in self._tracks_actions:
            action.setVisible(
                True if self._time._selected_track is not None else False
            )

    

    def __open_track_properties_evt(self):
        """
        This controls makes possible the edition of a track in the
        timeline, based on the position of the mouse.

        Updates:
        - Track label
        - Track default color
        """
        current_track = self._time.current_mouseover_track
        parent = self._time

        # Tracks info dict and index
        i = current_track

        # Save current default color to override with selected track color
        timeline_default_color = parent.color
        try:
            parent.color = self._time._tracks[current_track].color
        except Exception as e:
            error_message = ("You tried to edit an empty track.",
                             "\n",
                             "Initialize it by creating an event first.")
            QMessageBox.warning(
                parent, "Attention!", "".join(error_message))
            return e

        # Create dialog
        dialog = TimelinePopupWindow(parent, i)
        dialog.setModal(True)  # to disable main application window

        # If dialog is accepted, update dict info
        if dialog._ui.exec_() == dialog.Accepted:
            # Update label
            if dialog.behavior is not None:
                self._time._tracks[i].title = dialog.behavior

            # Update color
            if self._time._tracks[i].color != dialog.color:
                for delta in self._time._tracks[i].events:
                    delta.color = dialog.color
                self._time._tracks[i].color = dialog.color
            self._time.repaint()
        else:
            pass

        # Restore timeline default color
        parent.color = timeline_default_color

    def __lockSelected(self):
        self._time.toggle_selected_event_lock()

    def __removeSelected(self):
        self._time.remove_selected_event()

    def __open_import_win_evt(self):
        """Import annotations from a file."""
        if self._importwin is None:
            self._importwin = ImportWindow(self)
        self._importwin.show()

    def __export(self):
        """Export annotations to a file."""

        try:

            if conf.PYFORMS_DIALOGS_OPTIONS:
                filename, ffilter = QFileDialog.getSaveFileName(parent=self,
                     caption="Export annotations file",
                     directory="untitled.csv",
                     filter="CSV Files (*.csv);;CSV Matrix Files (*.csv)",
                     options=conf.PYFORMS_DIALOGS_OPTIONS)
            else:
                filename, ffilter = QFileDialog.getSaveFileName(parent=self,
                                                                caption="Export annotations file",
                                                                directory="untitled.csv",
                                                                filter="CSV Files (*.csv);;CSV Matrix Files (*.csv)")

            filename = str(filename)
            ffilter = str(ffilter)
            if filename != "":
                with open(filename, 'w') as csvfile:
                    spamwriter = csv.writer(csvfile, dialect='excel')
                    if ffilter == 'CSV Files (*.csv)':
                        self._time.export_events_to_csvwriter(spamwriter)
                    elif ffilter == 'CSV Matrix Files (*.csv)':
                        self._time.exportmatrix_events_to_csvwriter(spamwriter)

        except Exception as e:
            traceback.print_exc()
            m = QMessageBox(QMessageBox.Critical, 'Error', str(e))
            m.exec_()

    def __export_2_csv_matrix(self):
        try:
            QMessageBox.warning(
                self, "Important!", 'Please note that this file cannot be imported after.')

            filename, _ = QFileDialog.getSaveFileName(parent=self,
                                                   caption="Export matrix file",
                                                   directory="untitled.csv",
                                                   filter="CSV Files (*.csv)",
                                                   options=QFileDialog.DontUseNativeDialog)
            if filename != "":
                with open(filename, 'w') as csvfile:
                    spamwriter = csv.writer(csvfile, dialect='excel')
                    self._time.exportmatrix_events_to_csvwriter(spamwriter)
        except Exception as e:
            traceback.print_exc()
            m = QMessageBox(QMessageBox.Critical, 'Error', str(e))
            m.exec_()

    def __remove_current_track_evt(self):
        reply = QMessageBox.question(self, 'Confirm',
                                     "Are you sure you want to remove the row and its events?",
                                     QMessageBox.Yes |
                                     QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self._time.remove_selected_track()


    def clean(self):
        reply = QMessageBox.question(self, 'Confirm',
                                     "Are you sure you want to clean everything?", QMessageBox.Yes |
                                     QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self._time.clean()


    def __scaleSliderChange(self, value):
        scale = 0.1 * value
        self._time.setMinimumWidth(scale * self._max)
        self._time.scale = scale
        self._zoomLabel.setText(str(value * 10).zfill(3) + "%")

    def __scrollAreaKeyReleaseEvent(self, event):
        modifiers = int(event.modifiers())
        self._time.keyReleaseEvent(event)

        QScrollArea.keyReleaseEvent(self._scrollArea, event)

    def __scrollAreaKeyPressEvent(self, event):
        modifiers = int(event.modifiers())

        if modifiers == QtCore.Qt.ControlModifier:
            event.ignore()

        if modifiers == QtCore.Qt.ShiftModifier:
            event.ignore()

        if modifiers == int(QtCore.Qt.ShiftModifier | QtCore.Qt.ControlModifier):
            event.ignore()

        if event.isAccepted():
            QScrollArea.keyPressEvent(self._scrollArea, event)
