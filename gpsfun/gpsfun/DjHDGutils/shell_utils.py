# "manage.py shell" with all autoloaded modules

import subprocess
import random
import os
import re


def is_process_running(pid):
    """ Returns True if process specified by `pid` is running """
    if not pid:
        return False
    pipe = subprocess.Popen("ps axu",
                            shell=True, bufsize=1024,
                            stdout=subprocess.PIPE).stdout
    for l in pipe.xreadlines():
        found_pid=re.split('\s+',l)[1]
        if found_pid.isdigit():
            if int(found_pid)==pid:
                return True
    return False


def get_fixed_random_port(path, port_min=1024, port_max=20000):
    """ Random fixed port meaning: for a typical directory path, the
    fixed number of specified range is returned """
    random.seed(path)
    port = random.randrange(port_min, port_max)
    return port

def get_local_server_address():
    server_address = ('127.0.0.1', 'localhost')
    if os.path.exists('/etc/hosts'):
        with open('/etc/hosts') as f:
            for line in f.readlines():
                if line.find('local.dev') != -1:
                    server_address=(re.split('\s+', line)[0], 'local.dev')
                    break
    return server_address

def read_pid(pidfile):
    """ Will read pid or return none """
    pid = None
    if os.path.exists(pidfile):
        pid = int(open(pidfile).read().strip())
    return pid


def startprocess(cmd, verboose=False):
    if verboose:
        print cmd
    p = subprocess.Popen(cmd, shell=True)
    sts = os.waitpid(p.pid, 0)[1]
    assert sts == 0, sts
    return p.pid

def killpid(pid, as_superuser=False):
    cmdline = 'kill %s' % pid
    if as_superuser:
        cmdline = 'sudo '+cmdline
    p = subprocess.Popen(cmdline, shell=True)
    sts = os.waitpid(p.pid, 0)[1]
    assert sts == 0, sts

def cmd_read(cmd):
    return subprocess.Popen(cmd, shell=True,
                            stdout=subprocess.PIPE).stdout.read()

