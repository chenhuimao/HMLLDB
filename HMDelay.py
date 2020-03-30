""" File: HMDelay.py

An lldb Python script to execute specified lldb command after delay.

"""

import lldb
import HMLLDBHelpers as HM
import shlex
import optparse
from threading import Timer


def __lldb_init_module(debugger, internal_dict):
    debugger.HandleCommand('command script add -f HMDelay.delay delay -h "Executes specified lldb command after delay."')


# Inspired by https://github.com/facebook/chisel/blob/master/commands/FBDelay.py
def delay(debugger, command, exe_ctx, result, internal_dict):
    """
    Syntax:
        delay [--continue] <second> <lldb command>

    Options:
        --continue/-c; "process continue" after executing specified lldb command

    Notice:
        If <lldb command> has options, you should enclose it in quotes.

    Examples:
        (lldb) delay 1 showfps
        (lldb) delay -c 1 showfps
        (lldb) delay 0.5 push PersonalViewController
        (lldb) delay 2 "deletefile -f path/to/fileOrDirectory"

    This command is implemented in HMDelay.py
    """

    command_args = shlex.split(command)
    parser = generate_option_parser()
    try:
        # options: optparse.Values
        # args: list
        (options, args) = parser.parse_args(command_args)
    except:
        result.SetError(parser.usage)
        return

    if len(args) < 2:
        HM.DPrint("Requires two arguments(second and lldb command), Please enter \"help delay\" for help.")
        return

    debugger.SetAsync(True)
    debugger.HandleCommand("process continue")
    seconds = float(args[0])
    specifiedCommand: str = ""
    for i, item in enumerate(args):
        if i == 0:
            continue
        specifiedCommand += item + " "
    specifiedCommand = specifiedCommand.rstrip()

    HM.DPrint("Execute lldb command after {second} seconds: {command}".format(second=seconds, command=specifiedCommand))
    t = Timer(seconds, lambda: runDelayed(specifiedCommand, options.isContinue))
    t.start()


def runDelayed(command: str, isContinue: bool) -> None:
    lldb.debugger.HandleCommand('process interrupt')
    lldb.debugger.HandleCommand(command)

    if isContinue:
        lldb.debugger.HandleCommand("process continue")


def generate_option_parser() -> optparse.OptionParser:
    command = "delay"
    usage = "usage: {arg} [--continue] <second> <lldb command>".format(arg=command)
    parser = optparse.OptionParser(usage=usage, prog=command)
    parser.add_option("-c", "--continue",
                      action="store_true",
                      default=False,
                      dest="isContinue",
                      help='"process continue" after executing specified lldb command')

    return parser
