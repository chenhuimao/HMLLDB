""" File: HMLifeCycle.py

An lldb Python script to print life cycle of view controller.

"""

import lldb
import HMLLDBHelpers as HM


def __lldb_init_module(debugger, internal_dict):
    debugger.HandleCommand('command script add -f HMLifeCycle.plifecycle plifecycle -h "Print life cycle of UIViewController."')


def plifecycle(debugger, command, exe_ctx, result, internal_dict):
    """
    Syntax:
        plifecycle

    Notice:
        You should use plifecycle in symbolic breakpoint(UIViewController's life cycle) for easier control.
        This command removes the system generated UIViewController class, Otherwise you can use the following command directly.

        Method A: expression -l objc -O -- [[$arg1 description] stringByAppendingString:@"  dealloc/viewDidAppear:/..."]
        Method B: expression -l objc -O -- @import UIKit; [[NSString alloc] initWithFormat:@"%@  %s", (id)$arg1, (char *)$arg2]
        Method C: Add symbolic breakpoint of "UIApplicationMain" with command "expression -l objc -O -- @import UIKit",
                  then add symbolic breakpoint(UIViewController's life cycle) with command "expression -l objc -O -- [[NSString alloc] initWithFormat:@"%@  %s", (id)$arg1, (char *)$arg2]"

    This command is implemented in HMLifeCycle.py
    """

    ignoreClasses = ["UIInputWindowController",
                     "UIAlertController",
                     "_UIAlertControllerTextFieldViewController",
                     "UICompatibilityInputViewController",
                     "UIKeyboardCandidateGridCollectionViewController",
                     "UISystemKeyboardDockController",
                     "_UIRemoteInputViewController",
                     "UIApplicationRotationFollowingController"]

    selfDescription = HM.evaluateExpressionValue("(id)$arg1").GetObjectDescription()

    ignore = False
    for className in ignoreClasses:
        if className in selfDescription:
            ignore = True
            break

    if not ignore:
        selectorDescription = HM.evaluateExpressionValue("(char *)$arg2").GetSummary()
        print(selfDescription + '  ' + selectorDescription + '\n')

