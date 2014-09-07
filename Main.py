'''
Created on Jul 26, 2014

@author: JDH
'''
from Listener import Listener
from Database import Database
from Pagenator import Pagenator
from Server import server
import time


if __name__ == '__main__':
    db = Database()
    
    listener = Listener(6969,256,db)
    listener.start()
    
    print "Waiting 15 seconds for sensor data to populate the database...\n"
    time.sleep(15)
    
    serverdoc = Pagenator(db)
    #print serverdoc
    
    webpage = server(serverdoc,db)
    webpage.run()
    
    db.closedb()
    print "Stopped at "+time.strftime('%d-%m-%Y %H:%M:%S')