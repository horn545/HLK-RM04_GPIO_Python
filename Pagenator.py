'''
*-----------------------------------------------
* Pagenator Def
* Generates any static pages from database sensor
* data.
*
* Jason Harnish
* Jul 29, 2014
*-----------------------------------------------
'''
from Config import Config
import Utils
import logging
import os.path

def Pagenator(db):
    logging.info("Building Web Page...")
    sql = "SELECT DISTINCT name FROM sensor_data"
    names = db.query(sql)
    
    currdir = os.path.abspath(os.getcwd()+'/../')
    #print "Pagenator Dir... "+currdir

    header = '''<!DOCTYPE html>
    <html>
        <head>
         <title>Control Center</title>
         <link rel="shortcut icon" href="/css/favicon.ico">
         <meta charset="utf-8">
         <meta http-equiv="X-UA-Compatible" content="IE-edge">
         <meta name="viewport" content="width=device-width, initial-scale=1">
         <link href="css/bootstrap.min.css" rel="stylesheet">
         <link href="css/bootstrap-theme.min.css" rel="stylesheet">
         <link href="css/style.css" rel="stylesheet">
         <script src="js/jquery-2.0.3.min.js"></script>
         <script src="js/bootstrap.min.js"></script>
         '''
    ajax = '''            <script type="text/javascript">
           $(document).ready(function() {\n'''
    
    ajaxfooter = '''            });
            </script>
            </head>'''
    
    body = '''            <body role="document">
             <div class="container theme-showcase" role="main">
             <center>\n'''
    
    footer ='''        </center>
        </div>
    </body>
</html>'''
                     
    for name in names:
        config = Config(os.path.normpath(currdir+'/conf/gpio_wifi.cfg'))
        #print os.path.normpath(currdir+'/conf/gpio_wifi.cfg')
        for module in config.modules:
            if module.text.strip() == name[0]:
                #print 'Have data for '+name[0]

                for item in module:
                    if item.tag == "alias":
                        alias = item.text.strip()
                        #print 'The modules alias is '+item.text
                        body+='''<div class="page-header">
                        <h1>'''+alias+'''</h1>
                        </div>\n'''
                try:
                    sql = "SELECT DISTINCT ip FROM sensor_data WHERE name='"+name[0]+"'"
                    ips = db.query(sql)
                except:
                    raise
                
                for address in ips:
                    ip = address[0].strip()
                    #print "The module '"+alias+"' has an IP address of "+ip
                    
                try:
                    sql = "SELECT DISTINCT pin FROM sensor_data where name='"+name[0]+"'"
                    pinarray = db.query(sql)
                except:
                    raise
                
                for pin in pinarray:
                    
                    pindir = Utils.getdirection(ip, pin[0], db)
                    #print "The module has this pin..."+pin[0]
                    ajax+='''                    $("#'''+name[0]+pin[0]+'''").click(function(e) {
                                $( this ).attr('disabled','disabled').addClass('ui-state-disabled');
                                $.ajax({
                                type: "POST",
                                url: "/toggle",
                                data: { ip: "'''+ip+'", pin: "'+pin[0]+'''"}
                                })
                                  .done(function() {
                                  alert("'''+alias+''' Finished!");
                                  $( "#'''+name[0]+pin[0]+'''" ).removeAttr('disabled').removeClass('ui-state-disabled');
                                   });
                                e.preventDefault();
                              });\n'''
                    
                    for item in module:
                        if item.tag == 'pinalias':
                            for attrib in item.attrib.keys():
                                if attrib[0:4] == "gpio":
                                    if attrib[4:5] == pin[0]:
                                        pinitem = attrib
                                        pinalias = item.attrib[pinitem]
                                        if pinalias != 'NC':
                                            if pindir == 'out':
                                                config = Config(os.path.normpath(currdir+'/conf/gpio_wifi.cfg'))
                                                sleeptime = Utils.gettime(config, name[0],pin[0])
                                                #print "Got pin sleeptime..."+str(sleeptime)
                                                #print pinalias,pindir,sleeptime,type(sleeptime)
                                            
                                                if int(sleeptime) > 0:
                                                
                                                    header+='''        <script language="javascript">setInterval(function() { 
$.get("/toggle", {ip : "'''+ip+'''", pin : "'''+pin[0]+'''"},
function(data) {if (data == 0) {$("#'''+name[0]+pin[0]+'''").removeClass('btn-primary').removeClass('btn-danger').addClass('btn-success');
$("#'''+name[0]+pin[0]+'''").removeAttr('disabled').removeClass('ui-state-disabled');
} else if (data == 1) {$("#'''+name[0]+pin[0]+'''").removeClass('btn-primary').removeClass('btn-success').addClass('btn-danger');
$("#'''+name[0]+pin[0]+'''").attr('disabled','disabled').addClass('ui-state-disabled');}})}, 2000);</script>\n'''
                                                
                                                    body+='<p><button id="'+name[0]+pin[0]+'" type="button" class="btn btn-lg btn-primary" disabled>'+pinalias+'<br/>('+sleeptime+'s)</button></p>\n'
                                            
                                                elif int(sleeptime) == 0:
                                                    header+='''        <script language="javascript">setInterval(function() { 
$.get("/toggle", {ip : "'''+ip+'''", pin : "'''+pin[0]+'''"},
function(data) {if (data == 0) {$("#'''+name[0]+pin[0]+'''").removeClass('btn-primary').removeClass('btn-danger').addClass('btn-success').removeAttr('disabled');
} else if (data == 1) {$("#'''+name[0]+pin[0]+'''").removeClass('btn-primary').removeClass('btn-success').addClass('btn-danger').removeAttr('disabled');}})}, 2000);</script>\n'''
        
                                                    body+='<p><button id="'+name[0]+pin[0]+'" type="button" class="btn btn-lg btn-primary" disabled>'+pinalias+'<br/>(Toggle)</button></p>\n'
                                            
                                            elif pindir == 'in':
                                                
                                                header+='''        <script language="javascript">setInterval(function() { 
$.get("/toggle", {ip : "'''+ip+'''", pin : "'''+pin[0]+'''"},
function(data) {if (data == 0) {$("#'''+name[0]+pin[0]+'''").removeClass('btn-default').removeClass('btn-danger').addClass('btn-success');
} else if (data == 1) {$("#'''+name[0]+pin[0]+'''").removeClass('btn-default').removeClass('btn-success').addClass('btn-danger');}})}, 2000);</script>\n'''
        
                                                body+='<p><button id="'+name[0]+pin[0]+'" type="button" class="btn btn-default" disabled>'+pinalias+'</button></p>\n'
                                            
                                            else:
                                                print ''''A button was found who is not broadcasting a direction.\n
                                                 Check the configuration file on the modules, restart the 
                                                 errant module and restart this software.'''
                                                
                                        
    
    document = header+'\n'+ajax+'\n'+ajaxfooter+'\n'+body+'\n'+footer
    return document