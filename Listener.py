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
import errno
from threading import Thread

class Listener(Thread):
    def __init__(self, port, bufferSize, db):
        Thread.__init__(self)
        print "Initializing Listener on port "+str(port)+" with buffer size "+str(bufferSize)+"..."
        self.port = port
        self.bufferSize = bufferSize
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('', self.port))
        self.sock.setblocking(False)
        self.db = db
        
    def run(self):
        print 'Starting Listener...'
        while True:
            self.msg = ''
            while self.msg == '':
                try:
                    self.msg = self.sock.recv(self.bufferSize)
                except socket.error, e:
                    err = e.args[0]
                    if err == errno.EAGAIN or err == errno.EWOULDBLOCK:
                        continue
                    else:
                        raise
                else:
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