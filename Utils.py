'''
*-----------------------------------------------
* Utility Functions
* 
*
* Jason Harnish
* 7/26/2014
*-----------------------------------------------
'''
import socket
from des_crypt import des_crypt as crypt
from Config import Config
import time
import os.path


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
    sql = "SELECT DISTINCT pinval from sensor_data where ip='"+ip+"' and pin='"+pin+"' and timestamp >= datetime('now', '-5 seconds', 'localtime') group by pinval order by timestamp"
    try:
        states = db.query(sql)
        for state in states:
            #print "States..."+str(state[0])
            laststate = state[0]
        return laststate
    except:
        raise

def getport(ip,db):
    sql = "SELECT DISTINCT port from sensor_data where ip='"+ip+"' and timestamp >= datetime('now', '-5 seconds', 'localtime')"
    try:
        ports = db.query(sql)
        for port in ports:
            sensorport = port[0]
        return sensorport
    except:
        raise

def getname(ip,db):
    sql = "SELECT DISTINCT name FROM sensor_data WHERE ip='"+ip+"'"
    try:
        sensornames = db.query(sql)
        for sensor in sensornames:
            sensorname = sensor[0]
        return sensorname
    except:
        raise
    
def getdirection(ip,pin,db):
    sql = "SELECT DISTINCT pindir FROM sensor_data WHERE ip='"+ip+"' and pin='"+pin+"'"
    try:
        pindirs = db.query(sql)
        for pdir in pindirs:
            pindir = pdir[0]
        return pindir
    except:
        raise
    
def gettime(config,sensorname,pin):
    sleeptime = 0
    #print "Getting sleep time for module "+sensorname
    for module in config.modules:
        if module.text.strip() == sensorname:
            for item in module:
                if item.tag == 'pinalias':
                    for key in item.attrib.keys():
                        if key == 'timed':
                            sleeptime = item.attrib[key].strip()
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
        time.sleep(.5)
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
        time.sleep(.5)
        state = getstate(ip,pin,db)
        #print state,type(state)
    
def toggle(ip,pin,db):
    
    sensorport = getport(ip,db)
    #print "Sensor Port is..."+str(sensorport)
    
    sensorname = getname(ip,db)
    #print "Sensor Name is..."+sensorname
    
    laststate = getstate(ip,pin,db)
    #print "Last State was... "+str(laststate)
    
    currdir = os.path.abspath(os.getcwd()+'/../')
    config = Config(os.path.normpath(currdir+'/conf/gpio_wifi.cfg'))
             
    sleeptime = gettime(config,sensorname,pin)
    #print "Sleeptime is..."+sleeptime
                  
    try:
        if laststate == 0:
            #print "Last State was 0"
            #print "Running "+sensorname+" for "+str(sleeptime)+" seconds..."
            setto1(ip,sensorport,pin,db,config)
            if int(sleeptime) > 0:
                time.sleep(int(sleeptime))
                setto0(ip,sensorport,pin,db,config)
            return True            

        elif laststate == 1:
            #print "Last State was 1"
            #print "Running "+sensorname+" for "+str(sleeptime)+" seconds..."
            setto0(ip,sensorport,pin,db,config)
            if int(sleeptime) > 0:
                time.sleep(int(sleeptime))
                setto1(ip,sensorport,pin,db,config)
            return True
            
        else:
            toggle(ip,pin,db)
    except:
        raise
        return False
    