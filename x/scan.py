#
# Copyright 2018 justworx
# This file is part of the trix project, distributed under
# the terms of the GNU Affero General Public License.
#

from ..data.udata.charinfo import *
from ..util.stream.buffer import *


class Scanner(object):
	"""Scan unicode text one character at a time."""
	
	Debug = False
	Escape = "\\"
	BufSize = 2048
	
	def __init__(self, iterable_text, **k):
		"""Pass anything iterable that produces unicode characters."""
		self.__escape = k.get('escape', self.Escape)
		self.__bufsz = k.get('bufsz', self.BufSize)
		self.__itext = iter(iterable_text)
		
		# flag set to True on StopIteration
		self.__eof = False
	
	#
	# CHARACTERS
	#
	@property
	def c(self):
		"""Return current character info object."""
		if self.eof:
			raise StopIteration()
		try:
			return self.__cinfo
		except AttributeError:
			return self.cc
	
	@property
	def cc(self):
		"""Move forward one and return the character info object."""
		try:
			return self.__cinfo.next()
		except AttributeError:
			self.__cinfo = charinfo(self.__itext)
			return self.__cinfo.next()
		except StopIteration:
			self.__eof = True
	
	@property
	def char(self):
		"""Return the current character."""
		return self.c.c
	
	@property
	def eof(self):
		"""False until end of text is reached."""
		return self.__eof
	
	
	#
	# CONFIG PROPERTIES
	#
	@property
	def bufsz(self):
		"""
		The size of a buffer used to scan text. The default is 2048, but
		scans will not fail if that is exceeded (though they may be a 
		bit slower). If you expect larger scan chunks, it may improve
		performance if you specify a larger buffer size integer via the
		bufsz keyword argument. (I haven't tested this - it may be just
		the same or worse.)
		"""
		return self.__bufsz
	
	@property
	def esc(self):
		"""The escape character. Default: '\' (backslash)."""
		return self.__escape
	
	
	
	
	#
	# BASE SCAN METHODS
	#  - These always start from self.c (the current character) and
	#    end one character AFTER the last-scanned character.
	#
	
	# COLLECT
	def collect(self, fn):
		"""
		Collect each character that matches the criteria of `fn`. The 
		pointer is left directly after the last matching character.
		
		>>> s = Scanner("Abc 123")
		>>> s.char                          # 'A'
		>>> s.collect(lambda ci: ci.alpha)  # 'Abc'
		>>> s.char                          # ' '
		>>> s.cc                            # '1'
		>>> s.collect(lambda ci: ci.numeric)# '123'
		
		"""
		if self.eof:
			raise StopIteration()
		
		b = Buffer(mode='r', max_size=self.__bufsz)
		w = b.writer()
		try:
			while fn(self.c):
				if self.c.c != self.__escape:
					w.write(self.c.c)
				else:
					w.write(self.cc.c) # it IS an escape char; get next char.
				self.cc
		except StopIteration:
			self.__eof = True
		
		# read/return the whole buffer
		return b.read()
	
	
	# IGNORE
	def ignore(self, fn):
		"""
		Pass all characters for which executable `fn` returns True. The
		iterator stops on the first character following ignored text.
		
		NOTE: If the current character doesn't match what `fn` is looking
		      for, the pointer is not moved.
		"""
		
		# Calling self.c will raise StopIteration if self.eof is set.
		a = fn(self.c)
		try:
			while a:
				a = fn(self.cc)
		except StopIteration:
			self.__eof = True
	
	
	
	
	
	#
	# CONVENIENCE METHODS
	#  - These all rely on the Base Methods above.
	#
	
	# --- ignoring characters ---
	
	# PASS LINE-ENDING
	def passend(self):
		"""Pass existing white space, then any endlines."""
		self.passwhite()
		self.ignore(lambda c: c.lineend)
	
	# PASS WHITE
	def passwhite(self):
		"""Pass any white space."""
		self.ignore(lambda ci: ci.space)
	
	
	# --- collecting characters ---
	
	# SCAN DIGITS
	def scandigits(self):
		"""Scan numeric digits."""
		return self.collect(lambda ci: ci.dig)
	
	# SCAN IDENTIFIER
	def scanid(self):
		"""
		Collect the next sequence of characters that match the rules for 
		an "identifier". The default rules are: a letter followed by any
		number of letters, digits, or underscores (cat=='Pc').
		"""
		self.passwhite()
		if not self.c.digit:
			return self.collect(lambda ci: ci.alphanum or ci.connector)
	
	# SCAN TO
	def scanto(self, char):
		"""Collect all text to the given character `c`."""
		return self.collect(lambda ci: ci.c != char)
	
	# SCAN TO C
	def scantoc(self):
		"""
		Store the current character, then collect all characters up to
		and including the next occurrence of the current character.
		
		>>> Scanner("abacab").scantoc() # "aba"
		"""
		c = self.c
		return self.collect(lambda ci: ci.cc != c)
	
	
	
	
	#
	# COMPLEX METHODS
	#  - These all rely on the Base Methods above.
	#
	
	# SCAN
	def scan(self):
		"""
		Pass white space then scan one item - either bidi/quote or a 
		single string that contains no space characters.
		"""
		self.passwhite()
		
		# Quoted strings will probably be more common than brackets,
		# so try that first.
		q = self.scanquote()
		if q:
			return q
		
		# Try bidi - this will capture full "quoted strings", dict,
		# list, or sets.
		b = self.scanbidi()
		if b:
			return b
		
		# This should capture individual space-separated elements.
		else:
			return self.collect(lambda ci: ci.cat != "Zs")
	
	
	# SPLIT
	def split(self):
		"""
		Split text on white characters, excpet those included in a bidi
		enclosure or quotes, where whitespace is included in the result.
		"""
		r = []
		try:
			v = True
			while v:
				self.passwhite()
				v = self.scan()
				if v:
					r.append(v)
		except StopIteration:
			self.__eof = True
		return r
	
	
	# SCAN BIDI
	def scanbidi(self):
		"""
		Scan recursively through bidi open/close characters, until the
		first bidi character is matched.
		"""
		DEBUG = False
		
		b = Buffer(mode='r', max_size=self.bufsz)
		w = b.writer()
		
		self.passwhite()
		
		if self.Debug:
			print ("FIRST: %s" % (self.c))
			print ("BREAK: %s" % (self.c.linebreak))
		
		try:
			
			dbg = []
			
			#
			# BRACKET/BRACE/ETC...
			#
			if self.c.bracket:
				
				if self.Debug:
					print ("BRACKET")
				
				# keep count of the number of unclosed brackets
				ct = 1
				
				# Get the first character (an open bracket) and write it to
				# the result buffer.
				br = self.char
				
				if self.Debug:
					dbg.append(br)
					print (" -- :", ''.join(dbg), ';', str(ct))
				
				# Store the ending (close bracket) in `end`
				end = self.c.bracket[1]
				
				if self.Debug:
					print ("BR/END:", br, '/', end)
				
				try:
					while (ct > 0):
						w.write(self.c.c)
						ci = self.cc
						
						if self.Debug:
							dbg.append(ci.c)
							print (" -- :", ''.join(dbg), ';', str(ct))
						
						if ci.c == br:
							ct += 1
						elif ci.c == end:
							ct -= 1
							if not ct > 0:
								w.write(self.c.c)
								self.cc
								return b.read()
				
				except StopIteration:
					self.__eof = True
					return b.read()
		
		except StopIteration:
			self.__eof = True
			return b.read()
	
	
	# SCAN QUOTE
	def scanquote(self):
		"""
		Scan recursively through bidi open/close characters, until the
		first bidi character is matched.
		"""
		
		b = Buffer(mode='r', max_size=self.bufsz)
		w = b.writer()
		
		self.passwhite()
		
		if self.Debug:
			print ("FIRST: %s" % (self.c))
			print ("BREAK: %s" % (self.c.linebreak))
		
		try:
			
			dbg = []
			
			if self.c.linebreak == "QU":
				if self.Debug:
					print ("QUOTE")
				
				q = self.c.c
				if self.Debug:
					print (" -  q:", q)
				
				w.write(q)
				self.cc # move one ahead
				cn = self.scanto(q)
				w.write(cn)
				cz = self.c.c
				
				if self.Debug:
					print (" - cz:", cz)
				
				# write the closing quote before chancing the self.cc!
				w.write(cz)
				
				# must end on the character following the closing quote!
				self.cc
				
				return b.read()
		
		except StopIteration:
			self.__eof = True
			return b.read()


	# ----------------------------------------------------------
	
	def splits(self, chars):
		"""
		Pass a string containing characters to split on, in the order
		they're to be used. Each char in `chars` is used only once, so
		for each place a particular split should be made, the same
		character must be repeated.
		
		REMEMBER! This is not `split()`! Characters in `chars` must be 
		repeated in order to cause a split on multiple instances of the 
		same character within the text.
		
		Pass "xy" to retrieve ["A","B"] from "AxByCz". Anything following
		the last split character ('y') is considered the "remainder", and
		may be retrieved by calling `self.remainder()`.
		
		```
		s = Scanner('aa_DJ.iso88591.json')
		s.splits("_..")
		s.remainder()
		```
		"""
		try:
			r = []
			for c in chars:
				r.append(self.scanto(c))
				self.cc
			return r
		except StopIteration:
			self.__eof = True
			return r
	
	def remainder(self):
		"""Return whatever's left of the scan text."""
		return self.collect(lambda c: True)
		



