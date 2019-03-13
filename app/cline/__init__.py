#
# Copyright 2018 justworx
# This file is part of the trix project, distributed under 
# the terms of the GNU Affero General Public License.
#


from ... import *


class cline(object):
	"""Command-line plugin."""
	
	@classmethod
	def handle(cls):
		"""
		The trix.__main__.py module calls cline handle to create the
		proper command-line handler, which will automatically perform
		its task immediately.
		
		If you're trying to track down a bug, your next step is probably
		to open the module (within the cline directory) that has the same
		module and class name as the command being executed. 
		
		NOTE: Every cline class name matches its module name, so the 
		      last two items in the "ncreate" method's argument match. 
		      EG., app.cline.test.test, app.cline.http.http, etc...
		
		"""
		cls.app = sys.argv[0]
		cls.cmd = sys.argv[1] if len(sys.argv) > 1 else ''
		if cls.cmd:
			if cls.cmd == 'help':
				cls.help()
			else:
				#
				# Creating the command actually runs the command.
				# All plugins must be named the same as their module.
				#
				trix.ncreate("app.cline.%s.%s" % (cls.cmd, cls.cmd))
	
	@classmethod
	def help(cls):
		"""Print help for subclasses."""
		if len(sys.argv) > 2:
			help4 = sys.argv[2]
			print("Help for:", help4)
			CLS = trix.nvalue("app.cline.%s.%s" % (help4, help4))
			print (CLS.__doc__)
		else:
			d = path('trix/app/cline').dir()
			print("Available commands:")
			for item in d.ls():
				if (item[:2] == '__') or (item[-2:] != 'py'):
					pass
				else:
					print (" - " + ".".join(item.split('.')[:-1]))
	
	
	def __init__(self):
		"""Parse and store args, kwargs, and flags."""
		self.args = []
		self.flags = ''
		self.kwargs = {}
		
		args = sys.argv[2:]
		for a in args:
			if a[:2]=="--":
				kv = a[2:].split("=")
				self.kwargs[kv[0]] = kv[1] if len(kv)>1 else True
			elif a[:1] == '-':
				self.flags += a[1:]
			else:
				self.args.append(a)
		
		#DBG print (str(seelf.args), str(self.flags), str(self.kwargs))
	
	
	def write(self, result):
		print (result)
	
	
	def display(self, result, *a, **k):
		trix.display(result, *a, **k)


