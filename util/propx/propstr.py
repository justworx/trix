#
# Copyright 2019-2020 justworx
# This file is part of the trix project, distributed under 
# the terms of the GNU Affero General Public License.
#


from .propseq import *


# -------------------------------------------------------------------
#
#
# PROP-STR - Wrapping strings
#
#
# -------------------------------------------------------------------

class propstr(propseq):
	"""
	Wrapping lots of cool features around text strings.
	"""
	
	@property
	def reader(self):
		a = self.a
		k = self.k
		return trix.ncreate("util.stream.reader.Reader", self.o, *a, **k)
	
	@property
	def lines(self):
		"""
		Return a proplist object containing a list of the lines
		of text contained by this propstr object.
		
		EXAMPLE
		>>> from trix.util.propx import *
		>>> px = propx("Hello, World! How are you?")
		>>> px.lines.output()
		
		"""
		return trix.ncreate(
				"util.propx.proplist.proplist", self.o.splitlines()
			)
	
	
	def scan(self, **k):
		"""
		Return a data/Scanner object loaded with text `self.o`.
		
		>>> from trix.util.propx import *
		>>> px = propx("[1,2,3] means 'one, two, three'")
		>>> px.scan().split()
		["'[1,2,3]', 'means', "'one, two, three'"]
		>>>
		
		"""
		try:
			return trix.ncreate('data.scan.Scanner', self.o, **k)
		except BaseException as ex:
			raise type(ex)("err-propstr-scan", xdata(
					data=self.o, k=k, python=str(ex)
				))
	
	
	#
	#
	# EXPERIMENTAL
	#  - Not sure how helpful this could be. Might remvoe it.
	#
	#
	def pdq(self, *a, **k):
		"""
		Wrap a python `data.Query` around this object's string.
		
		Returns the Query object.
		
		The pdq Query object is a bit outdated, but it can still be
		useful for exploring data, particularly value-separated text
		like csv or tab-separated values. It could be helpful in
		designing `trix.data.cursor.Cursor` callbacks.
		
		SEE ALSO:
		>>> from trix.data.pdq import *
		>>> help(Query)
		
		"""
		return trix.ncreate('data.pdq.Query', self.o, **k)
	
	
		
	#
	# needs a regex method
	#
	






