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
import xml.etree.ElementTree as xml


class Config(object):
    def __init__(self,filename):
        
        try:
            tree = xml.parse(filename)
            root = tree.getroot()
            
            self.password = root.attrib['password']
            self.modules = tree.iter('module')
            
        except:
            raise