""" File: HMLLDBClassInfo.py

An lldb Python script to print infomation of lldb class.

"""

import lldb
from typing import Optional
import optparse
import shlex
import HMLLDBHelpers as HM


def __lldb_init_module(debugger, internal_dict):
    debugger.HandleCommand('command script add -f HMLLDBClassInfo.plldbClassInfo plldbClassInfo -h "Print infomation of lldb class."')


gLastCommand = ""
gUnlimited = False


def plldbClassInfo(debugger, command, exe_ctx, result, internal_dict):
    """
    Syntax:
        plldbClassInfo [--entire] <className/all>

    Options:
        --entire/-e; Print all elements of the list, otherwise only 100

    Examples:
        (lldb) plldbClassInfo all
        (lldb) plldbClassInfo SBValue
        (lldb) plldbClassInfo SBTarget
        (lldb) plldbClassInfo -e SBTarget

    This command is implemented in HMLLDBClassInfo.py
    """

    command_args = shlex.split(command)
    parser = generate_option_parser()
    try:
        # options: optparse.Values
        # args: list
        (options, args) = parser.parse_args(command_args)
    except:
        result.SetError(parser.usage)
        return

    if len(args) != 1:
        HM.DPrint("Error input, plase input 'help plldbClassInfo' for more infomation")
        return

    global gUnlimited
    gUnlimited = options.entire

    global gLastCommand
    gLastCommand = args[0]

    if compareName("SBHostOS"):
        pSBHostOS(None)

    if compareName("SBDebugger"):
        pSBDebugger(None)
    if compareName("SBTarget"):
        pSBTarget(None)
    if compareName("SBProcess"):
        pSBProcess(None)
    if compareName("SBProcessInfo"):
        pSBProcessInfo(None)
    if compareName("SBThread"):
        pSBThread(None)
    if compareName("SBFrame"):
        pSBFrame(None)
    if compareName("SBValue"):
        pSBValue(None)

    if compareName("SBSymbolContext"):
        pSBSymbolContext(None)
    if compareName("SBModule"):
        pSBModule(None)
    if compareName("SBSymbol"):
        pSBSymbol(None)
    if compareName("SBInstruction"):
        pSBInstruction(None)
    if compareName("SBFunction"):
        pSBFunction(None)
    if compareName("SBBlock"):
        pSBBlock(None)
    if compareName("SBCompileUnit"):
        pSBCompileUnit(None)
    if compareName("SBLineEntry"):
        pSBLineEntry(None)

    if compareName("SBFileSpec"):
        pSBFileSpec(None)
    if compareName("SBAddress"):
        pSBAddress(None)
    if compareName("SBBreakpoint"):
        pSBBreakpoint(None)
    if compareName("SBError"):
        pSBError(None)

    if compareName("SBType"):
        pSBType(None)
    if compareName("SBTypeMemberFunction"):
        pSBTypeMemberFunction(None)
    if compareName("SBTypeCategory"):
        pSBTypeCategory(None)

    if compareName("SBPlatform"):
        pSBPlatform(None)
    if compareName("SBBroadcaster"):
        pSBBroadcaster(None)
    if compareName("SBListener"):
        pSBListener(None)
    if compareName("SBSourceManager"):
        pSBSourceManager(None)
    if compareName("SBStructuredData"):
        pSBStructuredData(None)
    if compareName("SBUnixSignals"):
        pSBUnixSignals(None)
    if compareName("SBLaunchInfo"):
        pSBLaunchInfo(None)
    if compareName("SBCommandInterpreter"):
        pSBCommandInterpreter(None)
    if compareName("SBQueue"):
        pSBQueue(None)
    if compareName("SBSection"):
        pSBSection(None)
    if compareName("SBExpressionOptions"):
        pSBExpressionOptions(None)


def compareName(className: str) -> bool:
    global gLastCommand
    if gLastCommand.lower() in className.lower() or gLastCommand.lower() == "all":
        return True
    else:
        return False


def printFormat(desc: str, value: object) -> None:
    print("[{arg1}]: {arg2}\n\ttype: {arg3}".format(arg1=desc, arg2=value, arg3=type(value)))


def printClassName(title: str) -> None:
    print("\n\n====={arg1}================================".format(arg1=title))


def printTraversal(obj: object, getsize: str, getelem: str) -> None:
    size = getattr(obj, getsize)
    elem = getattr(obj, getelem)
    global gUnlimited

    print("\n##### [{arg1}]({arg2}) #####".format(arg1=getelem, arg2=size()))

    for i in range(size()):
        if i == 100 and not gUnlimited:
            break
        if i == 0:
            print(type(elem(i)))
        print(elem(i))


def generate_option_parser() -> optparse.OptionParser:
    usage = "usage: plldbClassInfo [--entire] <className/all>"
    parser = optparse.OptionParser(usage=usage, prog="plldbClassInfo")

    parser.add_option("-e", "--entire",
                      action="store_true",
                      default=False,
                      dest="entire",
                      help="Print all elements of the list, otherwise only 100")

    return parser


