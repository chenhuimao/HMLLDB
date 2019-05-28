""" File: HMPushViewController.py

An lldb Python script to push view controller.

"""

import lldb


def __lldb_init_module(debugger, internal_dict):
    debugger.HandleCommand('command script add -f HMPushViewController.push push -h "Find navigationController in keyWindow then push a viewController."')


gModulesName = []   # List of module names that may be user-written


def push(debugger, command, result, internal_dict):
    """
    Syntax:
        push <className>

    Examples:
        (lldb) push PersonalViewController

    This command is implemented in HMPushViewController.py
    """

    # print (command) # <type 'str'>
    # print (result)  # <class 'lldb.SBCommandReturnObject'>
    # print (internal_dict) # <type 'dict'>

    print ("Waiting...")

    state = False
    makeVCExpression = "(UIViewController *)[[NSClassFromString(@\"{UIViewController}\") alloc] init]".format(UIViewController=command)
    VCObject = evaluateExpressionValue(makeVCExpression).GetValue()     # address
    navigationVC = getNavigationVC()
    if navigationVC is None:
        print("Cannot find a UINavigationController")
        return

    if verifyObjIsKindOfClass(VCObject, "UIViewController"):
        pushExpression = "(void)[{arg1} pushViewController:(id){arg2} animated:YES]".format(arg1=navigationVC, arg2=VCObject)
        debugger.HandleCommand('expression -l objc -O -- ' + pushExpression)
        state = True
    else:
        global gModulesName
        if len(gModulesName) == 0:
            gModulesName = getModulesName()
        for modlue in gModulesName:  # for Swift file
            makeVCExpression = "(UIViewController *)[[NSClassFromString(@\"{prefix}.{UIViewController}\") alloc] init]".format(prefix=modlue, UIViewController=command)
            VCObject = evaluateExpressionValue(makeVCExpression).GetValue()  # address
            if verifyObjIsKindOfClass(VCObject, "UIViewController"):
                pushExpression = "(void)[{arg1} pushViewController:(id){arg2} animated:YES]".format(arg1=navigationVC, arg2=VCObject)
                debugger.HandleCommand('expression -l objc -O -- ' + pushExpression)
                state = True
                break

    print ("push succeed" if state else "push failed")
    if state:
        processContinue()


def verifyObjIsKindOfClass(obj, className):
    result = evaluateExpressionValue("(BOOL)[(id){obj} isKindOfClass:[{objClass} class]]".format(obj=obj, objClass=className)).GetValue()
    if result == "True" or result == "true" or result == "YES":
        return True
    else:
        return False


def getNavigationVC():
    rootViewController = evaluateExpressionValue("[[[UIApplication sharedApplication] keyWindow] rootViewController]").GetValue()
    if verifyObjIsKindOfClass(rootViewController, "UINavigationController"):
        return rootViewController
    elif verifyObjIsKindOfClass(rootViewController, "UITabBarController"):
        selectedViewController = evaluateExpressionValue("[(UITabBarController *){tabBarVC} selectedViewController]".format(tabBarVC=rootViewController)).GetValue()
        if verifyObjIsKindOfClass(selectedViewController, "UINavigationController"):
            return selectedViewController
        else:
            return None
    else:
        return None


# Get list of module names that may be user-written
def getModulesName():
    print ("Getting module names when using this command for the first time")
    numOfModules = lldb.debugger.GetSelectedTarget().GetNumModules()
    modulesName = []
    for i in range(numOfModules):
        module = lldb.debugger.GetSelectedTarget().GetModuleAtIndex(i)
        fileSpec = module.GetFileSpec()
        directory = fileSpec.GetDirectory()
        filename = fileSpec.GetFilename()
        if directory is None or filename is None:
            continue

        if '.app' in directory and '.' not in filename:  # Filter out modules that may be user-written
            modulesName.append(filename)

    # print (modulesName)
    return modulesName


def processContinue():
    asyncState = lldb.debugger.GetAsync()
    lldb.debugger.SetAsync(True)
    lldb.debugger.HandleCommand('process continue')
    lldb.debugger.SetAsync(asyncState)


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

