#
# Copyright 2020 justworx
# This file is part of the trix project, distributed under
# the terms of the GNU Affero General Public License.
#


from trix.util.xiter import *
import os, fnmatch


# -------------------------------------------------------------------
#
#
# SEARCH
#
#
# -------------------------------------------------------------------


DEF_SEARCH_PATH = "~/"


class Search(xiter):
	"""
	A file search class.
	
	When an fnmatch pattern is passed via the pattern keyword argument,
	a complete search of the selected directory gathers all matching 
	file paths. The `Search.matches` property returns a proplist that
	contains the results. Call it as a function to retrieve the result
	as a python list, or use the `matches.display()` propx method to 
	view the results.
	
	EXAMPLE 1
	#
	# Perform a pattern matching search
	#
	>>> from trix import *
	>>> s = trix.npath('fs').search(pattern="*.pyc")
	>>> s.matches.display()
	[
	  "/home/me/trix/fs/__pycache__/search.cpython-36.pyc",
	  "/home/me/trix/fs/__pycache__/dir.cpython-36.pyc",
	  "/home/me/trix/fs/__pycache__/__init__.cpython-36.pyc"
	]
	>>> 
	
	
	ALTERNATELY:
	The Search object can be used to walk directories one at a time.
	Use the `Search.next()` method to proceed through each of the 
	`os.walk` results.
	
	Note that this alternate method can not be used when a pattern is
	given. To walk the directory manually, pass only the path to the 
	directory.
	
	
	EXAMPLE 2
	#
	# Walk the directory one step at a time.
	#
	>>> from trix.fs.search import *
	>>> s = Search("trix/fs")
	>>> s.next()
	>>> s.dict.display()
	{
	  "dir": "trix/fs",
	  "dirs": [
	    "__pycache__"
	  ],
	  "files": [
	    "__init__.py",
	    "archive.py",
	    "bzip.py",
	    "dir.py",
	    "file.py",
	    "gzip.py",
	    "search.py",
	    "strings.json",
	    "tar.py",
	    "zip.py"
	  ]
	}
	>>>
	
	"""				
	
	
	#
	#
	# INIT
	#
	#
	def __init__(self, path=None, **k):
		"""
		Search for files.
		
		The `Search` class uses `os.walk` to find files based on fnmatch
		patterns. Walk the list one by one, or pass a pattern keyword
		argument and call `search()` to receive a list of file paths that
		match the given pattern.
		
		Valid keyword arguments:
		 * pattern: Pass an fnmatch pattern string indicating files to
		            select.
		 * ignore : Pass an fnmatch pattern string indicating files to
		            ignore.
		
		Keyword argument aliases:
		 * p      : An alias for pattern.
		 * pi     : An alias for ignore.
		 
		 I use the full names, "pattern" and "ignore", when writing 
		 serious code, but these aliases are useful when working in the 
		 cramped space of the interpreter. 
		
		EXAMPLE:
		>>> trix.npath().search(p="*.conf").display()
		[
		  "/home/nine/trix/app/config/app.conf",
		  "/home/nine/trix/app/config/console.conf",
		  "/home/nine/trix/app/config/example.conf",
		  "/home/nine/trix/app/config/service/en.service.conf"
		]
		>>>		
		
		"""
		
		self.__k = k
		
		# Set the `path` as given, or use `DEF_SEARCH_PATH`.
		if not path:
			path = trix.path(DEF_SEARCH_PATH).path
		
		#
		# Initialize the `xiter` base class object.
		#
		xiter.__init__(self, os.walk(path))
		
		self.__path = path
		self.__item = ()
		self.__count= 0
		self.__dir = trix.path(path) # returns an fs.Dir!
		
		
		#
		#  - Finding things to ignore should lead to simply
		#    calling next without storing the result.
		#
		ignore = k.get('ignore', k.get("pi", ''))
		
		#
		# Now create a (possibly empty) list of things which,
		# if they match, should be left out of the results.
		#
		if ignore:
			self.__ignore = ignore.split("|") or []
		else:
			self.__ignore = None
		
		
		#
		# GET THE PATTERN
		#
		self.__pattern = k.get('pattern', k.get('p', None))
		
		#
		# Don't make me specify a pattern if I only want to ignore 
		# certain patterns.
		#
		if self.__ignore and not self.__pattern:
			self.__pattern = "*"
		
		if self.__pattern:
			self.__matches = []
			self.__next__ = self.__next_pat
			self.__search()
		else:
			self.__next__ = self.__next 
	
	
	#
	#
	# GET	ITEM
	#
	#
	def __getitem__(self, key):
		"""
		Returns a wrapper for the search result matching `key`, an integer
		index into the results.
		
		EXAMPLE:
		>>> import trix
		>>> trix.npath().search(p="*.conf")[0].rx().parse().display()
		{
		  "A": "Alpha",
		  "B": "Bet"
		}
		>>> 
		
		"""
		return trix.path(self.__matches[key]).w(**self.__k)
	
	
	#
	#
	# __NEXT
	#
	#
	def __next(self):
		"""
		This is the ultimate iterator. It can not be replaced. It provides
		content for the various "next" methods.
		
		"""
		try:
			self.__item = xiter.__next__(self)
			self.__count += 1
			
		except BaseException as ex:
			raise type(ex)('err-search-fail', xdata(
				path=self.__path, item=self.__item, k=self.__k
			))
	
	
	#
	#
	# __NEXT_PAT
	#
	#
	def __next_pat(self):
		"""
		Filter by pattern. 
		
		Matches are returned as full filepaths.
		
		EXAMPLE
		>>> from trix.fs.search import *
		>>> s = Search("trix/fs", pattern="*.py")
		>>> s.matches.o
		['trix/fs/__init__.py', 'trix/fs/bzip.py', 'trix/fs/tar.py', 
		 'trix/fs/file.py', 'trix/fs/gzip.py', 'trix/fs/search.py', 
		 'trix/fs/dir.py', 'trix/fs/archive.py', 'trix/fs/zip.py']
		>>> 
	
		"""
		#
		# Calling `next` is going to give the full dict.
		#
		self.__next()
		
		#
		# Filter the files, then add them to `self.__matches`.
		#
		files   = self.__item[2]
		pattern = self.__pattern
		ignore  = self.__ignore
		pathdir = self.__item[0]
		
		
		#
		# GET ALL FILE RESULTS FOR THIS DIRECTORY
		#
		results = fnmatch.filter(files, pattern)
		
		
		#
		# THERE IS AN `IGNORE` list.
		#  - Skip results that match any of its patterns. 
		#
		if ignore:
			#
			# LOOP THROUGH RESULTS
			#  - Discard any matches in `self.__ignore`.
			#  - Matches are given as a full file path.
			#
			for r in results:
				#
				# Skip results that are in the `ignore` list.
				#
				if self.__do_ignore(r):
					pass
				
				# Otherwise, add it to `matches`.
				else:
					self.__matches.append("%s/%s" % (pathdir, r))
		
		#
		# THERE IS NO `IGNORE`.
		#  - Take all pattern-matching results.
		#
		else:
			#
			# Here, there's not `ignore` specified, so just add every
			# match to the `matches` list.
			#
			for r in results:
				# Matches are given as a full file path.
				self.__matches.append("%s/%s" % (pathdir, r))
	
	
	
	def __do_ignore (self, one_result):
		"""
		Return True if any `ignore` item matches the current file,
		passed as `one_result`.
		
		"""
		
		for ig in self.__ignore:
			#
			# Handle one item at a time. If the path contains an 
			# fnmatch to `ig`, return True to indicate it should
			# be ignored.
			#
			if fnmatch.fnmatch(one_result, ig):
				return True
		
		#
		# If we got this far, it means that the item does not 
		# match any ignore specification, so return False.
		#
		return False
	
	
	
	
	#
	#
	# __SEARCH
	#
	#
	def __search(self):
		"""
		Loop until StopIteration.
		
		All files matching `pattern` will be returned as file paths
		stored in the self.matches proplist.
		"""
		try:
			while True:
				self.next()			
		except StopIteration:
			return self.matches
	
	
	#
	#
	# NEXTS
	#
	#
	def nexts(self):
		"""
		Calls the current `self.__next__` (whether __next or __next_pat)
		and then returns self. This is to allow call-chaining. It's most
		useful for debugging.
		"""
		self.__next__()
		return self
	
	
	#
	#
	# MATCHES
	#
	#
	@property
	def matches(self):
		"""
		Returns proplist containing `k` matches.
		
		This list will be populated only if a pattern keyword argument
		was specified to the constructor.
		"""
		try:
			return trix.propx(self.__matches)
		except:
			return None
	
	
	#
	#
	# DISPLAY
	#
	#
	def display(self, **k):
		"""
		Display sorted pattern search results.
		"""
		trix.propx(self.__matches).sorted.display(**k)
	
	
	#
	#
	# K - Keyword Argument dict
	#
	#
	@property
	def k(self):
		"""Returns propdict containing `k`. Call as a method."""
		return trix.propx(self.__k)
	
	
	#
	#
	# PATH
	#
	#
	def path(self):
		"""
		Returns the path at the current point of iteration generated by
		the most recent call to `next`.
		"""
		return self.__dir[0]
	
	
	#
	#
	# BASEPATH
	#
	#
	def basepath(self):
		"""
		Returns the path given to the constructor.
		"""
		return self.__path
	
	
	#
	#
	# IGNORE
	#
	#
	def ignore(self):
		"""
		Returns the current set of ignored match strings.
		
		EXMAPLE:
		>>> 
		"""
		return self.__ignore
	
	
	#
	#
	# PATTERN
	#
	#
	def pattern(self):
		"""
		Returns the current search pattern.
		"""
		return self.__pattern
	
	
	
	# -----------------------------------------------------------------
	#
	#
	# CURRENT ITEM RESULTS
	#  - This is mostly for cases when one might wish to walk through 
	#    the results one at a time, examining each step of the process.
	#    These methods could be very useful for debugging, or for when
	#    looking at ways to expand the feature set.
	#
	#
	# -----------------------------------------------------------------
	
	#
	#
	# DICT
	#
	#
	@property
	def dict(self):
		"""
		Returns a dict of the current item's contents, wrapped in a propx.
		"""
		itm = self.__item
		return trix.propx({
			"dir": itm[0],
			"dirs": sorted(itm[1]),
			"files": sorted(itm[2])
		})
	
	
	#
	#
	# ITEM
	#
	#
	@property
	def item(self):
		"""
		Returns current item, wrapped in a propx.
		"""
		return trix.propx(self.__item)
	
	
	#
	#
	# DIR
	#
	#
	@property
	def dir(self):
		"""
		Returns the base directory, wrapped in a propx.
		"""
		return trix.propx(self.__item[0])
	
	
	#
	#
	# DIRS
	#
	#
	@property
	def dirs(self):
		"""
		Returns the current items directories, wrapped in a propx.
		"""
		return trix.propx(self.__item[1])
	
	
	#
	#
	# FILES
	#
	#
	@property
	def files(self):
		"""
		Returns the current items files, wrapped in a propx.
		"""
		return trix.propx(self.__item[2])


