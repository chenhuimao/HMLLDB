""" File: HMLLDBHelpers.py

lldb Python script helpers.

"""

import lldb


def processContinue():
    asyncState = lldb.debugger.GetAsync()
    lldb.debugger.SetAsync(True)
    lldb.debugger.HandleCommand('process continue')
    lldb.debugger.SetAsync(asyncState)


# https://github.com/facebook/chisel/blob/master/fblldbbase.py
# evaluates expression in Objective-C++ context, so it will work even for Swift projects
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


# https://github.com/facebook/chisel/blob/master/fblldbbase.py
def isSuccess(error):
    # When evaluating a `void` expression, the returned value will indicate an
    # error. This error is named: kNoResult. This error value does *not* mean
    # there was a problem. This logic follows what the builtin `expression`
    # command does. See: https://git.io/vwpjl (UserExpression.h)
    kNoResult = 0x1001
    return error.success or error.value == kNoResult


# https://github.com/facebook/chisel/blob/master/fblldbbase.py
def importModule(frame, module):
    options = lldb.SBExpressionOptions()
    options.SetLanguage(lldb.eLanguageTypeObjC)
    value = frame.EvaluateExpression('@import ' + module, options)
    return isSuccess(value.error)
