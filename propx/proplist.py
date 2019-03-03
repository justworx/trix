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
	
	def __getitem__(self, key):
		return type(self)(self.o[key])
	
	def __setitem__(self, key, v):
		self.o[key] = v
	
	@property
	def sorted(self):
		"""
		Return a proplist with sorted content.
		"""
		return type(self)(sorted(self.o))
	
	@property
	def reversed(self):
		"""Return a proplist with reversed content."""
		return type(self)(reversed(self.o))
	
	@property
	def lines(self):
		"""Generate string items (lines)."""
		for line in self.o:
			yield (str(line))
	
	
	#
	#
	# SIMPLE - iterators, data values
	#
	#
	def filter(self, fn, *a, **k):
		"""
		Pass callable `fn` that returns False for items that should not
		be selected. Optional args/kwargs are received by fn.
		
		Returns filter object.
		"""
		return filter(fn, self.o, *a, **k)
	
	
	def filtered(self, fn, *a, **k):
		"""
		Return a proplist containing results filtered by function `fn`.
		
		```
		d = trix.path('~').dir()
		d.list.filtered(lambda x: x[1]=='f').o
		```
		"""
		return proplist(list(self.filter(fn,*a,**k)))
	
	
	#
	#
	# COMPLEX - Use, select, and manipulate list data.
	#
	#	
	def each (self, fn, *a, **k):
		"""
		Argument `fn` is a callable that operates on items from `self.o` 
		in place, one item at a time. 
		
		Returns `self`.
		"""
		for v in self.o:
			fn(v, *a, **k)
		return self
	
	
	def select (self, fn, *a, **k):
		"""
		Argument `fn` is a callable that selects/alters  items one at a 
		time, storing them in an xprop wrapper and returning the result.
		
		```
		from trix.propx import *
		pl = proplist([1,2,3])
		pl.select(lambda o: o*9) 
		```
		"""
		r = []
		for v in self.o:
			r.append(fn(v, *a, **k))
		return type(self)(r)
	
	
	#
	#
	# DISPLAY
	#  - Display lists as json or in grids/tables/lists
	#
	#
	def grid(self, *a, **k):
		"""Display as Grid."""
		k['f'] = 'Grid'
		trix.display(self.o, *a, **k)
	
	def list(self, *a, **k):
		"""Display as List."""
		k['f'] = 'List'
		trix.display(self.o, *a, **k)
	
	def table(self, *a, **k):
		"""Display as Table. Pass keyword argument 'width'."""
		k['f'] = 'Table'
		trix.display(self.o, *a, **k)
	
	
	
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
		g.add(tableName, self.o)
		return g





# -------------------------------------------------------------------
#
#
# PROP-GRID 
#
#
# -------------------------------------------------------------------

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
			# get the grid from the propx.__call__ method, where it will
			# be created from stored constructor args.
			#
			grid = proplist.__call__(self, *a, **k)
			
			# now split the grid header from grid data (if necessary)
			self.__o = grid
			if self.has_header:
				self.__o = grid
				self.__h = self.k.get('header')
			else:
				self.__h = grid[0]
				self.__o = grid[1:]
				return self.__o
	
	
	@property
	def gen(self):
		#
		# Generates the header row and all data rows.
		#
		yield(self.header)
		for r in self.o:
			yield(r)

	
	@property
	def has_header(self):
		"""
		Return True if a header row was given to the constructor by
		keyword argument, else False.
		"""
		try:
			return self.__hh
		except:
			self.__hh = bool(self.k.get('header'))
			return self.__hh
		
	
	@property
	def header(self):
		"""
		Return a proplist containing grid header (column names).
		Call as a function to return the header list.
		"""
		try:
			return proplist(self.__h)  # return that header
		except:
			# after self.o is called, self.header (self.__h) exists.
			self.o
			return proplist(self.__h)
	
	
	def grid(self, *a, **k):
		"""
		Display this data formatted as a grid.
		
		Overrides `proplist.grid` to expose the header, which propgrid
		separates from the data for easier data-manipulation.
		"""
		k['f'] = 'Grid'
		trix.display(list(self.gen), *a, **k)
