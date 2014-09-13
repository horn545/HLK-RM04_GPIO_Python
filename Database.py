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
import logging

class Database(object):
    def __init__(self):
        self.db_name = "gpio.db"
        self.table_name = "sensor_data"
        logging.info("Initializing Database "+self.db_name+" with data table "+self.table_name+"...")
        conn = sqlite3.connect(self.db_name)
        with conn:
            conn.execute("DROP TABLE IF EXISTS "+self.table_name)
            conn.execute("CREATE TABLE IF NOT EXISTS "+self.table_name+" (name TEXT, ip TEXT, port INT, pin TEXT, pinval INT, pindir TEXT, timestamp DATE)")
            conn.commit()
        #conn.close()
        
    def insert(self, name, ip, port, pins, pinvals, datetime):
        if self != '' and name !='' and ip != '' and port != '' and pins != '' and pinvals !='' and datetime != '':
            try:
                for pin in pins:
                    pinindex = pins.index(pin)
                    conn = sqlite3.connect(self.db_name)
                    with conn:
                        #print "Committing..."
                        conn.execute("INSERT INTO sensor_data VALUES(?,?,?,?,?,?,?)", (name, ip, port, pin, pinvals[pinindex][0], pinvals[pinindex][1], datetime))
                        conn.commit()
                    conn.close()
                    return True
            except:
                raise
            
    def query(self,sql):
        if sql != '':
            try:
                conn = sqlite3.connect(self.db_name)
                with conn:
                    #print "Querying..."
                    output = conn.execute(sql)
                #conn.close()
                return output
            except:
                raise
    
    def closedb(self):
        logging.info("Closing Database...")
        conn = sqlite3.connect(self.db_name)
        conn.commit()
        conn.close()
        return True
    
    def __del__(self):
        self.closedb()
    
    def __exit__(self):
        self.closedb()
        
                
                