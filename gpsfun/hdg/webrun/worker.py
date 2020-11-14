#!/usr/bin/env python
import os

from twisted.enterprise import adbapi
from twisted.internet import task, reactor, protocol
from twisted.python import log

import settings
from registrar import WAIT, PROCESSING, FINISHED, ERROR, KILLED
from utils import queryFailed
from webrun_file import INPUT, InputFile, OutputFile

log.startLogging(open('webrun.log', 'a'))

class Job(object):
    def __init__(self, db, id, key, command, arguments):
        self.db = db
        self.id = id
        self.key = key
        self.pid = None
        self.command = command
        self.arguments = arguments.split()
        self.in_files = []
        self.out_files = []


    def start(self):
        log.msg('start command: %s with args: %s' % (self.command, self.arguments))
        change_status = """
        update jobs set status = %s, started=now() where id=%s
        """

        df = self.db.runOperation(change_status, [PROCESSING, self.id])
        df.addCallback(self.get_files)
        df.addErrback(queryFailed, request=None,
                      message="Job.start: Error to update job status: %s")

    def get_files(self,res):
        query = """
        select type,filename,path,url from files where job_id=%s

        """

        df = self.db.runQuery(query, [self.id])
        df.addCallback(self._load_files)
        #TODO: change as internal error
        df.addErrback(queryFailed, request=None,
                      message = "Job.get_files: Error to get files for job with id: '"+str(self.id)+"'. Error:%s")

    def _load_files(self, results):
        for f in results:
            if f[0] == INPUT:
                in_file = InputFile(self.db, self.id, f[1], f[2], f[3])
                in_file.download_or_copy_file()
                self.in_files.append(in_file)
                try:
                    self.arguments[self.arguments.index(f[1])] = in_file.build_work_path()
                except:
                    # TODO: do anything
                    pass
            else:
                out_file = OutputFile(self.db, self.id, f[1], f[2])
                try:
                    self.arguments[self.arguments.index(f[1])] = out_file.build_work_path()
                except:
                    # TODO: do anything
                    pass
                self.out_files.append(out_file)
        self._spawnProcess()


    def _spawnProcess(self):
        res =  reactor.spawnProcess(JobProtocol(self),
                                    self.command,
                                    args=[self.command] + self.arguments,
                                    env = os.environ)
        self.save_pid(res.pid)

    def save_pid(self, pid):
        query = """
        update jobs set worker_pid = %s where id = %s
        """

        df = self.db.runOperation(query, [pid, self.id])
        df.addErrback(queryFailed, request=None,
                      message="Error to save process` pid: %s")


    def _savePIDFailed(self, failure, pid, message):
        #TODO: kill runing process
        queryFailed(failure, request=None, message=message)


    #-----------------------------------
    # store results
    #___________________________________
    def _store_results(self, is_present, args):
        insert_results = """
        insert into results(results, error, job_id) values (%s, %s, %s)
        """
        if args['data'] or args['error_data']:
            df = self.db.runOperation(insert_results, [args['data'], args['error_data'], self.id])
            df.addCallback(self._finish, args['status'])
            df.addErrback(self._error_save_results, args,
                          message="Job._store_results: error to save results for job_id:'"+str(self.id)+"'.Error: %s")
        else:
            self._finish(None, args['status'])


    def reseived_data(self, args):
        check_results_presents = """
        delete from results where job_id = %s
        """

        df = self.db.runOperation(check_results_presents % self.id)
        df.addCallback(self._store_results, args)
        df.addErrback(self._error_save_results, args,
                      message="Job.reseived_data: error to delete results for job_id:'"+str(self.id)+"'.Error:%s")

    def _finish(self, result,status):
        change_status = """
        update jobs set status = %s,finished=now() where id=%s
        """
        df = self.db.runOperation(change_status, [status, self.id])
        df.addErrback(queryFailed, request=None,
                      message="Job._finish: error to change status of job with id:'"+str(self.id)+"'.Error: %s" )

    def _error_save_results(self, failure, args, message):
        queryFailed(failure, request=None, message=message)
        args['status'] = 'internal_error'
        args['error_data'] = message % (failure.getErrorMessage())
        self._finish(None, args['status'])

    def onFinish(self, status_object, data, error_data):
        status = FINISHED
        if status_object.value.signal:
            status = KILLED
        elif status_object.value.signal is None and status_object.value.exitCode:
            status = ERROR
        args = dict(status=status,
                    data=data,
                    error_data = error_data)

        self.reseived_data(args)

class JobProtocol(protocol.ProcessProtocol):
    def __init__(self,job):
        self.job = job
        self.data = ""
        self.error_data = ""

    def outReceived(self, data):
        self.data = self.data + data

    def errReceived(self, error_data):
        self.error_data += error_data

    def processEnded(self, status_object):
        self.job.onFinish(status_object, self.data, self.error_data)


def check_wait_job(db):
    query = """
    select id, secure_key, command, args, status from jobs where status = %s order by id
    """

    df = db.runQuery(query, [WAIT])
    df.addCallback(_run_job, db)
    df.addErrback(queryFailed, request=None,
                  message="Error check wait jobs: %s")

    check_hung(db)

def check_hung(db):
    query = """
    select worker_pid from jobs where status = %s and now() > started + interval '%s minutes'
    """

    db.runQuery(query, [PROCESSING, settings.KILL_PROCESS_AFTER]).addCallback(
        _kill_processes).addErrback(
        _queryFailed)

def _kill_processes(results):
    import os, signal
    for pid in results:
        if pid[0]:
            os.kill(int(pid[0]), signal.SIGKILL)

def _run_job(result, db):
    if result:
        job=Job(db, result[0][0], result[0][1], result[0][2], result[0][3])
        job.start()



def _queryFailed(failure):
    log.err("Error check wait jobs: %s" % (failure.getErrorMessage()))


if __name__ == '__main__':
    dbConnection = adbapi.ConnectionPool(settings.DB_DRIVER, **settings.DB_ARGS)

    l = task.LoopingCall(check_wait_job,db=dbConnection)
    l.start(settings.CHECK_JOB_PERIOD)

    reactor.run()