class RScan(Scanner):
	"""Reverse scanner. Scans text backward."""
	
	def __init__(self, forward_iterable,  **k):
		"""
		Pass text to split from the reversed direction.
		"""
		Scanner.__init__(self, reversed(forward_iterable))
	
	
	def rsplits(self, chars):
		"""
		Pass characters to split on. Each character results in one
		split for as long as the following character is found in the
		text. 
		
		NOTE! This is not `split()`! Characters in `chars` must be 
		repeated in order to cause a split on multiple instances of the 
		same character within the text. Passing '_' as chars when trying
		to split "a_b_c" will result in ['c'], with a remainder of "a_b".
		You must pass "_"*2 to get the result ['b','c'] with a remainder
		of "a".
		
		With `rsplits()`, as with `splits()`, split characters should be 
		given in the forward direction with the last of the splitting 
		chars being last in the list of `chars`. 
		
		```
		>>> s = RScan("Fi-fie-fo-fum! Hello_World.xyz")
		>>> s.rsplits(" _.")
		['Hello', 'World', 'xyz']
		
		```
		
		REMEMBER:
		Use `s.remainder()` if you want to retrieve whatever came before 
		"Hello".
		
		```
		>>> s.remainder()
		'Fi-fie-fo-fum!'
		
		```
		"""
		
		lv = self.splits(reversed(chars))
		rr = []
		for item in lv:
			rr.append(item[::-1]) # or ''.join(reversed("123"))
		
		return list(reversed(rr))
	
	
	def remainder(self):
		"""Return whatever's left of the scan text."""
		return self.collect(lambda c: True)[::-1]




