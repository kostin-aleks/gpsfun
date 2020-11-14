import time
import hashlib
import os.path
import errno

from django.conf import settings
from django.core.files import locks
from django.core.files.move import file_move_safe
from django.core.files.storage import FileSystemStorage
from hdg.djangoapps.MD5Storage.models import Refcount

def file_md5sum(file_obj):
    file_obj.seek(0)
    md5 = hashlib.md5()
    md5.update(file_obj.read())
    file_obj.seek(0)
    return md5.hexdigest()


def filename_constructor(name, md5sum, size):
    ext = os.path.splitext(name)[1]
    path = os.path.split(name)[0]
    dir0 = md5sum[:2]
    dir1 = md5sum[2]
    newname = "%s/%s/%s/%s_%d%s" % (path,
                                    dir0,
                                    dir1,
                                    md5sum, size, ext)
    return newname


class MD5Storage(FileSystemStorage):
    def get_available_name(self, name):
        return name

    def save(self, name, fileobject):
        md5sum = file_md5sum(fileobject)
        newname = filename_constructor(name, md5sum, fileobject.size)
        refcount, created = Refcount.objects.get_or_create(md5=md5sum, size=fileobject.size)
        refcount.refs += 1
        refcount.save()
        return super(MD5Storage, self).save(newname, fileobject)

    def size(self, name):
        if os.path.exists(self.path(name)):
            return os.path.getsize(self.path(name))
        return 0 # FIXME!?!

    def _save(self, name, content):
        full_path = self.path(name)

        directory = os.path.dirname(full_path)
        if not os.path.exists(directory):
            os.makedirs(directory)
        elif not os.path.isdir(directory):
            raise IOError("%s exists and is not a directory." % directory)

        try:
            # This file has a file path that we can move.
            if hasattr(content, 'temporary_file_path'):
                file_move_safe(content.temporary_file_path(), full_path)
                content.close()

            # This is a normal uploadedfile that we can stream.
            else:
                # This fun binary flag incantation makes os.open throw an
                # OSError if the file already exists before we open it.
                fd = os.open(full_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, 'O_BINARY', 0))
                try:
                    locks.lock(fd, locks.LOCK_EX)
                    for chunk in content.chunks():
                        os.write(fd, chunk)
                finally:
                    locks.unlock(fd)
                    os.close(fd)
        except OSError, e:
            if e.errno == errno.EEXIST:
                return name
            else:
                raise

        if settings.FILE_UPLOAD_PERMISSIONS is not None:
            os.chmod(full_path, settings.FILE_UPLOAD_PERMISSIONS)

        return name
