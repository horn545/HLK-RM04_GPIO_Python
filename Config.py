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
            tree = xml.ElementTree(file=filename)
            self.root = tree.getroot()
            self.password = self.root.attrib['password']
        except:
            raise




