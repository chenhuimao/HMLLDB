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
    printFormat("GetInputFileHandle", debugger.GetInputFileHandle())  # FILE
    printFormat("GetOutputFileHandle", debugger.GetOutputFileHandle())  # FILE
    printFormat("GetErrorFileHandle", debugger.GetErrorFileHandle())  # FILE
    printFormat("GetCommandInterpreter", debugger.GetCommandInterpreter())  # SBCommandInterpreter
    printFormat("GetListener", debugger.GetListener())  # SBListener
    printFormat("GetDummyTarget", debugger.GetDummyTarget())  # SBTarget
    printFormat("GetNumTargets", debugger.GetNumTargets())
    printFormat("GetSelectedTarget", debugger.GetSelectedTarget())  # SBTarget
    printFormat("GetSelectedPlatform", debugger.GetSelectedPlatform())  # GetSelectedPlatform
    printFormat("GetNumPlatforms", debugger.GetNumPlatforms())
    printFormat("GetNumAvailablePlatforms", debugger.GetNumAvailablePlatforms())
    printFormat("GetSourceManager", debugger.GetSourceManager())  # SBSourceManager
    printFormat("GetUseExternalEditor", debugger.GetUseExternalEditor())
    printFormat("GetUseColor", debugger.GetUseColor())
    printFormat("GetVersionString", debugger.GetVersionString())
    printFormat("GetBuildConfiguration", debugger.GetBuildConfiguration())  # SBStructuredData
    printFormat("GetInstanceName", debugger.GetInstanceName())
    printFormat("GetTerminalWidth", debugger.GetTerminalWidth())
    printFormat("GetID", debugger.GetID())
    printFormat("GetPrompt", debugger.GetPrompt())
    printFormat("GetScriptLanguage", debugger.GetScriptLanguage())  # ScriptLanguage int
    printFormat("GetCloseInputOnEOF", debugger.GetCloseInputOnEOF())
    printFormat("GetNumCategories", debugger.GetNumCategories())
    printFormat("GetDefaultCategory", debugger.GetDefaultCategory())  # SBTypeCategory

    printTraversal(debugger, "GetNumTargets", "GetTargetAtIndex")  # [SBTarget]
    printTraversal(debugger, "GetNumPlatforms", "GetPlatformAtIndex")  # [SBPlatform]
    printTraversal(debugger, "GetNumCategories", "GetCategoryAtIndex")  # [SBTypeCategory]


def pSBTarget():
    target = lldb.debugger.GetSelectedTarget()

    printClassName("SBTarget")
    printFormat("SBTarget", target)
    printFormat("IsValid", target.IsValid())
    printFormat("GetBroadcasterClassName", target.GetBroadcasterClassName())
    printFormat("GetProcess", target.GetProcess())  # SBProcess
    printFormat("GetPlatform", target.GetPlatform())  # SBPlatform
    printFormat("GetExecutable", target.GetExecutable())  # SBFileSpec
    printFormat("GetNumModules", target.GetNumModules())
    printFormat("GetDebugger", target.GetDebugger())  # SBDebugger
    printFormat("GetByteOrder", target.GetByteOrder())  # ByteOrder int
    printFormat("GetAddressByteSize", target.GetAddressByteSize())
    printFormat("GetTriple", target.GetTriple())
    printFormat("GetDataByteSize", target.GetDataByteSize())
    printFormat("GetCodeByteSize", target.GetCodeByteSize())
    printFormat("FindFunctions.first", target.FindFunctions("viewDidLoad")[0])  # SBSymbolContext
    printFormat("FindFirstType", target.FindFirstType("UIAlertAction"))  # SBType
    printFormat("FindTypes", target.FindTypes("UIAlertAction"))  # SBTypeList
    printFormat("GetSourceManager", target.GetSourceManager())  # SBSourceManager
    printFormat("FindFirstGlobalVariable", target.FindFirstGlobalVariable("shared"))  # SBValue
    printFormat("FindGlobalVariables", target.FindGlobalVariables("shared", 2))  # SBValueList
    printFormat("FindGlobalFunctions.first", target.FindGlobalFunctions("viewDidLoad", 1, 0)[0])  # SBSymbolContext
    printFormat("GetNumBreakpoints", target.GetNumBreakpoints())
    printFormat("GetNumWatchpoints", target.GetNumWatchpoints())
    printFormat("GetBroadcaster", target.GetBroadcaster())  # SBBroadcaster
    printFormat("FindSymbols", target.FindSymbols("UIAlertAction"))  # SBSymbolContextList
    printFormat("GetStackRedZoneSize", target.GetStackRedZoneSize())
    printFormat("GetLaunchInfo", target.GetLaunchInfo())  # SBLaunchInfo
    printFormat("GetCollectingStats", target.GetCollectingStats())
    printFormat("GetStatistics", target.GetStatistics())  # SBStructuredData

    printTraversal(target, "GetNumModules", "GetModuleAtIndex")  # [SBModule]
    printTraversal(target, "GetNumBreakpoints", "GetBreakpointAtIndex")  # [SBBreakpoint]
    printTraversal(target, "GetNumWatchpoints", "GetWatchpointAtIndex")  # [SBWatchpoint]


