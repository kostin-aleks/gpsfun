import re
import os

def save_file_from_formfield(filepath, requestfile):
    destination = open(filepath, 'wb+')
    for chunk in requestfile.chunks():
        destination.write(chunk)
    destination.close()

def last_file_in_dir(d, mask_regexp=''):
    savedir = os.getcwd()
    os.chdir(d)
    l = [(os.path.getmtime(x), x) for x in os.listdir(".") \
         if re.match(re.compile(mask_regexp), x)]
    l.sort()
    os.chdir(savedir)
    if l:
        return l[-1][1]
