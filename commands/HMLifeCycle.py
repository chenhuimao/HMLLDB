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
    debugger.HandleCommand('command script add -f HMLifeCycle.plifecycle plifecycle -h "Print life cycle of UIViewController."')


def plifecycle(debugger, command, exe_ctx, result, internal_dict):
    """
    Syntax:
        plifecycle [-i/--ignore_system_classes]

    Options:
        --ignore_system_classes/-i; Ignore the system generated UIViewController classes

    Notice:
        You should use plifecycle in symbolic breakpoint(UIViewController's life cycle) for easier control.
        This command can ignore the system generated UIViewController classes, Otherwise you may use the following command directly.

        Method A: expression -l objc -O -- [[$arg1 description] stringByAppendingString:@"  dealloc/viewDidAppear:/..."]
        Method B: expression -l objc -O -- @import UIKit; [[NSString alloc] initWithFormat:@"%@  %s", (id)$arg1, (char *)$arg2]
        Method C: Add symbolic breakpoint of "UIApplicationMain" with command "expression -l objc -O -- @import UIKit",
                  then add symbolic breakpoint(UIViewController's life cycle) with command "expression -l objc -O -- [[NSString alloc] initWithFormat:@"%@  %s", (id)$arg1, (char *)$arg2]"

    This command is implemented in HMLifeCycle.py
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

    selfDescription = HM.evaluateExpressionValue("(id)$arg1").GetObjectDescription()

    ignore = False
    if options.ignore_system_classes:
        ignoreClasses = ["UIAlertController",
                         "_UIAlertControllerTextFieldViewController",
                         "UIInputWindowController",
                         "UICompatibilityInputViewController",
                         "UIKeyboardCandidateGridCollectionViewController",
                         "UISystemKeyboardDockController",
                         "_UIRemoteInputViewController",
                         "UIApplicationRotationFollowingController",
                         "UISystemInputAssistantViewController",
                         "UIPredictionViewController",
                         "UICandidateViewController",
                         "_SFAppPasswordSavingViewController",
                         "SFPasswordSavingRemoteViewController"]

        for className in ignoreClasses:
            if className in selfDescription:
                ignore = True
                break

    if not ignore:
        selectorDescription = HM.evaluateExpressionValue("(char *)$arg2").GetSummary().strip('"')
        HM.DPrint(selfDescription + '  ' + selectorDescription + '\n')


def generate_option_parser() -> optparse.OptionParser:
    usage = "usage: plifecycle [-i/--ignore_system_classes]"
    parser = optparse.OptionParser(usage=usage, prog="plifecycle")

    parser.add_option("-i", "--ignore_system_classes",
                      action="store_true",
                      default=False,
                      dest="ignore_system_classes",
                      help="Ignore system classes")

    return parser
