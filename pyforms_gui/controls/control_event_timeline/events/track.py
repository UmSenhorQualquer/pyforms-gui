# !/usr/bin/python
# -*- coding: utf-8 -*-

from AnyQt.QtGui import QColor
from AnyQt import QtCore
from .event import Event


class Track(object):
	"""
	Track
	"""

	DEFAULT_COLOR = QColor(100, 100, 255)

	def __init__(self, widget, title='', color=None):
		self._title   = title
		self._color   = self.DEFAULT_COLOR if color is None else color
		self._widget  = widget
		self._index   = len(widget.tracks)
		self._periods = []

	def __len__(self):
		return len(self._periods)

	def __add__(self, other):
		if isinstance(other, Event):
			self._periods.append(other)
		return self

	def __sub__(self, other):
		if isinstance(other, Event):
			self._periods.remove(other)
		return self

	@staticmethod
	def whichTrack(y):
		return (y - 20) // 34

	@staticmethod
	def which_top(track):
		return track * 34 + 20

	@property
	def periods(self):
		return self._periods

	@property
	def color(self):
		return self._color

	@color.setter
	def color(self, value):
		self._color = value

	@property
	def title(self):
		return self._title

	@title.setter
	def title(self, value):
		self._title = value

	@property
	def index(self):
		"""
		:return: Index of the track in the timeline.
		"""
		return self._index

	@property
	def events(self):
		return self._events

	def draw_background(self, painter, start, end):
		painter.setOpacity(0.1)
		painter.fillRect(start, self.top_coordinate, end-start, self._widget.TRACK_HEIGHT, QtCore.Qt.black)
		painter.setOpacity(1.0)

	def draw(self, painter, start, end):
		"""
		
		:param painter: 
		:param start: 
		:param end: 
		:param index: 
		:return: 
		"""
		painter.drawLine(start, self.top_coordinate, end, self.top_coordinate)

	def draw_periods(self, painter, start, end):
		"""
		
		:param painter: 
		:param start: 
		:param end: 
		:return: 
		"""
		for time in self._periods:
			painter.setBrush(time.color)
			time.draw(painter)

	def draw_title(self, painter, start, end):
		"""
		
		:param painter: 
		:param index: 
		:return: 
		"""
		painter.setPen(QtCore.Qt.black)
		painter.setOpacity(0.5)
		painter.drawText(start+10, self.top_coordinate + painter.fontMetrics().height(), self.title)
		painter.setOpacity(1.0)

	def select_event(self, x, y):
		"""
		
		:param x: 
		:param y: 
		:return: 
		"""
		for delta in self._periods:
			if delta.collide(x, y): return delta
		return None


	def clear(self):
		"""
		
		"""
		del self._periods[:]
		self._periods = []

	@property
	def properties(self):
		return ['T', self.title, self.color.name()]

	@property
	def top_coordinate(self):
		"""
		:return: Top pixel coordinate
		"""
		return self._index*self._widget.TRACK_HEIGHT + self._widget.TOPTRACK_HEIGHT

	@property
	def bottom_coordinate(self):
		"""
		:return: Bottom pixel coordinate
		"""
		return self.top_coordinate + self._widget.TRACK_HEIGHT
