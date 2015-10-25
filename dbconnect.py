import MySQLdb

def connection():
	conn = MySQLdb.connect(host="localhost", user = "root", passwd = "fall0order", db = "postdb")

	c = conn.cursor()

	return c, conn