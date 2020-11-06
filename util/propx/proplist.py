#
# Copyright 2019-2020 justworx
# This file is part of the trix project, distributed under 
# the terms of the GNU Affero General Public License.
#


from .propseq import *


# -------------------------------------------------------------------
#
#
# PROP-LIST - Wrapping lists.
#
#
# -------------------------------------------------------------------

class proplist(propseq):
	"""
	Wrap objects in a proplist to provide a variety of useful features
	for manipulation and display.
	"""
	
	#
	#
	#  JOIN
	#
	#
	def join(self, glue=DEF_NEWL, **k):
		"""Join lines of text."""
		x = []
		try:
			for line in self.o:
				x.append(str(line, **k))
		except:
			for line in self.o:
				x.append(str(line))
				
		return glue.join(x)
	
	
	#
	#
	#  TEXT
	#
	#
	def text(self):
		"""Use to join those lines of text."""
		return self.join(encoding=DEF_ENCODE)
	
	
	#
	#
	#  UNIQUE
	#
	#
	def unique(self):
		"""Return a proplist containing the unique set of items."""
		return proplist(list(set(self.o)))
	
	
	#
	#
	#  EXTEND
	#
	#
	def extend(self, additems):
		"""
		Return a proplist containing this list extended by items from the
		list argument `additems`.
		"""
		L = []
		L.extend(self.o)
		L.extend(additems)
		return proplist(L)
	
	
	#
	#
	#  COMPARE
	#
	#
	def compare (self, other_list):
		"""
		Return a propdict object showing a comparison between the
		contents of this object and `other_list`. The dict results are
		interpreted as follows:
		
		 * '+' : objects contained by self.o that are NOT found in other
		 * '=' : objects contained by self.o and other
		 * '-' : objects contained by other, but not self.o 
		
		EXAMPLE
		#
		# Compare list [1,2,3] against list [2,3,4]
		#
		>>> from trix.util.propx import *
		>>> propx([1,2,3]).compare([2,3,4]).o
		{'-': [4], '+': [1], '=': [2, 3]}
		>>>
		
		In the example, above, the original list [1,2,3] was compared
		to comparison list [2,3,4].
		
		Key values show results as follows:
		 * The minus sign (-) shows items not found in the original list,
		   but found in the comparison list.
		 * The plus sign (+) shows items found in the original list but 
		   not in the comparison list.
		 * The equal sign (=) shows items found in both lists.
		
		The results of comparison are:
		 - 4 was missing from the original list, [1,2,3]
		 + 1 was found in the original list [1,2,3] but not in the 
		   comparison list.
		 = 2 and 3 were found in both lists
		
		"""
		d = {'-':[], '+':[], "=":[]}
		for o in self.o:
			if o in other_list:
				d["="].append(o)   # items in both lists
			else:
				d["+"].append(o)   # items in self.o but not other_list
		
		for x in other_list:
			if not x in self.o:
				d['-'].append(x)
		
		return trix.propx(d)
	
	
	#
	#
	#  MERGE
	#
	#
	def merge(self, additems):
		"""
		Return a proplist containing a unique set of items from this list
		and the given `additems` list. 
		
		It is exactly: `return self.extend(additems).unique()`
		
		EXAMPLE:
		>>> px = propx([1,2,3]).merge([3,4,5])
		[1, 2, 3, 4, 5]
		>>>
		
		"""
		return propx(self.extend(additems)).unique()
	
	
	#
	#
	#  PROPGRID
	#
	#
	@property
	def propgrid(self, *a, **k):
		"""
		Use only with lists that contain a set of lists of equal length.
		"""
		return propgrid(self.o, *a, **k)
	
	
	#
	#
	# DB-GRID
	#
	#
	def dbgrid(self, *a, **k):
		"""
		Returns a `propgrid.dbgrid.DBGrid` object. 
		
		This method is an alias to `propgrid.dbgrid`. It prevents 
		stumbles, and helps keep typing in the python interpreter 
		to a single line.
		
		SEE ALSO:
		Documentation of the dbgrid method can be found in the 
		`propgrid.dbgrid` method, below.
		
		"""
		return self.propgrid.dbgrid(*a, **k)



# -------------------------------------------------------------------
#
#
# PROP GRID
#
#
# -------------------------------------------------------------------

