""" File: HMLLDBHelpers.py

lldb Python script helpers.

"""

import lldb
from typing import Any


gIsFirstCall = True


def processContinue() -> None:
    asyncState = lldb.debugger.GetAsync()
    lldb.debugger.SetAsync(True)
    lldb.debugger.HandleCommand('process continue')
    lldb.debugger.SetAsync(asyncState)


def DPrint(obj: Any) -> None:
    print('[HMLLDB] ', end='')
    print(obj)
    

# Based on https://github.com/facebook/chisel/blob/master/fblldbbase.py
def evaluateExpressionValue(expression: str) -> lldb.SBValue:
    frame = lldb.debugger.GetSelectedTarget().GetProcess().GetSelectedThread().GetSelectedFrame()

    global gIsFirstCall
    if gIsFirstCall:
        gIsFirstCall = False
        op = lldb.SBExpressionOptions()
        op.SetLanguage(lldb.eLanguageTypeObjC_plus_plus)
        frame.EvaluateExpression('''
            @import Foundation;
            @import UIKit;
            @import ObjectiveC;
        ''', op)


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

    options.SetSuppressPersistentResult(True)

    value = frame.EvaluateExpression(expression, options)
    error = value.GetError()

    kNoResult = 0x1001  # 4097
    isSuccess = error.success or error.value == kNoResult
    if not isSuccess:
        DPrint(error)

    return value


def judgeSBValueHasValue(val: lldb.SBValue) -> bool:
    if val.GetValue() is None or val.GetValueAsSigned() == 0:
        return False
    return True


def boolOfSBValue(val: lldb.SBValue) -> bool:
    result = val.GetValue()
    if result == "True" or result == "true" or result == "YES":
        return True
    return False


def addOneShotBreakPointInIMP(imp: lldb.SBValue, callbackFunc: str, name: str) -> None:
    target = lldb.debugger.GetSelectedTarget()
    bp = target.BreakpointCreateByAddress(imp.GetValueAsUnsigned())
    bp.AddName(name)
    bp.SetOneShot(True)
    bp.SetScriptCallbackFunction(callbackFunc)


def existClass(className: str) -> bool:
    command_script = '''
        Class cls = (Class)objc_getClass("{arg}");
        BOOL exist = NO;
        if (cls) {{
            exist = YES;
        }}
        exist;
    '''.format(arg=className)

    result = evaluateExpressionValue(command_script).GetValue()
    if result == "True" or result == "true" or result == "YES":
        return True
    else:
        return False


def allocateClass(className: str, superClassName: str) -> lldb.SBValue:
    command_script = '''
        Class newCls = (Class)objc_getClass("{arg0}");
        if (!newCls) {{
            Class superCls = (Class)objc_getClass("{arg1}");
            newCls = (Class)objc_allocateClassPair(superCls, "{arg0}", 0);
        }}
        newCls;
    '''.format(arg0=className, arg1=superClassName)

    return evaluateExpressionValue(command_script)


def registerClass(classAddress: str) -> None:
    command_script = "(void)objc_registerClassPair(Class({arg}))".format(arg=classAddress)
    evaluateExpressionValue(command_script)


def addIvar(classAddress: str, ivarName: str, types: str) -> bool:
    command_script = '''
        const char * types = @encode({arg2});
        NSUInteger size;
        NSUInteger alingment;
        NSGetSizeAndAlignment(types, &size, &alingment);
        (BOOL)class_addIvar((Class){arg0}, "{arg1}", size, alingment, types);
    '''.format(arg0=classAddress, arg1=ivarName, arg2=types)

    return evaluateExpressionValue(command_script).GetValue()


def addClassMethod(className: str, selector: str, impAddress: str, types: str) -> None:
    command_script = '''
        Class metaCls = (Class)objc_getMetaClass("{arg0}");
        if (metaCls) {{
            SEL selector = NSSelectorFromString([[NSString alloc] initWithUTF8String:"{arg1}"]);
            (BOOL)class_addMethod(metaCls, selector, (void (*)()){arg2}, "{arg3}");
        }}
    '''.format(arg0=className, arg1=selector, arg2=impAddress, arg3=types)

    evaluateExpressionValue(command_script)


def addInstanceMethod(className: str, selector: str, impAddress: str, types: str) -> None:
    command_script = '''
        Class cls = (Class)objc_getClass("{arg0}");
        if (cls) {{
            SEL selector = NSSelectorFromString([[NSString alloc] initWithUTF8String:"{arg1}"]);
            (BOOL)class_addMethod(cls, selector, (void (*)()){arg2}, "{arg3}");
        }}
    '''.format(arg0=className, arg1=selector, arg2=impAddress, arg3=types)

    evaluateExpressionValue(command_script)
