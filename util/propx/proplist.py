#
# Copyright 2019 justworx
# This file is part of the trix project, distributed under 
# the terms of the GNU Affero General Public License.
#


from .propseq import *


# -------------------------------------------------------------------
#
#
# PROP-LIST
#
#
# -------------------------------------------------------------------

class proplist(propseq):
	"""
	Wrap objects in a proplist to provide a variety of useful features
	for manipulation and display.
	"""
	# Now what am I going to do with this? The superclasses handle
	# everything proplist needed to do. Guess I'll just...
	pass



class propgrid(proplist):
	"""
	The `propgrid` class separates a header row from the data rows
	that follow. It's intended for data that consists of a list of
	equal-length lists, such as is generated by data.dbgrid.
	
	NOTE: data.dbgrid always prepends the header row to query results.
	      The 'header' kwarg is accepted in case we need to pass a grid
	      (list of lists) that's not prepended with column titles.
	"""
	
	def __call__(self, *a, **k):
		"""
		The __call__ method overridden to separate the header from the
		data portion of this grid.
		
		When the class is propgrid, all calls to .o are returned from 
		propgrid.o, and all calls to __call__ are returned from here - 
		even when it's superclasses (or even subclasses)  making the
		call - so it's OK to have a different self.__o.
		"""
		try:
			return self.__o
		except:
			#
			# FIRST:
			#  - Get the grid from the propx.__call__ method, where it will
			#    be created from stored constructor args.
			#
			grid = proplist.__call__(self, *a, **k)
			
			#
			# NEXT:
			#  - Intuitively, we *should*, here, be getting the actual grid 
			#    list, but we're not. Instead, we're getting the method that 
			#    was passed to __init__ (along with kwargs) to be executed - 
			#    and a return value set into self.__o - on first call to 
			#    __call__ (and just self.__o returned on subsequent calls).
			#
			
			#
			# SO...
			#  - split the grid header from grid data (if necessary).
			#
			header = self.k.get('header')
			if header:
				self.__o = grid
				self.__h = header
				self.__hh = True
			else:
				self.__o = grid[1:]
				self.__h = grid[0]
				self.__hh = False
			
			return self.__o
	
	
	
	
	
	@property
	def o(self):
		"""
		Override default `self.o` to reflect value custom to this 
		class. That is, the header in grids.
		"""
		try:
			return self.__o
		except:
			self.__call__(*self.a, **self.k)
			return self.__o
	
	@property
	def h(self):
		"""Short alias. Returns the value of the header row."""
		try:
			return self.__h
		except:
			self.o
			return self.__h
	
	@property
	def header(self):
		"""Return the value of the header row."""
		return self.h
	
	@property
	def hh(self):
		"""
		Short alias for `self.has_header` - True if a header row exists.
		"""
		try:
			return self.__hh
		except:
			self.o
			return self.__hh
	
	@property
	def has_header(self):
		"""
		Indicates True or False - whether this grid has a header row.
		"""
		return self.hh
	
	
			
	@property
	def gen(self):
		"""
		Generates the header row (if it exists) and all data rows.
		"""
		
		try:
			yield(self.__h)
		except AttributeError:
			#self.__call__()
			self.o
			yield(self.__h)
		
		for r in self.o:
			yield(r)
	
	
	
	def grid(self, *a, **k):
		"""
		Display this data formatted as a grid.
		
		Overrides `proplist.grid` to expose the header, which propgrid
		separates from the data for easier data-manipulation.
		"""
		
		k['f'] = 'Grid'
		trix.display(list(self.gen), *a, **k)
	
	
	
	#
	# DB-GRID
	#
	def dbgrid(self, tableName, **k):
		"""
		Returns a `DBGrid` object containing this object's data in a table
		named `tableName`.
		
		The value of any keyword arguments given must be a grid - a list
		of lists containing an equal number of values, with a column name
		list prepended as item zero. An additional table (named for the
		keyword) will be created in the resulting `DBGrid` object.
		
		NOTE: 
		Calling this method will fail if `self.o` (or any suplimentary
		tables defined by the passage of keyword arguments) is not a list
		of lists each containing an equal number of items. 
		"""
		g = trix.ncreate('data.dbgrid.DBGrid', **k)
		g.add(tableName, self.o, self.h)
		return g

