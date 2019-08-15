""" File: HMLLDBClassInfo.py

An lldb Python script to print infomation of lldb class.(In order to learn)

"""

import lldb


def __lldb_init_module(debugger, internal_dict):
    debugger.HandleCommand(
        'command script add -f HMLLDBClassInfo.plldbClassInfo plldbClassInfo -h "Print infomation of lldb class."')


gLastCommand = ""  # List of module names that may be user-written


def plldbClassInfo(debugger, command, exe_ctx, result, internal_dict):
    """
    Syntax:
        plldbClassInfo <className>

    Examples:
        (lldb) plldbClassInfo all
        (lldb) plldbClassInfo SBTarget
        (lldb) plldbClassInfo SBValue

    This command is implemented in HMLLDBClassInfo.py
    """
    if len(command) == 0:
        print ("Error input, plase input 'help plldbClassInfo' for more infomation")
        return

    global gLastCommand
    gLastCommand = command

    if compareName("SBDebugger"):
        pSBDebugger()
    if compareName("SBTarget"):
        pSBTarget()


def compareName(className):
    global gLastCommand
    if gLastCommand in className.lower() or gLastCommand == "all":
        return True
    else:
        return False


def formatPrint(desc, value):
    print ("[{arg1}]: {arg2}\n\ttype: {arg3}".format(arg1=desc, arg2=value, arg3=type(value)))


def pSBDebugger():
    debugger = lldb.debugger
    print ("=====SBDebugger================================")
    formatPrint("SBDebugger", debugger)
    formatPrint("IsValid", debugger.IsValid())
    formatPrint("GetAsync", debugger.GetAsync())
    formatPrint("GetInputFileHandle", debugger.GetInputFileHandle())
    formatPrint("GetOutputFileHandle", debugger.GetOutputFileHandle())
    formatPrint("GetErrorFileHandle", debugger.GetErrorFileHandle())
    formatPrint("GetCommandInterpreter", debugger.GetCommandInterpreter())
    formatPrint("GetListener", debugger.GetListener())
    formatPrint("GetDummyTarget", debugger.GetDummyTarget())
    formatPrint("GetNumTargets", debugger.GetNumTargets())
    formatPrint("GetSelectedTarget", debugger.GetSelectedTarget())
    formatPrint("GetSelectedPlatform", debugger.GetSelectedPlatform())
    formatPrint("GetNumPlatforms", debugger.GetNumPlatforms())
    formatPrint("GetNumAvailablePlatforms", debugger.GetNumAvailablePlatforms())
    formatPrint("GetSourceManager", debugger.GetSourceManager())
    formatPrint("GetUseExternalEditor", debugger.GetUseExternalEditor())
    formatPrint("GetUseColor", debugger.GetUseColor())
    formatPrint("GetVersionString", debugger.GetVersionString())
    formatPrint("GetBuildConfiguration", debugger.GetBuildConfiguration())
    formatPrint("GetInstanceName", debugger.GetInstanceName())
    formatPrint("GetTerminalWidth", debugger.GetTerminalWidth())
    formatPrint("GetID", debugger.GetID())
    formatPrint("GetPrompt", debugger.GetPrompt())
    formatPrint("GetScriptLanguage", debugger.GetScriptLanguage())
    formatPrint("GetCloseInputOnEOF", debugger.GetCloseInputOnEOF())
    formatPrint("GetNumCategories", debugger.GetNumCategories())
    formatPrint("GetDefaultCategory", debugger.GetDefaultCategory())

    print ("\n##### all targets[SBTarget] #####")
    numTargets = debugger.GetNumTargets()
    for i in range(numTargets):
        target = debugger.GetTargetAtIndex(i)
        if i == 0:
            print (type(target))
        print (target)

    print ("\n##### all platforms #####")
    numPlatforms = debugger.GetNumPlatforms()
    for i in range(numPlatforms):
        platform = debugger.GetPlatformAtIndex(i)
        if i == 0:
            print (type(platform))
        print (platform)

    print ("\n##### all categories #####")
    numCategories = debugger.GetNumCategories()
    for i in range(numCategories):
        category = debugger.GetCategoryAtIndex(i)
        if i == 0:
            print (type(category))
        print (category)


def pSBTarget():
    target = lldb.debugger.GetSelectedTarget()
    print ("=====SBTarget================================")


def pSBCommandInterpreter():
    interpreter = lldb.debugger.GetCommandInterpreter()


def pSBListener():
    listener = lldb.debugger.GetListener()


def pSBPlatform():
    platform = lldb.debugger.GetSelectedPlatform()


def pSBSourceManager():
    manager = lldb.debugger.GetSourceManager()


def pSBStructuredData():
    structuredData = lldb.debugger.GetBuildConfiguration()


def pSBTypeCategory():
    category = lldb.debugger.GetDefaultCategory()

