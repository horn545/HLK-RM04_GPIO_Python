'''
Created on Jul 26, 2014

@author: JDH
'''
from Listener import Listener
from Database import Database
from Pagenator import Pagenator
from Server import server
import time
import logging
import os.path

if __name__ == '__main__':
    
    currdir = os.path.abspath(os.getcwd()+'/../')
    
    try:
        logging.basicConfig(filename=os.path.normpath(currdir+'/logs/runlog.log'), level=logging.DEBUG)
           
        db = Database()
        
        listener = Listener(6969,256,db)
        listener.start()
        
        logging.info("Waiting 15 seconds for sensor data to populate the database...")
        time.sleep(15)
        
        serverdoc = Pagenator(db)
        #print serverdoc
        
        webpage = server(serverdoc,db)
        webpage.run()
        
    except SystemExit:
        print "Shutting Down..."
        logging.info("Shutting Down Main Thread...")
        webpage.stop()
        listener.stop()
        db.closedb()
        exit(0)
            