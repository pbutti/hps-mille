"""Run a command"""

import os
import sys
import subprocess

def run(cmd, log = sys.stdout, **kwargs) :
    # point stderr to stdout
    kwargs['stderr'] = subprocess.STDOUT
    # pipe stdout to whatever log is passed
    kwargs['stdout'] = log

    # change default of check to True
    if 'check' not in kwargs :
        kwargs['check'] = True

    return subprocess.run(cmd, **kwargs)
