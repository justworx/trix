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
	
	
	def update (self, fn, *a, **k):
		"""
		Create an updated copy of `self.o` one item at a time and then
		replace `self.o` with the result. 
		
		Returns `self`.
		
		```
		from trix.propx import *
		pl = proplist(trix.path('trix').grid.)
		pl.select(lambda o: o*9) 
		```
		"""
		self.o = self.select(fn, *a, **k)
		return self
	
	
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





# -------------------------------------------------------------------
#
#
# PROP-GRID 
#  - I'm really starting to regret that whole "header" thing, below.
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
		# ~ Override default `self.o` to reflect value custom to this class.
		try:
			return self.__o
		except:
			self.__call__(*self.a, **self.k)
			return self.__o
	
	@property
	def h(self):
		try:
			return self.__h
		except:
			self.o
			return self.__h
	
	@property
	def header(self):
		return self.h
	
	@property
	def hh(self):
		try:
			return self.__hh
		except:
			self.o
			return self.__hh
	
	@property
	def has_header(self):
		return self.hh
	
	
			
	@property
	def gen(self):
		#
		# Generates the header row and all data rows.
		#
		
		try:
			yield(self.__h)
		except AttributeError:
			#self.__call__()
			self.o
			yield(self.__h)
		
		for r in self.o:
			yield(r)
	
	
	
	def grid(self, *a, **k):
		#
		# Display this data formatted as a grid.
		#
		# Overrides `proplist.grid` to expose the header, which propgrid
		# separates from the data for easier data-manipulation.
		#
		
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



"""
class propgrid(proplist):
	# ~ 
	# ~ The `propgrid` class separates a header row from the data rows
	# ~ that follow. It's intended for data that consists of a list of
	# ~ equal-length lists, such as is generated by data.dbgrid.
	
	# ~ NOTE: data.dbgrid always prepends the header row to query results.
	      # ~ The 'header' kwarg is accepted in case we need to pass a grid
	      # ~ (list of lists) that's not prepended with column titles.
	# ~ 
	
	@property
	def has_header(self):
		# ~ 
		# ~ Return True if a header row was given to the constructor by
		# ~ keyword argument, else False.
		# ~ 
		try:
			return self.__hh
		except:
			self.__hh = bool(self.k.get('header'))
			return self.__hh
	
	@property
	def o(self):
		# ~ 
		# ~ Return this property's actual object value, as originally
		# ~ calculated by `self.__call__()`.
		# ~ 
		try:
			return self.__o
		except:
			o = self.__call__(*self.a, **self.k)
			self.__oupdate(o)
	
	@o.setter
	def o(self, grid):
		# ~ 
		# ~ Set the value of `self.o`. Given `grid` must be a list of lists
		# ~ of equal length, with header row prepended.
		# ~ 
		self.__hh = False
		self.__oupdate(grid)
	
	
	def __oupdate(self, grid):
		self.__o = grid
		if self.has_header:
			self.__o = grid
			self.__h = self.k.get('header')
		else:
			self.__h = grid[0]
			self.__o = grid[1:]
			return self.__o
		
	
	@property
	def header(self):
		# ~ 
		# ~ Return a proplist containing grid header (column names).
		# ~ Call as a function to return the header list.
		
		# ~ ```
		# ~ self.header()
		# ~ self.update(lambda x: str(x).upper())
		
		# ~ ```
		# ~ 
		try:
			return proplist(self.__h)  # return that header
		except:
			# after self.o is called, self.header (self.__h) exists.
			self.o
			return proplist(self.__h)
	
	@property
	def gen(self):
		#
		# Generates the header row and all data rows.
		#
		yield(self.header)
		for r in self.o:
			yield(r)
	
	
	def grid(self, *a, **k):
		# ~ 
		# ~ Display as Grid.
		
		# ~ Overrides `proplist.grid` to expose the header, which propgrid
		# ~ separates from the data for easier data-manipulation.
		# ~ 
		k['f'] = 'Grid'
		trix.display(list(self.gen), *a, **k)
"""
