import gc
from collections import defaultdict
import datetime
import os
import subprocess

rcount = 0
def reflect():
    global rcount
    counts = defaultdict(int)
    for obj in gc.get_objects():
        counts[type(obj).__name__] += 1
    timestrnow=datetime.datetime.now().strftime('%Y%m%d-%H:%m.%S')
    if not os.path.exists('dump'):
        os.mkdir('dump')
    f = open('dump/dump_%s.dump-%d' % (timestrnow, rcount), 'w+')
    for item in counts:
        f.write("%s %s\n" % (counts[item], item))
    f.close()
    rcount += 1

def display_html(text):
    """ Create temp file and display text in firefox """
    debug_html = os.tmpnam()+'.html'
    open(debug_html, "w").write(text)
    if os.getenv('DISPLAY'):
        subprocess.call("browser.py %s" % debug_html, shell=True)
    else:
        print 'Debug output saved as: %s' % debug_html

