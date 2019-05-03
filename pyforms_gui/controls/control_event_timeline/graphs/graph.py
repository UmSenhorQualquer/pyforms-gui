# !/usr/bin/python
# -*- coding: utf-8 -*-
from AnyQt.QtGui import QColor
from PyQt5.QtCore import QPoint


class Graph(object):
	"""
	"""

	def __init__(self, timeLineWidget, color=QColor(255, 0, 0), name='undefined'):
		"""		
		:param timeLineWidget: 
		:param color: 
		:param name: 
		"""
		self._data 		= []
		self._graph_max = None
		self._graph_min = None
		self._widget 	= timeLineWidget
		self._color 	= color
		self._zoom 		= 1.0
		self._top 		= 0
		self._name 		= name

		timeLineWidget += self

	def __unicode__(self): return self._name
	def __str__(self):     return self._name

	def __len__(self): 					 return len(self._data)
	def __getitem__(self, index):
		return self._data[index] if index<len(self) else None
	def __setitem__(self, index, value): 
		if index >= len(self):
			for i in range(len(self), index + 1): self._data.append(None)

		if value is not None:
			if value > self._graph_max: self._graph_max = value
			if value < self._graph_min: self._graph_min = value

		if index is None or value is None: 
			self._data[index] = None
		else:
			self._data[index] = value
	
	def import_data(self, data):
		"""
		Import the data from an array
		:param list(tuple(int,float)) data: List of coordinates (frame, value).
		"""
		self._graph_max = 0
		self._graph_min = 100000000000
		self._data 		= []
		for x, y in data:
			self[int(x)] = float(y)


	def remove(self):
		"""
		Remove the graph from the timeline
		"""
		self._widget -= self


	#####################################################################################
	###### PROPERTIES ###################################################################
	#####################################################################################

	@property
	def graph_min(self):
		return self._graph_min

	@graph_min.setter
	def graph_min(self, value):
		self._graph_min = value

	@property
	def graph_max(self):
		return self._graph_max

	@graph_max.setter
	def graph_max(self, value):
		self._graph_max = value

	@property
	def zoom(self):
		return self._zoom

	@zoom.setter
	def zoom(self, value):
		self._zoom = value

	@property
	def top(self):
		return self._top

	@top.setter
	def top(self, value):
		self._top = value

	#####################################################################################
	#####################################################################################
	#####################################################################################

	def draw(self, painter, left, right, top, bottom):
		"""
		
		:param painter: 
		:param left: 
		:param right: 
		:param top: 
		:param bottom: 
		:return: 
		"""
		painter.setPen(self._color)
		painter.setOpacity(0.7)

		fov_height 	 = (bottom - top) * self.zoom  #calculate the height visible
		start 		 = self._widget.x2frame(left)  #calculate the start frame to draw
		end 		 = self._widget.x2frame(right) #calculate the end frame to draw
		end 		 = len(self) if end > len(self) else end #check if the end frame his higher than the available data
		diff_max_min = (self._graph_max - self._graph_min) #calculate the difference bettween the lower and higher value

		# in case the frames have always de same value
		# set artificially a min and max to plot values at the middle
		if diff_max_min == 0:
			self._graph_min = self._graph_max - 1
			self._graph_max = self._graph_max + 1
			diff_max_min = 2
		elif diff_max_min < 0:
			diff_max_min = 1

		top = (-self._graph_min if self._graph_min > 0 else abs(self._graph_min)) * self._zoom

		last_coordinate   = None
		last_real_x_coord = None

		data_len_minus1 = len(self)-1

		for x in range(start, end+1):
			y = self[x]
			if y is None:
				last_coordinate = None
				last_real_x_coord = None
			else:
				y_pixel = self._top + ((top + y) * fov_height) // diff_max_min

				if 0<x<data_len_minus1 and self[x-1] is None and self[x+1] is None:
					painter.drawEllipse(
						QPoint(self._widget.frame2x(x), fov_height - y_pixel),
						2, 2
					)
				else:
					if last_coordinate:
						diff_frames = abs(x - last_real_x_coord)
						draw_from_coord = last_coordinate if diff_frames == 1 else (self._widget.frame2x(x), fov_height - y_pixel)
						painter.drawLine(draw_from_coord[0], draw_from_coord[1], self._widget.frame2x(x), fov_height - y_pixel)

					last_coordinate = self._widget.frame2x(x), fov_height - y_pixel
					last_real_x_coord = x


		painter.setOpacity(1.0)

	@property
	def name(self): return self._name

	@name.setter
	def name(self, value):
		if value != self._name:
			self._name = value

			if not hasattr(self, 'renaming_graph_flag'):
				self.renaming_graph_flag = True
				i = self._widget.graphs.index(self)
				self._widget.control.rename_graph(i, value)
				del self.renaming_graph_flag
		

	def mouse_move_evt(self, event, top, bottom):
		"""
		:param event: 
		:param top: 
		:param bottom: 
		:return: 
		"""

		frame 			= self._widget.x2frame(event.x())
		fov_height 		= (bottom - top) * self._zoom
		top 			= (-self._graph_min if self._graph_min > 0 else abs(self._graph_min)) * self._zoom
		diff_max_min 	= (self._graph_max - self._graph_min)
		if diff_max_min <= 0: diff_max_min = 1

		# no value
		if self[frame] is None: 
			self._widget.graphs_properties.coordinate_text = None
		else:
			self._widget.graphs_properties.coordinate_text = "Frame: {0} Value: {1}".format(frame, self[frame])


	def export_2_file(self, filename):
		"""
		
		:param filename: 
		:return: 
		"""
		with open(filename, 'w') as outfile:
			outfile.write(';'.join(['frame', 'value']) + '\n')
			for x, y in enumerate(self._data):
				if y is not None: outfile.write(';'.join([str(x), str(y)]) + '\n')
