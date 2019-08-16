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
    if compareName("SBTypeCategory"):
        pSBTypeCategory()

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


def printFormat(desc, value):
    print ("[{arg1}]: {arg2}\n\ttype: {arg3}".format(arg1=desc, arg2=value, arg3=type(value)))


def printClassName(title):
    print ("\n\n====={arg1}================================".format(arg1=title))


def printTraversal(obj, getsize, getelem):
    print ("\n##### [{arg1}] #####".format(arg1=getelem))
    size = getattr(obj, getsize)
    elem = getattr(obj, getelem)
    for i in range(size()):
        if i == 0:
            print (type(elem(i)))
        print (elem(i))


def pSBDebugger():
    debugger = lldb.debugger
    printClassName("SBDebugger")
    printFormat("SBDebugger", debugger)
    printFormat("IsValid", debugger.IsValid())
    printFormat("GetAsync", debugger.GetAsync())
    printFormat("GetInputFileHandle", debugger.GetInputFileHandle())
    printFormat("GetOutputFileHandle", debugger.GetOutputFileHandle())
    printFormat("GetErrorFileHandle", debugger.GetErrorFileHandle())
    printFormat("GetCommandInterpreter", debugger.GetCommandInterpreter())
    printFormat("GetListener", debugger.GetListener())
    printFormat("GetDummyTarget", debugger.GetDummyTarget())
    printFormat("GetNumTargets", debugger.GetNumTargets())
    printFormat("GetSelectedTarget", debugger.GetSelectedTarget())
    printFormat("GetSelectedPlatform", debugger.GetSelectedPlatform())
    printFormat("GetNumPlatforms", debugger.GetNumPlatforms())
    printFormat("GetNumAvailablePlatforms", debugger.GetNumAvailablePlatforms())
    printFormat("GetSourceManager", debugger.GetSourceManager())
    printFormat("GetUseExternalEditor", debugger.GetUseExternalEditor())
    printFormat("GetUseColor", debugger.GetUseColor())
    printFormat("GetVersionString", debugger.GetVersionString())
    printFormat("GetBuildConfiguration", debugger.GetBuildConfiguration())
    printFormat("GetInstanceName", debugger.GetInstanceName())
    printFormat("GetTerminalWidth", debugger.GetTerminalWidth())
    printFormat("GetID", debugger.GetID())
    printFormat("GetPrompt", debugger.GetPrompt())
    printFormat("GetScriptLanguage", debugger.GetScriptLanguage())
    printFormat("GetCloseInputOnEOF", debugger.GetCloseInputOnEOF())
    printFormat("GetNumCategories", debugger.GetNumCategories())
    printFormat("GetDefaultCategory", debugger.GetDefaultCategory())

    printTraversal(debugger, "GetNumTargets", "GetTargetAtIndex")  # [SBTarget]
    printTraversal(debugger, "GetNumPlatforms", "GetPlatformAtIndex")  # [SBPlatform]
    printTraversal(debugger, "GetNumCategories", "GetCategoryAtIndex")  # [SBTypeCategory]


def pSBTarget():
    target = lldb.debugger.GetSelectedTarget()
    printClassName("SBTarget")
    printFormat("SBTarget", target)


def pSBProcess():
    process = lldb.debugger.GetCommandInterpreter().GetProcess()


def pSBListener():
    listener = lldb.debugger.GetListener()
    printClassName("SBListener")
    printFormat("SBListener", listener)
    printFormat("IsValid", listener.IsValid())


def pSBPlatform():
    platform = lldb.debugger.GetSelectedPlatform()
    printClassName("SBPlatform")
    printFormat("SBPlatform", platform)
    printFormat("IsValid", platform.IsValid())
    printFormat("GetWorkingDirectory", platform.GetWorkingDirectory())
    printFormat("GetName", platform.GetName())
    printFormat("IsConnected", platform.IsConnected())
    printFormat("GetTriple", platform.GetTriple())
    printFormat("GetHostname", platform.GetHostname())
    printFormat("GetOSBuild", platform.GetOSBuild())
    printFormat("GetOSDescription", platform.GetOSDescription())
    printFormat("GetOSMajorVersion", platform.GetOSMajorVersion())
    printFormat("GetOSMinorVersion", platform.GetOSMinorVersion())
    printFormat("GetOSUpdateVersion", platform.GetOSUpdateVersion())
    printFormat("GetUnixSignals", platform.GetUnixSignals())


