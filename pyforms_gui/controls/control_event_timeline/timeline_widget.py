# !/usr/bin/python
# -*- coding: utf-8 -*-

from AnyQt import QtCore
from AnyQt.QtWidgets import QWidget, QMessageBox
from AnyQt.QtGui import QColor, QPainter, QFont, QCursor, QKeyEvent
from pyforms_gui.controls.control_event_timeline.events.track import Track
from pyforms_gui.controls.control_event_timeline.events.event import Event
from pyforms_gui.controls.control_event_timeline.graphs.graph import Graph
from pyforms_gui.controls.control_event_timeline.events.pointer import Pointer

class TimelineWidget(QWidget):
    """
    Timeline widget definition to be used in the ControlEventTimeline
    """
    TOPTRACK_HEIGHT     = 20  # Space in pixels of the top frames track.
    TRACK_HEIGHT        = 34  # Track height in pixels.
    TRACK_TITLE_TOP_POS = 12  # Relative position of the title of the track in pixels.

    EVENT_HEIGHT        = 30  # Height of each event in pixels.
    EVENT_TITLE_TOP_POS = 19  # Relative position of the title of each event in pixels.
    EVENT_RANGE_TOP_POS = 44  # Relative position of the range of each event in pixels.

    GRAPHS_COLORS = [
        QColor(240, 163, 255), QColor(0, 117, 220), QColor(153, 63, 0), QColor(76, 0, 92),
        QColor(25, 25, 25), QColor(0, 92, 49), QColor(43, 206, 72), QColor(255, 204, 153),
        QColor(128, 128, 128), QColor(148, 255, 181), QColor(143, 124, 0), QColor(157, 204, 0),
        QColor(194, 0, 136), QColor(0, 51, 128), QColor(255, 164, 5), QColor(255, 168, 187),
        QColor(66, 102, 0), QColor(255, 0, 16), QColor(94, 241, 242), QColor(0, 153, 143),
        QColor(116, 10, 255), QColor(153, 0, 0), QColor(255, 255, 0), QColor(255, 80, 5)
    ]  # List of colors to be used in new graphs


    def __init__(self, control):
        """
        Timeline widget
        :param control: object of the Pyforms control.
        """
        super(TimelineWidget, self).__init__()

        self.setMouseTracking(True)
        self.setMinimumWidth(300000)

        # timeline background color
        palette = self.palette()
        palette.setColor(self.backgroundRole(), QtCore.Qt.white)
        self.setPalette(palette)

        self.control = control  # parent control

        self._defautcolor = QColor(100, 100, 255)  # default events color


        self._graphs = []  # list of graphs
        self._tracks = []  # list of tracks

        self._scale = 1.0               # scale of the timeline
        self._last_mousex = None        # last know X coordinate of the mouse. Used for mouse drag.
        self._mouse_current_pos = None  # mouse current position

        self._moving = False          # flag: moving an event.
        self._resizing_began = False  # flag: resize of an event is active.
        self._resizing_ended = False  # flag: resize of an event ended.
        self._creating_event = False  # flag: event is being created
        self._creating_event_start = None  # flag: the S key pressed to create an event is active
        self._creating_event_end = None    # flag: the S key was pressed to finish the event

        self._selected = None             # selected event.
        self._selected_track = None       # selected track.
        self._pointer = Pointer(0, self)  # timeline pointer.

        # Video playback controls
        self._video_playing = False
        self._video_fps = None
        self._video_fps_min = None
        self._video_fps_max = None
        self._video_fps_inc = None

        self._repainting = False

    ##########################################################################
    #### HELPERS/FUNCTIONS ###################################################
    ##########################################################################

    def __add__(self, other):
        if isinstance(other, Track):
            self._tracks.append( other )
        else:
            self.control.__add__(other)
        return self

    def __sub__(self, other):
        if isinstance(other, Track):
            if self.selected_row == other:
                self.selected_row = None
            self._tracks.remove( other )
            for i, track in enumerate(self._tracks):
                track.index = i
            self.setMinimumHeight(Track.which_top(len(self._tracks)))
        elif isinstance(other, Graph):
            self._graphs.remove(other)
            self.repaint()
        else:
            self.control.__sub__(other)
        return self


    def add_graph(self, name, data):
        """
        Add a graph to the timeline.
        :param str name: Name of the graph
        :param list(int) data: List the size of the video with the graph value in each position.
        :return: Created graph.
        """
        graph = Graph(self, name=name, color=self.GRAPHS_COLORS[len(self._graphs)])
        graph.import_data(data)
        self._graphs.append(graph)
        self.repaint()
        return graph

    def add_track(self, title='', color=None):
        """
        Add a new track.
        :param str title: Title of the track.
        :param QColor color: Default color of the events in the track.
        :return: Return the added track.
        """
        t = Track(self, title=title, color=color)
        if self.selected_row is not None:
            index = self.selected_row.index
            self._tracks.insert(index, t)
            for i, track in enumerate(self.tracks):
                track.index = i
        else:
            self._tracks.append(t)
        self.setMinimumHeight(Track.which_top(len(self._tracks)))
        return t

    def get_track(self, title):
        """
        Get a track by its title
        :param str title: Title of the track.
        :return: Return the track with the matching title.
        """
        for track in self.tracks:
            if track.title==title:
                return track
        return None

    def add_event(self, begin, end, title='', track=None, lock=False, color=None, row=0):
        """
        Add a new event to the timeline.
        :param int begin: Initial frame of the event.
        :param int end: Final frame of the event.
        :param str title: Title of the event.
        :param Track track: Track object of the event.
        :param bool lock: Flag indicating if the event is lock or not.
        :param QColor color: Color of the event.
        :return: Return the created Event object.
        """
        if track is None:
            for i in range( len(self._tracks), row+1):
                self.add_track()
            track = self._tracks[row]
        return Event( begin, end, title=title, lock=lock, color=color, track=track, widget=self)

    def remove_selected_event(self):
        """
        Remove the selected event from the timeline.
        """
        if self._selected is not None and not self._selected.lock:
            self._selected.remove()
            self._selected = None
            self.repaint()

    def remove_selected_track(self):
        """
        Remove the selected track from the timeline.
        """
        if self._selected_track is not None:
            self._selected_track.remove()
            self.repaint()

    def move_track_up(self, track):
        """
        Move a track up
        :param Track track: Track to move
        """
        if track.index<=0: return

        i = track.index
        self._tracks[i-1], self._tracks[i] = self._tracks[i], self._tracks[i-1]
        for i, track in enumerate(self._tracks):
            track.index = i
        self.repaint()

    def move_track_down(self, track):
        """
        Move a track down
        :param Track track: Track to move
        """
        if track.index>=(len(self.tracks)-1): return

        i = track.index
        self._tracks[i+1], self._tracks[i] = self._tracks[i], self._tracks[i+1]
        for i, track in enumerate(self._tracks):
            track.index = i
        self.repaint()

    def toggle_selected_event_lock(self):
        """
        Toggle lock of the selected event.
        """
        if self._selected is not None:
            self._selected.lock = not self._selected.lock
            self.repaint()




    def clean(self):
        """
        Clean everything in the timeline
        """
        # remove tracks
        for i in range( len(self.tracks)-1 , -1, -1):
            track = self.tracks[i]
            track.remove()

        # remove graphs
        for i in range( len(self.graphs)-1 , -1, -1):
            graph = self.graphs[i]
            graph.remove()

        self.repaint()



    def find_track(self, ycoord):
        """
        Find a track.
        :param int ycoord: Y coordinate in pixels of the track to find.
        :return: Track object
        """
        if ycoord<=self.TOPTRACK_HEIGHT: return self._selected_track

        track_index = (ycoord - self.TOPTRACK_HEIGHT) // self.TRACK_HEIGHT
        ntracks 	= len(self.tracks)

        # if the track does not exists yet, create it
        if track_index >= ntracks:
            for i in range(ntracks, track_index+1):
                self.add_track()

        return self.tracks[track_index]



    def select_event(self, xcoord, ycoord):
        """
        Select an event based on the x and y pixel coordinates.
        :param int xcoord: X pixel coordinate.
        :param int ycoord: Y pixel coordinate.
        :return: Return the selected event.
        """
        # Check if the timeline pointer was selected
        if ycoord <= self.TOPTRACK_HEIGHT:
            return self._pointer if self._pointer.collide(xcoord, ycoord) else None

        # Check if the timeline events were selected
        i = Track.whichTrack(ycoord)
        if i >= len(self._tracks):
            return None

        return self._tracks[i].select_event(xcoord, ycoord)


    def x2frame(self, x):
        """
        Convert X pixel coordinate to a video frame number.
        :param int x: X coordinate in pixels.
        :return: Number of the correspondent frame.
        """
        return int(x / self._scale)

    def frame2x(self, frame):
        """
        Convert a video frame number to X pixel coordinate in the widget.
        :param int frame: Frame number in the video.
        :return: X coordinate of the correspondent pixel.
        """
        return int(frame * self._scale)




    ##########################################################################
    #### IO Functions ########################################################
    ##########################################################################

    def import_events_from_csvreader(self, csvreader):
        """
        Import events from a csv.reader object.
        :param csv.reader csvreader: csv.reader object from where the data will be imported.
        """
        self._selected = None

        track = self.tracks[-1] if len(self.tracks)>0 else None
        for row in csvreader:
            if len(row) == 0:
                continue

            if row[0] == "T":
                track = self.add_track( title = row[1], color = QColor(row[2]) )

            elif row[0] == "P":
                self.add_event( int(row[2]), int(row[3]), title=row[4], color=QColor(row[5]), lock=(row[1]=='True'), track=track)


    def export_events_to_csvwriter(self, csvwriter):
        """
        Export events to a csv.writer object.
        :param csv.writer csvwriter: csv.writer object to where the data will be exported.

        Current file structure:
        =======================

        --- CSV FILE BEGIN ---
        Track info line
        Event info line
        Event info line
        ...
        Track info line
        Event info line
        Event info line
        ...
        Track info line
        Event info line
        Event info line
        ...
        --- CSV FILE END ---

        Track info line format:
        =======================
        | T | Total # of events in this track |  |  | Color | Label |

        Event info line format:
        =======================
        | P | Lock status | Begin frame | End frame | Comment | Color |s
        """
        for index, track in enumerate(self._tracks):
            csvwriter.writerow(track.properties)
            for delta in track.events:
                csvwriter.writerow(delta.properties)


    def exportmatrix_events_to_csvwriter(self, csvwriter):
        """
        Export events to a csv.writer object in a matrix format.
        :param csv.writer csvwriter: csv.writer object to where the data will be exported.
        """
        for index, track in enumerate(self._tracks):
            _, track_title, _ = track.properties
            for delta in track.events:
                _, _, begin, end, delta_title, _, _ = delta.properties
                row = [track_title, begin, end, delta_title]
                csvwriter.writerow(row)


    ##########################################################################
    #### EVENTS ##############################################################
    ##########################################################################

    def paintEvent(self, event):
        """
        Paint event
        :param event:
        """
        super(TimelineWidget, self).paintEvent(event)

        painter = QPainter()
        painter.begin(self)

        painter.setRenderHint(QPainter.Antialiasing)
        painter.setFont(QFont('Decorative', 8))

        # find the start and end X coordinate to draw
        start = self.scrollbar.sliderPosition()
        end = start + self.parent().width() + 50

        # Draw graphs ##########################################################
        if len(self._graphs) > 0:
            painter.setPen(QtCore.Qt.black)
            middle = self.height() // 2
            painter.setOpacity(0.1)
            painter.drawLine(start, middle, end, middle)

        for chart in self._graphs:
            chart.draw(painter, start, end, 0, self.height())
        # End draw graph #######################################################

        for track in self.tracks:
            track.draw_title(painter, start, end)

        self.__draw_track_lines(painter, start, end)

        if self._selected_track is not None:
            self._selected_track.draw_background(painter, start, end)

        for track in self.tracks:
            track.draw_events(painter, start, end)

        # Draw the selected element
        if self._selected != None:
            painter.setBrush(QColor(255, 0, 0))
            self._selected.draw(painter, showvalues=True)

        # Draw the time pointer
        self._pointer.draw(painter, highlight=self._creating_event)
        painter.end()

        if not hasattr(self, '_is_refreshing'):
            self._is_refreshing = True
            self.update()
        else:
            del self._is_refreshing


    def mouseDoubleClickEvent(self, event):
        """

        :param event:
        :return:
        """
        xcoord = event.x()
        ycoord = event.y()

        if  self._selected is not None and \
                self._selected != self._pointer and \
                self._selected.collide( xcoord, ycoord ):
            # check if a period event is selected,
            # if so open the properties window
            self._selected.open_properties()

        elif ycoord > self.TOPTRACK_HEIGHT:
            # check if click was bellow the time track
            # if so create a new event
            track = self.find_track( ycoord )
            x     = xcoord / self._scale
            time  = Event(x, x + 10, title='', track=track, widget=self)
            self._selected = time
            self._selected_track = track
            self.repaint()

    def key_release_event(self, event):
        if self._selected is not None:
            modifier = int(event.modifiers())

            # Move the event (or the pointer) left
            if modifier == QtCore.Qt.ControlModifier and event.key() == QtCore.Qt.Key_Left:
                self._selected.move(-1, 0)
                event.ignore()
                self.repaint()

            # Move the event (or the pointer) right
            if modifier == QtCore.Qt.ControlModifier and event.key() == QtCore.Qt.Key_Right:
                self._selected.move(1, 0)
                event.ignore()
                self.repaint()

            if self._selected != self._pointer:
                # Delete the selected event
                if event.key() == QtCore.Qt.Key_Delete:
                    self.remove_selected_event()

                # Lock or unlock an event
                if event.key() == QtCore.Qt.Key_L:
                    self.toggle_selected_event_lock()

                # Move to the next event
                if event.key() == QtCore.Qt.Key_E:
                    index = self.selected_row.events.index(self._selected)
                    if index < len(self.selected_row.events)-1:
                        self._selected = self.selected_row.events[index+1]
                        self.position = self._selected.begin

                # Move to the previous event
                if event.key() == QtCore.Qt.Key_Q:
                    index = self.selected_row.events.index(self._selected)
                    if index > 0:
                        self._selected = self.selected_row.events[index - 1]
                        self.position = self._selected.begin

                # Move the event up
                if modifier == QtCore.Qt.ControlModifier and event.key() == QtCore.Qt.Key_Up:
                    self._selected.move(0, self._selected.top_coordinate - self.TRACK_HEIGHT)
                    self.repaint()

                # Move the event down
                if modifier == QtCore.Qt.ControlModifier and event.key() == QtCore.Qt.Key_Down:
                    self._selected.move(0, self._selected.top_coordinate + self.TRACK_HEIGHT)
                    self.repaint()

                # Move the event end left
                if modifier == int(
                        QtCore.Qt.ShiftModifier | QtCore.Qt.ControlModifier) and event.key() == QtCore.Qt.Key_Left:
                    self._selected.move_end(-1)
                    self.repaint()

                # Move the event end right
                if modifier == int(
                        QtCore.Qt.ShiftModifier | QtCore.Qt.ControlModifier) and event.key() == QtCore.Qt.Key_Right:
                    self._selected.move_end(1)
                    self.repaint()

                # Move the event begin left
                if modifier == QtCore.Qt.ShiftModifier and event.key() == QtCore.Qt.Key_Left:
                    self._selected.move_begin(-1)
                    self.repaint()

                # Move the event begin right
                if modifier == QtCore.Qt.ShiftModifier and event.key() == QtCore.Qt.Key_Right:
                    self._selected.move_begin(1)
                    self.repaint()

        else:
            # Keybinds to create an event at current frame
            if event.key() == QtCore.Qt.Key_S and not self._creating_event:
                # Start
                self._creating_event_start = self._pointer.frame
                self._creating_event = True

                # TODO Add some indicator that an event is being recorded, like
                # using the track selector circle to become red

                return

            elif event.key() == QtCore.Qt.Key_S and self._creating_event:
                # End, must be followed right after Start key and have no
                # effect otherwise
                self._creating_event_end = self._pointer.frame

                start = self._creating_event_start
                end = self._creating_event_end
                comment = ""

                if end > start:
                    track = self._selected_track
                    if track is None and len(self.tracks)>0:
                        track = self.tracks[0]
                    if track is None:
                        track = self.add_track()

                    self.add_event(start, end, comment, track=track )
                    self.repaint()
                    self._creating_event = False
                else:
                    self._creating_event = False

            # walk backwards 1 step
            elif event.key() == QtCore.Qt.Key_A:
                self.position = self.position - 1

            # forward 1 step
            elif event.key() == QtCore.Qt.Key_D:
                self.position = self.position + 1

            # Move to the first event
            elif event.key() == QtCore.Qt.Key_E:
                if self.selected_row is not None and len(self.selected_row)>0:
                    self._selected = self.selected_row.events[0]
                    self.position = self._selected.begin

            # Move to the last event
            elif event.key() == QtCore.Qt.Key_Q:
                if self.selected_row is not None and len(self.selected_row)>0:
                    self._selected = self.selected_row.events[len(self.selected_row)-1]
                    self.position = self._selected.begin

    def keyReleaseEvent(self, event:  QKeyEvent):
        super(TimelineWidget, self).keyReleaseEvent(event)

        self.key_release_event(event)


    def mousePressEvent(self, event):
        """
        Event called when the mouse buttons are pressed
        :param event: Mouse event
        """
        xcoord = event.x()
        ycoord = event.y()

        self._selected_track = self.find_track(ycoord)

        # Select the period bar
        self._selected = self.select_event(xcoord, ycoord)
        self._moving   = False
        self._resizing_began = False
        self._resizing_ended = False

        if self._selected is not None:
            # if no event is selected

            if event.buttons() == QtCore.Qt.LeftButton:
                # check the action to execute

                if self._selected.can_slide_end(xcoord, ycoord):
                    # Resize the event at the end
                    self._resizing_ended = True

                elif self._selected.can_slide_begin(xcoord, ycoord):
                    # Resize the event at the beginning
                    self._resizing_began = True

                elif self._selected.collide(xcoord, ycoord):
                    # Move the period
                    self._moving = True

        if ycoord <= self.TOPTRACK_HEIGHT and not self._moving:
            # move the time pointer
            self._pointer.position = self.x2frame(xcoord)

        self.repaint()

    def mouseMoveEvent(self, event):
        """
        Event called when the mouse is moved
        :param event: Mouse move event.
        """
        super(TimelineWidget, self).mouseMoveEvent(event)
        self.control.mouse_moveover_timeline_event(event)

        xcoord, ycoord = event.x(), event.y()
        self._mouse_current_pos = xcoord, ycoord

        # Do nothing if no event bar is selected
        if self._selected is None:
            return

        # set cursors
        if  self._selected.can_slide_begin(xcoord, ycoord) or \
                self._selected.can_slide_end(xcoord, ycoord):
            # resize cursor.
            self.setCursor(QCursor(QtCore.Qt.SizeHorCursor))

        elif self._selected.collide(xcoord, ycoord):
            # move cursor
            self.setCursor(QCursor(QtCore.Qt.SizeAllCursor))

        else:
            # normal cursor
            self.setCursor(QCursor(QtCore.Qt.ArrowCursor))

        if event.buttons() == QtCore.Qt.LeftButton:
            # move the period
            if self._last_mousex is not None:
                diff = xcoord - self._last_mousex
                if diff != 0:
                    if self._moving:
                        # move the selected period
                        self._selected.move(diff, ycoord)

                    elif self._resizing_began:
                        # resize the beginning of the period
                        self._selected.move_begin(diff)

                    elif self._resizing_ended:
                        # resize the end of the period
                        self._selected.move_end(diff)

                    self.repaint()
            self._last_mousex = xcoord



    def mouseReleaseEvent(self, event):
        """
        Event called when the mouse is released
        :param event: Mouse event
        """
        self._last_mousex = None


    ##########################################################################
    #### PRIVATE FUNTIONS ####################################################
    ##########################################################################

    def __draw_track_lines(self, painter, start, end):
        """
        Draw the track lines.
        :param QPainter painter: Qt QPainter object.
        :param int start: Initial X coordinate pixel to paint.
        :param int end: Final X coordinate pixel to paint.
        """
        # Draw only from pixel start to end
        painter.setPen(QtCore.Qt.DashLine)
        painter.setOpacity(0.3)
        for i, track in enumerate(self._tracks):
            track.draw(painter, start, end)

        # Draw vertical lines
        for x in range(start - (start % 100), end, 100):
            painter.drawLine(x, self.TOPTRACK_HEIGHT, x, self.height())
            string = "{0}".format(int(round(x / self._scale)))
            boundtext = painter.boundingRect(QtCore.QRectF(), string)
            painter.drawText(x - boundtext.width() / 2, 15, string)

            if self._video_fps:
                string = "{0}".format(int(round((x / self._scale) * (1000.0 / self._video_fps))))
                boundtext = painter.boundingRect(QtCore.QRectF(), string)
                painter.drawText(x - boundtext.width() / 2, 30, string)

        painter.setOpacity(1.0)


    def __set_frame_visible(self,  frame_index):
        """
        Set the frame index visible.
        :param int frame_index: Video frame index.
        """
        xcoord = self.frame2x(frame_index)
        scroll_limit = self.scrollbar.sliderPosition() + self.parent().width()-50

        if xcoord > scroll_limit:
            self.scrollbar.setSliderPosition(xcoord - self.parent().width() + 50)

        elif xcoord < self.scrollbar.sliderPosition():
            self.scrollbar.setSliderPosition(xcoord)

    ##########################################################################
    #### PROPERTIES ##########################################################
    ##########################################################################

    @property
    def scrollbar(self):
        """
        :return: The horizontal scrollbar.
        """
        return self._scroll.horizontalScrollBar()

    @property
    def position(self):
        """
        :return: The current position of the timeline.
        """
        return self._pointer._position

    @position.setter
    def position(self, value):
        self._pointer.position = value
        # Check if the player position is inside the scroll
        # if is not in, update the scroll position
        self.__set_frame_visible(value)
        self.repaint()

    @property
    def scale(self):
        """
        :return: Scale of the timeline.
        """
        return self._scale

    @scale.setter
    def scale(self, value):
        self._scale = value
        self.repaint()

    @property
    def color(self):
        """
        :return: Default color of the track events.
        """
        return self._defautcolor

    @color.setter
    def color(self, value):
        self._defautcolor = value

    @property
    def tracks(self):
        """
        :return: List of tracks in the timeline.
        """
        return self._tracks

    @property
    def graphs(self):
        """
        :return: List of graphs in the timeline.
        """
        return self._graphs

    @property
    def is_playing(self):
        return self._video_playing

    @property
    def fps(self):
        return self._video_fps

    @fps.setter
    def fps(self, value):
        self._video_fps = value

    @property
    def graphs_properties(self):
        return self.control._graphs_prop_win

    @property
    def current_mouseover_track(self):
        """
        :return: Return the track where the mouse is over.
        """
        if self._mouse_current_pos is None:
            return None
        return (self._mouse_current_pos[1] - self.EVENT_HEIGHT) // self.TRACK_HEIGHT

        self._moving = False          # flag: moving an event.
        self._resizing_began = False  # flag: resize of an event is active.
        self._resizing_ended = False  # flag: resize of an event ended.
        self._creating_event = False  # flag: event is being created
        self._creating_event_start = None  # flag: the S key pressed to create an event is active
        self._creating_event_end = None    # flag: the S key was pressed to finish the event

        self._selected = None             # selected event.
        self._selected_track = None       # selected track.
        self._pointer = Pointer(0, self)  # timeline pointer.

        # Video playback controls
        self._video_playing = False
        self._video_fps = None
        self._video_fps_min = None
        self._video_fps_max = None
        self._video_fps_inc = None

    @property
    def selected(self):
        return self._selected

    @selected.setter
    def selected(self, value):
        self._selected = value

    @property
    def pointer(self):
        return self._pointer

    @pointer.setter
    def pointer(self, value):
        self._pointer = value
    
    @property
    def moving(self):
        return self._moving

    @moving.setter
    def moving(self, value):
        self._moving = value

    @property
    def resizing_began(self):
        return self._resizing_began

    @resizing_began.setter
    def resizing_began(self, value):
        self._resizing_began = value

    @property
    def resizing_ended(self):
        return self._resizing_ended

    @resizing_ended.setter
    def resizing_ended(self, value):
        self._resizing_ended = value

    @property
    def creating_event(self):
        return self._creating_event

    @creating_event.setter
    def creating_event(self, value):
        self._creating_event = value

    @property
    def creating_event_start(self):
        return self._creating_event_start

    @creating_event_start.setter
    def creating_event_start(self, value):
        self._creating_event_start = value

    @property
    def creating_event_end(self):
        return self._creating_event_end

    @creating_event_end.setter
    def creating_event_end(self, value):
        self._creating_event_end = value

    @property
    def selected_row(self):
        """
        Return the selected track
        """
        return self._selected_track

    @selected_row.setter
    def selected_row(self, value):
        self._selected_track=value

    @property
    def selected_event(self):
        """
        Return the selected event.
        """
        return self._selected