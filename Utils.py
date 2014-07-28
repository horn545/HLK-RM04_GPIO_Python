'''
*-----------------------------------------------
* Config Class
* Creates a sqllite3 database with a table to store
* GPIO pin data
*
* Jason Harnish
* 7/26/2014
*-----------------------------------------------
'''
import socket

def getsalt(ip,port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((ip,port))
        recvsalt = sock.recv(256)
        sock.shutdown(socket.SHUT_RDWR)
        sock.close()
        return recvsalt
    except:
        raise
    
def setpin(ip,port,password,pin,value):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((ip,port))
        sock.send("setpin,gpio"+pin+":"+value+","+password)
        sock.shutdown(socket.SHUT_RDWR)
        sock.close()
        return True
    except:
        raise
        return False
        
    