def pSBHostOS(obj: Optional[lldb.SBHostOS]) -> None:
    if obj:
        hostOS = obj
    else:
        hostOS = lldb.SBHostOS

    printClassName("SBHostOS")
    printFormat("GetProgramFileSpec", hostOS.GetProgramFileSpec())  # SBFileSpec
    printFormat("GetLLDBPythonPath", hostOS.GetLLDBPythonPath())  # SBFileSpec
    printFormat("GetUserHomeDirectory", hostOS.GetUserHomeDirectory())  # SBFileSpec

    printFormat("GetLLDBPath(ePathTypeLLDBShlibDir)", hostOS.GetLLDBPath(lldb.ePathTypeLLDBShlibDir))  # SBFileSpec
    printFormat("GetLLDBPath(ePathTypeSupportExecutableDir)", hostOS.GetLLDBPath(lldb.ePathTypeSupportExecutableDir))  # SBFileSpec
    printFormat("GetLLDBPath(ePathTypeSupportFileDir)", hostOS.GetLLDBPath(lldb.ePathTypeSupportFileDir))  # SBFileSpec
    printFormat("GetLLDBPath(ePathTypeHeaderDir)", hostOS.GetLLDBPath(lldb.ePathTypeHeaderDir))  # SBFileSpec
    printFormat("GetLLDBPath(ePathTypePythonDir)", hostOS.GetLLDBPath(lldb.ePathTypePythonDir))  # SBFileSpec
    printFormat("GetLLDBPath(ePathTypeLLDBSystemPlugins)", hostOS.GetLLDBPath(lldb.ePathTypeLLDBSystemPlugins))  # SBFileSpec
    printFormat("GetLLDBPath(ePathTypeLLDBUserPlugins)", hostOS.GetLLDBPath(lldb.ePathTypeLLDBUserPlugins))  # SBFileSpec
    printFormat("GetLLDBPath(ePathTypeLLDBTempSystemDir)", hostOS.GetLLDBPath(lldb.ePathTypeLLDBTempSystemDir))  # SBFileSpec
    printFormat("GetLLDBPath(ePathTypeGlobalLLDBTempSystemDir)", hostOS.GetLLDBPath(lldb.ePathTypeGlobalLLDBTempSystemDir))  # SBFileSpec
    printFormat("GetLLDBPath(ePathTypeClangDir)", hostOS.GetLLDBPath(lldb.ePathTypeClangDir))  # SBFileSpec
    printFormat("GetLLDBPath(ePathTypeSwiftDir)", hostOS.GetLLDBPath(lldb.ePathTypeSwiftDir))  # SBFileSpec


def pSBDebugger(obj: Optional[lldb.SBDebugger]) -> None:
    if obj:
        debugger = obj
    else:
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
    printFormat("GetReproducerPath", debugger.GetReproducerPath())
    printFormat("GetScriptLanguage", debugger.GetScriptLanguage())  # ScriptLanguage int
    printFormat("GetCloseInputOnEOF", debugger.GetCloseInputOnEOF())
    printFormat("GetNumCategories", debugger.GetNumCategories())
    printFormat("GetDefaultCategory", debugger.GetDefaultCategory())  # SBTypeCategory

    printTraversal(debugger, "GetNumTargets", "GetTargetAtIndex")  # [SBTarget]
    printTraversal(debugger, "GetNumPlatforms", "GetPlatformAtIndex")  # [SBPlatform]
    printTraversal(debugger, "GetNumCategories", "GetCategoryAtIndex")  # [SBTypeCategory]


def pSBTarget(obj: Optional[lldb.SBTarget]) -> None:
    if obj:
        target = obj
    else:
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


def pSBProcess(obj: Optional[lldb.SBProcess]) -> None:
    if obj:
        process = obj
    else:
        process = lldb.debugger.GetSelectedTarget().GetProcess()
        # process = lldb.debugger.GetCommandInterpreter().GetProcess()

    printClassName("SBProcess")
    printFormat("SBProcess", process)
    printFormat("GetBroadcasterClassName", process.GetBroadcasterClassName())
    printFormat("GetPluginName", process.GetPluginName())
    printFormat("GetShortPluginName", process.GetShortPluginName())
    printFormat("IsValid", process.IsValid())
    printFormat("GetTarget", process.GetTarget())  # SBTarget
    printFormat("GetByteOrder", process.GetByteOrder())  # ByteOrder int
    printFormat("GetNumThreads", process.GetNumThreads())
    printFormat("GetSelectedThread", process.GetSelectedThread())  # SBThread
    printFormat("GetNumQueues", process.GetNumQueues())
    printFormat("GetState", process.GetState())  # StateType int
    printFormat("GetExitStatus", process.GetExitStatus())
    printFormat("GetExitDescription", process.GetExitDescription())
    printFormat("GetProcessID", process.GetProcessID())
    printFormat("GetUniqueID", process.GetUniqueID())
    printFormat("GetAddressByteSize", process.GetAddressByteSize())
    printFormat("GetUnixSignals", process.GetUnixSignals())  # SBUnixSignals
    printFormat("GetBroadcaster", process.GetBroadcaster())  # SBBroadcaster
    printFormat("GetNumExtendedBacktraceTypes", process.GetNumExtendedBacktraceTypes())
    printFormat("GetMemoryRegions", process.GetMemoryRegions())  # SBMemoryRegionInfoList
    printFormat("GetProcessInfo", process.GetProcessInfo())  # SBProcessInfo
    printFormat("__get_is_alive__", process.__get_is_alive__())
    printFormat("__get_is_running__", process.__get_is_running__())
    printFormat("__get_is_stopped__", process.__get_is_stopped__())

    printTraversal(process, "GetNumThreads", "GetThreadAtIndex")  # [SBThread]
    printTraversal(process, "GetNumQueues", "GetQueueAtIndex")  # [SBQueue]
    printTraversal(process, "GetNumExtendedBacktraceTypes", "GetExtendedBacktraceTypeAtIndex")  # [str]


def pSBProcessInfo(obj: Optional[lldb.SBProcessInfo]) -> None:
    if obj:
        info = obj
    else:
        info = lldb.debugger.GetSelectedTarget().GetProcess().GetProcessInfo()

    printClassName("SBProcessInfo")
    printFormat("SBProcessInfo", info)
    printFormat("IsValid", info.IsValid())
    printFormat("GetName", info.GetName())
    printFormat("GetExecutableFile", info.GetExecutableFile())  # SBFileSpec
    printFormat("GetProcessID", info.GetProcessID())
    printFormat("GetUserID", info.GetUserID())
    printFormat("GetGroupID", info.GetGroupID())
    printFormat("UserIDIsValid", info.UserIDIsValid())
    printFormat("GroupIDIsValid", info.GroupIDIsValid())
    printFormat("GetEffectiveUserID", info.GetEffectiveUserID())
    printFormat("GetEffectiveGroupID", info.GetEffectiveGroupID())
    printFormat("EffectiveUserIDIsValid", info.EffectiveUserIDIsValid())
    printFormat("EffectiveGroupIDIsValid", info.EffectiveGroupIDIsValid())
    printFormat("GetParentProcessID", info.GetParentProcessID())


