""" File: HMLifeCycle.py

An lldb Python script to print life cycle of view controller.

"""

import lldb


def __lldb_init_module(debugger, internal_dict):
    debugger.HandleCommand('command script add -f HMLifeCycle.plifecycle plifecycle -h "Print life cycle of UIViewController."')


def plifecycle(debugger, command, result, internal_dict):
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
                     "UIApplicationRotationFollowingController"]

    selfDescription = evaluateExpressionValue("(id)$arg1").GetObjectDescription()

    ignore = False
    for className in ignoreClasses:
        if className in selfDescription:
            ignore = True
            break

    if not ignore:
        selectorDescription = evaluateExpressionValue("(char *)$arg2").GetSummary()
        print (selfDescription + '  ' + selectorDescription + '\n')


# evaluates expression in Objective-C++ context, so it will work even for
# Swift projects
def evaluateExpressionValue(expression):
    frame = lldb.debugger.GetSelectedTarget().GetProcess().GetSelectedThread().GetSelectedFrame()
    options = lldb.SBExpressionOptions()
    options.SetLanguage(lldb.eLanguageTypeObjC_plus_plus)

    # Allow evaluation that contains a @throw/@catch.
    #   By default, ObjC @throw will cause evaluation to be aborted. At the time
    #   of a @throw, it's not known if the exception will be handled by a @catch.
    #   An exception that's caught, should not cause evaluation to fail.
    options.SetTrapExceptions(False)

    # Give evaluation more time.
    options.SetTimeoutInMicroSeconds(5000000)  # 5s

    # Most commands are not multithreaded.
    options.SetTryAllThreads(False)

    value = frame.EvaluateExpression(expression, options)
    error = value.GetError()

    # Retry if the error could be resolved by first importing UIKit.
    if error.type == lldb.eErrorTypeExpression and error.value == lldb.eExpressionParseError and importModule(frame, 'UIKit'):
        value = frame.EvaluateExpression(expression, options)
        error = value.GetError()

    if not isSuccess(error):
        print(error)

    return value


def isSuccess(error):
    # When evaluating a `void` expression, the returned value will indicate an
    # error. This error is named: kNoResult. This error value does *not* mean
    # there was a problem. This logic follows what the builtin `expression`
    # command does. See: https://git.io/vwpjl (UserExpression.h)
    kNoResult = 0x1001
    return error.success or error.value == kNoResult


def importModule(frame, module):
    options = lldb.SBExpressionOptions()
    options.SetLanguage(lldb.eLanguageTypeObjC)
    value = frame.EvaluateExpression('@import ' + module, options)
    return isSuccess(value.error)

