#!/usr/bin/env python

import sys
from os import path

SITE_ROOT = path.split( path.dirname( path.abspath(sys.argv[0]) ))[0]
sys.path.insert(0, SITE_ROOT)

from settings import *


#from twisted.protocols import http
#from subprocess import Popen, PIPE
from twisted.web import resource, server#, static
#from twisted.enterprise import adbapi, util as dbutil
#import os
#from datetime import datetime
from twisted.internet import protocol, reactor
from dev.pages import *
#import settings
#from webrun_file import InputFile, OutputFile
import httplib, urllib
import simplejson as json
from registrar import FINISHED
from utils import sign

def send_request(url, params):
    headers = {"Content-type": "application/x-www-form-urlencoded",
               "Accept": "text/plain"}
    conn = httplib.HTTPConnection("localhost:5678")
    conn.request("POST", url, urllib.urlencode(params), headers)
    response = conn.getresponse()
    data = response.read()
    conn.close()
    return data

class CheckStatus(resource.Resource):
    def render(self, request):
        params = dict(key=request.args['key'][0])
        data = send_request("/get_status",params)
        data = send_request("/get_status",params)
        print data
        res = json.loads(data,encoding='koi8-r')
        print res
        res['secure_key'] = params['key']
        
        if res['status'] == 'error':
            result_page = str('<br />'.join(res['errors']))

        elif res['status'] == FINISHED:
            result_page = command_res_page % res
        else:
            result_page = check_status_page % res

        request.write(result_page.encode('utf8'))
        return ''

class NewJob(resource.Resource):
    def render(self, request):
        params = {}
        for (name,value) in request.args.items():
            params[name]=value[0]
        params['sign'] = sign(params['command']+params['args'])

        res = send_request("/", params)
        print res
        res = json.loads(res)
        if res['status'] == 'Ok':
            print dir(res['secure_key'])
            request.write(job_add_success % dict(secure_key=str(res['secure_key'])))
        else:
            request.write(str('<br />'.join(res['errors'])))
        return ''

class HomePage(resource.Resource):
    def render(self, request):
        return form_page

class RootResource(resource.Resource):
    def __init__ (self):
        resource.Resource.__init__(self)
        self.putChild('', HomePage())
        self.putChild("add_job", NewJob())
        self.putChild('check_status', CheckStatus())

if __name__ == '__main__':
    site = server.Site(RootResource())
    # TODO: use params to set port
    reactor.listenTCP(9000, site)
    reactor.run()
