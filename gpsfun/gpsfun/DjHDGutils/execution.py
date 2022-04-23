"""
execution
"""
from subprocess import Popen


def shellcmd(cmd):
    """ shell command """
    try:
        p = Popen(cmd, shell=True)
        sts = os.waitpid(p.pid, 0)
    except OSError as e:
        print(sys.stderr, f"Execution of command [cmd] failed:", e)