def pSBThread(obj: Optional[lldb.SBThread]) -> None:
    if obj:
        thread = obj
    else:
        thread = lldb.debugger.GetSelectedTarget().GetProcess().GetSelectedThread()

    printClassName("SBThread")
    printFormat("SBThread", thread)
    printFormat("GetBroadcasterClassName", thread.GetBroadcasterClassName())
    printFormat("IsValid", thread.IsValid())
    printFormat("GetStopReason", thread.GetStopReason())  # StopReason int
    printFormat("GetStopReasonDataCount", thread.GetStopReasonDataCount())
    printFormat("GetStopReturnValue", thread.GetStopReturnValue())  # SBValue
    printFormat("GetStopErrorValue", thread.GetStopErrorValue())  # SBValue
    printFormat("GetThreadID", thread.GetThreadID())
    printFormat("GetIndexID", thread.GetIndexID())
    printFormat("GetName", thread.GetName())
    printFormat("GetQueueName", thread.GetQueueName())
    printFormat("GetQueueID", thread.GetQueueID())
    printFormat("GetQueue", thread.GetQueue())  # SBQueue
    printFormat("IsSuspended", thread.IsSuspended())
    printFormat("IsStopped", thread.IsStopped())
    printFormat("GetNumFrames", thread.GetNumFrames())
    printFormat("GetSelectedFrame", thread.GetSelectedFrame())  # SBFrame
    printFormat("GetProcess", thread.GetProcess())  # SBProcess
    stream = lldb.SBStream()
    thread.GetStatus(stream)
    printFormat("GetStatus", stream.GetData())
    printFormat("GetExtendedBacktraceOriginatingIndexID", thread.GetExtendedBacktraceOriginatingIndexID())
    printFormat("GetCurrentException", thread.GetCurrentException())  # SBValue
    printFormat("GetCurrentExceptionBacktrace", thread.GetCurrentExceptionBacktrace())  # SBValue
    printFormat("SafeToCallFunctions", thread.SafeToCallFunctions())

    printTraversal(thread, "GetStopReasonDataCount", "GetStopReasonDataAtIndex")  # [int]
    printTraversal(thread, "GetNumFrames", "GetFrameAtIndex")  # [SBFrame]


def pSBFrame(obj: Optional[lldb.SBFrame]) -> None:
    if obj:
        frame = obj
    else:
        frame = lldb.debugger.GetSelectedTarget().GetProcess().GetSelectedThread().GetSelectedFrame()

    printClassName("SBFrame")
    printFormat("SBFrame", frame)
    printFormat("IsValid", frame.IsValid())
    printFormat("GetFrameID", frame.GetFrameID())
    printFormat("GetCFA", frame.GetCFA())
    printFormat("GetPC", frame.GetPC())
    printFormat("GetSP", frame.GetSP())
    printFormat("GetFP", frame.GetFP())
    printFormat("GetPCAddress", frame.GetPCAddress())  # SBAddress
    printFormat("GetSymbolContext", frame.GetSymbolContext(lldb.eSymbolContextEverything))  # SBSymbolContext
    printFormat("GetModule", frame.GetModule())  # SBModule
    printFormat("GetCompileUnit", frame.GetCompileUnit())  # SBCompileUnit
    printFormat("GetFunction", frame.GetFunction())  # SBFunction
    printFormat("GetSymbol", frame.GetSymbol())  # SBSymbol
    printFormat("GetBlock", frame.GetBlock())  # SBBlock
    printFormat("GetDisplayFunctionName", frame.GetDisplayFunctionName())
    printFormat("GetFunctionName", frame.GetFunctionName())
    printFormat("GuessLanguage", frame.GuessLanguage())  # LanguageType int
    printFormat("IsSwiftThunk", frame.IsSwiftThunk())
    printFormat("IsInlined", frame.IsInlined())
    printFormat("IsArtificial", frame.IsArtificial())
    printFormat("GetFrameBlock", frame.GetFrameBlock())  # SBBlock
    printFormat("GetLineEntry", frame.GetLineEntry())  # SBLineEntry
    printFormat("GetThread", frame.GetThread())  # SBThread
    printFormat("Disassemble", frame.Disassemble())

    printFormat("GetVariables", frame.GetVariables(True, True, True, False))  # SBValueList
    # printFormat("get_arguments", frame.get_arguments())  # SBValueList
    # printFormat("get_locals", frame.get_locals())  # SBValueList
    # printFormat("get_statics", frame.get_statics())  # SBValueList

    printFormat("GetRegisters", frame.GetRegisters())  # SBValueList
    printFormat("FindVariable", frame.FindVariable("self"))  # SBValue
    printFormat("GetValueForVariablePath", frame.GetValueForVariablePath("self.customVariable"))  # SBValue
    printFormat("get_parent_frame", frame.get_parent_frame())  # SBFrame


