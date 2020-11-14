import os
import shutil

#files type
INPUT = 'input'
OUTPUT = 'output'

class File(object):
    def __init__(self, db, job_id, type, filename, path=None, url=None):
        self.type = type
        print 'init'
        # TODO: delete db param
        self.db = db
        self.job_id = job_id
        self.filename = filename
        self.url = url
        self.path = path 


    def build_work_path(self):
        #replace filename on random name
        # replace absolute path on settigns path
        return '/home/stclaus/dev/webrun/files/'+self.filename

    def delete_exists_file(self):
        print 'delete_exists_file'
        query = """
        delete from files where job_id = %s and type=%s and filename=%s
        """
        self.db.runOperation(query, [self.job_id, self.type, self.filename]).addCallback(
            self._save_file_info).addErrback(
            self._saveFailed)

    def _save_file_info(self,res):
        print '_save_file_info'
        query = """
        insert into files(job_id, type, filename, url, path)
        values(%s, %s, %s, %s, %s)
        """

        self.db.runOperation(query, [self.job_id, self.type, self.filename, self.url, self.path]).addErrback(
            self._saveFailed)


    def store_file_info(self):
        self.delete_exists_file()

    def check_access(self, path):
        return os.path.exists(self.path)

    def _copy(self, src, dst):
        if self.check_access(src):
            print 'copy'
            shutil.copy(src, dst)
        else:
            # TODO raise exception
            pass
        
    def _saveFailed(self, failure):
        print "Error save file info: %s" % (failure.getErrorMessage())

    def __str__(self):
        return '<%s:%s:%s>' % (self.filename, self.path, self.url)

    def __unicode__(self):
        return 'unicode'

class InputFile(File):
    def __init__(self, db, job_id, filename, path=None, url=None):
        if url is None and path is None:
            # TODO: raise exception
            pass
        super(InputFile, self).__init__(db, job_id, INPUT, filename, path, url)

    def download_or_copy_file(self):
        # check is_file and is_read
        if self.path:
            self._copy(self.path, self.build_work_path())
        elif self.url:
            print 'download'
            import urllib2
            f = urllib2.urlopen(self.url)
            open(self.build_work_path(), 'wb').write(f.read())

class OutputFile(File):
    def __init__(self, db, job_id, filename, path=None):
        super(OutputFile, self).__init__(db, job_id, OUTPUT, filename, path)

    def download_or_copy_file(self):
        # check is_file and is_read
        if self.path:
            self._copy(self.build_work_path(), self.path)

    
