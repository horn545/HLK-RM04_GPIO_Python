'''
Created on Jul 23, 2014

@author: JDH
'''

import cherrypy
from cherrypy.lib import auth_digest
import os.path
import Utils
import logging
from cherrypy.wsgiserver import ssl_builtin

#Used to force compile-time import of the ssl library
ssl=ssl_builtin

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
        super(server, self).__init__()
        self.htmldoc = htmldoc
        self.db = db
        self.currdir = os.path.abspath(os.getcwd()+'/../')
    
    def stop(self):
        logging.info("Stopping Web Server...")
        cherrypy.engine.exit()
    
    def __del__(self):
        self.stop()
        
    def __exit__(self):
        self.stop()
        
    def run(self):
        logging.info("Starting Web Server...")
        logging.info("Working Dir: "+self.currdir)
        
        users = {}
        with open(os.path.normpath(self.currdir+'/conf/users.conf'),'r') as f:
            for line in f:
                (user,password) = line.split(':')
                #logging.info("...Users...")
                #logging.info("User: "+user+" Password: "+password)
                users[user] = password
                
        conf = {
        '/': {
            'tools.sessions.on': True,
            'tools.auth_digest.on': True,
            'tools.auth_digest.realm': 'control',
            'tools.auth_digest.get_ha1': auth_digest.get_ha1_dict_plain(users),
            'tools.auth_digest.key': 'a231324bagh6g3t0',
            'tools.staticdir.root': os.path.abspath(os.getcwd()+'/../')
        },
        '/toggle': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.response_headers.on': True,
            'tools.response_headers.headers': [('Content-Type', 'text/plain')],
            'tools.auth_digest.on': True,
            'tools.auth_digest.realm': 'control',
            'tools.auth_digest.get_ha1': auth_digest.get_ha1_dict_plain(users),
            'tools.auth_digest.key': 'a231324bagh6g3t0'
        },
        '/css': {
            'tools.staticdir.on': True,
            'tools.auth_digest.on': True,
            'tools.auth_digest.realm': 'control',
            'tools.auth_digest.get_ha1': auth_digest.get_ha1_dict_plain(users),
            'tools.auth_digest.key': 'a231324bagh6g3t0',
            'tools.staticdir.dir': './css'
        },
        '/js': {
            'tools.staticdir.on': True,
            'tools.auth_digest.on': True,
            'tools.auth_digest.realm': 'control',
            'tools.auth_digest.get_ha1': auth_digest.get_ha1_dict_plain(users),
            'tools.auth_digest.key': 'a231324bagh6g3t0',
            'tools.staticdir.dir': './js'
        },
        '/fonts': {
            'tools.staticdir.on': True,
            'tools.auth_digest.on': True,
            'tools.auth_digest.realm': 'control',
            'tools.auth_digest.get_ha1': auth_digest.get_ha1_dict_plain(users),
            'tools.auth_digest.key': 'a231324bagh6g3t0',
            'tools.staticdir.dir': './fonts'
        },
        '/favicon.ico': {
            'tools.staticfile.on': True,
            'tools.auth_digest.on': True,
            'tools.auth_digest.realm': 'control',
            'tools.auth_digest.get_ha1': auth_digest.get_ha1_dict_plain(users),
            'tools.auth_digest.key': 'a231324bagh6g3t0',
            'tools.staticfile.filename': './css/favicon.ico'
        }
        }
        
        webapp = GPIOToggler(self.htmldoc)
        webapp.toggle = GPIOTogglerWebService(self.db)
        cherrypy.tree.mount(webapp, '/', config=conf)

        cherrypy.server.unsubscribe()
        
        if os.path.isfile(os.path.normpath(self.currdir+'/certs/cert.cer')) and os.path.isfile(os.path.normpath(self.currdir+'/certs/cert.key')):
            logging.info("Starting HTTPS Server...")
            server1 = cherrypy._cpserver.Server()
            server1.socket_port=443
            server1._socket_host='0.0.0.0'
            server1.thread_pool=10
            server1.ssl_module = 'builtin'
            server1.ssl_certificate = os.path.normpath(self.currdir+'/certs/cert.cer')
            server1.ssl_private_key = os.path.normpath(self.currdir+'/certs/cert.key')
            #server1.ssl_certificate_chain = os.path.normpath(self.currdir+'/cert_bundle.crt')
            server1.subscribe()
        else:
            logging.info("HTTPS DISABLED -- No cert.cer or cert.key found")
    
        logging.info("Starting HTTP Server...")
        server2 = cherrypy._cpserver.Server()
        server2.socket_port=80
        server2._socket_host="0.0.0.0"
        server2.thread_pool=10
        server2.subscribe()

        cherrypy.log.screen = None
        
        #print os.path.normpath(currdir+'/access_log')
        cherrypy.log.access_file = os.path.normpath(self.currdir+'/logs/access_log')
        cherrypy.log.error_file = os.path.normpath(self.currdir+'/logs/error_log')
        
        cherrypy.log.access_log.propagate = False
        cherrypy.log.error_log.propagate = False
        
        cherrypy.engine.autoreload.on = False
        
        cherrypy.engine.start()
        cherrypy.engine.block()
        
        logging.info("Web Server Stopped.")
        return
    
