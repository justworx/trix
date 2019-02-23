#
# Copyright 2018 justworx
# This file is part of the trix project, distributed under the terms 
# of the GNU Affero General Public License.
#


from ..util.enchelp import *


class Chain(object):
	"""Holds a value; provides methods to manipulate that value."""
	
	def __init__(self, v=None):
		self.v = v
	
	def __call__(self, *a):
		"""Return a new Chain (or subclass) with given arguments."""
		return type(self)(*a)
	
	def __getitem__(self, key):
		"""Return item `key` from `self.v`."""
		return self.v[key]
	
	def __setitem__(self, key, v):
		"""Set item `key` in `self.v`."""
		self.v[key] = v
	
	def each(self, fn, *a, **k):
		"""
		Pass a callable that accepts Param object `p`, index (or key) `i`,
		and the value of p[i], `v`.
		"""
		for x in enumerate(self.v):
			fn(self, x[0], x[1], *a, **k)
		return self
	
	def proc(self, fn, *a, **k):
		"""
		Set this object's self.v to the result of the callable argument
		`fn`. All args and kwargs are passed on to the callable. Use this 
		when you want to set self.v to the callable's result.
		"""
		self.v = fn(*a, **k)
		return self
	
	def procx(self, x, fn, *a, **k):
		"""
		Set item `x` in `self.v` to the result
		"""
		self.v[x] = fn(x, *a, **k)
		return self
	
	def call(self, fn, *a, **k):
		"""
		Same as `proc`, but does not set self.v; Use this (rather than
		`proc`) when the `fn` callable does not return a value but rather
		operates on parameters "in-place".
		"""
		fn(*a, **k)
		return self
	
	def split(self, *a, **k):
		"""
		Split `self.v` by the string given as the first argument, or by
		the default, if no arguments are given. Keyword args are applied
		to the `str.split()` method.
		"""
		self.v = self.v.split(*a, **k)
		return self
	
	def join(self, c=' ', *a):
		"""
		Join list items by character `c`. If no additional arguments are
		given, all items in list `self.v` are joined. If additional args
		are given, they must be integers that give offsets from self.v to 
		join.
		
		NOTE: All list values are cast as unicode before being joined.
		"""
		x = self.v
		u = unicode
		vv =  [u(x[i]) for i in a] if a else [u(v) for v in x]
		self.v = u(c).join(vv)
		return self
	
	def pad(self, mlen, val=''):
		"""
		Pad a sequence with `val` items to a minimum length of `mlen`.
		This method allows the expansion of string values to a minimum
		length (eg., for visual formatting of grids in a terminal).
		""" 
		val = val if len(str(val)) else ' '
		while len(self.v) < mlen:
			self.v.append(val)
		return self

	def strip(self, c=None, alignment=0):
		"""
		Strip characters matching `c`, or whitespace, if c==None.
		If `alignment` < 0, only left-stripping is done using `lstrip()`. 
		If it's > 0, `rstrip()` is used. Default is 0, `strip()`
		"""
		if alignment < 0:
			self.v = self.v.lstrip(c)
		elif alignment > 0:
			self.v = self.v.rstrip(c)
		else:
			self.v = self.v.strip(c)
		return self
	
	def set(self, v):
		"""Set `self.v` directly."""
		self.v = v
		return self
	
	def setx(self, x, v):
		"""Set index (or key) `x` with value `v`."""
		self.v[x] = v
		return self
	
	
	# util
	def output(self, v=None, *a):
		"""Print `self.v`; for testing."""
		print(v if v else self.v, *a)
		return self
	
	@property
	def null(self):
		"""
		Tack this method to the end of a chain of calls to return None.
		Eg., Param(["Hello", "World"]).output().null
		"""
		return None



#
# PARAM
#
class Param(Chain):
	"""
	Param methods manipulate or evaluate data; usually the self.v value
	is involved. All methods work with either self.v, or in some cases,
	an optional second argument to use instead of self.v.
	
	Comparison methods eq, neq, gt, ge, lt, and le all require one
	argument and accept an optional second argument (which defaults to
	self.v).
	
	Methods inherrited from Chain always return `self`, so that calls 
	can be chained through a lambda, whereas Param methods typically, 
	if not always, return value resulting from the method. It may take
	a while to what you're getting back as you chain calls together, 
	but once you get it, it's a powerful tool for use in lambdas.
	"""
	def __init__(self, v=None, i=None):
		self.v = v
		self.i = i
	
	def __call__(self, *a):
		"""Return a new Param object with given arguments."""
		if len(a) < 1:
			return type(self)(self.v, self.i)
		elif len(a) < 2:
			return type(self)(a[0], self.i)
		else:
			return type(self)(*a)
	
	def __getitem__(self, key):
		return self.v[key]
	
	def __len__(self):
		return len(self.v)
	
	
	# PARAM INFO
	@property
	def iv(self):
		"""Return (index,value)"""
		return (self.i, self.v)
	
	@property
	def vi(self):
		"""Return (value,index)"""
		return (self.v, self.i)
	
	
	# VALUE INFO
	@property
	def type(self):
		"""Return the type of the current value."""
		return type(self.v)
	
	@property
	def len(self):
		"""Return the length of the current value."""
		return len(self.v)
	
	
	# reg-ex module access
	@property
	def re(self):
		"""Return the regular expression module `re`."""
		try:
			return self.__re
		except:
			self.__re = __import__('re')
			return self.__re
	
	
	# EVALUATION
	@property
	def true(self):
		return True
	
	@property
	def false(self):
		return False
	
	# BOOL
	def bool(self, v):
		return v
	
	# SKIP
	def skip(self, *a):
		"""
		Skip this item if the first given argument is True.
		
		Use this method at the end of a lambda to return True or False 
		based on the given argument's boolean evaluation.
		"""
		return len(a) and bool(a[0])
	
	
	#
	# COMPARISON
	#
	def eq(self, v):
		"""Comparison: `v` equal to self.v"""
		return self.v == v
	
	def neq(self, v):
		"""Comparison: not equal to;"""
		return self.v != v
	
	def ge(self, v):
		"""Comparison: greater than/equal to;"""
		return self.v >= v 
	
	def le(self, v):
		"""Comparison: less than/equal to;"""
		return self.v <= v 
	
	def gt(self, v):
		"""Comparison: greater than;"""
		return self.v > v
	
	def lt(self, v):
		"""Comparison: less than;"""
		return self.v < v

	# CONTAINS
	def contains(self, v, b=True):
		"""Return `b` (default True) if `v` exists in `self.v`."""
		return b if v in self.v else not b
	