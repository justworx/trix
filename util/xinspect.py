#
# Copyright 2018 justworx
# This file is part of the trix project, distributed under
# the terms of the GNU Affero General Public License.
#

from .. import *
import inspect


class Inspect(object):
	"""
	Covers the python `inspect` module.
	
	NOTES
	I guess an important thing to remember here is that the object
	you pass to init determines the values that are available in
	Inspect results. If you pass a module, all its functions and
	classes and methods will be available; If you want only the 
	functions and methods of a specific object/class, you must pass,
	only that.
	
	python3
	>>> from trix.util.xinspect import *
	>>> from trix.util.lineq import *
	>>> ii = Inspect(LineQueue())
	>>> ii.methods.keys()
	>>> ii.properties.keys()
	"""
	
	#
	#
	# INIT	
	#
	#
	def __init__(self, o):
		"""Pass an object, module, class, etc..."""
		self.__o = o
		self.__d = {}
	
	
	#
	#
	# OBJECT	
	#
	#
	@property
	def object(self):
		"""Return the object passed to the constructor."""
		return self.__o
	
	
	#
	#
	# CLASSES	
	#
	#	
	@property
	def classes(self):
		"""Return a dict containing class information."""
		try:
			return self.__classes
		except:
			r = self.__classes = {}
			for cls in self.get(inspect.isclass):
				typeString = str(cls[0])
				classObj   = cls[1]
				modulePath = classObj.__module__
				className  = classObj.__name__
				fullPath   = "%s.%s" % (modulePath, className)
				
				r[className] = dict(
						typestring = typeString, 
						modulepath = modulePath, 
						modulename = className, 
						fullmodpath = fullPath, 
						classobject = classObj
					)
			return self.__classes
	
	
	#
	#
	# METHODS	
	#
	#		
	@property
	def methods(self):
		"""Return a dict containing method information."""
		try:
			return self.__methods
		except:
			r = self.__methods = {}
			try:
				methodName = None
				methodType = None
				m = None
				
				is_method = self.get(inspect.ismethod)
				
				
				for m in is_method:
					methodName = m[0]
					methodType = m[1]
					r[methodName] = methodType
				
				return self.__methods
			
			except BaseException as ex:
				raise type(ex)("err-xinspect-methods", xdata(ex=str(ex),
							m=m, methodName=methodName, methodType=methodType,
							methods_processed=r
					)
				)
	
	
	#
	#
	# PROPERTIES	
	#
	#	
	@property
	def properties(self):
		"""Return a dict containing properties."""
		try:
			return self.__properties
		except:
			r = self.__properties = {}
			for cls in self.get(inspect.isclass):
				lx = lambda o: isinstance(o,property)
				pp = inspect.getmembers(cls[1], lx)
				for item in pp:
					r[item[0]] = item[1]
			return self.__properties
	
	
	#
	#
	# FUNCTIONS	
	#
	#	
	@property
	def functions(self):
		"""Returns a dict containing the functions of self.object."""
		try:
			return self.__functions
		except:
			r = self.__functions = {}
			for f in self.get(inspect.isfunction):
				r[f[0]] = f[1]
			return self.__functions
	
	
	#
	#
	# GET	
	#
	#
	def get(self, predicate=None):
		"""
		Utility. Calls inspect.getmembers, passing self.object as the
		first argument. You must provide the predicate if you call this
		method directly.
		"""
		return inspect.getmembers(self.__o, predicate)