class propgrid(proplist):
	"""
	The `propgrid` class separates a header row from the data rows
	that follow. It's intended for data that consists of a list of
	equal-length lists, such as is generated by data.dbgrid.
	
	NOTE: data.dbgrid always prepends the header row to query results.
	      The 'header' kwarg `self.h` is accepted in case we need to 
	      pass a grid (list of lists) that's not prepended with column 
	      titles.
	
	"""
	
	#
	#
	# CALL
	#
	#
	def __call__(self, *a, **k):
		"""
		This __call__ method is overridden to separate the header from
		the data portion of this grid.
		
		Pass a list of lists (grid) and, optionally, a header keyword 
		argument to indicate whether or from whence the heading is 
		taken.
		
		 * Pass keyword argument header=[list of headings] if you have a
		   list of headings to pass.
		 * Pass keyword argument header=True if you want to take the list
		   of headings from the first row of the grid.
		 * Pass header=False if there is no header, and the grid will be
		   displayed with no headings. NOTE: If you pass header=False and
		   the first list in the grid actually consists of headings, that
		   heading list will be treated as the first row of data.
		
		EXAMPLE
		>>> import trix
		>>>
		>>> # pass a plain grid with no headings
		>>> trix.propx([[1,2],[3,4]])
		<trix/propgrid list len=2> # <--------- THE LIST LENGTH IS 2
		>>>
		>>> # headings plus one row of data (three and four)
		>>> trix.propx([["three","four"],[3,4]], h=True)
		<trix/propgrid list len=1> # <--------- THE LIST LENGTH IS 1
		>>>
		>>> # no headings, just a grid with no headings
		>>> trix.propx([[1,2],[3,4]], h=False)
		<trix/propgrid list len=2> # <--------- THE LIST LENGTH IS 2
		>>>
		>>> # 
		>>> trix.propx([[1,2],[3,4]], h="left right".split())
		<trix/propgrid list len=2> # <--------- THE LIST LENGTH IS 2
		>>> 
		
		In the example above, only when h=True was passed did the
		length of the grid change, the first row being taken away
		by the call to header=True.
		
		
		NOTES:
		 * The "h" keyword argument is an alias for the "header"
		   keyword argument.
		 * You can pass 1 or 0 in lieu of True or False. Eg, h=1
		
		
		TECHNICAL NOTE:
		When the class is propgrid, all calls to .o are returned from 
		propgrid.o, and all calls to __call__ are returned from here 
		(even when its superclasses (or even subclasses) are making the
		call) so it's OK to have a different self.__o.
		
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
			#  - split the grid header from grid data (if necessary).
			#
			k = self.k
			header = k.get('h', k.get('header')) or False
			
			if header == False:
				self.__o = grid
				self.__h = []
				self.__hh = False
			
			elif header == True:
				self.__o = grid[1:]
				self.__h = grid[0]
				self.__hh = True
				
			elif header:
				# header must be a list
				self.__o = grid
				self.__h = header or []
				self.__hh = bool(self.__h)
			return self.__o
	
	
	#
	#
	# O PROPERTY
	#
	#
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
	
	
	#
	#
	# H PROPERTY
	#
	#
	@property
	def h(self):
		"""
		Short alias. Returns the value of the header row.
		"""
		try:
			return self.__h
		except:
			self.o
			return self.__h
	
	
	#
	#
	# HEADER PROPERTY (SAME AS H)
	#
	#
	@property
	def header(self):
		"""Return the value of the header row."""
		return self.h
	
	
	#
	#
	# HH PROPERTY
	#
	#
	@property
	def hh(self):
		"""
		Short alias for `self.has_header` - True if a header row exists.
		"""
		try:
			return self.__hh
		except:
			self.__hh = bool(self.h)
			return self.__hh
	
	
	#
	#
	# HAS HEADER PROPERTY - SAME AS HH
	#
	#
	@property
	def has_header(self):
		"""
		Indicates True or False - whether this grid has a header row.
		"""
		return self.hh
	
	
	#
	#
	# GEN PROPERTY
	#
	#
	@property
	def gen(self):
		"""
		Generates the header row (if it exists), then appends all data 
		rows.
		"""
		
		try:
			yield(self.__h)
		except AttributeError:
			#
			# Calling self.o will generate the table if it has not already
			# been created.
			#
			self.o
			if self.__h:
				yield(self.__h)
		
		for r in self.o:
			yield(r)
	
	
	#
	#
	# GRID
	#
	#
	def grid(self, *a, **k):
		"""
		Display this data formatted as a grid.
		
		Overrides `proplist.grid` to expose the header, which propgrid
		separates from the data for easier data-manipulation.
		
		"""
		
		k['f'] = 'Grid'
		trix.display(list(self.gen), *a, **k)
	
	
	#
	#
	# DB-GRID
	#
	#
	def dbgrid(self, tableName=None, **k):
		"""
		Returns a `DBGrid` object containing this object's data in an 
		sqlite3 table.
		
		
		NOTE: 
		Database Tables are Always Grids!
		
		This method will fail if `self.o` (or any suplimentary tables
		defined by the passage of keyword arguments) is not a list of 
		lists each containing an equal number of items.
		
		
		EXAMPLE 1
		>>> import trix
		>>> d = trix.npath()
		>>> dg = d.list.dbgrid()
		>>> dg("select * from dbgrid").grid()
		
		EXAMPLE 2
		>>> import trix
		>>> lg = trix.propx([[1,2],[3,4]])
		>>> lg.dbgrid(columns=["left","right"])
		>>> lg.grid()
		
		
		"""
		t = k.get('t') or k.get('table') or tableName or "dbgrid"
		c = k.get('c') or k.get('columns') or self.h or None
		g = trix.ncreate('data.dbgrid.DBGrid')
		#g = trix.ncreate('data.dbgrid.DBGrid', **k)
		
		self.debug   = propx(dict(
			k          = k,
			table      = t,
			columns    = c,
			header     = self.h
		))
		
		"""
		DEBUGGING
		print ("table      = " + str(t)) 
		print ("columns    = " + str(c)) 
		print ("k.get('c') = " + str(k.get('c')))
		print ("k.get('c') = " + str(k.get('c')))
		print ("self.h     = " + str(self.h))
		print ("t          = " + str(t))
		print ("c          = " + str(c))
		print ("o          = " + str(self.o))
		"""
		
		g.add(t, self.o, c)
		
		return g


"""
		
		EXAMPLE
		>>> from trix.data.dbgrid import *
		>>> dg = DBGrid()
		>>> dg.add('LS', [[1,2],[3,4]], columns=['left','right'])
		>>> dg.x('select * from LS').grid()

"""
