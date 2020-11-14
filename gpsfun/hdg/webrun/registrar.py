#!/usr/bin/env python

#from twisted.protocols import http
from twisted.enterprise import adbapi
from twisted.internet import reactor
from twisted.web import resource, server

import settings
import simplejson as json
from utils import queryFailed, make_random_job_key, check_correct_sign
from webrun_file import InputFile


# TODO: moved to worker
WAIT='wait'
PROCESSING = 'processing'
FINISHED = 'finished'
ERROR = 'error'
KILLED = 'killed'

class CheckStatus(resource.Resource):
    def __init__(self, db):
        self.db = db

    def render(self, request):
        query = """
        select command, args, status,results,error from jobs LEFT OUTER JOIN results ON (jobs.id = job_id) where secure_key = '%s'
        """
        key = request.args.get('key', [None])[0]
        if not key:
            request.write(json.dumps({'status':'error',
                                      'errors':["key not found in request"]}))
            return ""

        df = self.db.runQuery(query % key)
        df.addCallback(self._got_status, request, key)
        df.addErrback(queryFailed, request,
                      message = "CheckStatus.render:Error getting status of job with key: '"+key+"'. %s")

        return server.NOT_DONE_YET

    def _got_status(self, results, request,secure_key):
        for command, args, status,results,error in results:
            request.write(json.dumps({'status':status,
                                      'command':command,
                                      'args':args,
                                      'results':results,
                                      'errors':[error]},encoding='koi8-r'))
        request.finish()

class NewJob(resource.Resource):
    def __init__(self, db):
        self.db = db

    def is_validate(self, params):
        if not params['command']:
            params['errors'].append("command not found")

        if not params['args']:
            params['errors'].append("arguments not found")

        for f in params['in_files']:
            if params['args'] and f.filename not in params['args']:
                params['errors'].append('File with name "%s" not found in comand`s arguments ' % f.filename)
            if f.path is None and f.url is None:
                params['errors'].append('You must set file`s path or url')

        if not params['errors']:
            return True
        return False

    def parseArgs(self, request):
        params = {'command': None,
                  'args': None,
                  'in_files': [],
                  'errors': []
            }
        if request.args.has_key('in_filename') and request.args['in_filename'][0]:
            # TODO: many files
            params['in_files'].append(InputFile(self.db, None, request.args['in_filename'][0],
                                              request.args.get('in_file_path', [''])[0] or None,
                                              request.args.get('in_file_url', [''])[0] or None
                                              )
                                    )

        params['command'] = request.args.get('command', [''])[0] or None
        params['args'] = request.args.get('args', [''])[0] or None
        assert check_correct_sign(params['command']+params['args'], request.args['sign'][0])

        return params


    def _get_job_id(self, results, request, params):
        query = """
        select id from jobs where secure_key = %s
        """

        df = self.db.runQuery(query, [params['secure_key']])
        df.addCallback(self._save_files, request, params)
        df.addErrback(queryFailed, request,
                      message = "NewJob._get_job_id:Error getting job id for key: "+params['secure_key']+". %s")

        return server.NOT_DONE_YET

    def _save_files(self,results, request, params):
        for in_file in params['in_files']:
            in_file.job_id = results[0][0]
            in_file.store_file_info()

        return self._on_create_success(request, params)

    def register_job(self, request, params):
        query = """
        insert into jobs(command, args, secure_key, added, status)
          values (%s, %s, %s, now(), %s)
        """
        params['secure_key'] = make_random_job_key()

        df = self.db.runOperation(query, [params['command'],
                                          params['args'],
                                          params['secure_key'],
                                          WAIT])
        df.addCallback(self._get_job_id, request, params)
        df.addErrback(queryFailed, request,
                      message="NewJob.register_job: Error add new job: %s")
        return server.NOT_DONE_YET


    def render(self, request):
        params = self.parseArgs(request)
        if self.is_validate(params):
            return self.register_job(request, params)
        else:
            request.write(json.dumps({'status':'error','errors':params['errors']}))
            return ""

    def _on_create_success(self, request, params):
        request.write(json.dumps({'status':'Ok','secure_key':params['secure_key']}))
        request.finish()

class RootResource(resource.Resource):
    def __init__ (self, dbConnection):
        resource.Resource.__init__(self)
        self.putChild("", NewJob(dbConnection))
        self.putChild('get_status', CheckStatus(dbConnection))


if __name__ == '__main__':
    dbConnection = adbapi.ConnectionPool(settings.DB_DRIVER, **settings.DB_ARGS)

    site = server.Site(RootResource(dbConnection))
    reactor.listenTCP(settings.LISTEN_TCP_PORT, site)
    reactor.run()
