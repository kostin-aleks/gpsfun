"""
debug
"""
import gc
from collections import defaultdict
import datetime
import os
import subprocess


rcount = 0


def reflect():
    """ reflect """
    global rcount
    counts = defaultdict(int)
    for obj in gc.get_objects():
        counts[type(obj).__name__] += 1
    timestrnow = datetime.datetime.now().strftime('%Y%m%d-%H:%m.%S')
    if not os.path.exists('dump'):
        os.mkdir('dump')
    f = open(f'dump/dump_{timestrnow}.dump-{rcount}', 'w+')
    for item in counts:
        f.write(f"{counts[item]} {item}\n")
    f.close()
    rcount += 1


def display_html(text):
    """ Create temp file and display text in firefox """
    debug_html = os.tmpnam() + '.html'
    open(debug_html, "w").write(text)
    if os.getenv('DISPLAY'):
        subprocess.call(f"browser.py {debug_html}", shell=True)
    else:
        print(f'Debug output saved as: {debug_html}')
