""" File: HMLLDB.py

An lldb Python script to initialize LLDBCommands.

Add to ~/.lldbinit:
    command script import ~/path/to/HMLLDB.py

"""

import lldb
import os


def __lldb_init_module(debugger, internal_dict):
    file_path = os.path.realpath(__file__)  # Absolute path
    dir_name = os.path.dirname(file_path)
    loadPythonScriptsDir(dir_name)


def loadPythonScriptsDir(dir_name: str) -> None:
    ignoreFiles = {"HMLLDB.py"}
    
    for file in os.listdir(dir_name):
        fullPath = dir_name + '/' + file

        if file in ignoreFiles:
            continue
        elif file.endswith('.py'):
            cmd = 'command script import '
        elif file.endswith('.h'):
            cmd = 'command source -e0 -s1 '
        elif os.path.isdir(fullPath):
            loadPythonScriptsDir(fullPath)
            continue
        else:
            continue

        lldb.debugger.HandleCommand(cmd + fullPath)
