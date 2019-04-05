#
# Copyright 2019 justworx
# This file is part of the trix project, distributed under 
# the terms of the GNU Affero General Public License.
#

from .. import *

class propbase(object):
	"""
	Wraps objects with a set of methods convenitent for manipulation,
	query, display, and compression.
	"""
	
	#
	# INIT
	#
	# There are two ways to create any propbase object:
	#  * Pass value or callback `o`, plus args/kwargs needed for 
	#    callback.
	#  * Pass an instance of the object the callback would have created.
	#
	#  The reason both these methods are need is that sometimes it's
	#  more convenient to return a propbase subclass using a property.
	#  This allows the property to act like a method, returning the
	#  "normal" expected value, while still allowing the property to
	#  be called as a property to give access to the extra methods 
	#  propbase (and subclasses) provide. Eg., see `fs.Dir.list`.
	#
	#  ```
	#  trix.path().list()
	#  trix.path().list.table(width=3)
	#  ```
	#
	def __init__(self, o=None, *a, **k):
		"""
		Pass object `o`, a value or callable that returns a value.
		
		In the case `o` is a callable, pass also any args/kwargs required
		to execute that callable. When `self.o` is first accessed, the
		value will be calculated and stored as self.o (even if it's the
		first calling of property `self.o`).
		"""
		self.__p = o
		self.__a = a
		self.__k = k
	
	
	
	def __repr__(self):
		return "<trix/%s %s>" % (self.T.__name__, self.To.__name__) 
	
	
	
	def __call__(self, *a, **k):
		"""
		On first call, sets the value for the `self.o` property. On
		subsequent calls, returns that value.
		
		The value of `self.o` is, on the first call to this method,
		undefined. If this object has been constructed given a callable
		as the first argument, it will be calculated here (given any
		additional constructor args/kwargs) and stored as a private
		member variable self.__o.
		
		On all calls, self.__o is returned.
		
		REMEMBER:
		The __call__ method *MUST NOT* be overridden by subclasses except
		to make necessary subclass-specific manipulations or additions
		before calling the superclass `__call__` method.
		"""
		try:
			return self.__o
		except:
			try:
				# if self.__p is callable...
				self.__o = self.__p(*a, **k)
			except TypeError:
				# or, self.__p must be an object/value
				self.__o = self.__p
			
			return self.__o
	
	
	@property
	def o(self):
		"""
		Return this property's actual object value, as originally
		calculated by `self.__call__()`.
		"""
		try:
			return self.__o
		except:
			# __call__ sets self.__o
			return self.__call__(*self.__a, **self.__k)
			#self.__o = self.__call__(*self.__a, **self.__k)
			#return self.__o
	
	@property
	def a(self):
		"""Returns arguments given to constructor."""
		return self.__a
	
	@property
	def k(self):
		"""Returns keyword args given to constructor."""
		return self.__k
	
	@property
	def T(self):
		return type(self)
	
	@property
	def To(self):
		return type(self.o)
	
	#
	# UTILITY
	#
	@property
	def compenc(self):
		"""
		Returns the compenc module on demand; Does not load the module 
		until first call to this property.
		"""
		try:
			return self.__compenc
		except:
			self.__compenc = trix.nmodule("util.compenc")
			return self.__compenc
	
	@property
	def jparse(self, **k):
		"""
		Return propx containing object parsed from json text. May be a
		proplist, propdict, propstr, etc...
		"""
		try:
			return propx(trix.jparse(str(self.o), **k))
		except Exception as ex:
			raise type(ex)(xdata(o=self.o, k=k))
	
	
	# ---- Methods that can handle pretty much any data type -----
	
	#
	# DISPLAY
	#
	def display(self, *a, **k):
		"""Display using trix.fmt. Default params: f='JDisplay'"""
		trix.display(self.o, *a, **k)
	
	
	#
	# FORMATTING
	#
	def json(self, *a, **k):
		"""
		Return self.o as json text. Default format is compact json. 
		Note: Use the `display()` method for JSON in display format. 
		"""
		k.setdefault('f', 'JCompact')
		return trix.formatter(*a, **k).format(self.o)
	
	
	#
	# DATA MANIPULATION
	# 
	def param(self, o=None):
		"""Returns arg `o` or `self.o` wrapped in a Param object."""
		try:
			return self.__Param(o or self.o)
		except:
			self.__Param = trix.nvalue("data.param", "Param")
			return self.__Param(o or self.o)
	
	# CURSOR
	def cursor(self, **k):
		"""
		Return a cursor containing self.o; any given keyword arguments
		are passed to the cursor's constructor.
		"""
		return trix.ncreate("data.cursor.Cursor", self.o, **k)
	
	# PDQ
	def pdq(self, **k):
		"""
		Return a python data Query object given self.o and any kwargs.
		"""
		return trix.ncreate("data.pdq.Query", self.o, **k)
	
	
	#
	# ENCODING , COMPRESSION
	#
	def b64(self, **k):
		"""Return self.o as (compact) JSON bytes encoded to base64."""
		return self.compenc.b64.encode(self.json(**k).encode(**k))
	
	def b64s(self, **k):
		"""Return self.o as (compact) JSON bytes encoded to base64."""
		return self.compenc.b64.sencode(self.json(**k).encode('utf8'))
	
	def b64u(self, **k):
		"""
		Return self.o as (compact) JSON bytes encoded to url-safe base64.
		"""
		return self.compenc.b64.uencode(self.json(**k).encode('utf8'))
	
	def b32(self, **k):
		"""Return self.o as (compact) JSON bytes encoded to base32."""
		return self.compenc.b32.encode(self.json(**k).encode(**k))
	
	def b16(self, **k):
		"""Return self.o as (compact) JSON bytes encoded to base16."""
		return self.compenc.b16.encode(self.json(**k).encode(**k))
	
	def compact(self, **k):
		"""
		Convert self.o to json, zlib-compress, and return base-64 bytes.
		Use trix.compenc.expand to revert to json.
		"""
		return self.compenc.compact(self.json(**k).encode('utf8'))
	
	@property
	def expand(self, **k):
		"""
		Return propx containing data "expanded" from data that had
		previously been compressed by `self.compact()`.
		"""
		return propx(self.compenc.expand(self.o))
	


#
#
# CONVENIENCE
#  - Easy access to subclasses defined in other modules within
#    this package.
#
#


def propx(o, *a, **k):
	"""Try to calculate and return the correct wrapper."""
	
	#
	# ORDER IS IMPORTANT HERE
	#  - Checking keys/values for dict must come first.
	#  - Checking setitem must come before checking __getitem__,
	#    followed by __iter__ and generator.
	#
	
	try:
		if o.values and o.keys:
			return trix.ncreate("propx.propdict.propdict", o, *a, **k)
	except:
		pass
		
	try:
		o.encode
		return trix.ncreate("propx.propstr.propstr", o, *a, **k)
	except:
		pass
	
	try:
		o.__setitem__
		return trix.ncreate("propx.proplist.proplist", o, *a, **k)
	except:
		pass
	
	try:
		o.__getitem__
		return trix.ncreate("propx.propseq.propseq", o, *a, **k)
	except:
		pass
	
	try:
		if o.__iter__ or (type(o).__name__ == 'generator'):
			return trix.ncreate("propx.propiter.propiter", iter(o),*a,**k)
	except:
		pass
	
	
	# anything else...
	return propbase(o, *a, **k)
	