def pSBValue(obj: Optional[lldb.SBValue]) -> None:
    if obj:
        value = obj
    else:
        value = lldb.debugger.GetSelectedTarget().GetProcess().GetSelectedThread().GetSelectedFrame().FindVariable("self")

    printClassName("SBValue")
    printFormat("SBValue", value)
    printFormat("IsValid", value.IsValid())
    printFormat("GetError", value.GetError())  # SBError
    printFormat("GetID", value.GetID())
    printFormat("GetName", value.GetName())
    printFormat("GetTypeName", value.GetTypeName())
    printFormat("GetDisplayTypeName", value.GetDisplayTypeName())
    printFormat("GetByteSize", value.GetByteSize())
    printFormat("IsInScope", value.IsInScope())
    printFormat("GetFormat", value.GetFormat())  # Format int
    printFormat("GetValue", value.GetValue())
    printFormat("GetValueAsSigned", value.GetValueAsSigned())
    printFormat("GetValueAsUnsigned", value.GetValueAsUnsigned())
    printFormat("GetValueAsAddress", value.GetValueAsAddress())
    printFormat("GetValueType", value.GetValueType())  # ValueType int
    printFormat("GetValueDidChange", value.GetValueDidChange())
    printFormat("GetSummary", value.GetSummary())
    printFormat("GetObjectDescription", value.GetObjectDescription())
    printFormat("GetTypeValidatorResult", value.GetTypeValidatorResult())
    printFormat("GetStaticValue", value.GetStaticValue())  # SBValue
    printFormat("GetNonSyntheticValue", value.GetNonSyntheticValue())  # SBValue
    printFormat("GetPreferDynamicValue", value.GetPreferDynamicValue())  # DynamicValueType int
    printFormat("GetPreferSyntheticValue", value.GetPreferSyntheticValue())
    printFormat("IsDynamic", value.IsDynamic())
    printFormat("IsSynthetic", value.IsSynthetic())
    printFormat("IsSyntheticChildrenGenerated", value.IsSyntheticChildrenGenerated())
    printFormat("GetLocation", value.GetLocation())
    printFormat("GetTypeFormat", value.GetTypeFormat())  # SBTypeFormat
    printFormat("GetTypeSummary", value.GetTypeSummary())  # SBTypeSummary
    printFormat("GetTypeFilter", value.GetTypeFilter())  # SBTypeFilter
    printFormat("GetTypeSynthetic", value.GetTypeSynthetic())  # SBTypeSynthetic
    printFormat("GetType", value.GetType())  # SBType
    printFormat("GetDeclaration", value.GetDeclaration())  # SBDeclaration
    printFormat("MightHaveChildren", value.MightHaveChildren())
    printFormat("IsRuntimeSupportValue", value.IsRuntimeSupportValue())
    printFormat("GetNumChildren", value.GetNumChildren())
    printFormat("GetOpaqueType", value.GetOpaqueType())
    printFormat("Dereference", value.Dereference())  # SBValue
    printFormat("AddressOf", value.AddressOf())  # SBValue
    printFormat("TypeIsPointerType", value.TypeIsPointerType())
    printFormat("GetTarget", value.GetTarget())  # SBTarget
    printFormat("GetProcess", value.GetProcess())  # SBProcess
    printFormat("GetThread", value.GetThread())  # SBThread
    printFormat("GetFrame", value.GetFrame())  # SBFrame
    printFormat("GetPointeeData", value.GetPointeeData())
    printFormat("GetData", value.GetData())  # SBData
    printFormat("GetLoadAddress", value.GetLoadAddress())
    printFormat("GetAddress", value.GetAddress())  # SBAddress
    printFormat("Persist", value.Persist())  # SBValue
    printFormat("__get_dynamic__", value.__get_dynamic__())  # SBValue
    printFormat("get_expr_path", value.get_expr_path())

    printTraversal(value, "GetNumChildren", "GetChildAtIndex")  # [SBValue]


def pSBSymbolContext(obj: Optional[lldb.SBSymbolContext]) -> None:
    if obj:
        ctx = obj
    else:
        ctx = lldb.debugger.GetSelectedTarget().GetProcess().GetSelectedThread().GetSelectedFrame().GetSymbolContext(lldb.eSymbolContextEverything)
        # ctx = lldb.debugger.GetSelectedTarget().FindFunctions("viewDidLoad")[0]

    printClassName("SBSymbolContext")
    printFormat("SBSymbolContext", ctx)
    printFormat("IsValid", ctx.IsValid())
    printFormat("GetModule", ctx.GetModule())  # SBModule
    printFormat("GetCompileUnit", ctx.GetCompileUnit())  # SBCompileUnit
    printFormat("GetFunction", ctx.GetFunction())  # SBFunction
    printFormat("GetBlock", ctx.GetBlock())  # SBBlock
    printFormat("GetLineEntry", ctx.GetLineEntry())  # SBLineEntry
    printFormat("GetSymbol", ctx.GetSymbol())  # SBSymbol


def pSBModule(obj: Optional[lldb.SBModule]) -> None:
    if obj:
        module = obj
    else:
        module = lldb.debugger.GetSelectedTarget().GetProcess().GetSelectedThread().GetSelectedFrame().GetModule()
        # module = lldb.debugger.GetSelectedTarget().FindFunctions("viewDidLoad")[0].GetModule()

    printClassName("SBModule")
    printFormat("SBModule", module)
    printFormat("IsValid", module.IsValid())
    printFormat("GetFileSpec", module.GetFileSpec())  # SBFileSpec
    printFormat("GetPlatformFileSpec", module.GetPlatformFileSpec())  # SBFileSpec
    printFormat("GetRemoteInstallFileSpec", module.GetRemoteInstallFileSpec())  # SBFileSpec
    printFormat("GetUUIDString", module.GetUUIDString())
    printFormat("GetNumCompileUnits", module.GetNumCompileUnits())
    printFormat("GetNumSymbols", module.GetNumSymbols())
    printFormat("FindSymbol", module.FindSymbol("CGRectMake"))  # SBSymbol
    printFormat("FindSymbols", module.FindSymbols("CGRectMake"))  # SBSymbolContextList
    printFormat("GetNumSections", module.GetNumSections())
    printFormat("GetTypes", module.GetTypes())  # SBTypeList
    printFormat("GetByteOrder", module.GetByteOrder())  # ByteOrder int
    printFormat("GetAddressByteSize", module.GetAddressByteSize())
    printFormat("GetTriple", module.GetTriple())
    printFormat("GetVersion", module.GetVersion())
    printFormat("GetSymbolFileSpec", module.GetSymbolFileSpec())  # SBFileSpec
    printFormat("GetObjectFileHeaderAddress", module.GetObjectFileHeaderAddress())  # SBAddress
    printFormat("GetObjectFileEntryPointAddress", module.GetObjectFileEntryPointAddress())  # SBAddress

    printTraversal(module, "GetNumCompileUnits", "GetCompileUnitAtIndex")  # [SBCompileUnit]
    printTraversal(module, "GetNumSymbols", "GetSymbolAtIndex")  # [SBSymbol]
    printTraversal(module, "GetNumSections", "GetSectionAtIndex")  # [SBSection]


def pSBSymbol(obj: Optional[lldb.SBSymbol]) -> None:
    if obj:
        symbol = obj
    else:
        symbol = lldb.debugger.GetSelectedTarget().GetProcess().GetSelectedThread().GetSelectedFrame().GetSymbol()
        # symbol = lldb.debugger.GetSelectedTarget().FindFunctions("viewDidLoad")[0].GetSymbol()

    printClassName("SBSymbol")
    printFormat("SBSymbol", symbol)
    printFormat("IsValid", symbol.IsValid())
    printFormat("GetName", symbol.GetName())
    printFormat("GetDisplayName", symbol.GetDisplayName())
    printFormat("GetMangledName", symbol.GetMangledName())
    printFormat("GetStartAddress", symbol.GetStartAddress())  # SBAddress
    printFormat("GetEndAddress", symbol.GetEndAddress())  # SBAddress
    printFormat("GetPrologueByteSize", symbol.GetPrologueByteSize())
    printFormat("GetType", symbol.GetType())  # SymbolType int
    printFormat("IsExternal", symbol.IsExternal())
    printFormat("IsSynthetic", symbol.IsSynthetic())
    printFormat("GetInstructions", symbol.GetInstructions(lldb.debugger.GetSelectedTarget()))  # SBInstructionList


