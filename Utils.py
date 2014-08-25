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
from passlib.hash import des_crypt as crypt
from Config import Config
import time


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
    
def getstate(ip,pin,db):
    sql = "SELECT DISTINCT pinval from sensor_data where ip=? and pin=? and timestamp >= datetime('now', '-5 seconds', 'localtime') group by pinval order by timestamp"
    states = db.db.execute(sql,(ip,pin))
    for state in states:
        #print "States..."+str(state[0])
        laststate = state[0]
    return laststate

def getport(ip,db):
    sql = "SELECT DISTINCT port from sensor_data where ip=? and timestamp >= datetime('now', '-5 seconds', 'localtime')"
    ports = db.db.execute(sql,(ip,))
    for port in ports:
        sensorport = port[0]
    return sensorport

def getname(ip,db):
    sql = "SELECT DISTINCT name FROM sensor_data WHERE ip=?"
    sensornames = db.db.execute(sql,(ip,))
    for sensor in sensornames:
        sensorname = sensor[0]
    return sensorname

def gettime(config,sensorname):
    sleeptime = 0
    #print "Getting sleep time for module "+sensorname
    for module in config.modules:
        if module.text.strip() == sensorname:
            for item in module:
                if item.tag == 'timed':
                    #print "Got this..."+item.text
                    if item.text.strip() > '0':
                        sleeptime = int(item.text.strip())
    return sleeptime

def setto1(ip,sensorport,pin,db,config):
    #print "-----Setting pin to 1"
    recvsalt = getsalt(ip,int(sensorport))
    passhash = crypt.encrypt(config.password,salt=recvsalt[0:2])
    setpin(ip,sensorport,passhash,pin,"1")
    time.sleep(1)
    state = getstate(ip,pin,db)
    while state == 0:
        recvsalt = getsalt(ip,int(sensorport))
        passhash = crypt.encrypt(config.password,salt=recvsalt[0:2])
        setpin(ip,sensorport,passhash,pin,"1")
        time.sleep(0.5)
        state = getstate(ip,pin,db)
        #print state,type(state)

def setto0(ip,sensorport,pin,db,config):
    #print "-----Setting pin to 0"
    recvsalt = getsalt(ip,int(sensorport))
    passhash = crypt.encrypt(config.password,salt=recvsalt[0:2])
    setpin(ip,sensorport,passhash,pin,"0")
    time.sleep(1)
    state = getstate(ip,pin,db)
    while state == 1:
        recvsalt = getsalt(ip,int(sensorport))
        passhash = crypt.encrypt(config.password,salt=recvsalt[0:2])
        setpin(ip,sensorport,passhash,pin,"0")
        time.sleep(0.5)
        state = getstate(ip,pin,db)
        #print state,type(state)
    
def toggle(ip,pin,db):
    
    sensorport = getport(ip,db)
    #print "Sensor Port is..."+str(sensorport)
    
    sensorname = getname(ip,db)
    #print "Sensor Name is..."+sensorname
    
    laststate = getstate(ip,pin,db)
    #print "Last State was... "+str(laststate)
    
    config = Config('gpio_wifi.cfg')
             
    sleeptime = gettime(config,sensorname)
    #print "Sleeptime is..."+str(sleeptime)
                  
    try:
        if laststate == 0:
            #print "Last State was 0"
            #print "Running "+sensorname+" for "+str(sleeptime)+" seconds..."
            setto1(ip,sensorport,pin,db,config)
            if sleeptime > 0:
                time.sleep(sleeptime)
                setto0(ip,sensorport,pin,db,config)
            return True            

        elif laststate == 1:
            #print "Last State was 1"
            #print "Running "+sensorname+" for "+str(sleeptime)+" seconds..."
            setto0(ip,sensorport,pin,db,config)
            if sleeptime > 0:
                time.sleep(sleeptime)
                setto1(ip,sensorport,pin,db,config)
            return True
            
        else:
            toggle(ip,pin,db)
    except:
        raise
        return False
    