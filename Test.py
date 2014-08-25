'''
Created on Jul 26, 2014

@author: JDH
'''
from Listener import Listener
from Database import Database
from Pagenator import Pagenator
from Server import server
import os.path
import time

if __name__ == '__main__':
    db = Database()
    
    listener = Listener(6969,256,db)
    listener.start()
    
    print "Waiting 10 seconds for sensor data to populate the database..."
    time.sleep(10)
    
    serverdoc = Pagenator(db)
    #print serverdoc
    
    webpage = server(serverdoc,db)
    webpage.start()
    
    while True:
        pwd = os.path.abspath(os.getcwd())

