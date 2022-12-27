# The MIT License (MIT)
#
# Copyright (c) 2020 Huimao Chen
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# https://github.com/chenhuimao/HMLLDB

import lldb
import HMLLDBHelpers as HM
import shlex
import optparse
from threading import Timer


def __lldb_init_module(debugger, internal_dict):
    debugger.HandleCommand('command script add -f HMDelay.delay delay -h "(deprecated)Executes specified lldb command after delay."')


# Inspired by https://github.com/facebook/chisel/blob/main/commands/FBDelay.py
def delay(debugger, command, exe_ctx, result, internal_dict):
    """
    Syntax:
        delay [--continue] <second> <lldb command>

    Options:
        --continue/-c; "process continue" after executing specified lldb command

    Notice:
        If <lldb command> has options, you should enclose it in quotes.

    Examples:
        (lldb) delay 3 showhud
        (lldb) delay -c 2 phomedirectory
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

    secondString = args[0]
    if not isNumber(secondString):
        HM.DPrint(f"\"{secondString}\" cannot be converted to seconds, Please enter \"help delay\" for help.")
        return

    debugger.SetAsync(True)
    debugger.HandleCommand("process continue")
    seconds = float(secondString)
    specifiedCommand: str = ""
    for i, item in enumerate(args):
        if i == 0:
            continue
        specifiedCommand += item + " "
    specifiedCommand = specifiedCommand.rstrip()

    HM.DPrint(f"Execute lldb command after {seconds} seconds: {specifiedCommand}")
    t = Timer(seconds, lambda: runDelayed(specifiedCommand, options.isContinue))
    t.start()


def runDelayed(command: str, isContinue: bool) -> None:
    lldb.debugger.HandleCommand('process interrupt')
    lldb.debugger.HandleCommand(command)

    if isContinue:
        lldb.debugger.HandleCommand("process continue")


def isNumber(s: str) -> bool:
    try:
        float(s)
        return True
    except ValueError:
        return False


def generate_option_parser() -> optparse.OptionParser:
    command = "delay"
    usage = f"usage: {command} [--continue] <second> <lldb command>"
    parser = optparse.OptionParser(usage=usage, prog=command)
    parser.add_option("-c", "--continue",
                      action="store_true",
                      default=False,
                      dest="isContinue",
                      help='"process continue" after executing specified lldb command')

    return parser
