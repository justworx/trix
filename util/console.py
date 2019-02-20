#
# Copyright 2018 justworx
# This file is part of the trix project, distributed under
# the terms of the GNU Affero General Public License.
#


from .output import * # trix, enchelp, sys
from .event import *
from .xinput import *
from .wrap import *


#
# ---- CONSOLE -----
#

class Console(BaseOutput):
	"""
	Base class for an interactive command-line user interface.
	"""
	
	Debug = 0 
	
	def __init__(self, config=None, **k):
		
		config = config or {}
		config.update(k)
		
		BaseOutput.__init__(self, config)
		
		# debugging
		self.__debug = config.get('debug', self.Debug)
		
		# wrapper
		self.__wrap = Wrap(config.get('wrap'))
	
	
	
	def __del__(self):
		self.__wrap = None
	
	
	
	@property
	def debug(self):
		"""Debug setting."""
		return self.__debug
	
	@property
	def jformat(self):
		"""Object display format (default: JDisplay)."""
		try:
			return self.__jformat
		except:
			self.__jformat = trix.formatter(f='JDisplay')
			return self.__jformat
	
	@property
	def prompt(self):
		"""Console prompt."""
		return "> "

	
	
	#
	# BANNER
	#
	def banner(self):
		"""Display entry banner."""
		self.output("\n#\n# CONSOLE\n", newl='')
		
		#
		# Some of this needs to be transferred to a /help section.
		# The command characters need to be configurable, and the
		# msg (or help message) need to use the udb 'NAME' property
		# to describe them (instead of, eg, "exclamation point" and 
		# "forward-slash").
		#
		msg = """
		-- THIS CLASS IS UNDER CONSTRUCTION! EXPECT CHANGES. --
			
			* Entered text will be sent to the target stream.
			* Prefix Console commands with the forward-slash "/" 
			  character. Eg., "/exit", "/debug True", etc...
			* Commands prefixed with an exclamation point "!" character
			  are directed to the 'wrapped' object..
			* Ctrl-c to exit.
		"""
		ll = msg.splitlines()
		for line in ll:
			self.output("#  " + line.lstrip("\t"))
	
	
	
	#
	# CREATE EVENT
	#
	def create_event(self, commandLineText):
		"""Returns a TextEvent."""
		return LineEvent(commandLineText)
	
	
	
	#
	#
	# CONSOLE - Run the console (Loop)
	#
	#
	def console(self):
		"""Call this method to start a console session."""
		self.banner()
		self.__active = True
		while self.__active:
			e=None
			try:
				# get input, create Event
				line = xinput(self.prompt).strip()
				
				# make sure there's some text to parse
				if line:
					# get and handle event
					if line[0] == '/':
						# this is a command for the console object
						e = self.create_event(line[1:])
						self.handle_command(e)
					elif line[0] == '!':
						# this is a command for the wrapped object
						e = self.create_event(line[1:])
						self.handle_wrapper(e)
					else:
						e = self.create_event(line)
						self.handle_input(e)
			
			except (EOFError, KeyboardInterrupt) as ex:
				# Ctrl-C exits this prompt with EOFError; end the session.
				self.__active = False
				self.output("\n#\n# Console Exit\n#\n")
			
			except BaseException as ex:
				self.output('') # get off the "input" line
				self.output("#\n# %s: %s\n#" % (type(ex).__name__, str(ex)))
				if self.debug:
					if e and e.error:
						self.output(self.jformat(dict(event=e.dict,err=e.error)))
					self.output(self.jformat(xdata))
					#self.output(self.newl.join(trix.tracebk()))
					self.output(self.jformat(trix.tracebk()))
	
	
	
	
	#
	#
	# ---- HANDLE INPUT, COMMANDS -----
	#
	#
	
	def handle_input(self, e):
		"""Send `e.text` to the target stream."""
		self.output(e.text)
	
	
	
	
	def handle_command(self, e):
		"""
		Handle input event `e`.
		"""
		if e.argvl[0] == 'debug':
			if e.arg(1):
				self.__debug = int(e.arg(1))
			else:
				self.output(str(self.__debug))
		
		# exit the console session
		elif e.argvl[0] == 'exit':
			self.__active = False
		
		# leave the console session
		elif e.argvl[0] in ['wrap', 'wrapper']:
			wrap = type(self.__wrap.o).__name__
			self.output("%s: %s" % (wrap, self.__wrap.name))
	
	
	
	
	def handle_wrapper(self, e):
		"""
		Handle commands prefixed with the exclamation point '!' 
		character - wrapped object commands.
		
		NOTE: Wrapper commands are case-sensitive.
		"""		
		if self.__wrap:
			# wrapper commands are case-sensitive, so use e.arg(0)
			r = self.__wrap(e.arg(0), *e.argv[1:], **e.kwargs)
			if r:
				self.output(str(r))
	



