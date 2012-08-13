from sniffer.api import *
from subprocess import call
import os


# This gets invoked on every file that gets changed in the directory. Return
# True to invoke any runnable functions, False otherwise.
#
# This fires runnables only if files ending with .py extension and not prefixed
# with a period.
@file_validator
def py_files(filename):
    return filename.endswith('.py') and \
        not filename.endswith('flymake.py') and \
        not os.path.basename(filename).startswith('.')


# This gets invoked for verification. This is ideal for running tests of some sort.
# For anything you want to get constantly reloaded, do an import in the function.
#
# sys.argv[0] and any arguments passed via -x prefix will be sent to this function as
# it's arguments. The function should return logically True if the validation passed
# and logicially False if it fails.
#
# This example simply runs nose.
@runnable
def execute_tests(*args):
    return not call(['python2', 'setup.py', '-q', 'test'])