def pSBInstruction(obj: Optional[lldb.SBInstruction]) -> None:
    target = lldb.debugger.GetSelectedTarget()

    if obj:
        instruction = obj
    else:
        instructionList = target.GetProcess().GetSelectedThread().GetSelectedFrame().GetSymbol().GetInstructions(lldb.debugger.GetSelectedTarget())
        # instructionList = lldb.debugger.GetSelectedTarget().FindFunctions("viewDidLoad")[0].GetSymbol().GetInstructions(lldb.debugger.GetSelectedTarget())
        instruction = instructionList.GetInstructionAtIndex(0)

    printClassName("SBInstruction")
    printFormat("SBInstruction", instruction)
    printFormat("IsValid", instruction.IsValid())
    printFormat("GetAddress", instruction.GetAddress())  # SBAddress
    printFormat("GetMnemonic", instruction.GetMnemonic(target))
    printFormat("GetOperands", instruction.GetOperands(target))
    printFormat("GetComment", instruction.GetComment(target))
    printFormat("GetData", instruction.GetData(target))  # SBData
    printFormat("GetByteSize", instruction.GetByteSize())
    printFormat("DoesBranch", instruction.DoesBranch())
    printFormat("HasDelaySlot", instruction.HasDelaySlot())
    printFormat("CanSetBreakpoint", instruction.CanSetBreakpoint())


def pSBFunction(obj: Optional[lldb.SBFunction]) -> None:
    if obj:
        func = obj
    else:
        func = lldb.debugger.GetSelectedTarget().GetProcess().GetSelectedThread().GetSelectedFrame().GetFunction()
        # func = lldb.debugger.GetSelectedTarget().FindFunctions("viewDidLoad")[0].GetFunction()

    printClassName("SBFunction")
    printFormat("SBFunction", func)
    printFormat("IsValid", func.IsValid())
    printFormat("GetName", func.GetName())
    printFormat("GetDisplayName", func.GetDisplayName())
    printFormat("GetMangledName", func.GetMangledName())
    printFormat("GetInstructions", func.GetInstructions(lldb.debugger.GetSelectedTarget()))  # SBInstructionList
    printFormat("GetStartAddress", func.GetStartAddress())  # SBAddress
    printFormat("GetEndAddress", func.GetEndAddress())  # SBAddress
    printFormat("GetPrologueByteSize", func.GetPrologueByteSize())
    printFormat("GetArgumentName", func.GetArgumentName(0))
    printFormat("GetType", func.GetType())  # SBType
    printFormat("GetBlock", func.GetBlock())  # SBBlock
    printFormat("GetLanguage", func.GetLanguage())  # LanguageType int
    printFormat("GetIsOptimized", func.GetIsOptimized())
    printFormat("GetCanThrow", func.GetCanThrow())


def pSBBlock(obj: Optional[lldb.SBBlock]) -> None:
    if obj:
        block = obj
    else:
        block = lldb.debugger.GetSelectedTarget().GetProcess().GetSelectedThread().GetSelectedFrame().GetBlock()
        # block = lldb.debugger.GetSelectedTarget().GetProcess().GetSelectedThread().GetSelectedFrame().GetFrameBlock()
        # block = lldb.debugger.GetSelectedTarget().GetProcess().GetSelectedThread().GetSelectedFrame().GetFunction().GetBlock()
        # block = lldb.debugger.GetSelectedTarget().FindFunctions("viewDidLoad")[0].GetBlock()

    printClassName("SBBlock")
    printFormat("SBBlock", block)
    printFormat("IsInlined", block.IsInlined())
    printFormat("IsValid", block.IsValid())
    printFormat("GetInlinedName", block.GetInlinedName())
    printFormat("GetInlinedCallSiteFile", block.GetInlinedCallSiteFile())  # SBFileSpec
    printFormat("GetInlinedCallSiteLine", block.GetInlinedCallSiteLine())
    printFormat("GetInlinedCallSiteColumn", block.GetInlinedCallSiteColumn())
    printFormat("GetParent", block.GetParent())  # SBBlock
    printFormat("GetContainingInlinedBlock", block.GetContainingInlinedBlock())  # SBBlock
    printFormat("GetSibling", block.GetSibling())  # SBBlock
    printFormat("GetFirstChild", block.GetFirstChild())  # SBBlock
    printFormat("GetNumRanges", block.GetNumRanges())
    printFormat("GetRangeStartAddress", block.GetRangeStartAddress(0))  # SBAddress


def pSBCompileUnit(obj: Optional[lldb.SBCompileUnit]) -> None:
    if obj:
        unit = obj
    else:
        unit = lldb.debugger.GetSelectedTarget().GetProcess().GetSelectedThread().GetSelectedFrame().GetCompileUnit()
        # unit = lldb.debugger.GetSelectedTarget().FindFunctions("viewDidLoad")[0].GetCompileUnit()

    printClassName("SBCompileUnit")
    printFormat("SBCompileUnit", unit)
    printFormat("IsValid", unit.IsValid())
    printFormat("GetFileSpec", unit.GetFileSpec())  # SBFileSpec
    printFormat("GetNumLineEntries", unit.GetNumLineEntries())
    printFormat("GetNumSupportFiles", unit.GetNumSupportFiles())
    printFormat("GetTypes", unit.GetTypes())  # SBTypeList
    printFormat("GetLanguage", unit.GetLanguage())  # LanguageType int


    printTraversal(unit, "GetNumLineEntries", "GetLineEntryAtIndex")  # [SBLineEntry]
    printTraversal(unit, "GetNumSupportFiles", "GetSupportFileAtIndex")  # [SBFileSpec]


