""" File: HMLifeCycle.py

An lldb Python script to print life cycle of view controller.

"""

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

    Notice:
        You should use plifecycle in symbolic breakpoint(UIViewController's life cycle) for easier control.
        This command can ignore the system generated UIViewController class, Otherwise you may use the following command directly.

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
        selectorDescription = HM.evaluateExpressionValue("(char *)$arg2").GetSummary()
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
