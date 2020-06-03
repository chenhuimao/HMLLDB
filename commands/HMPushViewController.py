""" File: HMPushViewController.py

An lldb Python script to push view controller.

"""

from typing import Optional, List
import lldb
import HMLLDBHelpers as HM
import optparse
import shlex


def __lldb_init_module(debugger, internal_dict):
    debugger.HandleCommand('command script add -f HMPushViewController.push push -h "Find navigationController in keyWindow then push a viewController."')


gModulesName: List[str] = []   # List of module names that may be user-written


def push(debugger, command, exe_ctx, result, internal_dict):
    """
    Syntax:
        push <className>
        push [--instance] <classInstance>

    Options:
        --instance/-i; Push the UIViewController instance.

    Examples:
        (lldb) push PersonalViewController
        (lldb) push -i [[PersonalViewController alloc] init]

        (lldb) expression -l objc -O -- [PersonalViewController new] (<PersonalViewController: 0x7fed30c5a070>)
        (lldb) push -i 0x7fed30c5a070


    This command is implemented in HMPushViewController.py
    """

    # HM.DPrint(type(command))  # <class 'str'>
    # HM.DPrint(type(exe_ctx))  # <class 'lldb.SBExecutionContext'>
    # HM.DPrint(type(result))  # <class 'lldb.SBCommandReturnObject'>
    # HM.DPrint(type(internal_dict))  # <class 'dict'>


    command_args = shlex.split(command)
    parser = generate_option_parser()
    try:
        # options: optparse.Values
        # args: list
        (options, args) = parser.parse_args(command_args)
    except:
        result.SetError(parser.usage)
        return

    if len(args) == 0:
        HM.DPrint("Error input, plase input 'help push' for more infomation")
        return

    HM.DPrint("Waiting...")

    navigationVC = getNavigationVC()
    if navigationVC is None:
        HM.DPrint("Cannot find a UINavigationController")
        return

    state = False
    if options.instance:
        instanceExpr: str = ""
        for string in args:
            instanceExpr += string + " "
        instanceExpr = instanceExpr.rstrip()
        VCObject = HM.evaluateExpressionValue(instanceExpr).GetValue()
    else:
        makeVCExpression = "(UIViewController *)[[NSClassFromString(@\"{UIViewController}\") alloc] init]".format(UIViewController=command)
        VCObject = HM.evaluateExpressionValue(makeVCExpression).GetValue()     # address

    if verifyObjIsKindOfClass(VCObject, "UIViewController"):
        pushExpression = "(void)[{arg1} pushViewController:(id){arg2} animated:YES]".format(arg1=navigationVC, arg2=VCObject)
        debugger.HandleCommand('expression -l objc -O -- ' + pushExpression)
        state = True
    elif not options.instance:
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
    if obj is None or len(obj) == 0:
        return False
    
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


def generate_option_parser() -> optparse.OptionParser:
    usage = "usage: \npush <className> \npush [--instance] <classInstance>"
    parser = optparse.OptionParser(usage=usage, prog="push")

    parser.add_option("-i", "--instance",
                      action="store_true",
                      default=False,
                      dest="instance",
                      help="Push the UIViewController instance.")

    return parser
