'''
*-----------------------------------------------
* Database Class
* Creates a sqllite3 database with a table to store
* GPIO pin data
*
* Jason Harnish
* 7/26/2014
*-----------------------------------------------
'''
import sqlite3

class Database(object):
    def __init__(self):
        self.db_name = "gpio.db"
        self.table_name = "sensor_data"
        print "Initializing Database "+self.db_name+" with data table "+self.table_name+"..."
        self.db = sqlite3.connect(self.db_name)
        self.cur = self.db.cursor()
        self.db.execute("CREATE TABLE IF NOT EXISTS "+self.table_name+" (name TEXT, ip TEXT, port INT, pin TEXT, pinval INT, pindir TEXT, datetime DATE)")
        self.db.commit()


    def insert(self, name, ip, port, pins, pinvals, datetime):
        try:
            for pin in pins:
                pinindex = pins.index(pin)
                self.db.execute("INSERT INTO sensor_data VALUES(?,?,?,?,?,?,?)", (name, ip, port, pin, pinvals[pinindex][0], pinvals[pinindex][1], datetime))
        except:
            raise


    def get(self, query):
        try:
            self.cur.execute(query)
            output = self.cur.fetchall()
            return output
        except:
            raise