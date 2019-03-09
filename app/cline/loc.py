#
# Copyright 2019 justworx
# This file is part of the trix project, distributed under the terms 
# of the GNU Affero General Public License.
#

from . import *
import locale

class loc(cline):
	"""
	Return a locale conversion dict for the given language.
	
	```
	python3 -m trix loc en_CA.UTF_8
	
	```
	"""
	
	def __init__(self):
		"""Handle loc requests."""
		
		# create object base, and self.sig signature (Eg., "en_US.utf_8")
		cline.__init__(self)
		try:
			self.sig = self.args[0]
		except IndexError:
			self.sig = '.'.join(locale.getlocale()) # default to System
		
		#
		# SET THE LOCAL
		#
		locale.setlocale(self.sig)
		
		# output value format
		if 'c' in self.flags:
			self.rfmt = 'JCompact'
		else:
			self.rfmt = 'JDisplay'
		
		# specialized function call - must be compacted
		if 'currency' in self.kwargs:
			# TEST
			k = self.kwargs
			if 'currency' in k:
				c = k.get('currency')
				print (locale.currency(float(c)))
			
			#sortlist = trix.jparse(self.arg[0])
		
		else:
			# return locale info dict
			self.get_loc_info()
	
	
	
	
	def get_loc_info(self):
		"""The default action - return locale info dict."""
		
		rdict = {}
		
		# think about joining all these dicts into one...
		rdict['locale'] = self.sig # eg. en_US.UTF_8
		rdict['loconv'] = locale.localeconv()
		rdict['format'] = {
			"datetime" : locale.nl_langinfo(locale.D_T_FMT),
			"date" : locale.nl_langinfo(locale.D_FMT),
			"time" : locale.nl_langinfo(locale.T_FMT),
			"ampm" : locale.nl_langinfo(locale.T_FMT_AMPM),
			"era" : locale.nl_langinfo(locale.ERA)
		}
		
		# values
		rdict['day'] = [locale.nl_langinfo(x) for x in loc.DAY]
		rdict['abday'] = [locale.nl_langinfo(x) for x in loc.ABDAY]
		rdict['mon'] = [locale.nl_langinfo(x) for x in loc.MON]
		rdict['abmon'] = [locale.nl_langinfo(x) for x in loc.ABMON]
		
		# other
		rdict['radix'] = locale.nl_langinfo(locale.RADIXCHAR)
		rdict['thousep'] = locale.nl_langinfo(locale.THOUSEP)
		rdict['YESEXPR'] = locale.nl_langinfo(locale.YESEXPR)
		rdict['NOEXPR'] = locale.nl_langinfo(locale.NOEXPR)
		rdict['CRNCYSTR'] = locale.nl_langinfo(locale.CRNCYSTR)
		rdict['ERA'] = locale.nl_langinfo(locale.ERA)
		rdict['ERA_D_T_FMT'] = locale.nl_langinfo(locale.ERA_D_T_FMT)
		rdict['ERA_D_FMT'] = locale.nl_langinfo(locale.ERA_D_FMT)
		rdict['ERA_T_FMT'] = locale.nl_langinfo(locale.ERA_T_FMT)
		
		trix.display(rdict, f=self.rfmt)
	
	
	# -----------------------------------------------------------------
	
	#
	# CONSTANT LISTS
	#  - These constants help make the above date-related methods easier
	#    to call.
	#
	DAY = [
		locale.DAY_1, locale.DAY_2, locale.DAY_3, locale.DAY_4,
		locale.DAY_5, locale.DAY_6, locale.DAY_7
	]
	
	ABDAY = [
		locale.ABDAY_1, locale.ABDAY_2, locale.ABDAY_3, locale.ABDAY_4,
		locale.ABDAY_5, locale.ABDAY_6, locale.ABDAY_7
	]
	
	MON = [
		locale.MON_1, locale.MON_2, locale.MON_3, locale.MON_4,
		locale.MON_5, locale.MON_6, locale.MON_7, locale.MON_8,
		locale.MON_9, locale.MON_10, locale.MON_11, locale.MON_12
	]
	
	ABMON = [
		locale.ABMON_1, locale.ABMON_2, locale.ABMON_3, locale.ABMON_4,
		locale.ABMON_5, locale.ABMON_6, locale.ABMON_7, locale.ABMON_8,
		locale.ABMON_9, locale.ABMON_10, locale.ABMON_11, locale.ABMON_12
	]




