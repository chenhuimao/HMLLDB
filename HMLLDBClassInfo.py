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

    if compareName("SBPlatform"):
        pSBPlatform()
    if compareName("SBCommandInterpreter"):
        pSBCommandInterpreter()
    if compareName("SBListener"):
        pSBListener()
    if compareName("SBSourceManager"):
        pSBSourceManager()
    if compareName("SBStructuredData"):
        pSBStructuredData()
    if compareName("SBUnixSignals"):
        pSBUnixSignals()
    if compareName("SBBroadcaster"):
        pSBBroadcaster()


def compareName(className):
    global gLastCommand
    if gLastCommand in className.lower() or gLastCommand == "all":
        return True
    else:
        return False


def formatPrint(desc, value):
    print ("[{arg1}]: {arg2}\n\ttype: {arg3}".format(arg1=desc, arg2=value, arg3=type(value)))


def titlePrint(title):
    print ("\n\n====={arg1}================================".format(arg1=title))


def listTitlePrint(title):
    print ("\n##### {arg1} #####".format(arg1=title))


def pSBDebugger():
    debugger = lldb.debugger
    titlePrint("SBDebugger")
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


    listTitlePrint("all targets[SBTarget]")
    numTargets = debugger.GetNumTargets()
    for i in range(numTargets):
        target = debugger.GetTargetAtIndex(i)
        if i == 0:
            print (type(target))
        print (target)

    listTitlePrint("all platforms[SBPlatform]")
    numPlatforms = debugger.GetNumPlatforms()
    for i in range(numPlatforms):
        platform = debugger.GetPlatformAtIndex(i)
        if i == 0:
            print (type(platform))
        print (platform)

    listTitlePrint("all categories[SBTypeCategory]")
    numCategories = debugger.GetNumCategories()
    for i in range(numCategories):
        category = debugger.GetCategoryAtIndex(i)
        if i == 0:
            print (type(category))
        print (category)


def pSBTarget():
    target = lldb.debugger.GetSelectedTarget()


def pSBProcess():
    process = lldb.debugger.GetCommandInterpreter().GetProcess()


def pSBListener():
    listener = lldb.debugger.GetListener()
    titlePrint("SBListener")
    formatPrint("SBListener", listener)
    formatPrint("IsValid", listener.IsValid())


def pSBPlatform():
    platform = lldb.debugger.GetSelectedPlatform()
    titlePrint("SBPlatform")
    formatPrint("SBPlatform", platform)
    formatPrint("IsValid", platform.IsValid())
    formatPrint("GetWorkingDirectory", platform.GetWorkingDirectory())
    formatPrint("GetName", platform.GetName())
    formatPrint("IsConnected", platform.IsConnected())
    formatPrint("GetTriple", platform.GetTriple())
    formatPrint("GetHostname", platform.GetHostname())
    formatPrint("GetOSBuild", platform.GetOSBuild())
    formatPrint("GetOSDescription", platform.GetOSDescription())
    formatPrint("GetOSMajorVersion", platform.GetOSMajorVersion())
    formatPrint("GetOSMinorVersion", platform.GetOSMinorVersion())
    formatPrint("GetOSUpdateVersion", platform.GetOSUpdateVersion())
    formatPrint("GetUnixSignals", platform.GetUnixSignals())


def pSBCommandInterpreter():
    ci = lldb.debugger.GetCommandInterpreter()
    titlePrint("SBCommandInterpreter")
    formatPrint("SBCommandInterpreter", ci)
    formatPrint("IsValid", ci.IsValid())
    formatPrint("GetPromptOnQuit", ci.GetPromptOnQuit())
    formatPrint("HasCustomQuitExitCode", ci.HasCustomQuitExitCode())
    formatPrint("GetQuitStatus", ci.GetQuitStatus())
    formatPrint("GetBroadcaster", ci.GetBroadcaster())
    formatPrint("GetBroadcasterClass", ci.GetBroadcasterClass())
    formatPrint("HasCommands", ci.HasCommands())
    formatPrint("HasAliases", ci.HasAliases())
    formatPrint("HasAliasOptions", ci.HasAliasOptions())
    formatPrint("GetProcess", ci.GetProcess())
    formatPrint("GetDebugger", ci.GetDebugger())
    formatPrint("IsActive", ci.IsActive())
    formatPrint("WasInterrupted", ci.WasInterrupted())


def pSBSourceManager():
    manager = lldb.debugger.GetSourceManager()
    titlePrint("SBSourceManager")
    formatPrint("SBSourceManager", manager)


def pSBStructuredData():
    sd = lldb.debugger.GetBuildConfiguration()
    titlePrint("SBStructuredData")
    formatPrint("SBStructuredData", sd)
    formatPrint("IsValid", sd.IsValid())
    formatPrint("GetType", sd.GetType())
    formatPrint("GetSize", sd.GetSize())
    formatPrint("GetIntegerValue", sd.GetIntegerValue())
    formatPrint("GetFloatValue", sd.GetFloatValue())
    formatPrint("GetBooleanValue", sd.GetBooleanValue())


def pSBTypeCategory():
    category = lldb.debugger.GetDefaultCategory()


def pSBUnixSignals():
    signals = lldb.debugger.GetSelectedPlatform().GetUnixSignals()
    titlePrint("SBUnixSignals")
    formatPrint("SBUnixSignals", signals)
    formatPrint("IsValid", signals.IsValid())
    formatPrint("GetNumSignals", signals.GetNumSignals())


    listTitlePrint("all signals")
    numSignals = signals.GetNumSignals()
    for i in range(numSignals):
        s = signals.GetSignalAtIndex(i)
        if i == 0:
            print (type(s))
        print (s)


def pSBBroadcaster():
    broadcaster = lldb.debugger.GetCommandInterpreter().GetBroadcaster()
    titlePrint("SBBroadcaster")
    formatPrint("SBBroadcaster", broadcaster)
    formatPrint("IsValid", broadcaster.IsValid())
    formatPrint("GetName", broadcaster.GetName())
