#
# Copyright 2019 justworx
# This file is part of the trix project, distributed under 
# the terms of the GNU Affero General Public License.
#

from .propiter import *


class propset(propiter):
	"""
	Superclass for iterable subclasses.
	
	The propset class is superclass to propseq, defined below. Because
	sets and tuples are immutable, this is the class that should be
	their wrapper. Other sequence types should be contained in  
	
	NOTE: The `propset` class is experimental.
	      
	      I think maybe this class isn't needed. These functions
	      probably belong in propseq, and will move there if/when I 
	      discover there's no use for an iterator without a sequence.
	      
	      First I want to make sure it can't useful to pass an iterator
	      and let values be generated that way.
	"""
	
	def __iter__(self):
		"""Return an iterator this object's list."""
		return trix.ncreate('util.xiter', self.gen())
	
	#
	# CHECK THIS...
	#  - Should this be a property? Don't i usually make it a property?
	#    I can't remember... I need to check it so as to be consistent.
	#
	def gen(self):
		for x in self.o:
			yield(x)
	
	
	def __getitem__(self, key):
		return type(self)(self.o[key])
	
	
	@property
	def sorted(self):
		"""Return a proplist with sorted content."""
		return type(self)(sorted(self.o))
	
	@property
	def reversed(self):
		"""Return a proplist with reversed content."""
		return type(self)(type(self.o)(reversed(self.o)))


#
# PROP-SEQ
#  - NOTE: be sure to check whether xrange should be wrapped with
#          propseq, propset, or propiter.
#
class propseq(propset):
	"""
	Use this class to wrap objects that implement str, unicode, list, 
	tuple, bytearray, or buffer.
	
	NOTE: I'm not sure, but I think xrange would belong in propiter...
	      Whether iterators can be used that way, i'm not sure.
	"""
	
	def __setitem__(self, key, v):
		self.o[key] = v
	
	
	
	#
	# DB-GRID
	#  - this will be moved to an intermediate class between 
	#    propx and proplist
	#
	def dbgrid(self, tableName, **k):
		"""
		Return a dbgrid() object with this list's data stored as
		`tableName`. (Additional name/values may be passed by kwarg.)
		"""
		g = trix.ncreate('data.dbgrid.DBGrid', **k)
		g.add(tableName, self.o)
		return g
	
	
	#
	# EACH / SELECT
	#  - Use/selection of `self.o` data
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
		Argument `fn` is a callable that selects/alters items one at
		a time. This object's data
		
		Returns the resulting list.
		
		```
		from trix.propx import *
		pl = proplist([1,2,3])
		pl.select(lambda o: o*9) 
		```
		"""
		r = []
		for v in self.o:
			r.append(fn(v, *a, **k))
		return r

	
	
	def text(self, glue=None):
		"""
		Join list items into lines of text. Pass optional `glue` value, 
		the char(s) on which to join list items (Default: '').
		"""
		try:
			g = glue or ''
			return g.join(self.o)
		except TypeError:
			g = glue or b''
			return g.join(self.o)
