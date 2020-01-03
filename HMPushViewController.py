""" File: HMPushViewController.py

An lldb Python script to push view controller.

"""

from typing import Optional, List
import lldb
import HMLLDBHelpers as HM


def __lldb_init_module(debugger, internal_dict):
    debugger.HandleCommand('command script add -f HMPushViewController.push push -h "Find navigationController in keyWindow then push a viewController."')


gModulesName = []   # List of module names that may be user-written


def push(debugger, command, exe_ctx, result, internal_dict):
    """
    Syntax:
        push <className>

    Examples:
        (lldb) push PersonalViewController

    This command is implemented in HMPushViewController.py
    """

    # HM.DPrint(type(command))  # <class 'str'>
    # HM.DPrint(type(exe_ctx))  # <class 'lldb.SBExecutionContext'>
    # HM.DPrint(type(result))  # <class 'lldb.SBCommandReturnObject'>
    # HM.DPrint(type(internal_dict))  # <class 'dict'>

    if len(command) == 0:
        HM.DPrint("Error input, plase input 'help push' for more infomation")
        return

    HM.DPrint("Waiting...")

    state = False
    makeVCExpression = "(UIViewController *)[[NSClassFromString(@\"{UIViewController}\") alloc] init]".format(UIViewController=command)
    VCObject = HM.evaluateExpressionValue(makeVCExpression).GetValue()     # address
    navigationVC = getNavigationVC()
    if navigationVC is None:
        HM.DPrint("Cannot find a UINavigationController")
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
            VCObject = HM.evaluateExpressionValue(makeVCExpression).GetValue()  # address
            if verifyObjIsKindOfClass(VCObject, "UIViewController"):
                pushExpression = "(void)[{arg1} pushViewController:(id){arg2} animated:YES]".format(arg1=navigationVC, arg2=VCObject)
                debugger.HandleCommand('expression -l objc -O -- ' + pushExpression)
                state = True
                break

    HM.DPrint("push succeed" if state else "push failed")
    if state:
        HM.processContinue()


def verifyObjIsKindOfClass(obj: str, className: str) -> bool:
    result = HM.evaluateExpressionValue("(BOOL)[(id){obj} isKindOfClass:[{objClass} class]]".format(obj=obj, objClass=className)).GetValue()
    if result == "True" or result == "true" or result == "YES":
        return True
    else:
        return False


def getNavigationVC() -> Optional[str]:
    rootViewController = HM.evaluateExpressionValue("[[[UIApplication sharedApplication] keyWindow] rootViewController]").GetValue()
    if verifyObjIsKindOfClass(rootViewController, "UINavigationController"):
        return rootViewController
    elif verifyObjIsKindOfClass(rootViewController, "UITabBarController"):
        selectedViewController = HM.evaluateExpressionValue("[(UITabBarController *){tabBarVC} selectedViewController]".format(tabBarVC=rootViewController)).GetValue()
        if verifyObjIsKindOfClass(selectedViewController, "UINavigationController"):
            return selectedViewController
        else:
            return None
    else:
        return None


# Get list of module names that may be user-written
def getModulesName() -> List[str]:
    HM.DPrint("Getting module names when using this command for the first time")
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

    # HM.DPrint(modulesName)
    return modulesName

