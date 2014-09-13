'''
*-----------------------------------------------
* Listener Class
* Creates a UDP Listening socket and returns True
* whenever a new message is received
*
* Jason Harnish
* 7/26/2014
*-----------------------------------------------
'''
import socket
#import errno
from threading import Thread, Event
import logging

class Listener(Thread):
    def __init__(self, port, bufferSize, db):
        super(Listener, self).__init__()
        self._stop = Event()
        #Thread.daemon = True
        logging.info("Initializing Listener on port "+str(port)+" with buffer size "+str(bufferSize)+"...")
        self.port = port
        self.bufferSize = bufferSize
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('', self.port))
        #self.sock.setblocking(False)
        self.sock.setblocking(True)
        self.db = db
        self.setName("Listener Thread")
        
    def stop(self):
        logging.info("Stopping Listener...")
        self._stop.set()
        self._Thread__stop()
        
    def __del__(self):
        self.stop()
        
    def __exit__(self):
        self.stop()
        
    def run(self):
        logging.info('Starting Listener...')
        while not self._stop.isSet():
            #print time.clock()
            self.msg = self.sock.recv(self.bufferSize)
            #print time.clock()

            message = self.msg.split(',')
            msgIP = message[0]
            msgPort = int(message[1])
            msgName = message[2]
            msgDateRaw = message[-1]
            msgDate = '20'+msgDateRaw[0:2]+"-"+msgDateRaw[2:4]+"-"+msgDateRaw[4:6]
            msgTime = msgDateRaw[6:8]+":"+msgDateRaw[8:10]+":"+msgDateRaw[10:12]
            
            pinInfo = {}
            for item in message[3:-1]:
                if 'gpio' in item:
                    pin = item.split(':')
                    pinInfo[str(pin[0][4:])] = [pin[1], pin[2]]
            self.db.insert(msgName, msgIP, msgPort, pinInfo.keys(), pinInfo.values(), str(msgDate)+" "+str(msgTime))
            #print "Data Inserted..."
            #print datetime.datetime.now().time()
            #print msgName, msgIP, msgPort, pinInfo.keys(), pinInfo.values(), str(msgDate)+" "+str(msgTime)
        logging.info("Listener Stopped.")
        return