def pSBProcess():
    # TODO
    process = lldb.debugger.GetCommandInterpreter().GetProcess()
    process = lldb.debugger.GetSelectedTarget().GetProcess()


def pSBSymbolContext():
    # TODO
    ctx = lldb.debugger.GetSelectedTarget().FindFunctions("viewDidLoad")[0]


def pSBType():
    # TODO
    type = lldb.debugger.GetSelectedTarget().FindFirstType("UIAlertAction")


def pSBBreakpoint():
    # TODO
    bp = lldb.debugger.GetSelectedTarget().GetBreakpointAtIndex(0)


def pSBWatchpoint():
    # TODO
    wp = lldb.debugger.GetSelectedTarget().GetWatchpointAtIndex(0)


def pSBPlatform():
    platform = lldb.debugger.GetSelectedPlatform()
    # platform = lldb.debugger.GetSelectedTarget().GetPlatform()

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
    printFormat("GetUnixSignals", platform.GetUnixSignals())  # SBUnixSignals


def pSBCommandInterpreter():
    ci = lldb.debugger.GetCommandInterpreter()

    printClassName("SBCommandInterpreter")
    printFormat("SBCommandInterpreter", ci)
    printFormat("IsValid", ci.IsValid())
    printFormat("GetPromptOnQuit", ci.GetPromptOnQuit())
    printFormat("HasCustomQuitExitCode", ci.HasCustomQuitExitCode())
    printFormat("GetQuitStatus", ci.GetQuitStatus())
    printFormat("CommandExists", ci.CommandExists("breakpoint"))
    printFormat("AliasExists", ci.AliasExists('bt'))
    printFormat("GetBroadcaster", ci.GetBroadcaster())  # SBBroadcaster
    printFormat("GetBroadcasterClass", ci.GetBroadcasterClass())
    printFormat("HasCommands", ci.HasCommands())
    printFormat("HasAliases", ci.HasAliases())
    printFormat("HasAliasOptions", ci.HasAliasOptions())
    printFormat("GetProcess", ci.GetProcess())  # SBProcess
    printFormat("GetDebugger", ci.GetDebugger())  # SBDebugger
    printFormat("IsActive", ci.IsActive())
    printFormat("WasInterrupted", ci.WasInterrupted())


def pSBSourceManager():
    manager = lldb.debugger.GetSourceManager()
    # manager = lldb.debugger.GetSelectedTarget().GetSourceManager()

    printClassName("SBSourceManager")
    printFormat("SBSourceManager", manager)


def pSBStructuredData():
    sd = lldb.debugger.GetBuildConfiguration()
    # sd = lldb.debugger.GetSelectedTarget().GetStatistics()

    printClassName("SBStructuredData")
    printFormat("SBStructuredData", sd)
    printFormat("IsValid", sd.IsValid())
    printFormat("GetType", sd.GetType())  # StructuredDataType int
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
    # broadcaster = lldb.debugger.GetSelectedTarget().GetBroadcaster()

    printClassName("SBBroadcaster")
    printFormat("SBBroadcaster", broadcaster)
    printFormat("IsValid", broadcaster.IsValid())
    printFormat("GetName", broadcaster.GetName())


def pSBListener():
    listener = lldb.debugger.GetListener()

    printClassName("SBListener")
    printFormat("SBListener", listener)
    printFormat("IsValid", listener.IsValid())


def pSBLaunchInfo():
    # TODO
    info = lldb.debugger.GetSelectedTarget().GetLaunchInfo()

