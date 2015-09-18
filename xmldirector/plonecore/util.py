# -*- coding: utf-8 -*-

################################################################
# xmldirector.plonecore
# (C) 2014,  Andreas Jung, www.zopyx.com, Tuebingen, Germany
################################################################

import sys
from subprocess import Popen, PIPE
from xmldirector.plonecore.logger import LOG


win32 = (sys.platform == 'win32')


def runcmd(cmd):
    """ Execute a command using the subprocess module """

    LOG.info(cmd)
    if win32:
        cmd = cmd.replace('\\', '/')
        s = Popen(cmd, shell=False)
        s.wait()
        return 0, ''
    else:
        stdin = open('/dev/null')
        stdout = stderr = PIPE
        p = Popen(cmd,
                  shell=True,
                  stdin=stdin,
                  stdout=stdout,
                  stderr=stderr,
                  )

        status = p.wait()
        stdout_ = p.stdout.read().strip()
        stderr_ = p.stderr.read().strip()

        if stdout_:
            LOG.info(stdout_)
        if stderr_:
            LOG.info(stderr_)
        return status, (stdout_ + stderr_).decode('utf-8')