def pSBLineEntry(obj: Optional[lldb.SBLineEntry]) -> None:
    if obj:
        le = obj
    else:
        le = lldb.debugger.GetSelectedTarget().GetProcess().GetSelectedThread().GetSelectedFrame().GetLineEntry()
        # le = lldb.debugger.GetSelectedTarget().FindFunctions("viewDidLoad")[0].GetLineEntry()
        # le = lldb.debugger.GetSelectedTarget().GetProcess().GetSelectedThread().GetSelectedFrame().GetCompileUnit().GetLineEntryAtIndex(0)

    printClassName("SBLineEntry")
    printFormat("SBLineEntry", le)
    printFormat("IsValid", le.IsValid())
    printFormat("GetStartAddress", le.GetStartAddress())  # SBAddress
    printFormat("GetEndAddress", le.GetEndAddress())  # SBAddress
    printFormat("GetFileSpec", le.GetFileSpec())  # SBFileSpec
    printFormat("GetLine", le.GetLine())
    printFormat("GetColumn", le.GetColumn())


def pSBFileSpec(obj: Optional[lldb.SBFileSpec]) -> None:
    if obj:
        fileSpec = obj
    else:
        fileSpec = lldb.debugger.GetSelectedTarget().GetExecutable()
        # fileSpec = lldb.debugger.GetSelectedTarget().GetLaunchInfo().GetExecutableFile()
        # fileSpec = lldb.debugger.GetSelectedTarget().GetProcess().GetSelectedThread().GetSelectedFrame().GetModule().GetFileSpec()
        # fileSpec = lldb.debugger.GetSelectedTarget().GetProcess().GetSelectedThread().GetSelectedFrame().GetCompileUnit().GetFileSpec()

    printClassName("SBFileSpec")
    printFormat("SBFileSpec", fileSpec)
    printFormat("IsValid", fileSpec.IsValid())
    printFormat("Exists", fileSpec.Exists())
    printFormat("ResolveExecutableLocation", fileSpec.ResolveExecutableLocation())
    printFormat("GetFilename", fileSpec.GetFilename())
    printFormat("GetDirectory", fileSpec.GetDirectory())
    printFormat("fullpath", fileSpec.fullpath)


def pSBAddress(obj: Optional[lldb.SBAddress]) -> None:
    if obj:
        address = obj
    else:
        address = lldb.debugger.GetSelectedTarget().GetProcess().GetSelectedThread().GetSelectedFrame().GetPCAddress()
        # address = lldb.debugger.GetSelectedTarget().FindFunctions("viewDidLoad")[0].GetSymbol().GetStartAddress()
        # address = lldb.debugger.GetSelectedTarget().GetProcess().GetSelectedThread().GetSelectedFrame().FindVariable("self").GetAddress()
        # address = lldb.debugger.GetSelectedTarget().GetProcess().GetSelectedThread().GetSelectedFrame().GetModule().GetObjectFileHeaderAddress()
        # address = lldb.debugger.GetSelectedTarget().GetProcess().GetSelectedThread().GetSelectedFrame().GetLineEntry().GetStartAddress()
        # address = lldb.debugger.GetSelectedTarget().GetProcess().GetSelectedThread().GetSelectedFrame().GetFunction().GetStartAddress()

    printClassName("SBAddress")
    printFormat("SBAddress", address)
    printFormat("IsValid", address.IsValid())
    printFormat("GetFileAddress", address.GetFileAddress())
    printFormat("GetSection", address.GetSection())  # SBSection
    printFormat("GetOffset", address.GetOffset())
    printFormat("GetSymbolContext", address.GetSymbolContext(lldb.eSymbolContextEverything))  # SBSymbolContext
    printFormat("GetModule", address.GetModule())  # SBModule
    printFormat("GetCompileUnit", address.GetCompileUnit())  # SBCompileUnit
    printFormat("GetFunction", address.GetFunction())  # SBFunction
    printFormat("GetBlock", address.GetBlock())  # SBBlock
    printFormat("GetSymbol", address.GetSymbol())  # SBSymbol
    printFormat("GetLineEntry", address.GetLineEntry())  # SBLineEntry


def pSBBreakpoint(obj: Optional[lldb.SBBreakpoint]) -> None:
    if obj:
        bp = obj
    else:
        bp = lldb.debugger.GetSelectedTarget().GetBreakpointAtIndex(0)

    printClassName("SBBreakpoint")
    printFormat("SBBreakpoint", bp)
    printFormat("GetID", bp.GetID())
    printFormat("IsValid", bp.IsValid())
    printFormat("IsEnabled", bp.IsEnabled())
    printFormat("IsOneShot", bp.IsOneShot())
    printFormat("IsInternal", bp.IsInternal())
    printFormat("GetHitCount", bp.GetHitCount())
    printFormat("GetIgnoreCount", bp.GetIgnoreCount())
    printFormat("GetCondition", bp.GetCondition())
    printFormat("GetAutoContinue", bp.GetAutoContinue())
    printFormat("GetThreadID", bp.GetThreadID())
    printFormat("GetThreadIndex", bp.GetThreadIndex())
    printFormat("GetThreadName", bp.GetThreadName())
    printFormat("GetQueueName", bp.GetQueueName())
    printFormat("GetNumLocations", bp.GetNumLocations())
    printFormat("IsHardware", bp.IsHardware())

    printTraversal(bp, "GetNumLocations", "GetLocationAtIndex")  # [SBBreakpointLocation]


def pSBError(obj: Optional[lldb.SBError]) -> None:
    if obj:
        error = obj
    else:
        error = lldb.debugger.GetSelectedTarget().GetProcess().GetSelectedThread().GetSelectedFrame().FindVariable("self").GetError()

    printClassName("SBError")
    printFormat("SBError", error)
    printFormat("GetCString", error.GetCString())
    printFormat("Fail", error.Fail())
    printFormat("Success", error.Success())
    printFormat("GetError", error.GetError())
    printFormat("GetType", error.GetType())  # ErrorType int
    printFormat("IsValid", error.IsValid())


