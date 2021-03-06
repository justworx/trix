#
# Copyright 2019-2020 justworx
# This file is part of the trix project, distributed under the terms 
# of the GNU Affero General Public License.
#

from trix import *
from .database import *
from ..util.propx.proplist import *   # trix, propgrid, et al
import sqlite3, re, time
import atexit


class DBGrid(Database):
	"""
	Query given grid data in an sqlite3 table.
	
	GRIDS:
	A grid is a list containing a set of lists of equal length.
	Below, are some examples of "grids".
	
	# a 2x2 grid    # a 3x2 grid        # a 3x3 grid
	[               [                   [
	  [1, 2],         ['a', 'b', 99],     [1,2,3] 
	  [3, 4]          ['C', 'D', 99],     [4,5,6]
	]               ]                     [7,8,9]
	                                    ]
	
	Create a DBGrid, add a table, and operate on the grid as though
	it were an sqlite3.db table.
	
	EXAMPLE:
	>>>
	>>> from trix.data.dbgrid import *
	>>> g = DBGrid()
	>>> g.add('four', [[1,2], [3,4]], columns=['left','right'])
	>>> g("select * from four").grid()
	>>>
	
	EXAMPLE 2:
	>>> 
	>>> SQL = "select name, size from LS where type='f' order by size"
	>>> 
	>>> from trix.data.dbgrid import *
	>>> d = trix.path( trix.innerfpath() )  # get the `trix` directory
	>>> dg = d.list.dbgrid("LS")            # create dbgrid table "LS"
	>>> dq(SQL).grid()                      # run query; view results
	name          size 
	__main__.py  215  
	.gitignore   1626 
	README.md    2174 
	LICENSE      34523
	__init__.py  53164
	>>> 
	
	"""
	
	PATHLIST = []
	
	#
	#
	# INIT
	#
	#
	def __init__(self, **k):
		"""
		Create a database for manipulation of grids.
		
		DBGrid is based on the `data.database.Database` class. All its 
		methods should be available.
		
		A `grid` is a list containing a set of lists of equal length.
		
		NOTES:
		 * DBGrid database files are always sqlite3.
		 * DBGrid database files are always temporary. Their names are
		   always auto-generated.
		 * The temporary database files are stored in `trix.DEF_CACHE`, 
		   and are deleted by the class destructor or at exit.
		 
		USAGE NOTES:
		 * See the `add()` method for details on how to create tables.
		
		"""
		
		#
		# Where the temporary sqlite3 database file is kept until the
		# object is deleted.
		#
		self.__cache = trix.path(DEF_CACHE).path
		
		#
		# Generate time-based filename in DEF_CACHE.
		#
		f='%s/dbgrid/dbgrid.%s.sqlite3' % (
				DEF_CACHE, str(time.time())
			)
		self.__fpath = f
		
		
		#
		# List of files to delete on exit.
		#
		type(self).PATHLIST.append(self.__fpath)
		
		
		#
		# Initialize the base class, Database.
		#
		Database.__init__(self, self.__fpath)
		
		#
		# Set up a class value containing a regex that validates
		# and (if necessary) deletes characters sqlite3 can't use
		# as column names.
		#
		self.__T = type(self)
		self.__T.re_columns = re.compile("^[_A-Za-z0-9]*$")
	
		
		#
		# Open the database immediately (unless kwarg autoopen=False).
		#
		self.__autoopen = k.get('autoopen', True)
		if self.__autoopen:
			self.open()
	
	
	#
	#
	# DEL
	#
	#
	def __del__(self):
		"""
		Delete the temp file.
		"""
		try:
			self.close()
		except BaseException as ex:
			print ("DBGrid __del__ Error: " + ex)
	
	
	#
	#
	# CALL METHOD - Returns result of `self.execute`.
	#
	#
	def __call__(self, sql, *a):
		"""
		Execute an sql query on the grid data.
		
		 * Pack headers and data into a DBGrid.
		 * In the event of an error, the connection is rolled back.
		
		For queries that return rows, the data is packed into a propgrid
		object.
		
		>>>
		>>> from trix.data.dbgrid import *
		>>> 
		>>> # make a dbgrid
		>>> t = DBGrid()
		>>> 
		>>> #
		>>> # Add the tablename `lr`, the columns (left and right),
		>>> # and the data.
		>>> #
		>>> t.add("lr", [ ['left', 'right'], [1,2], [3,4] ])
		>>> 
		>>> #
		>>> pl = t("select * from lr")
		>>> pl()
		[(1, 2), (3, 4)]
		>>> 
		>>> #
		>>> t('insert into lr values (5,6)')
		>>> t.commit()
		>>> 
		>>> #
		>>> t("select * from lr order by left").grid()
		1  2
		3  4
		5  6
		>>> 
				
		"""
		
		try:
			#
			# CALL EXECUTE
			#
			c = self.cur.execute(sql, *a)
			#print (['c', c])
			
			#
			# GET CURSOR DESC (from superclass Database)
			#
			cdesc = self.cdesc(c)
			#print (['cdesc', cdesc])
			
			
			#
			# CDATA is the column list taken from the sql heading results
			#
			cdata = []
			cdata.append(cdesc)
			
			#print (['cdata', cdata])
			
			for row in c.fetchall():
				cdata.append(list(row))
			
			return propgrid(list(iter(cdata)))
			
		except sqlite3.OperationalError as ex:
			#
			# If there was an error, rollback and rethrow the exception.
			#
			self.con.rollback()
			raise type(ex)(xdata(
					sql=sql, a=a, cdesc=cdesc, len_cdata=len(cdata)
				)
			)
			
		except BaseException as ex:
			raise type(ex)(xdata(
					sql=sql, a=a, cdesc=cdesc, len_cdata=len(cdata), ex=ex
				)
			)
	
	
	#
	#
	# Q 
	#
	#
	def q(self, *a, **k):
		"""
		Run an sql query on the grid data. For select statements, returns 
		rows as a list of lists.
		
		The `q` method is a convenience for inline use. It calls
		`self.__call__` passing any arguments and keyword args, and
		returning the query result wrapped in a propgrid object.
		
		EXAMPLE 1
		>>> import trix
		>>> d = trix.npath()
		>>> dg = d.list.dbgrid()
		>>>
		>>> dg.q('select * from foo order by size desc')
		
		
		"""
		return self.__call__(*a, **k)
	
	
	#
	#
	# X - Execute alias returning a propx (propgrid) with the results.
	#
	#
	def x(self, *a, **k):
		"""
		This is a shortcut for `execute`. It could be handy when space in
		the terminal is short.
		
		Execute an sql statement. Returns an sqlite3 cursor.
		
		SEE ALSO:
		>>> from trix.util.propx.propgrid import *
		>>> help(propgrid)
		
		"""
		return self.execute(*a, **k)
	
	
	#
	#
	# CC (Columns)
	#
	#
	@property
	def cc(self):
		"""Alias for `DBGrid.columns`."""
		return self.__cols
	
	
	#
	#
	# TT (Tables)
	#
	#
	@property
	def tt(self):
		"""Alias for `DBGrid.tables`."""
		return self.tables
	
	
	#
	#
	# COLUMNS
	#
	#
	@property
	def columns(self):
		return self.__cols
	
	
	#
	#
	# TABLES
	#
	#
	@property
	def tables(self):
		"""
		The tables property returns a propx object containing the names 
		of tables added to this object.
		
		If you want a straight python list, call this property as though
		it were a method.
		
		Otherwise, all the proplist features are available.
		
		EXAMPLE:
		>>> from trix.data.dbgrid import *
		>>> g = DBGrid()
		>>> g.add('four', [[1,2], [3,4]], columns=['left','right'])
		>>> g("select * from four").grid()
		left  right
		1     2    
		3     4 
		>>>   
		>>> g.tables()
		['four']
		
		
		EXAMPLE 2: 
		#
		# All on one line (sort of).
		#
		trix.npath().list.dbgrid('lgrid').x(
			'select * from lgrid order by size').grid()

		"""
		
		i = 0
		tableList = []
		while True:
			try:
				tableList.append(self.master()[i][1])
				i+=1
			except:
				pass
			
			return trix.propx(tableList)
	
	
	#
	#
	# FPATH
	#
	#
	@property
	def fpath(self):
		"""
		The fpath property returns the file path to this sqlite3 file.
		
		NOTE:
		DBGrid tables are stored in a temporary sqlite3 table, and are
		deleted on close, or at_exit.
		
		"""
		return self.__fpath
	
	
	
	#
	#
	# ADD - It converts the grid to a real table.
	#
	#
	def add(self, table_name, grid, columns=None):
		"""
		Add a table to this dbgrid.
		
		To add a table, pass the following arguments to the `DBGrid.add`
		method:
		
		 * table_name: a string value, the name of the table to add 
		   into this dbgrid.
		   
				>>>
				>>> dg = DBGrid()
				>>>
				
		 * grid: a list of lists.
				
				>>>
				>>> #
				>>> # Here, there is no `columns` argument, so the
				>>> # first list is taken to be the column headings.
				>>> #
				>>> dg.add("oh_my_grid", [ ['left','right'], [1,2], [3,4] ])
				>>> 
		 	
				OR
		 	
				If you pass a `grid` with `columns` specified, do not pass 
				the column names in the list of lists.
				
				>>> #
				>>> # Here, there IS a third (`columns`) argument, so the
				>>> # column names should NOT be prepended to the second
				>>> # argument's list.
				>>> #
				>>> dg.add("oh_my_grid", [[1,2],[3,4]], columns)
				>>> 
		
		REMEMBER: When you pass your grid without a `columns` specifier,
		          the first list in the grid is taken as a list of column
		          names.
		
		>>>
		>>> from trix.data.dbgrid import *
		>>> t = DBGrid()
		>>> t.add('four', [[1,2],[3,4]], columns=["left","right"])
		>>> t('select * from four')
		<trix/propgrid list len=2>
		>>> t('select * from four').grid()
		left  right
		1     2
		3     4
		
		"""
		
		#
		# If a columns value was specified, it will be set directly
		# into the `cols` value, and rows will be separated into 
		# the `rows` variable.
		#
		if columns:
			cols = columns
			rows = grid
		
		#
		# If a columns value is NOT specified, the first list in the
		# grid is taken to be the heading, providing column names.
		#
		else:
			cols = grid[0]
			rows = grid[1:]
		
		#
		# generate list of valid sqlite3 column names from `columns`
		#
		i = 0
		valid_cols = []
		for columnName in cols:
			valid_chars = []
			for c in columnName:
				if self.__T.re_columns.match(c):
					valid_chars.append(c)
			if valid_chars:
				valid_cols.append("".join(valid_chars))
			else:
				valid_cols.append("COLUMN_%i" % i)
				i+=1
		
		#
		# Set the validated columns in `self.__cols`.
		#
		self.__cols = valid_cols
		
		#
		# Create a table in the temporary database.
		#
		sql = "create table %s (%s)" % (table_name, ','.join(self.__cols))
		try:
			self.con.execute(sql)
		except:
			raise Exception("dbgrid.add", xdata(
					columns=self.__cols, row_ct=len(rows), sql=sql, table=table_name
				))
		
		# get the cursor
		self.cur = self.con.cursor()
		
		# populate database
		qms = ",".join("?"*len(self.__cols))
		sql = "insert into %s values (%s)" % (table_name, qms)
		self.cur.executemany(sql, iter(rows))
		
		return self
	
	
	#
	#
	# EXECUTE - returns a cursor
	#
	#
	def execute(self, sql, *a):
		"""
		Execute an sql query on the grid data. Returns an sqlite3 cursor.
		In the event of an error, the connection is rolled back.
		
		"""
		try:
			return Database.execute(self, sql, *a)
		except sqlite3.OperationalError as ex:
			#
			# If there was an error, rollback and rethrow the exception.
			#
			self.con.rollback()
			raise type(ex)(xdata(
					sql=sql, a=a, cols=self.__cols, tables=self.__T
				)
			)
	
	
	#
	#
	# CLOSE
	#
	#
	def close(self):
		try:
			Database.close(self)
		except BaseException as ex:
			pass
		try:
			trix.path(self.fpath).wrapper().remove()
		except BaseException as ex:
			pass
	
	
	#
	#
	# AT EXIT
	#  - Make sure those temp databases get removed
	#
	#
	@classmethod
	def _at_exit(cls):
		for path in cls.PATHLIST:
			w = trix.path(path).wrapper()
			try:
				w.close()
				w.remove()
			except:
				try:
					w.remove()
				except:
					pass


#
# Close and clean up temp files when program terminates.
#
atexit.register(DBGrid._at_exit)


