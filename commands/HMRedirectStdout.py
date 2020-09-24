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

import lldb
import HMLLDBHelpers as HM
import optparse
import shlex


def __lldb_init_module(debugger, internal_dict):
    debugger.HandleCommand('command script add -f HMRedirectStdout.redirect redirect -h "Redirect stdout/stderr."')


def redirect(debugger, command, exe_ctx, result, internal_dict):
    """
    Syntax:
        redirect [--append] <stdout/stderr/both> <path>

    Options:
        --append/-a; Use "a+" mode instead of "w+" mode in freopen function

    Examples:
        (lldb) redirect both /dev/ttys000  (Simulator)
        (lldb) redirect stdout /path/to/file
        (lldb) redirect -a stderr /path/to/file

    This command is implemented in HMRedirectStdout.py
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

    argsLen = len(args)
    if argsLen != 2:
        HM.DPrint("Error input, plase enter 'help redirect' for more infomation")
        return

    stream = args[0]
    path = args[1]

    mode = "w+"
    if options.append:
        mode = "a+"

    if stream == "stdout" or stream == "stderr":
        redirectValue = HM.evaluateExpressionValue(f"freopen(\"{path}\", \"{mode}\", {stream})")
        logRedirectResult(redirectValue, stream)

    elif stream == "both":
        stdoutValue = HM.evaluateExpressionValue(f"freopen(\"{path}\", \"{mode}\", stdout)")
        logRedirectResult(stdoutValue, "stdout")
        stderrValue = HM.evaluateExpressionValue(f"freopen(\"{path}\", \"{mode}\", stderr)")
        logRedirectResult(stderrValue, "stderr")

    else:
        HM.DPrint(f"Error input(\"{stream}\"), plase enter \"help redirect\" for more infomation")


def logRedirectResult(val: lldb.SBValue, stream: str) -> None:
    if val.GetValueAsSigned() == 0:
        HM.DPrint(f"redirect {stream} failed")
    else:
        HM.DPrint(f"redirect {stream} successful")


def generate_option_parser() -> optparse.OptionParser:
    usage = "usage: redirect [--append] <stdout/stderr/both> <path>"
    parser = optparse.OptionParser(usage=usage, prog="redirect")

    parser.add_option("-a", "--append",
                      action="store_true",
                      default=False,
                      dest="append",
                      help="Use \"a+\" mode instead of \"w+\" mode in freopen function")

    return parser
