# !/usr/bin/python
# -*- coding: utf-8 -*-

from AnyQt.QtGui import QColor
from .win_event import EventWindow

class Event(object):
	"""
	Class representing a time period \ event.
	"""

	def __init__(self, begin, end=30, title=None, lock=False, color=None, track=None, widget=None):
		"""
		Constructor
		
		:param int begin: First frame
		:param int end: Last frame
		:param str title: Event title
		:param bool lock: Flag to set the event lock
		:param AnyQt.QtGui.QColor color: Color of the event
		:param Track track: Track to witch the period will be added
		:param TimelineWidget widget: Parent timeline widget
		"""
		self._track  = track
		self._widget = widget
		self._title  = title
		self._lock 	 = lock
		self._begin  = begin
		self._end 	 = end
		self._end 	 = end
		self._color  = track.color if color is None else color
		
		track += self

	##########################################################################
	#### HELPERS/FUNCTIONS ###################################################
	##########################################################################


	def collide(self, xcoord, ycoord):
		"""
		Check if the x,y coordinate collides with the time period
		:param int xcoord: X coordinate in pixels.
		:param int ycoord: Y coordinate in pixels.
		:return: True if collide, False otherwise.
		"""
		return self.begin_coordinate <= xcoord <= self.end_coordinate and self.top_coordinate <= ycoord <= self.bottom_coordinate

	def in_range(self, start, end):
		"""
		Check if the period is within the limits [start;end]
		:param int start: Initial X coordinate
		:param int end: Final X coordinate
		:return: True if in range, False otherwise
		"""
		return start <= self.begin_coordinate and end >= self.end_coordinate or \
			   self.begin_coordinate <= start <= self.end_coordinate or \
			   self.begin_coordinate <= end <= self.end_coordinate

	def can_slide_begin(self, xcoord, ycoord):
		"""
		Checks if xcoord and ycoord pixel coordinate can slide the beginning of the period.
		:param int xcoord: X coordinate in pixels.
		:param int ycoord: Y coordinate in pixels.
		:return boolean: True if the event can be slided, false if not.
		"""
		# if locked does nothing
		if self._lock: return

		begin = int(round(self.begin_coordinate))
		end   = int(round(self.end_coordinate))
		return begin <= xcoord <= (begin+10) and \
			   self.top_coordinate <= ycoord <= self.bottom_coordinate and \
			   (xcoord-end)**2 > (xcoord-begin)**2

	def can_slide_end(self, x, y):
		"""
		Checks if x,y pixel coordinate can slide the end of the period.
		:param int x: X coordinate in pixels.
		:param int y: Y coordinate in pixels.
		:return boolean: True if the event can be slided, false if not.
		"""
		# if locked does nothing
		if self._lock: return

		begin = int(round(self.begin))
		end   = int(round(self.end))
		#check if the delta is not locked
		#check if the x is inside an range of 10 pixels
		#check if the y is within the boundaries of the delta
		return not self._lock and \
		   (end-10) <= x <= end and \
		   self.top_coordinate <= y <= self.bottom_coordinate and \
		   (x-end)**2 < (x-begin)**2

	def move_end(self, xdelta):
		"""
		Move the right edge of the period rectangle.
		:param int xdelta: X delta coordinate in pixels to move
		"""
		# Do nothing if locked
		if self._lock: return

		jump = xdelta / self._widget.scale

		# Do nothing if trying to go over the pther edge
		if (self.end_coordinate+jump) <= self.begin_coordinate and jump < 0:
			return

		# Increment accordingly
		self._end += jump

		# Minimum begin position is at 0
		if self._end > (self._widget.width() / self._widget.scale):
			self._end = (self._widget.width() / self._widget.scale)

	def move_begin(self, xcoord):
		"""
		Move the left edge of the period rectangle.
		:param int xdelta: X delta coordinate in pixels to move
		"""
		# Do nothing if locked
		if self._lock: return

		jump = xcoord/self._widget.scale

		# Do nothing if trying to go over the other edge
		if (self._begin+jump) >= self._end and jump > 0:
			return

		# Increment accordingly
		self._begin += jump

		# Minimum begin position is at 0
		if self._begin < 0: self._begin = 0



	def move(self, xdelta, ycoord):
		"""
		Move the event period more X and Y coordinates
		:param int xdelta: X delta to move in pixels
		:param int ycoord: Y coordinate to which the period should be moved
		"""
		# The period is locked, do nothing.
		if self._lock: return

		# if the new positions are within the 0 and maximum position,
		# then update the period positions
		if  (self.begin_coordinate + xdelta) >= 0 and \
			(self.end_coordinate + xdelta) <= self._widget.width():
			# update the positions
			delta = xdelta / self._widget.scale
			self._begin += delta
			self._end   += delta

		if not (self.track.bottom_coordinate <= ycoord <= self.track.top_coordinate):
			self.track = self._widget.find_track(ycoord)


	def draw(self, painter, showvalues=False):
		"""
		
		:param painter: 
		:param showvalues: 
		:return: 
		"""
		start, end 	 = self.begin_coordinate, self.end_coordinate
		transparency = 0.1 if self._lock else 0.5

		painter.setPen(QColor(0, 0, 0))
		painter.setOpacity(transparency)
		painter.drawRoundedRect( start, self.top_coordinate, end-start, self._widget.EVENT_HEIGHT, 3, 3)

		painter.setOpacity(1.0)
		painter.drawText(start + 3, self.top_coordinate + self._widget.EVENT_TITLE_TOP_POS, self.title)
		if showvalues:
			painter.drawText(
				start, self.top_coordinate + self._widget.EVENT_RANGE_TOP_POS,
				"[{};{}] delta:{}".format( int(self.begin_coordinate), int(self.end_coordinate), int(self.end_coordinate-self.begin_coordinate) )
			)

	def remove(self):
		"""
		Remove the period from the tracks
		"""
		self.track = None

	def open_properties(self):
		"""
		Open the properties window
		"""
		if hasattr(self, 'edit_form'):
			self.edit_form.update_form(self)
		else:
			self.edit_form = EventWindow(self._widget, self)

		self.edit_form.show()

	def __apply_properties_evt(self):
		"""
		Event called to apply the properties values in the Perido window
		:return:
		"""
		self._title = self.edit_form.comment
		self._begin = self.edit_form.begin
		self._end   = self.edit_form.end
		self._widget.repaint()
		self.edit_form.hide()

	##########################################################################
	#### PROPERTIES ##########################################################
	##########################################################################

	@property
	def title(self):
		return self._title

	@title.setter
	def title(self, value):
		self._title = value

	@property
	def lock(self):
		return self._lock

	@lock.setter
	def lock(self, value):
		self._lock = value

	@property
	def begin(self):
		return self._begin

	@begin.setter
	def begin(self, value):
		self._begin = value

	@property
	def end(self):
		return self._end

	@end.setter
	def end(self, value):
		self._end = value


	@property
	def track(self):
		"""
		:return: The current track
		"""
		return self._track

	@track.setter
	def track(self, value):
		"""
		Set the current track.
		:param value:
		"""
		# check if the new track is different from the previous.
		# if so update the tracks events lists
		if self._track != value:
			self._track -= self

			if value is not None:
				value += self

		self._track = value



	@property
	def top_coordinate(self):
		return self._track.top_coordinate + 2

	@property
	def bottom_coordinate(self):
		return self._track.bottom_coordinate - 2

	@property
	def begin_coordinate(self):
		return self._begin * self._widget.scale

	@begin_coordinate.setter
	def begin_coordinate(self, value):
		if self._lock: return
		self._begin = value / self._widget.scale
		if self._begin < 0: self._begin = 0

	@property
	def end_coordinate(self):
		return self._end * self._widget.scale

	@end_coordinate.setter
	def end_coordinate(self, value):
		if self._lock: return
		self._end = value / self._widget.scale
		if self._end > (self._widget.width() / self._widget.scale):
			self._end = (self._widget.width() / self._widget.scale)





	@property
	def color(self):
		return self._color

	@color.setter
	def color(self, value):
		self._color = QColor(value) if (type(value) == str) else value

	@property
	def bgrcolor(self):
		return self._color.blue(), self._color.green(), self._color.red()

	@property
	def properties(self):
		return ['P',
		        self._lock,
		        int(round(self._begin)),
		        int(round(self._end)),
		        self._title,
		        self._color.name(),
		        self.track]

	@properties.setter
	def properties(self, value):
		self._lock 	= value[1] == 'True'
		self._begin = int(value[2])
		self._end 	= int(value[3])
		self._title = value[4]
		self._color = QColor(value[5])
		self.track 	= int(value[6])

		self.checkNumberOfTracks()