def pSBType(obj: Optional[lldb.SBType]) -> None:
    if obj:
        t = obj
    else:
        t = lldb.debugger.GetSelectedTarget().GetProcess().GetSelectedThread().GetSelectedFrame().GetFunction().GetType()
        # t = lldb.debugger.GetSelectedTarget().GetProcess().GetSelectedThread().GetSelectedFrame().FindVariable("self").GetType()
        # t = lldb.debugger.GetSelectedTarget().FindFirstType("UIAlertAction")

    printClassName("SBType")
    printFormat("SBType", t)
    printFormat("IsValid", t.IsValid())
    printFormat("GetByteSize", t.GetByteSize())
    printFormat("IsPointerType", t.IsPointerType())
    printFormat("IsReferenceType", t.IsReferenceType())
    printFormat("IsFunctionType", t.IsFunctionType())
    printFormat("IsPolymorphicClass", t.IsPolymorphicClass())
    printFormat("IsArrayType", t.IsArrayType())
    printFormat("IsVectorType", t.IsVectorType())
    printFormat("IsTypedefType", t.IsTypedefType())
    printFormat("IsAnonymousType", t.IsAnonymousType())
    printFormat("GetPointerType", t.GetPointerType())  # SBType
    printFormat("GetPointeeType", t.GetPointeeType())  # SBType
    printFormat("GetReferenceType", t.GetReferenceType())  # SBType
    printFormat("GetTypedefedType", t.GetTypedefedType())  # SBType
    printFormat("GetDereferencedType", t.GetDereferencedType())  # SBType
    printFormat("GetUnqualifiedType", t.GetUnqualifiedType())  # SBType
    printFormat("GetCanonicalType", t.GetCanonicalType())  # SBType
    printFormat("GetArrayElementType", t.GetArrayElementType())  # SBType
    printFormat("GetVectorElementType", t.GetVectorElementType())  # SBType
    printFormat("GetBasicType", t.GetBasicType())  # BasicType int
    printFormat("GetNumberOfFields", t.GetNumberOfFields())
    printFormat("GetNumberOfDirectBaseClasses", t.GetNumberOfDirectBaseClasses())
    printFormat("GetNumberOfVirtualBaseClasses", t.GetNumberOfVirtualBaseClasses())
    printFormat("GetEnumMembers", t.GetEnumMembers())  # SBTypeEnumMemberList
    printFormat("GetName", t.GetName())
    printFormat("GetDisplayTypeName", t.GetDisplayTypeName())
    printFormat("GetTypeClass", t.GetTypeClass())  # TypeClass int
    printFormat("GetNumberOfTemplateArguments", t.GetNumberOfTemplateArguments())
    printFormat("GetFunctionReturnType", t.GetFunctionReturnType())  # SBType
    printFormat("GetFunctionArgumentTypes", t.GetFunctionArgumentTypes())  # SBTypeList
    printFormat("GetNumberOfMemberFunctions", t.GetNumberOfMemberFunctions())
    printFormat("IsTypeComplete", t.IsTypeComplete())
    printFormat("GetTypeFlags", t.GetTypeFlags())

    printTraversal(t, "GetNumberOfFields", "GetFieldAtIndex")  # [SBTypeMember]
    printTraversal(t, "GetNumberOfDirectBaseClasses", "GetDirectBaseClassAtIndex")  # [SBTypeMember]
    printTraversal(t, "GetNumberOfVirtualBaseClasses", "GetVirtualBaseClassAtIndex")  # [SBTypeMember]
    printTraversal(t, "GetNumberOfTemplateArguments", "GetTemplateArgumentType")  # [SBType]
    printTraversal(t, "GetNumberOfMemberFunctions", "GetMemberFunctionAtIndex")  # [SBTypeMemberFunction]


def pSBTypeMemberFunction(obj: Optional[lldb.SBTypeMemberFunction]) -> None:
    if obj:
        func = obj
    else:
        func = lldb.debugger.GetSelectedTarget().GetProcess().GetSelectedThread().GetSelectedFrame().FindVariable("self").GetType().GetMemberFunctionAtIndex(0)
        # func = lldb.debugger.GetSelectedTarget().FindFirstType("UIAlertAction").GetMemberFunctionAtIndex(0)

    printClassName("SBTypeMemberFunction")
    printFormat("SBTypeMemberFunction", func)
    printFormat("IsValid", func.IsValid())
    printFormat("GetName", func.GetName())
    printFormat("GetDemangledName", func.GetDemangledName())
    printFormat("GetMangledName", func.GetMangledName())
    printFormat("GetType", func.GetType())  # SBType
    printFormat("GetReturnType", func.GetReturnType())  # SBType
    printFormat("GetNumberOfArguments", func.GetNumberOfArguments())
    printFormat("GetKind", func.GetKind())  # MemberFunctionKind int

    printTraversal(func, "GetNumberOfArguments", "GetArgumentTypeAtIndex")  # [SBType]


def pSBTypeCategory(obj: Optional[lldb.SBTypeCategory]) -> None:
    if obj:
        category = obj
    else:
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


def pSBPlatform(obj: Optional[lldb.SBPlatform]) -> None:
    if obj:
        platform = obj
    else:
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


def pSBBroadcaster(obj: Optional[lldb.SBBroadcaster]) -> None:
    if obj:
        broadcaster = obj
    else:
        broadcaster = lldb.debugger.GetCommandInterpreter().GetBroadcaster()
        # broadcaster = lldb.debugger.GetSelectedTarget().GetBroadcaster()
        # broadcaster = lldb.debugger.GetSelectedTarget().GetProcess().GetBroadcaster()

    printClassName("SBBroadcaster")
    printFormat("SBBroadcaster", broadcaster)
    printFormat("IsValid", broadcaster.IsValid())
    printFormat("GetName", broadcaster.GetName())


def pSBListener(obj: Optional[lldb.SBListener]) -> None:
    if obj:
        listener = obj
    else:
        listener = lldb.debugger.GetListener()
        # listener = lldb.debugger.GetSelectedTarget().GetLaunchInfo().GetListener()

    printClassName("SBListener")
    printFormat("SBListener", listener)
    printFormat("IsValid", listener.IsValid())


def pSBSourceManager(obj: Optional[lldb.SBSourceManager]) -> None:
    if obj:
        manager = obj
    else:
        manager = lldb.debugger.GetSourceManager()
        # manager = lldb.debugger.GetSelectedTarget().GetSourceManager()

    printClassName("SBSourceManager")
    printFormat("SBSourceManager", manager)


def pSBStructuredData(obj: Optional[lldb.SBStructuredData]) -> None:
    if obj:
        sd = obj
    else:
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
    stream = lldb.SBStream()
    sd.GetAsJSON(stream)
    printFormat("GetAsJSON", stream.GetData())


