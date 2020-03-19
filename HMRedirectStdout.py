""" File: HMRedirectStdout.py

An lldb Python script to redirect stdout/stderr.

"""

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
        (lldb) redirect both /dev/ttys000
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
        HM.DPrint("Error input, plase input 'help redirect' for more infomation")
        return

    stream = args[0]
    path = args[1]

    mode = "w+"
    if options.append:
        mode = "a+"

    if stream == "stdout" or stream == "stderr":
        redirectValue = HM.evaluateExpressionValue("freopen(\"{path}\", \"{mode}\", {stream})".format(path=path, mode=mode, stream=stream))
        logRedirectResult(redirectValue, stream)

    elif stream == "both":
        stdoutValue = HM.evaluateExpressionValue("freopen(\"{path}\", \"{mode}\", stdout)".format(path=path, mode=mode))
        logRedirectResult(stdoutValue, "stdout")
        stderrValue = HM.evaluateExpressionValue("freopen(\"{path}\", \"{mode}\", stderr)".format(path=path, mode=mode))
        logRedirectResult(stderrValue, "stderr")

    else:
        HM.DPrint("Error input, plase input 'help redirect' for more infomation")


def logRedirectResult(val: lldb.SBValue, stream: str) -> None:
    if val.GetValueAsSigned() == 0:
        HM.DPrint("redirect {stream} failed".format(stream=stream))
    else:
        HM.DPrint("redirect {stream} successful".format(stream=stream))


def generate_option_parser() -> optparse.OptionParser:
    usage = "usage: redirect [--option]"
    parser = optparse.OptionParser(usage=usage, prog="redirect")

    parser.add_option("-a", "--append",
                      action="store_true",
                      default=False,
                      dest="append",
                      help="Use \"a+\" mode instead of \"w+\" mode in freopen function")

    return parser
