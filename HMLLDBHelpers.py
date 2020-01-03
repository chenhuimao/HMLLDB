""" File: HMLLDBHelpers.py

lldb Python script helpers.

"""

import lldb


def processContinue() -> None:
    asyncState = lldb.debugger.GetAsync()
    lldb.debugger.SetAsync(True)
    lldb.debugger.HandleCommand('process continue')
    lldb.debugger.SetAsync(asyncState)


def DPrint(obj):
    print('[HMLLDB] ', end='')
    print(obj)
    

# https://github.com/facebook/chisel/blob/master/fblldbbase.py
# evaluates expression in Objective-C++ context, so it will work even for Swift projects
def evaluateExpressionValue(expression: str) -> lldb.SBValue:
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
        DPrint(error)

    return value


# https://github.com/facebook/chisel/blob/master/fblldbbase.py
def isSuccess(error: lldb.SBError) -> bool:
    # When evaluating a `void` expression, the returned value will indicate an
    # error. This error is named: kNoResult. This error value does *not* mean
    # there was a problem. This logic follows what the builtin `expression`
    # command does. See: https://git.io/vwpjl (UserExpression.h)
    kNoResult = 0x1001
    return error.success or error.value == kNoResult


# https://github.com/facebook/chisel/blob/master/fblldbbase.py
def importModule(frame: lldb.SBFrame, module: str) -> bool:
    options = lldb.SBExpressionOptions()
    options.SetLanguage(lldb.eLanguageTypeObjC)
    value = frame.EvaluateExpression('@import ' + module, options)
    return isSuccess(value.error)


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
            (BOOL)class_addMethod(metaCls, selector, (IMP){arg2}, "{arg3}");
        }}
    '''.format(arg0=className, arg1=selector, arg2=impAddress, arg3=types)

    evaluateExpressionValue(command_script)


def addInstanceMethod(className: str, selector: str, impAddress: str, types: str) -> None:
    command_script = '''
        Class cls = (Class)objc_getClass("{arg0}");
        if (cls) {{
            SEL selector = NSSelectorFromString([[NSString alloc] initWithUTF8String:"{arg1}"]);
            (BOOL)class_addMethod(cls, selector, (IMP){arg2}, "{arg3}");
        }}
    '''.format(arg0=className, arg1=selector, arg2=impAddress, arg3=types)

    evaluateExpressionValue(command_script)