def pSBCommandInterpreter():
    ci = lldb.debugger.GetCommandInterpreter()
    printClassName("SBCommandInterpreter")
    printFormat("SBCommandInterpreter", ci)
    printFormat("IsValid", ci.IsValid())
    printFormat("GetPromptOnQuit", ci.GetPromptOnQuit())
    printFormat("HasCustomQuitExitCode", ci.HasCustomQuitExitCode())
    printFormat("GetQuitStatus", ci.GetQuitStatus())
    printFormat("GetBroadcaster", ci.GetBroadcaster())
    printFormat("GetBroadcasterClass", ci.GetBroadcasterClass())
    printFormat("HasCommands", ci.HasCommands())
    printFormat("HasAliases", ci.HasAliases())
    printFormat("HasAliasOptions", ci.HasAliasOptions())
    printFormat("GetProcess", ci.GetProcess())
    printFormat("GetDebugger", ci.GetDebugger())
    printFormat("IsActive", ci.IsActive())
    printFormat("WasInterrupted", ci.WasInterrupted())


def pSBSourceManager():
    manager = lldb.debugger.GetSourceManager()
    printClassName("SBSourceManager")
    printFormat("SBSourceManager", manager)


def pSBStructuredData():
    sd = lldb.debugger.GetBuildConfiguration()
    printClassName("SBStructuredData")
    printFormat("SBStructuredData", sd)
    printFormat("IsValid", sd.IsValid())
    printFormat("GetType", sd.GetType())
    printFormat("GetSize", sd.GetSize())
    printFormat("GetIntegerValue", sd.GetIntegerValue())
    printFormat("GetFloatValue", sd.GetFloatValue())
    printFormat("GetBooleanValue", sd.GetBooleanValue())


def pSBTypeCategory():
    category = lldb.debugger.GetDefaultCategory()
    printClassName("SBTypeCategory")
    printFormat("SBTypeCategory", category)
    printFormat("IsValid", category.IsValid())
    printFormat("GetEnabled", category.GetEnabled())
    printFormat("GetName", category.GetName())
    printFormat("GetNumLanguages", category.GetNumLanguages())
    printFormat("GetNumFormats", category.GetNumFormats())
    printFormat("GetNumSummaries", category.GetNumSummaries())
    printFormat("GetNumFilters", category.GetNumFilters())
    printFormat("GetNumSynthetics", category.GetNumSynthetics())

    printTraversal(category, "GetNumLanguages", "GetLanguageAtIndex")  # [LanguageType] [int]
    printTraversal(category, "GetNumFormats", "GetFormatAtIndex")  # [SBTypeFormat]
    printTraversal(category, "GetNumSummaries", "GetSummaryAtIndex")  # [SBTypeSummary]
    printTraversal(category, "GetNumFilters", "GetFilterAtIndex")  # [SBTypeFilter]
    printTraversal(category, "GetNumSynthetics", "GetSyntheticAtIndex")  # [SBTypeSynthetic]


def pSBUnixSignals():
    signals = lldb.debugger.GetSelectedPlatform().GetUnixSignals()
    printClassName("SBUnixSignals")
    printFormat("SBUnixSignals", signals)
    printFormat("IsValid", signals.IsValid())
    printFormat("GetNumSignals", signals.GetNumSignals())

    printTraversal(signals, "GetNumSignals", "GetSignalAtIndex")  # [int]


def pSBBroadcaster():
    broadcaster = lldb.debugger.GetCommandInterpreter().GetBroadcaster()
    printClassName("SBBroadcaster")
    printFormat("SBBroadcaster", broadcaster)
    printFormat("IsValid", broadcaster.IsValid())
    printFormat("GetName", broadcaster.GetName())
