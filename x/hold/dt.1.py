#
# Copyright 2019 justworx
# This file is part of the trix project, distributed under the terms 
# of the GNU Affero General Public License.
#

from .. import *
from .loc import *


class dt(object):
	"""Date/Time utility."""

	def __init__(self, dt=None):
		"""
		Date/Time formatting.
		
		Pass `dt` as (float) seconds or timestruct. Default None sets
		this object's time to now().
		
		Format strings default to locale-appropriate formats.
		"""
		if dt:
			try:
				self.__time = float(dt)  # int/float
			except TypeError:
				self.__struct = dt
				self.__time = time.mktime(dt) # struct
		else:
			self.__time = time.time()
	
	@property
	def float(self):
		"""
		Time stored in this object, in float seconds (ala time.time()).
		"""
		return self.__time
	
	@property
	def struct(self):
		"""
		A DateTime struct created from this object's self.time.
		"""
		try:
			return self.__struct
		except:
			self.__struct = time.localtime(self.__time)
			return self.__struct
	
	
	def format(self, fmt=None):
		"""Format using strftime."""
		return time.strftime(fmt, self.struct)
	
	def datetime(self, fmt=None):
		"""Format using locale-specific format string."""
		return self.format(fmt or loc().datetime())
	
	def date(self, fmt=None):
		"""
		Format using locale-specific format string. 
		"""
		return self.format(fmt or loc().date())
	
	def time(self, fmt=None):
		"""
		Format using locale-specific format string. .
		"""
		return self.format(fmt or loc().time())
	
	def ampm(self, fmt=None):
		"""
		Format using locale-specific format string. 
		"""
		return self.format(fmt or loc().ampm())
		
		
	
	
