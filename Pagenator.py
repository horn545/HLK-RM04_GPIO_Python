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

def Pagenator(db):
    print "Building Web Page..."
    names = db.db.execute('select distinct name from sensor_data')

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
         <script src="http://code.jquery.com/jquery-2.0.3.min.js"></script>
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
        config = Config('gpio_wifi.cfg')
        sleeptime = Utils.gettime(config, name[0])

        config = Config('gpio_wifi.cfg')
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
                ips = db.db.execute('select distinct ip from sensor_data where name=?',(name[0],))
                for address in ips:
                    ip = address[0].strip()
                    #print "The module '"+alias+"' has an IP address of "+ip
                pinarray = db.db.execute('select distinct pin from sensor_data where name=?',(name[0],))
                for pin in pinarray:
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
                            if item.attrib.keys()[0][4:5] == pin[0]:
                                pinitem = item.attrib.keys()[0]
                                pinalias = item.attrib[pinitem]
                                if pinalias != 'NC':
                                    header+='''        <script language="javascript">setInterval(function() { 
$.get("/toggle", {ip : "'''+ip+'''", pin : "'''+pin[0]+'''"},
function(data) {if (data == 0) {$("#'''+name[0]+pin[0]+'''").removeClass('btn-primary').removeClass('btn-danger').addClass('btn-success');
$("#'''+name[0]+pin[0]+'''").removeAttr('disabled').removeClass('ui-state-disabled');
} else if (data == 1) {$("#'''+name[0]+pin[0]+'''").removeClass('btn-primary').removeClass('btn-success').addClass('btn-danger');
$("#'''+name[0]+pin[0]+'''").attr('disabled','disabled').addClass('ui-state-disabled');}})}, 2500);</script>\n'''
                                    if sleeptime > 0:
                                        body+='<p><button id="'+name[0]+pin[0]+'" type="button" class="btn btn-lg btn-primary" disabled>'+pinalias+'</br>(Timed)</button></p>\n'
                                    elif sleeptime == 0:
                                        body+='<p><button id="'+name[0]+pin[0]+'" type="button" class="btn btn-lg btn-primary" disabled>'+pinalias+'<br/>(Toggle)</button></p>\n'
                                        
    
    document = header+'\n'+ajax+'\n'+ajaxfooter+'\n'+body+'\n'+footer
    return document