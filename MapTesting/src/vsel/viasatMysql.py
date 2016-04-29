import mysql.connector

class vMysql(object):

	# Pass in a configuration file that defines a dictionary for the connection parameters
	# the necessary connection parameters are
	# user, password, database, and host, but there
	# are optional ones found on the mysql website
	def __init__(self, user, password, database, host='127.0.0.1', port=3306):
		self.mysqlConnection = dict(user=user, password=password, database=database, host=host, port=port)
	def open(self):
		self.cnx = mysql.connector.connect(**self.mysqlConnection)

	def close(self):
		self.cnx.close()

	# Pass in a dictionary where the keys are the column names and the values
	# are the values you want to set in the database and pass in a string which
	# is the name of the table you wish to set. Optional update dictionary
	# that states what to update the fields to if the primary key value already exists
	def setTable(self, tableName, setDict, updateDict=None):
		self.open()
		cursor = self.cnx.cursor()
		statement = "INSERT INTO {} ".format(tableName)
		columns = "("
		values = "VALUES ("
		for key in setDict:
			columns += "{}, ".format(key)
			values += "'{}', ".format(setDict[key])
		columns = columns[:-2] + ") "
		values = values[:-2] + ") "
		update = ""
		if updateDict:
			update = " ON DUPLICATE KEY UPDATE "
			for key in updateDict:
				update += "{}='{}', ".format(key, updateDict[key])
			update = update[:-2]
		statement += columns + values + update
		cursor.execute(statement)
		self.cnx.commit()
		cursor.close()
		self.close()

	# Pass in the tableName you wish to query, a list of the columns you wish
	# to get, and an optional dictionary for further constraints on the query
	# getTable will return a list of dictionaries, where each row is
	# dicitonary, where the column names (ones specified in the getList, or al
	# if getList is emply) are the keys and the values are the corresponding
	# values from the database
	def getTable(self, tableName, getList=None, whereDict=None, extraConstraint=None):
		self.open()
		cursor = self.cnx.cursor(dictionary=True)
		statement = "SELECT "
		if getList:
			get = ""
			for column in getList:
				get += "{}, ".format(column)
			get = get[:-2]
		else:
			get = "*"
		statement += get + " FROM {} ".format(tableName)
		if whereDict:
			where = "WHERE "
			for key in whereDict:
				where += "{}='{}', ".format(key, whereDict[key])
			where = where[:-2]
		else:
			where = ""
		statement += where
		if extraConstraint:
			statement += extraConstraint
		cursor.execute(statement)
		result = []
		for row in cursor:
			result.append(row)
		cursor.close()
		self.close()
		return result

	def updateTable(self, tableName, updateDict, whereDict=None):
		self.open()
		cursor = self.cnx.cursor()
		statement = "UPDATE {} ".format(tableName)
		update = "SET "
		for key in updateDict:
			update += "{}='{}', ".format(key, updateDict[key])
		update = update[:-2]
		if whereDict:
			where = " WHERE "
			for key in whereDict:
				where += "{}='{}' AND".format(key, whereDict[key])
			where = where[:-4]
		else:
			where = ""
		statement += update + where
		cursor.execute(statement)
		self.cnx.commit()
		cursor.close()
		self.close()


	def getAutoIncrement(self):
		pass
