'''
Created on Jul 23, 2014

@author: JDH
'''

import cherrypy
from threading import Thread
import os.path
import Utils

class GPIOToggler(object):
    def __init__(self,htmldoc):
        self.htmldoc = htmldoc
    @cherrypy.expose
    def index(self):
        return self.htmldoc
    
class GPIOTogglerWebService(object):
    def __init__(self,db):
        self.db = db
            
    exposed = True
    
    @cherrypy.tools.accept(media='text/plain')
    def POST(self,ip,pin):
        Utils.toggle(ip,str(pin),self.db)
    
    @cherrypy.tools.accept(media='text/plain')    
    def GET(self,ip,pin):
        state = Utils.getstate(ip, pin, self.db)
        return str(state)
        
class server(object):
    def __init__(self,htmldoc,db):
        #Thread.__init__(self)
        self.htmldoc = htmldoc
        self.db = db
        
    def run(self):
        print "Starting Web Server..."
        conf = {
        '/': {
            'tools.sessions.on': True,
            'tools.staticdir.root': os.path.abspath(os.getcwd())
        },
        '/toggle': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.response_headers.on': True,
            'tools.response_headers.headers': [('Content-Type', 'text/plain')],
        },
        '/css': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': './css'
        },
        '/js': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': './js'
        },
        '/fonts': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': './fonts'
        },
        '/favicon.ico': {
            'tools.staticfile.on': True,
            'tools.staticfile.filename': './css/favicon.ico'
        }
        }
        webapp = GPIOToggler(self.htmldoc)
        webapp.toggle = GPIOTogglerWebService(self.db)
        cherrypy.log.screen = None
        currdir = os.path.abspath(os.getcwd())
        #print os.path.normpath(currdir+'/access_log')
        cherrypy.log.access_file = os.path.normpath(currdir+'/access_log')
        cherrypy.config.update({'server.socket_host': '0.0.0.0', 'server.socket_port': 80})
        cherrypy.quickstart(webapp, '/', conf)