def pSBUnixSignals(obj: Optional[lldb.SBUnixSignals]) -> None:
    if obj:
        signals = obj
    else:
        signals = lldb.debugger.GetSelectedPlatform().GetUnixSignals()
        # signals = lldb.debugger.GetSelectedTarget().GetProcess().GetUnixSignals()

    printClassName("SBUnixSignals")
    printFormat("SBUnixSignals", signals)
    printFormat("IsValid", signals.IsValid())
    printFormat("GetNumSignals", signals.GetNumSignals())

    printTraversal(signals, "GetNumSignals", "GetSignalAtIndex")  # [int]


def pSBLaunchInfo(obj: Optional[lldb.SBLaunchInfo]) -> None:
    if obj:
        info = obj
    else:
        info = lldb.debugger.GetSelectedTarget().GetLaunchInfo()

    printClassName("SBLaunchInfo")
    printFormat("SBLaunchInfo", info)
    printFormat("GetProcessID", info.GetProcessID())
    printFormat("GetUserID", info.GetUserID())
    printFormat("GetGroupID", info.GetGroupID())
    printFormat("UserIDIsValid", info.UserIDIsValid())
    printFormat("GroupIDIsValid", info.GroupIDIsValid())
    printFormat("GetExecutableFile", info.GetExecutableFile())  # SBFileSpec
    printFormat("GetListener", info.GetListener())  # SBListener
    printFormat("GetNumArguments", info.GetNumArguments())
    printFormat("GetNumEnvironmentEntries", info.GetNumEnvironmentEntries())
    printFormat("GetWorkingDirectory", info.GetWorkingDirectory())
    printFormat("GetLaunchFlags", info.GetLaunchFlags())
    printFormat("GetProcessPluginName", info.GetProcessPluginName())
    printFormat("GetShell", info.GetShell())
    printFormat("GetShellExpandArguments", info.GetShellExpandArguments())
    printFormat("GetResumeCount", info.GetResumeCount())
    printFormat("GetLaunchEventData", info.GetLaunchEventData())
    printFormat("GetDetachOnError", info.GetDetachOnError())

    printTraversal(info, "GetNumArguments", "GetArgumentAtIndex")  # [str]
    printTraversal(info, "GetNumEnvironmentEntries", "GetEnvironmentEntryAtIndex")  # [str]


def pSBCommandInterpreter(obj: Optional[lldb.SBCommandInterpreter]) -> None:
    if obj:
        ci = obj
    else:
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


def pSBQueue(obj: Optional[lldb.SBQueue]) -> None:
    if obj:
        queue = obj
    else:
        queue = lldb.debugger.GetSelectedTarget().GetProcess().GetSelectedThread().GetQueue()
        # queue = lldb.debugger.GetSelectedTarget().GetProcess().GetQueueAtIndex(0)

    printClassName("SBQueue")
    printFormat("SBQueue", queue)
    printFormat("IsValid", queue.IsValid())
    printFormat("GetProcess", queue.GetProcess())  # SBProcess
    printFormat("GetQueueID", queue.GetQueueID())
    printFormat("GetName", queue.GetName())
    printFormat("GetKind", queue.GetKind())
    printFormat("GetIndexID", queue.GetIndexID())
    printFormat("GetNumThreads", queue.GetNumThreads())
    printFormat("GetNumPendingItems", queue.GetNumPendingItems())
    printFormat("GetNumRunningItems", queue.GetNumRunningItems())

    printTraversal(queue, "GetNumThreads", "GetThreadAtIndex")
    printTraversal(queue, "GetNumPendingItems", "GetPendingItemAtIndex")  # [SBQueueItem]


def pSBSection(obj: Optional[lldb.SBSection]) -> None:
    if obj:
        section = obj
    else:
        section = lldb.debugger.GetSelectedTarget().GetProcess().GetSelectedThread().GetSelectedFrame().GetModule().FindSection("__TEXT")

    printClassName("SBSection")
    printFormat("SBSection", section)
    printFormat("IsValid", section.IsValid())
    printFormat("GetName", section.GetName())
    printFormat("GetParent", section.GetParent())  # SBSection
    printFormat("GetNumSubSections", section.GetNumSubSections())
    printFormat("GetFileAddress", section.GetFileAddress())
    printFormat("GetByteSize", section.GetByteSize())
    printFormat("GetFileOffset", section.GetFileOffset())
    printFormat("GetFileByteSize", section.GetFileByteSize())
    # printFormat("GetSectionData", section.GetSectionData())  # SBData
    printFormat("GetSectionType", section.GetSectionType())  # SectionType int
    printFormat("GetPermissions", section.GetPermissions())
    printFormat("GetTargetByteSize", section.GetTargetByteSize())
    printFormat("get_addr", section.get_addr())  # SBAddress

    printTraversal(section, "GetNumSubSections", "GetSubSectionAtIndex")  # [SBSection]


def pSBExpressionOptions(obj: Optional[lldb.SBExpressionOptions]) -> None:
    if obj:
        options = obj
    else:
        options = lldb.SBExpressionOptions()

    printClassName("SBExpressionOptions")
    printFormat("SBExpressionOptions", options)
    printFormat("GetCoerceResultToId", options.GetCoerceResultToId())
    printFormat("GetUnwindOnError", options.GetUnwindOnError())
    printFormat("GetIgnoreBreakpoints", options.GetIgnoreBreakpoints())
    printFormat("GetFetchDynamicValue", options.GetFetchDynamicValue())
    printFormat("GetTimeoutInMicroSeconds", options.GetTimeoutInMicroSeconds())
    printFormat("GetOneThreadTimeoutInMicroSeconds", options.GetOneThreadTimeoutInMicroSeconds())
    printFormat("GetTryAllThreads", options.GetTryAllThreads())
    printFormat("GetStopOthers", options.GetStopOthers())
    printFormat("GetTrapExceptions", options.GetTrapExceptions())
    printFormat("GetPlaygroundTransformEnabled", options.GetPlaygroundTransformEnabled())
    printFormat("GetREPLMode", options.GetREPLMode())
    printFormat("GetGenerateDebugInfo", options.GetGenerateDebugInfo())
    printFormat("GetSuppressPersistentResult", options.GetSuppressPersistentResult())
    printFormat("GetPrefix", options.GetPrefix())
    printFormat("GetAutoApplyFixIts", options.GetAutoApplyFixIts())
    printFormat("GetTopLevel", options.GetTopLevel())
    printFormat("GetAllowJIT", options.GetAllowJIT())
