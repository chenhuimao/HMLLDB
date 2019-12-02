""" File: HMFileCommands.py

An lldb Python script about file.

"""

import lldb
import HMLLDBHelpers as HM
import os
import shlex
import optparse


def __lldb_init_module(debugger, internal_dict):
    debugger.HandleCommand('command script add -f HMFileCommands.pHomeDirectory phomedirectory -h "Print the path of the home directory."')
    debugger.HandleCommand('command script add -f HMFileCommands.pBundlePath pbundlepath -h "Print the path of the main bundle."')



def pHomeDirectory(debugger, command, exe_ctx, result, internal_dict):
    """
    Syntax:
        phomedirectory [--open]

    Options:
      --open/-o ; open in Finder

    Examples:
        (lldb) phomedirectory --open

    This command is implemented in HMFileCommands.py
    """

    command_args = shlex.split(command)
    parser = generate_option_parser("phomedirectory")
    try:
        # options: optparse.Values
        # args: list
        (options, args) = parser.parse_args(command_args)
    except:
        result.SetError(parser.usage)
        return

    homeDirectoryValue = HM.evaluateExpressionValue('(NSString *)NSHomeDirectory()')
    path = homeDirectoryValue.GetObjectDescription()
    print(path)
    if options.open:
        os.system('open ' + path)


def pBundlePath(debugger, command, exe_ctx, result, internal_dict):
    """
    Syntax:
        pbundlepath [--open]

    Options:
      --open/-o ; open in Finder

    Examples:
        (lldb) pbundlepath --open

    This command is implemented in HMFileCommands.py
    """

    command_args = shlex.split(command)
    parser = generate_option_parser("pbundlepath")
    try:
        # options: optparse.Values
        # args: list
        (options, args) = parser.parse_args(command_args)
    except:
        result.SetError(parser.usage)
        return

    bundlePathValue = HM.evaluateExpressionValue('(NSString*)[[NSBundle mainBundle] bundlePath]')
    path = bundlePathValue.GetObjectDescription()
    print(path)
    if options.open:
        # Cannot open the bundle, so we open the directory where the bundle is located.
        directoryValue = HM.evaluateExpressionValue('(NSString *)[(NSString *){path} stringByDeletingLastPathComponent]'.format(path=bundlePathValue.GetValue()))
        os.system('open ' + directoryValue.GetObjectDescription())


def generate_option_parser(command: str) -> optparse.OptionParser:
    usage = "usage: {arg} [--open]".format(arg=command)
    parser = optparse.OptionParser(usage=usage, prog=command)
    parser.add_option("-o", "--open",
                      action="store_true",
                      default=False,
                      dest="open",
                      help="Opens the path in Finder")

    return parser

