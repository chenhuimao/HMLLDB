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
    load_python_scripts_dir(dir_name)


def load_python_scripts_dir(dir_name):
    ignoreFiles = {"HMLLDB.py", "HMLLDBHelpers.py"}

    for file in os.listdir(dir_name):
        if file in ignoreFiles:
            continue
        elif file.endswith('.py'):
            cmd = 'command script import '
        else:
            continue

        fullPath = dir_name + '/' + file
        lldb.debugger.HandleCommand(cmd + fullPath)
