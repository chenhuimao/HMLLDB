# The MIT License (MIT)
#
# Copyright (c) 2020 Huimao Chen
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# https://github.com/chenhuimao/HMLLDB

import lldb
from typing import Optional, Dict
import optparse
import shlex
import HMLLDBHelpers as HM


def __lldb_init_module(debugger, internal_dict):
    debugger.HandleCommand('command script add -f HMLLDBClassInfo.print_lldb_class_info plldbClassInfo -h "Print infomation of lldb class."')


g_last_command = ""
g_unlimited = False


def print_lldb_class_info(debugger, command, exe_ctx, result, internal_dict):
    """
    Syntax:
        plldbClassInfo [--entire] <className/all>

    Options:
        --entire/-e; Print all elements of the list, otherwise only 100

    Examples:
        (lldb) plldbClassInfo all
        (lldb) plldbClassInfo SBDebugger
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
        HM.DPrint("Error input, plase enter 'help plldbClassInfo' for more infomation")
        return

    global g_unlimited
    g_unlimited = options.entire

    global g_last_command
    g_last_command = args[0]

    if compare_name("SBHostOS"):
        pSBHostOS(None)

    if compare_name("SBDebugger"):
        pSBDebugger(None)
    if compare_name("SBTarget"):
        pSBTarget(None)
    if compare_name("SBProcess"):
        pSBProcess(None)
    if compare_name("SBProcessInfo"):
        pSBProcessInfo(None)
    if compare_name("SBThread"):
        pSBThread(None)
    if compare_name("SBThreadPlan"):
        pSBThreadPlan(None)
    if compare_name("SBFrame"):
        pSBFrame(None)
    if compare_name("SBValue"):
        pSBValue(None)

    if compare_name("SBSymbolContext"):
        pSBSymbolContext(None)
    if compare_name("SBModule"):
        pSBModule(None)
    if compare_name("SBSymbol"):
        pSBSymbol(None)
    if compare_name("SBInstruction"):
        pSBInstruction(None)
    if compare_name("SBFunction"):
        pSBFunction(None)
    if compare_name("SBBlock"):
        pSBBlock(None)
    if compare_name("SBCompileUnit"):
        pSBCompileUnit(None)
    if compare_name("SBLineEntry"):
        pSBLineEntry(None)

    if compare_name("SBFile"):
        pSBFile(None)
    if compare_name("SBFileSpec"):
        pSBFileSpec(None)
    if compare_name("SBAddress"):
        pSBAddress(None)
    if compare_name("SBBreakpoint"):
        pSBBreakpoint(None)
    if compare_name("SBBreakpointLocation"):
        pSBBreakpointLocation(None)
    if compare_name("SBError"):
        pSBError(None)

    if compare_name("SBType"):
        pSBType(None)
    if compare_name("SBTypeMemberFunction"):
        pSBTypeMemberFunction(None)
    if compare_name("SBTypeCategory"):
        pSBTypeCategory(None)

    if compare_name("SBBroadcaster"):
        pSBBroadcaster(None)
    if compare_name("SBListener"):
        pSBListener(None)
    if compare_name("SBEvent"):
        pSBEvent(None)
    if compare_name("SBStructuredData"):
        pSBStructuredData(None)

    if compare_name("SBPlatform"):
        pSBPlatform(None)
    if compare_name("SBSourceManager"):
        pSBSourceManager(None)
    if compare_name("SBUnixSignals"):
        pSBUnixSignals(None)
    if compare_name("SBLaunchInfo"):
        pSBLaunchInfo(None)
    if compare_name("SBEnvironment"):
        pSBEnvironment(None)
    if compare_name("SBCommandInterpreter"):
        pSBCommandInterpreter(None)
    if compare_name("SBCommandReturnObject"):
        pSBCommandReturnObject(None)
    if compare_name("SBQueue"):
        pSBQueue(None)
    if compare_name("SBSection"):
        pSBSection(None)
    if compare_name("SBMemoryRegionInfoList"):
        pSBMemoryRegionInfoList(None)
    if compare_name("SBMemoryRegionInfo"):
        pSBMemoryRegionInfo(None)
    if compare_name("SBExpressionOptions"):
        pSBExpressionOptions(None)


def compare_name(class_name: str) -> bool:
    global g_last_command
    if g_last_command.lower() in class_name.lower() or g_last_command.lower() == "all":
        return True
    else:
        return False


def generate_option_parser() -> optparse.OptionParser:
    usage = "usage: plldbClassInfo [--entire] <className/all>"
    parser = optparse.OptionParser(usage=usage, prog="plldbClassInfo")

    parser.add_option("-e", "--entire",
                      action="store_true",
                      default=False,
                      dest="entire",
                      help="Print all elements of the list, otherwise only 100")

    return parser


def print_format(desc: str, value: object) -> None:
    print(f"[{desc}]: {value}\n\ttype: {type(value)}")


def print_class_name(title: str) -> None:
    print(f"\n\n====={title}================================")


def print_traversal(obj: object, get_size: str, get_elem: str) -> None:
    size = getattr(obj, get_size)
    elem = getattr(obj, get_elem)
    global g_unlimited

    print(f"\n##### [{get_elem}]({size()}) #####")

    for i in range(size()):
        if i == 100 and not g_unlimited:
            break
        if i == 0:
            print(type(elem(i)))
        print(elem(i))


def get_string_from_SBStringList(string_list: lldb.SBStringList) -> str:
    size = string_list.GetSize()
    result = ""
    for i in range(size):
        result += "\n" + string_list.GetStringAtIndex(i)
    return result


def get_string_from_byte_order(order: int) -> str:
    result = 'unknown'
    if order == lldb.eByteOrderInvalid:
        result = 'eByteOrderInvalid'
    elif order == lldb.eByteOrderBig:
        result = 'eByteOrderBig'
    elif order == lldb.eByteOrderPDP:
        result = 'eByteOrderPDP'
    elif order == lldb.eByteOrderLittle:
        result = 'eByteOrderLittle'
    return result


def get_string_from_symbol_type(symbol_type: int) -> str:
    if symbol_type == lldb.eSymbolTypeInvalid:
        return "eSymbolTypeInvalid"
    elif symbol_type == lldb.eSymbolTypeAbsolute:
        return "eSymbolTypeAbsolute"
    elif symbol_type == lldb.eSymbolTypeCode:
        return "eSymbolTypeCode"
    elif symbol_type == lldb.eSymbolTypeResolver:
        return "eSymbolTypeResolver"
    elif symbol_type == lldb.eSymbolTypeData:
        return "eSymbolTypeData"
    elif symbol_type == lldb.eSymbolTypeTrampoline:
        return "eSymbolTypeTrampoline"
    elif symbol_type == lldb.eSymbolTypeRuntime:
        return "eSymbolTypeRuntime"
    elif symbol_type == lldb.eSymbolTypeException:
        return "eSymbolTypeException"
    elif symbol_type == lldb.eSymbolTypeSourceFile:
        return "eSymbolTypeSourceFile"
    elif symbol_type == lldb.eSymbolTypeHeaderFile:
        return "eSymbolTypeHeaderFile"
    elif symbol_type == lldb.eSymbolTypeObjectFile:
        return "eSymbolTypeObjectFile"
    elif symbol_type == lldb.eSymbolTypeCommonBlock:
        return "eSymbolTypeCommonBlock"
    elif symbol_type == lldb.eSymbolTypeBlock:
        return "eSymbolTypeBlock"
    elif symbol_type == lldb.eSymbolTypeLocal:
        return "eSymbolTypeLocal"
    elif symbol_type == lldb.eSymbolTypeParam:
        return "eSymbolTypeParam"
    elif symbol_type == lldb.eSymbolTypeVariable:
        return "eSymbolTypeVariable"
    elif symbol_type == lldb.eSymbolTypeVariableType:
        return "eSymbolTypeVariableType"
    elif symbol_type == lldb.eSymbolTypeLineEntry:
        return "eSymbolTypeLineEntry"
    elif symbol_type == lldb.eSymbolTypeLineHeader:
        return "eSymbolTypeLineHeader"
    elif symbol_type == lldb.eSymbolTypeScopeBegin:
        return "eSymbolTypeScopeBegin"
    elif symbol_type == lldb.eSymbolTypeScopeEnd:
        return "eSymbolTypeScopeEnd"
    elif symbol_type == lldb.eSymbolTypeAdditional:
        return "eSymbolTypeAdditional"
    elif symbol_type == lldb.eSymbolTypeCompiler:
        return "eSymbolTypeCompiler"
    elif symbol_type == lldb.eSymbolTypeInstrumentation:
        return "eSymbolTypeInstrumentation"
    elif symbol_type == lldb.eSymbolTypeUndefined:
        return "eSymbolTypeUndefined"
    elif symbol_type == lldb.eSymbolTypeObjCClass:
        return "eSymbolTypeObjCClass"
    elif symbol_type == lldb.eSymbolTypeObjCMetaClass:
        return "eSymbolTypeObjCMetaClass"
    elif symbol_type == lldb.eSymbolTypeObjCIVar:
        return "eSymbolTypeObjCIVar"
    elif symbol_type == lldb.eSymbolTypeReExported:
        return "eSymbolTypeReExported"
    elif symbol_type == lldb.eSymbolTypeASTFile:
        return "eSymbolTypeASTFile"
    return "unknown"


def get_string_from_stop_reason(stop_reason: int) -> str:
    if stop_reason == lldb.eStopReasonInvalid:
        return 'eStopReasonInvalid'
    elif stop_reason == lldb.eStopReasonNone:
        return 'eStopReasonNone'
    elif stop_reason == lldb.eStopReasonTrace:
        return 'eStopReasonTrace'
    elif stop_reason == lldb.eStopReasonBreakpoint:
        return 'eStopReasonBreakpoint'
    elif stop_reason == lldb.eStopReasonWatchpoint:
        return 'eStopReasonWatchpoint'
    elif stop_reason == lldb.eStopReasonSignal:
        return 'eStopReasonSignal'
    elif stop_reason == lldb.eStopReasonException:
        return 'eStopReasonException'
    elif stop_reason == lldb.eStopReasonExec:
        return 'eStopReasonExec'
    elif stop_reason == lldb.eStopReasonPlanComplete:
        return 'eStopReasonPlanComplete'
    elif stop_reason == lldb.eStopReasonThreadExiting:
        return 'eStopReasonThreadExiting'
    elif stop_reason == lldb.eStopReasonInstrumentation:
        return 'eStopReasonInstrumentation'
    elif stop_reason == lldb.eStopReasonProcessorTrace:
        return 'eStopReasonProcessorTrace'
    elif stop_reason == lldb.eStopReasonFork:
        return 'eStopReasonFork'
    elif stop_reason == lldb.eStopReasonVFork:
        return 'eStopReasonVFork'
    elif stop_reason == lldb.eStopReasonVForkDone:
        return 'eStopReasonVForkDone'
    return "unknown"


def get_string_from_instruction_control_flow_kind(kind: int) -> str:
    if kind == lldb.eInstructionControlFlowKindUnknown:
        return 'eInstructionControlFlowKindUnknown'
    elif kind == lldb.eInstructionControlFlowKindOther:
        return 'eInstructionControlFlowKindOther'
    elif kind == lldb.eInstructionControlFlowKindCall:
        return 'eInstructionControlFlowKindCall'
    elif kind == lldb.eInstructionControlFlowKindReturn:
        return 'eInstructionControlFlowKindReturn'
    elif kind == lldb.eInstructionControlFlowKindJump:
        return 'eInstructionControlFlowKindJump'
    elif kind == lldb.eInstructionControlFlowKindCondJump:
        return 'eInstructionControlFlowKindCondJump'
    elif kind == lldb.eInstructionControlFlowKindFarCall:
        return 'eInstructionControlFlowKindFarCall'
    elif kind == lldb.eInstructionControlFlowKindFarReturn:
        return 'eInstructionControlFlowKindFarReturn'
    elif kind == lldb.eInstructionControlFlowKindFarJump:
        return 'eInstructionControlFlowKindFarJump'
    return "unknown"


def get_string_from_structured_data_type(structured_data_type: int) -> str:
    structured_data_type_dic: Dict[int, str] = {
        lldb.eStructuredDataTypeInvalid: "eStructuredDataTypeInvalid",
        lldb.eStructuredDataTypeNull: "eStructuredDataTypeNull",
        lldb.eStructuredDataTypeGeneric: "eStructuredDataTypeGeneric",
        lldb.eStructuredDataTypeArray: "eStructuredDataTypeArray",
        lldb.eStructuredDataTypeInteger: "eStructuredDataTypeInteger",
        lldb.eStructuredDataTypeFloat: "eStructuredDataTypeFloat",
        lldb.eStructuredDataTypeBoolean: "eStructuredDataTypeBoolean",
        lldb.eStructuredDataTypeString: "eStructuredDataTypeString",
        lldb.eStructuredDataTypeDictionary: "eStructuredDataTypeDictionary",
        lldb.eStructuredDataTypeSignedInteger: "eStructuredDataTypeSignedInteger",
        lldb.eStructuredDataTypeUnsignedInteger: "eStructuredDataTypeUnsignedInteger"
    }
    return structured_data_type_dic.get(structured_data_type, "unknown")


def get_string_from_return_status(return_status: int) -> str:
    if return_status == lldb.eReturnStatusInvalid:
        return 'eReturnStatusInvalid'
    elif return_status == lldb.eReturnStatusSuccessFinishNoResult:
        return 'eReturnStatusSuccessFinishNoResult'
    elif return_status == lldb.eReturnStatusSuccessFinishResult:
        return 'eReturnStatusSuccessFinishResult'
    elif return_status == lldb.eReturnStatusSuccessContinuingNoResult:
        return 'eReturnStatusSuccessContinuingNoResult'
    elif return_status == lldb.eReturnStatusSuccessContinuingResult:
        return 'eReturnStatusSuccessContinuingResult'
    elif return_status == lldb.eReturnStatusStarted:
        return 'eReturnStatusStarted'
    elif return_status == lldb.eReturnStatusFailed:
        return 'eReturnStatusFailed'
    elif return_status == lldb.eReturnStatusQuit:
        return 'eReturnStatusQuit'
    return 'unknown'


def get_string_from_section_type(section_type: int) -> str:
    section_type_dic: Dict[int, str] = {
        lldb.eSectionTypeInvalid: "eSectionTypeInvalid",
        lldb.eSectionTypeCode: "eSectionTypeCode",
        lldb.eSectionTypeContainer: "eSectionTypeContainer",
        lldb.eSectionTypeData: "eSectionTypeData",
        lldb.eSectionTypeDataCString: "eSectionTypeDataCString",
        lldb.eSectionTypeDataCStringPointers: "eSectionTypeDataCStringPointers",
        lldb.eSectionTypeDataSymbolAddress: "eSectionTypeDataSymbolAddress",
        lldb.eSectionTypeData4: "eSectionTypeData4",
        lldb.eSectionTypeData8: "eSectionTypeData8",
        lldb.eSectionTypeData16: "eSectionTypeData16",
        lldb.eSectionTypeDataPointers: "eSectionTypeDataPointers",
        lldb.eSectionTypeDebug: "eSectionTypeDebug",
        lldb.eSectionTypeZeroFill: "eSectionTypeZeroFill",
        lldb.eSectionTypeDataObjCMessageRefs: "eSectionTypeDataObjCMessageRefs",
        lldb.eSectionTypeDataObjCCFStrings: "eSectionTypeDataObjCCFStrings",
        lldb.eSectionTypeDWARFDebugAbbrev: "eSectionTypeDWARFDebugAbbrev",
        lldb.eSectionTypeDWARFDebugAddr: "eSectionTypeDWARFDebugAddr",
        lldb.eSectionTypeDWARFDebugAranges: "eSectionTypeDWARFDebugAranges",
        lldb.eSectionTypeDWARFDebugCuIndex: "eSectionTypeDWARFDebugCuIndex",
        lldb.eSectionTypeDWARFDebugFrame: "eSectionTypeDWARFDebugFrame",
        lldb.eSectionTypeDWARFDebugInfo: "eSectionTypeDWARFDebugInfo",
        lldb.eSectionTypeDWARFDebugLine: "eSectionTypeDWARFDebugLine",
        lldb.eSectionTypeDWARFDebugLoc: "eSectionTypeDWARFDebugLoc",
        lldb.eSectionTypeDWARFDebugMacInfo: "eSectionTypeDWARFDebugMacInfo",
        lldb.eSectionTypeDWARFDebugMacro: "eSectionTypeDWARFDebugMacro",
        lldb.eSectionTypeDWARFDebugPubNames: "eSectionTypeDWARFDebugPubNames",
        lldb.eSectionTypeDWARFDebugPubTypes: "eSectionTypeDWARFDebugPubTypes",
        lldb.eSectionTypeDWARFDebugRanges: "eSectionTypeDWARFDebugRanges",
        lldb.eSectionTypeDWARFDebugStr: "eSectionTypeDWARFDebugStr",
        lldb.eSectionTypeDWARFDebugStrOffsets: "eSectionTypeDWARFDebugStrOffsets",
        lldb.eSectionTypeDWARFAppleNames: "eSectionTypeDWARFAppleNames",
        lldb.eSectionTypeDWARFAppleTypes: "eSectionTypeDWARFAppleTypes",
        lldb.eSectionTypeDWARFAppleNamespaces: "eSectionTypeDWARFAppleNamespaces",
        lldb.eSectionTypeDWARFAppleObjC: "eSectionTypeDWARFAppleObjC",
        lldb.eSectionTypeELFSymbolTable: "eSectionTypeELFSymbolTable",
        lldb.eSectionTypeELFDynamicSymbols: "eSectionTypeELFDynamicSymbols",
        lldb.eSectionTypeELFRelocationEntries: "eSectionTypeELFRelocationEntries",
        lldb.eSectionTypeELFDynamicLinkInfo: "eSectionTypeELFDynamicLinkInfo",
        lldb.eSectionTypeEHFrame: "eSectionTypeEHFrame",
        lldb.eSectionTypeSwiftModules: "eSectionTypeSwiftModules",
        lldb.eSectionTypeARMexidx: "eSectionTypeARMexidx",
        lldb.eSectionTypeARMextab: "eSectionTypeARMextab",
        lldb.eSectionTypeCompactUnwind: "eSectionTypeCompactUnwind",
        lldb.eSectionTypeGoSymtab: "eSectionTypeGoSymtab",
        lldb.eSectionTypeAbsoluteAddress: "eSectionTypeAbsoluteAddress",
        lldb.eSectionTypeDWARFGNUDebugAltLink: "eSectionTypeDWARFGNUDebugAltLink",
        lldb.eSectionTypeDWARFDebugTypes: "eSectionTypeDWARFDebugTypes",
        lldb.eSectionTypeDWARFDebugNames: "eSectionTypeDWARFDebugNames",
        lldb.eSectionTypeOther: "eSectionTypeOther",
        lldb.eSectionTypeDWARFDebugLineStr: "eSectionTypeDWARFDebugLineStr",
        lldb.eSectionTypeDWARFDebugRngLists: "eSectionTypeDWARFDebugRngLists",
        lldb.eSectionTypeDWARFDebugLocLists: "eSectionTypeDWARFDebugLocLists",
        lldb.eSectionTypeDWARFDebugAbbrevDwo: "eSectionTypeDWARFDebugAbbrevDwo",
        lldb.eSectionTypeDWARFDebugInfoDwo: "eSectionTypeDWARFDebugInfoDwo",
        lldb.eSectionTypeDWARFDebugStrDwo: "eSectionTypeDWARFDebugStrDwo",
        lldb.eSectionTypeDWARFDebugStrOffsetsDwo: "eSectionTypeDWARFDebugStrOffsetsDwo",
        lldb.eSectionTypeDWARFDebugTypesDwo: "eSectionTypeDWARFDebugTypesDwo",
        lldb.eSectionTypeDWARFDebugRngListsDwo: "eSectionTypeDWARFDebugRngListsDwo",
        lldb.eSectionTypeDWARFDebugLocDwo: "eSectionTypeDWARFDebugLocDwo",
        lldb.eSectionTypeDWARFDebugLocListsDwo: "eSectionTypeDWARFDebugLocListsDwo",
        lldb.eSectionTypeDWARFDebugTuIndex: "eSectionTypeDWARFDebugTuIndex"
    }

    return section_type_dic.get(section_type, "unknown")


def get_string_from_queue_kind(queue_kind: int) -> str:
    queue_kind_dic: Dict[int, str] = {
        lldb.eQueueKindUnknown: "eQueueKindUnknown",
        lldb.eQueueKindSerial: "eQueueKindSerial",
        lldb.eQueueKindConcurrent: "eQueueKindConcurrent"
    }
    return queue_kind_dic.get(queue_kind, "unknown")


def pSBHostOS(obj: Optional[lldb.SBHostOS]) -> None:
    if obj is not None:
        hostOS = obj
    else:
        hostOS = lldb.SBHostOS

    print_class_name("SBHostOS")
    print_format("GetProgramFileSpec", hostOS.GetProgramFileSpec())  # SBFileSpec
    print_format("GetLLDBPythonPath", hostOS.GetLLDBPythonPath())  # SBFileSpec
    print_format("GetUserHomeDirectory", hostOS.GetUserHomeDirectory())  # SBFileSpec

    print_format("GetLLDBPath(ePathTypeLLDBShlibDir)", hostOS.GetLLDBPath(lldb.ePathTypeLLDBShlibDir))  # SBFileSpec
    print_format("GetLLDBPath(ePathTypeSupportExecutableDir)", hostOS.GetLLDBPath(lldb.ePathTypeSupportExecutableDir))  # SBFileSpec
    print_format("GetLLDBPath(ePathTypeHeaderDir)", hostOS.GetLLDBPath(lldb.ePathTypeHeaderDir))  # SBFileSpec
    print_format("GetLLDBPath(ePathTypePythonDir)", hostOS.GetLLDBPath(lldb.ePathTypePythonDir))  # SBFileSpec
    print_format("GetLLDBPath(ePathTypeLLDBSystemPlugins)", hostOS.GetLLDBPath(lldb.ePathTypeLLDBSystemPlugins))  # SBFileSpec
    print_format("GetLLDBPath(ePathTypeLLDBUserPlugins)", hostOS.GetLLDBPath(lldb.ePathTypeLLDBUserPlugins))  # SBFileSpec
    print_format("GetLLDBPath(ePathTypeLLDBTempSystemDir)", hostOS.GetLLDBPath(lldb.ePathTypeLLDBTempSystemDir))  # SBFileSpec
    print_format("GetLLDBPath(ePathTypeGlobalLLDBTempSystemDir)", hostOS.GetLLDBPath(lldb.ePathTypeGlobalLLDBTempSystemDir))  # SBFileSpec
    print_format("GetLLDBPath(ePathTypeClangDir)", hostOS.GetLLDBPath(lldb.ePathTypeClangDir))  # SBFileSpec
    print_format("GetLLDBPath(ePathTypeSwiftDir)", hostOS.GetLLDBPath(lldb.ePathTypeSwiftDir))  # SBFileSpec


def pSBDebugger(obj: Optional[lldb.SBDebugger]) -> None:
    if obj is not None:
        debugger = obj
    else:
        debugger = lldb.debugger

    print_class_name("SBDebugger")
    print_format("SBDebugger", debugger)
    print_format("IsValid", debugger.IsValid())
    print_format("GetBroadcasterClass", lldb.SBDebugger.GetBroadcasterClass())
    print_format("GetBroadcaster", debugger.GetBroadcaster())  # SBBroadcaster
    print_format("GetAsync", debugger.GetAsync())
    print_format("GetSetting", debugger.GetSetting())  # SBStructuredData
    print_format("GetInputFile", debugger.GetInputFile())  # SBFile
    print_format("GetOutputFile", debugger.GetOutputFile())  # SBFile
    print_format("GetErrorFile", debugger.GetErrorFile())  # SBFile
    print_format("GetCommandInterpreter", debugger.GetCommandInterpreter())  # SBCommandInterpreter
    print_format("InterruptRequested", debugger.InterruptRequested())
    print_format("GetListener", debugger.GetListener())  # SBListener
    print_format("GetDummyTarget", debugger.GetDummyTarget())  # SBTarget
    print_format("GetNumTargets", debugger.GetNumTargets())
    print_format("GetSelectedTarget", debugger.GetSelectedTarget())  # SBTarget
    print_format("GetSelectedPlatform", debugger.GetSelectedPlatform())  # SBPlatform
    print_format("GetNumPlatforms", debugger.GetNumPlatforms())
    print_format("GetNumAvailablePlatforms", debugger.GetNumAvailablePlatforms())
    print_format("GetSourceManager", debugger.GetSourceManager())  # SBSourceManager
    print_format("GetUseExternalEditor", debugger.GetUseExternalEditor())
    print_format("GetUseColor", debugger.GetUseColor())
    print_format("GetUseSourceCache", debugger.GetUseSourceCache())
    print_format("GetVersionString", debugger.GetVersionString())
    print_format("GetBuildConfiguration", debugger.GetBuildConfiguration())  # SBStructuredData
    print_format("GetInstanceName", debugger.GetInstanceName())
    print_format("GetTerminalWidth", debugger.GetTerminalWidth())
    print_format("GetID", debugger.GetID())
    print_format("GetPrompt", debugger.GetPrompt())
    print_format("GetReproducerPath", debugger.GetReproducerPath())
    print_format("GetScriptLanguage", debugger.GetScriptLanguage())  # ScriptLanguage int
    print_format("GetREPLLanguage", debugger.GetREPLLanguage())  # lldb::LanguageType int
    print_format("GetCloseInputOnEOF", debugger.GetCloseInputOnEOF())
    print_format("GetNumCategories", debugger.GetNumCategories())
    print_format("GetDefaultCategory", debugger.GetDefaultCategory())  # SBTypeCategory
    print_format("GetInputFileHandle", debugger.GetInputFileHandle())  # FileSP
    print_format("GetOutputFileHandle", debugger.GetOutputFileHandle())  # FileSP
    print_format("GetErrorFileHandle", debugger.GetErrorFileHandle())  # FileSP

    print_traversal(debugger, "GetNumTargets", "GetTargetAtIndex")  # [SBTarget]
    print_traversal(debugger, "GetNumPlatforms", "GetPlatformAtIndex")  # [SBPlatform]
    print_traversal(debugger, "GetNumCategories", "GetCategoryAtIndex")  # [SBTypeCategory]


def pSBTarget(obj: Optional[lldb.SBTarget]) -> None:
    if obj is not None:
        target = obj
    else:
        target = lldb.debugger.GetSelectedTarget()

    print_class_name("SBTarget")
    print_format("SBTarget", target)
    print_format("IsValid", target.IsValid())
    print_format("GetBroadcasterClassName", lldb.SBTarget.GetBroadcasterClassName())
    print_format("GetProcess", target.GetProcess())  # SBProcess
    print_format("GetPlatform", target.GetPlatform())  # SBPlatform
    print_format("GetExecutable", target.GetExecutable())  # SBFileSpec
    print_format("GetNumModules", target.GetNumModules())
    print_format("GetDebugger", target.GetDebugger())  # SBDebugger
    byte_order = target.GetByteOrder()  # ByteOrder int
    print_format("GetByteOrder(raw)", byte_order)
    print_format("GetByteOrder(resolved)", get_string_from_byte_order(byte_order))
    print_format("GetAddressByteSize", target.GetAddressByteSize())
    print_format("GetTriple", target.GetTriple())
    print_format("GetABIName", target.GetABIName())
    print_format("GetLabel", target.GetLabel())
    print_format("GetDataByteSize", target.GetDataByteSize())
    print_format("GetCodeByteSize", target.GetCodeByteSize())
    print_format("GetMaximumNumberOfChildrenToDisplay", target.GetMaximumNumberOfChildrenToDisplay())
    print_format("FindFunctions.first", target.FindFunctions("viewDidLoad")[0])  # SBSymbolContext
    print_format("FindFirstType", target.FindFirstType("UIResponder"))  # SBType
    print_format("FindTypes", target.FindTypes("UIView"))  # SBTypeList
    print_format("GetSourceManager", target.GetSourceManager())  # SBSourceManager
    print_format("FindFirstGlobalVariable", target.FindFirstGlobalVariable("sharedInstance"))  # SBValue
    print_format("FindGlobalVariables", target.FindGlobalVariables("sharedInstance", 2))  # SBValueList
    print_format("FindGlobalFunctions.first", target.FindGlobalFunctions("viewDidLoad", 1, 0)[0])  # SBSymbolContext
    print_format("GetEnvironment", target.GetEnvironment())  # SBEnvironment
    print_format("GetNumBreakpoints", target.GetNumBreakpoints())
    string_list = lldb.SBStringList()
    target.GetBreakpointNames(string_list)
    print_format("GetBreakpointNames", get_string_from_SBStringList(string_list))
    print_format("GetNumWatchpoints", target.GetNumWatchpoints())
    print_format("GetBroadcaster", target.GetBroadcaster())  # SBBroadcaster
    print_format("FindSymbols", target.FindSymbols("UIView"))  # SBSymbolContextList
    print_format("GetStackRedZoneSize", target.GetStackRedZoneSize())
    module = target.GetProcess().GetSelectedThread().GetSelectedFrame().GetModule()
    print_format("IsLoaded", target.IsLoaded(module))
    print_format("GetLaunchInfo", target.GetLaunchInfo())  # SBLaunchInfo
    print_format("GetCollectingStats", target.GetCollectingStats())
    print_format("GetStatistics", target.GetStatistics())  # SBStructuredData
    print_format("GetTrace", target.GetTrace())  # SBTrace

    print_traversal(target, "GetNumModules", "GetModuleAtIndex")  # [SBModule]
    print_traversal(target, "GetNumBreakpoints", "GetBreakpointAtIndex")  # [SBBreakpoint]
    print_traversal(target, "GetNumWatchpoints", "GetWatchpointAtIndex")  # [SBWatchpoint]


def pSBProcess(obj: Optional[lldb.SBProcess]) -> None:
    if obj is not None:
        process = obj
    else:
        process = lldb.debugger.GetSelectedTarget().GetProcess()
        # process = lldb.debugger.GetCommandInterpreter().GetProcess()

    print_class_name("SBProcess")
    print_format("SBProcess", process)
    print_format("GetBroadcasterClassName", process.GetBroadcasterClassName())
    print_format("GetPluginName", process.GetPluginName())
    print_format("GetShortPluginName", process.GetShortPluginName())
    print_format("IsValid", process.IsValid())
    print_format("GetTarget", process.GetTarget())  # SBTarget
    byte_order = process.GetByteOrder()  # ByteOrder int
    print_format("GetByteOrder(raw)", byte_order)
    print_format("GetByteOrder(resolved)", get_string_from_byte_order(byte_order))
    print_format("GetNumThreads", process.GetNumThreads())
    print_format("GetSelectedThread", process.GetSelectedThread())  # SBThread
    print_format("GetNumQueues", process.GetNumQueues())
    print_format("GetState", process.GetState())  # StateType int
    print_format("SBDebugger.StateAsCString", lldb.SBDebugger.StateAsCString(process.GetState()))
    print_format("GetExitStatus", process.GetExitStatus())
    print_format("GetExitDescription", process.GetExitDescription())
    print_format("GetProcessID", process.GetProcessID())
    print_format("GetUniqueID", process.GetUniqueID())
    print_format("GetAddressByteSize", process.GetAddressByteSize())
    print_format("GetUnixSignals", process.GetUnixSignals())  # SBUnixSignals
    print_format("GetBroadcaster", process.GetBroadcaster())  # SBBroadcaster
    print_format("GetBroadcasterClass", lldb.SBProcess.GetBroadcasterClass())
    print_format("GetScriptedImplementation", process.GetScriptedImplementation())
    print_format("GetExtendedCrashInformation", process.GetExtendedCrashInformation())  # SBStructuredData
    print_format("GetNumExtendedBacktraceTypes", process.GetNumExtendedBacktraceTypes())
    print_format("GetMemoryRegions", process.GetMemoryRegions())  # SBMemoryRegionInfoList
    print_format("GetProcessInfo", process.GetProcessInfo())  # SBProcessInfo
    print_format("__get_is_alive__", process.__get_is_alive__())
    print_format("__get_is_running__", process.__get_is_running__())
    print_format("__get_is_stopped__", process.__get_is_stopped__())

    print_traversal(process, "GetNumThreads", "GetThreadAtIndex")  # [SBThread]
    print_traversal(process, "GetNumQueues", "GetQueueAtIndex")  # [SBQueue]
    print_traversal(process, "GetNumExtendedBacktraceTypes", "GetExtendedBacktraceTypeAtIndex")  # [str]


def pSBProcessInfo(obj: Optional[lldb.SBProcessInfo]) -> None:
    if obj is not None:
        info = obj
    else:
        info = lldb.debugger.GetSelectedTarget().GetProcess().GetProcessInfo()

    print_class_name("SBProcessInfo")
    print_format("SBProcessInfo", info)
    print_format("IsValid", info.IsValid())
    print_format("GetName", info.GetName())
    print_format("GetExecutableFile", info.GetExecutableFile())  # SBFileSpec
    print_format("GetProcessID", info.GetProcessID())
    print_format("GetUserID", info.GetUserID())
    print_format("GetGroupID", info.GetGroupID())
    print_format("UserIDIsValid", info.UserIDIsValid())
    print_format("GroupIDIsValid", info.GroupIDIsValid())
    print_format("GetEffectiveUserID", info.GetEffectiveUserID())
    print_format("GetEffectiveGroupID", info.GetEffectiveGroupID())
    print_format("EffectiveUserIDIsValid", info.EffectiveUserIDIsValid())
    print_format("EffectiveGroupIDIsValid", info.EffectiveGroupIDIsValid())
    print_format("GetParentProcessID", info.GetParentProcessID())
    print_format("GetTriple", info.GetTriple())


def pSBThread(obj: Optional[lldb.SBThread]) -> None:
    if obj is not None:
        thread = obj
    else:
        thread = lldb.debugger.GetSelectedTarget().GetProcess().GetSelectedThread()

    print_class_name("SBThread")
    print_format("SBThread", thread)
    print_format("GetBroadcasterClassName", lldb.SBThread.GetBroadcasterClassName())
    print_format("IsValid", thread.IsValid())
    stop_reason = thread.GetStopReason()  # StopReason int
    print_format("GetStopReason(raw)", stop_reason)
    print_format("GetStopReason(resolved)", get_string_from_stop_reason(stop_reason))
    print_format("GetStopReasonDataCount", thread.GetStopReasonDataCount())
    print_format("GetStopDescription", thread.GetStopDescription(1024))
    print_format("GetStopReturnValue", thread.GetStopReturnValue())  # SBValue
    print_format("GetStopErrorValue", thread.GetStopErrorValue())  # SBValue
    print_format("GetThreadID", thread.GetThreadID())
    print_format("GetIndexID", thread.GetIndexID())
    print_format("GetName", thread.GetName())
    print_format("GetQueueName", thread.GetQueueName())
    print_format("GetQueueID", thread.GetQueueID())
    print_format("GetQueue", thread.GetQueue())  # SBQueue
    print_format("IsSuspended", thread.IsSuspended())
    print_format("IsStopped", thread.IsStopped())
    print_format("GetNumFrames", thread.GetNumFrames())
    print_format("GetSelectedFrame", thread.GetSelectedFrame())  # SBFrame
    print_format("GetProcess", thread.GetProcess())  # SBProcess
    stream = lldb.SBStream()
    thread.GetStatus(stream)
    print_format("GetStatus", stream.GetData())
    print_format("GetExtendedBacktraceOriginatingIndexID", thread.GetExtendedBacktraceOriginatingIndexID())
    print_format("GetCurrentException", thread.GetCurrentException())  # SBValue
    print_format("GetCurrentExceptionBacktrace", thread.GetCurrentExceptionBacktrace())  # SBValue
    print_format("SafeToCallFunctions", thread.SafeToCallFunctions())
    print_format("GetSiginfo", thread.GetSiginfo())  # SBValue

    print_traversal(thread, "GetStopReasonDataCount", "GetStopReasonDataAtIndex")  # [int]
    print_traversal(thread, "GetNumFrames", "GetFrameAtIndex")  # [SBFrame]


def pSBThreadPlan(obj: Optional[lldb.SBThreadPlan]) -> None:
    if obj is not None:
        plan = obj
    else:
        plan = lldb.SBThreadPlan()

    print_class_name("SBThreadPlan")
    print_format("SBThreadPlan", plan)
    print_format("IsValid", plan.IsValid())
    stop_reason = plan.GetStopReason()  # StopReason int
    print_format("GetStopReason(raw)", stop_reason)
    print_format("GetStopReason(resolved)", get_string_from_stop_reason(stop_reason))
    print_format("GetStopReasonDataCount", plan.GetStopReasonDataCount())
    print_format("GetThread", plan.GetThread())  # SBThread
    stream = lldb.SBStream()
    plan.GetDescription(stream)
    print_format("GetDescription", stream.GetData())
    print_format("IsPlanComplete", plan.IsPlanComplete())
    print_format("IsPlanStale", plan.IsPlanStale())
    print_format("GetStopOthers", plan.GetStopOthers())

    print_traversal(plan, "GetStopReasonDataCount", "GetStopReasonDataAtIndex")  # [int]


def pSBFrame(obj: Optional[lldb.SBFrame]) -> None:
    if obj is not None:
        frame = obj
    else:
        frame = lldb.debugger.GetSelectedTarget().GetProcess().GetSelectedThread().GetSelectedFrame()

    print_class_name("SBFrame")
    print_format("SBFrame", frame)
    print_format("IsValid", frame.IsValid())
    print_format("GetFrameID", frame.GetFrameID())
    print_format("GetCFA", frame.GetCFA())
    print_format("GetPC", frame.GetPC())
    print_format("GetSP", frame.GetSP())
    print_format("GetFP", frame.GetFP())
    print_format("GetPCAddress", frame.GetPCAddress())  # SBAddress
    print_format("GetSymbolContext", frame.GetSymbolContext(lldb.eSymbolContextEverything))  # SBSymbolContext
    print_format("GetModule", frame.GetModule())  # SBModule
    print_format("GetCompileUnit", frame.GetCompileUnit())  # SBCompileUnit
    print_format("GetFunction", frame.GetFunction())  # SBFunction
    print_format("GetSymbol", frame.GetSymbol())  # SBSymbol
    print_format("GetBlock", frame.GetBlock())  # SBBlock
    print_format("GetDisplayFunctionName", frame.GetDisplayFunctionName())
    print_format("GetFunctionName", frame.GetFunctionName())
    print_format("GuessLanguage", frame.GuessLanguage())  # LanguageType int
    print_format("IsSwiftThunk", frame.IsSwiftThunk())
    print_format("IsInlined", frame.IsInlined())
    print_format("IsArtificial", frame.IsArtificial())
    print_format("GetFrameBlock", frame.GetFrameBlock())  # SBBlock
    print_format("GetLineEntry", frame.GetLineEntry())  # SBLineEntry
    print_format("GetThread", frame.GetThread())  # SBThread
    print_format("Disassemble", frame.Disassemble())

    print_format("GetVariables", frame.GetVariables(True, True, True, False))  # SBValueList
    # print_format("get_arguments", frame.get_arguments())  # SBValueList
    # print_format("get_locals", frame.get_locals())  # SBValueList
    # print_format("get_statics", frame.get_statics())  # SBValueList

    print_format("GetRegisters", frame.GetRegisters())  # SBValueList
    print_format("FindVariable", frame.FindVariable("self"))  # SBValue
    print_format("GetValueForVariablePath", frame.GetValueForVariablePath("self.customVariable"))  # SBValue
    print_format("GetLanguageSpecificData", frame.GetLanguageSpecificData())  # SBStructuredData
    print_format("get_parent_frame", frame.get_parent_frame())  # SBFrame


def pSBValue(obj: Optional[lldb.SBValue]) -> None:
    if obj is not None:
        value = obj
    else:
        value = lldb.debugger.GetSelectedTarget().GetProcess().GetSelectedThread().GetSelectedFrame().FindVariable("self")

    print_class_name("SBValue")
    print_format("SBValue", value)
    print_format("IsValid", value.IsValid())
    print_format("GetError", value.GetError())  # SBError
    print_format("GetID", value.GetID())
    print_format("GetName", value.GetName())
    print_format("GetTypeName", value.GetTypeName())
    print_format("GetDisplayTypeName", value.GetDisplayTypeName())
    print_format("GetByteSize", value.GetByteSize())
    print_format("IsInScope", value.IsInScope())
    print_format("GetFormat", value.GetFormat())  # Format int
    print_format("GetValue", value.GetValue())
    print_format("GetValueAsSigned", value.GetValueAsSigned())
    print_format("GetValueAsUnsigned", value.GetValueAsUnsigned())
    print_format("GetValueAsAddress", value.GetValueAsAddress())
    print_format("GetValueType", value.GetValueType())  # ValueType int
    print_format("GetValueDidChange", value.GetValueDidChange())
    print_format("GetSummary", value.GetSummary())
    print_format("GetObjectDescription", value.GetObjectDescription())
    print_format("GetStaticValue", value.GetStaticValue())  # SBValue
    print_format("GetNonSyntheticValue", value.GetNonSyntheticValue())  # SBValue
    print_format("GetPreferDynamicValue", value.GetPreferDynamicValue())  # DynamicValueType int
    print_format("GetPreferSyntheticValue", value.GetPreferSyntheticValue())
    print_format("IsDynamic", value.IsDynamic())
    print_format("IsSynthetic", value.IsSynthetic())
    print_format("IsSyntheticChildrenGenerated", value.IsSyntheticChildrenGenerated())
    print_format("GetLocation", value.GetLocation())
    print_format("GetTypeFormat", value.GetTypeFormat())  # SBTypeFormat
    print_format("GetTypeSummary", value.GetTypeSummary())  # SBTypeSummary
    print_format("GetTypeFilter", value.GetTypeFilter())  # SBTypeFilter
    print_format("GetTypeSynthetic", value.GetTypeSynthetic())  # SBTypeSynthetic
    print_format("GetType", value.GetType())  # SBType
    print_format("GetDeclaration", value.GetDeclaration())  # SBDeclaration
    print_format("MightHaveChildren", value.MightHaveChildren())
    print_format("IsRuntimeSupportValue", value.IsRuntimeSupportValue())
    print_format("GetNumChildren", value.GetNumChildren())
    print_format("GetOpaqueType", value.GetOpaqueType())
    print_format("Dereference", value.Dereference())  # SBValue
    print_format("AddressOf", value.AddressOf())  # SBValue
    print_format("TypeIsPointerType", value.TypeIsPointerType())
    print_format("GetTarget", value.GetTarget())  # SBTarget
    print_format("GetProcess", value.GetProcess())  # SBProcess
    print_format("GetThread", value.GetThread())  # SBThread
    print_format("GetFrame", value.GetFrame())  # SBFrame
    print_format("GetPointeeData", value.GetPointeeData())
    print_format("GetData", value.GetData())  # SBData
    print_format("GetLoadAddress", value.GetLoadAddress())
    print_format("GetAddress", value.GetAddress())  # SBAddress
    print_format("Persist", value.Persist())  # SBValue
    print_format("__get_dynamic__", value.__get_dynamic__())  # SBValue
    print_format("get_expr_path", value.get_expr_path())

    print_traversal(value, "GetNumChildren", "GetChildAtIndex")  # [SBValue]


def pSBSymbolContext(obj: Optional[lldb.SBSymbolContext]) -> None:
    if obj is not None:
        ctx = obj
    else:
        ctx = lldb.debugger.GetSelectedTarget().GetProcess().GetSelectedThread().GetSelectedFrame().GetSymbolContext(lldb.eSymbolContextEverything)
        # ctx = lldb.debugger.GetSelectedTarget().FindFunctions("viewDidLoad")[0]

    print_class_name("SBSymbolContext")
    print_format("SBSymbolContext", ctx)
    print_format("IsValid", ctx.IsValid())
    print_format("GetModule", ctx.GetModule())  # SBModule
    print_format("GetCompileUnit", ctx.GetCompileUnit())  # SBCompileUnit
    print_format("GetFunction", ctx.GetFunction())  # SBFunction
    print_format("GetBlock", ctx.GetBlock())  # SBBlock
    print_format("GetLineEntry", ctx.GetLineEntry())  # SBLineEntry
    print_format("GetSymbol", ctx.GetSymbol())  # SBSymbol
    stream = lldb.SBStream()
    ctx.GetDescription(stream)
    print_format("GetDescription", stream.GetData())


def pSBModule(obj: Optional[lldb.SBModule]) -> None:
    functionName = 'viewWillLayoutSubviews'
    # functionName = 'CGRectMake'

    if obj is not None:
        module = obj
    else:
        module = lldb.debugger.GetSelectedTarget().GetProcess().GetSelectedThread().GetSelectedFrame().GetModule()
        # module = lldb.debugger.GetSelectedTarget().FindFunctions(functionName)[0].GetModule()
        # module = lldb.debugger.GetSelectedTarget().GetModuleAtIndex(0)

    print_class_name("SBModule")
    print_format("SBModule", module)
    print_format("IsValid", module.IsValid())
    print_format("IsFileBacked", module.IsFileBacked())
    print_format("GetFileSpec", module.GetFileSpec())  # SBFileSpec
    print_format("GetPlatformFileSpec", module.GetPlatformFileSpec())  # SBFileSpec
    print_format("GetRemoteInstallFileSpec", module.GetRemoteInstallFileSpec())  # SBFileSpec
    print_format("GetUUIDBytes", module.GetUUIDBytes())
    print_format("GetUUIDString", module.GetUUIDString())
    print_format("GetNumCompileUnits", module.GetNumCompileUnits())
    print_format("GetNumSymbols", module.GetNumSymbols())
    print_format("FindSymbol", module.FindSymbol(functionName))  # SBSymbol
    print_format("FindSymbols", module.FindSymbols(functionName))  # SBSymbolContextList
    print_format("GetNumSections", module.GetNumSections())
    print_format("FindFunctions", module.FindFunctions(functionName, lldb.eFunctionNameTypeAny))  # SBSymbolContextList
    # print_format("GetTypes", module.GetTypes())  # SBTypeList
    byte_order = module.GetByteOrder()  # ByteOrder int
    print_format("GetByteOrder(raw)", byte_order)
    print_format("GetByteOrder(resolved)", get_string_from_byte_order(byte_order))
    print_format("GetAddressByteSize", module.GetAddressByteSize())
    print_format("GetTriple", module.GetTriple())
    print_format("GetVersion", module.GetVersion())
    print_format("GetSymbolFileSpec", module.GetSymbolFileSpec())  # SBFileSpec
    print_format("GetObjectFileHeaderAddress", module.GetObjectFileHeaderAddress())  # SBAddress
    print_format("GetObjectFileEntryPointAddress", module.GetObjectFileEntryPointAddress())  # SBAddress
    print_format("SBModule.GetNumberAllocatedModules", lldb.SBModule.GetNumberAllocatedModules())

    print_traversal(module, "GetNumCompileUnits", "GetCompileUnitAtIndex")  # [SBCompileUnit]
    print_traversal(module, "GetNumSymbols", "GetSymbolAtIndex")  # [SBSymbol]
    print_traversal(module, "GetNumSections", "GetSectionAtIndex")  # [SBSection]


def pSBSymbol(obj: Optional[lldb.SBSymbol]) -> None:
    if obj is not None:
        symbol = obj
    else:
        symbol = lldb.debugger.GetSelectedTarget().GetProcess().GetSelectedThread().GetSelectedFrame().GetSymbol()
        # symbol = lldb.debugger.GetSelectedTarget().FindFunctions("viewDidLoad")[0].GetSymbol()

    print_class_name("SBSymbol")
    print_format("SBSymbol", symbol)
    print_format("IsValid", symbol.IsValid())
    print_format("GetName", symbol.GetName())
    print_format("GetDisplayName", symbol.GetDisplayName())
    print_format("GetMangledName", symbol.GetMangledName())
    print_format("GetStartAddress", symbol.GetStartAddress())  # SBAddress
    print_format("GetEndAddress", symbol.GetEndAddress())  # SBAddress
    print_format("GetValue", symbol.GetValue())
    print_format("GetSize", symbol.GetSize())
    print_format("GetPrologueByteSize", symbol.GetPrologueByteSize())
    print_format("GetType(raw)", symbol.GetType())  # SymbolType int
    print_format("GetType(resolved)", get_string_from_symbol_type(symbol.GetType()))
    print_format("IsExternal", symbol.IsExternal())
    print_format("IsSynthetic", symbol.IsSynthetic())
    print_format("GetInstructions", symbol.GetInstructions(lldb.debugger.GetSelectedTarget()))  # SBInstructionList


def pSBInstruction(obj: Optional[lldb.SBInstruction]) -> None:
    target = lldb.debugger.GetSelectedTarget()

    if obj is not None:
        instruction = obj
    else:
        frame = target.GetProcess().GetSelectedThread().GetSelectedFrame()
        instruction_list = frame.GetSymbol().GetInstructions(lldb.debugger.GetSelectedTarget())
        for inst in instruction_list:
            if inst.GetAddress() == frame.GetPCAddress():
                instruction = inst
                break

        # instruction_list = lldb.debugger.GetSelectedTarget().FindFunctions("viewDidLoad")[0].GetSymbol().GetInstructions(lldb.debugger.GetSelectedTarget())
        # instruction = instruction_list.GetInstructionAtIndex(0)

    print_class_name("SBInstruction")
    print_format("SBInstruction", instruction)
    print_format("IsValid", instruction.IsValid())
    print_format("GetAddress", instruction.GetAddress())  # SBAddress
    print_format("GetMnemonic", instruction.GetMnemonic(target))
    print_format("GetOperands", instruction.GetOperands(target))
    print_format("GetComment", instruction.GetComment(target))
    control_flow_kind = instruction.GetControlFlowKind(target)  # InstructionControlFlowKind int
    print_format("GetControlFlowKind(raw)", control_flow_kind)
    print_format("GetControlFlowKind(resolved)", get_string_from_instruction_control_flow_kind(control_flow_kind))
    print_format("GetData", instruction.GetData(target))  # SBData
    print_format("GetByteSize", instruction.GetByteSize())
    print_format("DoesBranch", instruction.DoesBranch())
    print_format("HasDelaySlot", instruction.HasDelaySlot())
    print_format("CanSetBreakpoint", instruction.CanSetBreakpoint())


def pSBFunction(obj: Optional[lldb.SBFunction]) -> None:
    if obj is not None:
        func = obj
    else:
        func = lldb.debugger.GetSelectedTarget().GetProcess().GetSelectedThread().GetSelectedFrame().GetFunction()
        # func = lldb.debugger.GetSelectedTarget().FindFunctions("viewDidLoad")[0].GetFunction()

    print_class_name("SBFunction")
    print_format("SBFunction", func)
    print_format("IsValid", func.IsValid())
    print_format("GetName", func.GetName())
    print_format("GetDisplayName", func.GetDisplayName())
    print_format("GetMangledName", func.GetMangledName())
    print_format("GetInstructions", func.GetInstructions(lldb.debugger.GetSelectedTarget()))  # SBInstructionList
    print_format("GetStartAddress", func.GetStartAddress())  # SBAddress
    print_format("GetEndAddress", func.GetEndAddress())  # SBAddress
    print_format("GetPrologueByteSize", func.GetPrologueByteSize())
    print_format("GetArgumentName", func.GetArgumentName(0))
    print_format("GetType", func.GetType())  # SBType
    print_format("GetBlock", func.GetBlock())  # SBBlock
    print_format("GetLanguage", func.GetLanguage())  # LanguageType int
    print_format("GetIsOptimized", func.GetIsOptimized())
    print_format("GetCanThrow", func.GetCanThrow())


def pSBBlock(obj: Optional[lldb.SBBlock]) -> None:
    if obj is not None:
        block = obj
    else:
        block = lldb.debugger.GetSelectedTarget().GetProcess().GetSelectedThread().GetSelectedFrame().GetBlock()
        # block = lldb.debugger.GetSelectedTarget().GetProcess().GetSelectedThread().GetSelectedFrame().GetFrameBlock()
        # block = lldb.debugger.GetSelectedTarget().GetProcess().GetSelectedThread().GetSelectedFrame().GetFunction().GetBlock()
        # block = lldb.debugger.GetSelectedTarget().FindFunctions("viewDidLoad")[0].GetBlock()

    print_class_name("SBBlock")
    print_format("SBBlock", block)
    print_format("IsInlined", block.IsInlined())
    print_format("IsValid", block.IsValid())
    print_format("GetInlinedName", block.GetInlinedName())
    print_format("GetInlinedCallSiteFile", block.GetInlinedCallSiteFile())  # SBFileSpec
    print_format("GetInlinedCallSiteLine", block.GetInlinedCallSiteLine())
    print_format("GetInlinedCallSiteColumn", block.GetInlinedCallSiteColumn())
    print_format("GetParent", block.GetParent())  # SBBlock
    print_format("GetContainingInlinedBlock", block.GetContainingInlinedBlock())  # SBBlock
    print_format("GetSibling", block.GetSibling())  # SBBlock
    print_format("GetFirstChild", block.GetFirstChild())  # SBBlock
    print_format("GetNumRanges", block.GetNumRanges())
    print_format("GetRangeStartAddress", block.GetRangeStartAddress(0))  # SBAddress
    print_format("GetRangeEndAddress", block.GetRangeEndAddress(0))  # SBAddress


def pSBCompileUnit(obj: Optional[lldb.SBCompileUnit]) -> None:
    if obj is not None:
        unit = obj
    else:
        unit = lldb.debugger.GetSelectedTarget().GetProcess().GetSelectedThread().GetSelectedFrame().GetCompileUnit()
        # unit = lldb.debugger.GetSelectedTarget().FindFunctions("viewDidLoad")[0].GetCompileUnit()

    print_class_name("SBCompileUnit")
    print_format("SBCompileUnit", unit)
    print_format("IsValid", unit.IsValid())
    print_format("GetFileSpec", unit.GetFileSpec())  # SBFileSpec
    print_format("GetNumLineEntries", unit.GetNumLineEntries())
    print_format("GetNumSupportFiles", unit.GetNumSupportFiles())
    print_format("GetTypes", unit.GetTypes())  # SBTypeList
    print_format("GetLanguage", unit.GetLanguage())  # LanguageType int


    print_traversal(unit, "GetNumLineEntries", "GetLineEntryAtIndex")  # [SBLineEntry]
    print_traversal(unit, "GetNumSupportFiles", "GetSupportFileAtIndex")  # [SBFileSpec]


def pSBLineEntry(obj: Optional[lldb.SBLineEntry]) -> None:
    if obj is not None:
        le = obj
    else:
        le = lldb.debugger.GetSelectedTarget().GetProcess().GetSelectedThread().GetSelectedFrame().GetLineEntry()
        # le = lldb.debugger.GetSelectedTarget().FindFunctions("viewDidLoad")[0].GetLineEntry()
        # le = lldb.debugger.GetSelectedTarget().GetProcess().GetSelectedThread().GetSelectedFrame().GetCompileUnit().GetLineEntryAtIndex(0)

    print_class_name("SBLineEntry")
    print_format("SBLineEntry", le)
    print_format("IsValid", le.IsValid())
    print_format("GetStartAddress", le.GetStartAddress())  # SBAddress
    print_format("GetEndAddress", le.GetEndAddress())  # SBAddress
    print_format("GetFileSpec", le.GetFileSpec())  # SBFileSpec
    print_format("GetLine", le.GetLine())
    print_format("GetColumn", le.GetColumn())


def pSBFile(obj: Optional[lldb.SBFile]) -> None:
    if obj is not None:
        file = obj
    else:
        file = lldb.debugger.GetInputFile()
        # file = lldb.debugger.GetOutputFile()
        # file = lldb.debugger.GetErrorFile()

    print_class_name("SBFile")
    print_format("SBFile", file)
    print_format("IsValid", file.IsValid())
    print_format("GetFile", file.GetFile())  # lldb::FileSP


def pSBFileSpec(obj: Optional[lldb.SBFileSpec]) -> None:
    if obj is not None:
        file_spec = obj
    else:
        file_spec = lldb.debugger.GetSelectedTarget().GetExecutable()
        # file_spec = lldb.debugger.GetSelectedTarget().GetLaunchInfo().GetExecutableFile()
        # file_spec = lldb.debugger.GetSelectedTarget().GetProcess().GetSelectedThread().GetSelectedFrame().GetModule().GetFileSpec()
        # file_spec = lldb.debugger.GetSelectedTarget().GetProcess().GetSelectedThread().GetSelectedFrame().GetCompileUnit().GetFileSpec()

    print_class_name("SBFileSpec")
    print_format("SBFileSpec", file_spec)
    print_format("IsValid", file_spec.IsValid())
    print_format("Exists", file_spec.Exists())
    print_format("ResolveExecutableLocation", file_spec.ResolveExecutableLocation())
    print_format("GetFilename", file_spec.GetFilename())
    print_format("GetDirectory", file_spec.GetDirectory())
    print_format("fullpath", file_spec.fullpath)


def pSBAddress(obj: Optional[lldb.SBAddress]) -> None:
    if obj is not None:
        address = obj
    else:
        address = lldb.debugger.GetSelectedTarget().GetProcess().GetSelectedThread().GetSelectedFrame().GetPCAddress()
        # address = lldb.debugger.GetSelectedTarget().FindFunctions("viewDidLoad")[0].GetSymbol().GetStartAddress()
        # address = lldb.debugger.GetSelectedTarget().GetProcess().GetSelectedThread().GetSelectedFrame().FindVariable("self").GetAddress()
        # address = lldb.debugger.GetSelectedTarget().GetProcess().GetSelectedThread().GetSelectedFrame().GetModule().GetObjectFileHeaderAddress()
        # address = lldb.debugger.GetSelectedTarget().GetProcess().GetSelectedThread().GetSelectedFrame().GetLineEntry().GetStartAddress()
        # address = lldb.debugger.GetSelectedTarget().GetProcess().GetSelectedThread().GetSelectedFrame().GetFunction().GetStartAddress()

    print_class_name("SBAddress")
    print_format("SBAddress", address)
    print_format("IsValid", address.IsValid())
    print_format("GetFileAddress", address.GetFileAddress())
    print_format("GetLoadAddress", address.GetLoadAddress(lldb.debugger.GetSelectedTarget()))
    stream = lldb.SBStream()
    address.GetDescription(stream)
    print_format("GetDescription", stream.GetData())
    print_format("GetSection", address.GetSection())  # SBSection
    print_format("GetOffset", address.GetOffset())
    print_format("GetSymbolContext", address.GetSymbolContext(lldb.eSymbolContextEverything))  # SBSymbolContext
    print_format("GetModule", address.GetModule())  # SBModule
    print_format("GetCompileUnit", address.GetCompileUnit())  # SBCompileUnit
    print_format("GetFunction", address.GetFunction())  # SBFunction
    print_format("GetBlock", address.GetBlock())  # SBBlock
    print_format("GetSymbol", address.GetSymbol())  # SBSymbol
    print_format("GetLineEntry", address.GetLineEntry())  # SBLineEntry


def pSBBreakpoint(obj: Optional[lldb.SBBreakpoint]) -> None:
    if obj is not None:
        bp = obj
    else:
        bp = lldb.debugger.GetSelectedTarget().GetBreakpointAtIndex(0)

    print_class_name("SBBreakpoint")
    print_format("SBBreakpoint", bp)
    print_format("GetID", bp.GetID())
    print_format("IsValid", bp.IsValid())
    print_format("GetTarget", bp.GetTarget())  # SBTarget
    print_format("IsEnabled", bp.IsEnabled())
    print_format("IsOneShot", bp.IsOneShot())
    print_format("IsInternal", bp.IsInternal())
    print_format("GetHitCount", bp.GetHitCount())
    print_format("GetIgnoreCount", bp.GetIgnoreCount())
    print_format("GetCondition", bp.GetCondition())
    print_format("GetAutoContinue", bp.GetAutoContinue())
    print_format("GetThreadID", bp.GetThreadID())
    print_format("GetThreadIndex", bp.GetThreadIndex())
    print_format("GetThreadName", bp.GetThreadName())
    print_format("GetQueueName", bp.GetQueueName())
    string_list = lldb.SBStringList()
    bp.GetCommandLineCommands(string_list)
    print_format("GetCommandLineCommands", get_string_from_SBStringList(string_list))
    string_list.Clear()
    bp.GetNames(string_list)
    print_format("GetNames", get_string_from_SBStringList(string_list))
    print_format("GetNumResolvedLocations", bp.GetNumResolvedLocations())
    print_format("GetNumLocations", bp.GetNumLocations())
    print_format("SerializeToStructuredData", bp.SerializeToStructuredData())  # SBStructuredData
    print_format("IsHardware", bp.IsHardware())

    print_traversal(bp, "GetNumLocations", "GetLocationAtIndex")  # [SBBreakpointLocation]


def pSBBreakpointLocation(obj: Optional[lldb.SBBreakpointLocation]) -> None:
    if obj is not None:
        breakpoint_location = obj
    else:
        breakpoint_location = lldb.debugger.GetSelectedTarget().GetBreakpointAtIndex(0).GetLocationAtIndex(0)

    print_class_name("SBBreakpointLocation")
    print_format("SBBreakpointLocation", breakpoint_location)
    print_format("GetID", breakpoint_location.GetID())
    print_format("IsValid", breakpoint_location.IsValid())
    print_format("GetAddress", breakpoint_location.GetAddress())  # SBAddress
    print_format("GetLoadAddress", breakpoint_location.GetLoadAddress())
    print_format("IsEnabled", breakpoint_location.IsEnabled())
    print_format("GetHitCount", breakpoint_location.GetHitCount())
    print_format("GetIgnoreCount", breakpoint_location.GetIgnoreCount())
    print_format("GetCondition", breakpoint_location.GetCondition())
    print_format("GetAutoContinue", breakpoint_location.GetAutoContinue())
    string_list = lldb.SBStringList()
    breakpoint_location.GetCommandLineCommands(string_list)
    print_format("GetCommandLineCommands", get_string_from_SBStringList(string_list))
    print_format("GetThreadID", breakpoint_location.GetThreadID())
    print_format("GetThreadIndex", breakpoint_location.GetThreadIndex())
    print_format("GetThreadName", breakpoint_location.GetThreadName())
    print_format("GetQueueName", breakpoint_location.GetQueueName())
    print_format("IsResolved", breakpoint_location.IsResolved())
    print_format("GetBreakpoint", breakpoint_location.GetBreakpoint())  # SBBreakpoint


def pSBError(obj: Optional[lldb.SBError]) -> None:
    if obj is not None:
        error = obj
    else:
        error = lldb.debugger.GetSelectedTarget().GetProcess().GetSelectedThread().GetSelectedFrame().FindVariable("self").GetError()

    print_class_name("SBError")
    print_format("SBError", error)
    print_format("GetCString", error.GetCString())
    print_format("Fail", error.Fail())
    print_format("Success", error.Success())
    print_format("GetError", error.GetError())
    print_format("GetType", error.GetType())  # ErrorType int
    print_format("IsValid", error.IsValid())


def pSBType(obj: Optional[lldb.SBType]) -> None:
    if obj is not None:
        t = obj
    else:
        t = lldb.debugger.GetSelectedTarget().GetProcess().GetSelectedThread().GetSelectedFrame().GetFunction().GetType()
        # t = lldb.debugger.GetSelectedTarget().GetProcess().GetSelectedThread().GetSelectedFrame().FindVariable("self").GetType()
        # t = lldb.debugger.GetSelectedTarget().FindFirstType("UIAlertAction")

    print_class_name("SBType")
    print_format("SBType", t)
    print_format("IsValid", t.IsValid())
    print_format("GetByteSize", t.GetByteSize())
    print_format("IsPointerType", t.IsPointerType())
    print_format("IsReferenceType", t.IsReferenceType())
    print_format("IsFunctionType", t.IsFunctionType())
    print_format("IsPolymorphicClass", t.IsPolymorphicClass())
    print_format("IsArrayType", t.IsArrayType())
    print_format("IsVectorType", t.IsVectorType())
    print_format("IsTypedefType", t.IsTypedefType())
    print_format("IsAnonymousType", t.IsAnonymousType())
    print_format("IsScopedEnumerationType", t.IsScopedEnumerationType())
    print_format("IsAggregateType", t.IsAggregateType())
    print_format("GetPointerType", t.GetPointerType())  # SBType
    print_format("GetPointeeType", t.GetPointeeType())  # SBType
    print_format("GetReferenceType", t.GetReferenceType())  # SBType
    print_format("GetTypedefedType", t.GetTypedefedType())  # SBType
    print_format("GetDereferencedType", t.GetDereferencedType())  # SBType
    print_format("GetUnqualifiedType", t.GetUnqualifiedType())  # SBType
    print_format("GetCanonicalType", t.GetCanonicalType())  # SBType
    print_format("GetEnumerationIntegerType", t.GetEnumerationIntegerType())  # SBType
    print_format("GetArrayElementType", t.GetArrayElementType())  # SBType
    print_format("GetVectorElementType", t.GetVectorElementType())  # SBType
    print_format("GetBasicType", t.GetBasicType())  # BasicType int
    print_format("GetNumberOfFields", t.GetNumberOfFields())
    print_format("GetNumberOfDirectBaseClasses", t.GetNumberOfDirectBaseClasses())
    print_format("GetNumberOfVirtualBaseClasses", t.GetNumberOfVirtualBaseClasses())
    print_format("GetEnumMembers", t.GetEnumMembers())  # SBTypeEnumMemberList
    print_format("GetModule", t.GetModule())  # SBModule
    print_format("GetName", t.GetName())
    print_format("GetDisplayTypeName", t.GetDisplayTypeName())
    print_format("GetTypeClass", t.GetTypeClass())  # TypeClass int
    print_format("GetNumberOfTemplateArguments", t.GetNumberOfTemplateArguments())
    print_format("GetFunctionReturnType", t.GetFunctionReturnType())  # SBType
    print_format("GetFunctionArgumentTypes", t.GetFunctionArgumentTypes())  # SBTypeList
    print_format("GetNumberOfMemberFunctions", t.GetNumberOfMemberFunctions())
    print_format("IsTypeComplete", t.IsTypeComplete())
    print_format("GetTypeFlags", t.GetTypeFlags())

    print_traversal(t, "GetNumberOfFields", "GetFieldAtIndex")  # [SBTypeMember]
    print_traversal(t, "GetNumberOfDirectBaseClasses", "GetDirectBaseClassAtIndex")  # [SBTypeMember]
    print_traversal(t, "GetNumberOfVirtualBaseClasses", "GetVirtualBaseClassAtIndex")  # [SBTypeMember]
    print_traversal(t, "GetNumberOfTemplateArguments", "GetTemplateArgumentType")  # [SBType]
    print_traversal(t, "GetNumberOfMemberFunctions", "GetMemberFunctionAtIndex")  # [SBTypeMemberFunction]


def pSBTypeMemberFunction(obj: Optional[lldb.SBTypeMemberFunction]) -> None:
    if obj is not None:
        func = obj
    else:
        func = lldb.debugger.GetSelectedTarget().GetProcess().GetSelectedThread().GetSelectedFrame().FindVariable("self").GetType().GetMemberFunctionAtIndex(0)
        # func = lldb.debugger.GetSelectedTarget().FindFirstType("UIAlertAction").GetMemberFunctionAtIndex(0)

    print_class_name("SBTypeMemberFunction")
    print_format("SBTypeMemberFunction", func)
    print_format("IsValid", func.IsValid())
    print_format("GetName", func.GetName())
    print_format("GetDemangledName", func.GetDemangledName())
    print_format("GetMangledName", func.GetMangledName())
    print_format("GetType", func.GetType())  # SBType
    print_format("GetReturnType", func.GetReturnType())  # SBType
    print_format("GetNumberOfArguments", func.GetNumberOfArguments())
    print_format("GetKind", func.GetKind())  # MemberFunctionKind int

    print_traversal(func, "GetNumberOfArguments", "GetArgumentTypeAtIndex")  # [SBType]


def pSBTypeCategory(obj: Optional[lldb.SBTypeCategory]) -> None:
    if obj is not None:
        category = obj
    else:
        category = lldb.debugger.GetDefaultCategory()

    print_class_name("SBTypeCategory")
    print_format("SBTypeCategory", category)
    print_format("IsValid", category.IsValid())
    print_format("GetEnabled", category.GetEnabled())
    print_format("GetName", category.GetName())
    print_format("GetNumLanguages", category.GetNumLanguages())
    print_format("GetNumFormats", category.GetNumFormats())
    print_format("GetNumSummaries", category.GetNumSummaries())
    print_format("GetNumFilters", category.GetNumFilters())
    print_format("GetNumSynthetics", category.GetNumSynthetics())

    print_traversal(category, "GetNumLanguages", "GetLanguageAtIndex")  # [LanguageType] [int]
    print_traversal(category, "GetNumFormats", "GetFormatAtIndex")  # [SBTypeFormat]
    print_traversal(category, "GetNumSummaries", "GetSummaryAtIndex")  # [SBTypeSummary]
    print_traversal(category, "GetNumFilters", "GetFilterAtIndex")  # [SBTypeFilter]
    print_traversal(category, "GetNumSynthetics", "GetSyntheticAtIndex")  # [SBTypeSynthetic]


def pSBBroadcaster(obj: Optional[lldb.SBBroadcaster]) -> None:
    if obj is not None:
        broadcaster = obj
    else:
        broadcaster = lldb.debugger.GetCommandInterpreter().GetBroadcaster()
        # broadcaster = lldb.debugger.GetSelectedTarget().GetBroadcaster()
        # broadcaster = lldb.debugger.GetSelectedTarget().GetProcess().GetBroadcaster()

    print_class_name("SBBroadcaster")
    print_format("SBBroadcaster", broadcaster)
    print_format("IsValid", broadcaster.IsValid())
    print_format("GetName", broadcaster.GetName())


def pSBListener(obj: Optional[lldb.SBListener]) -> None:
    if obj is not None:
        listener = obj
    else:
        listener = lldb.debugger.GetListener()
        # listener = lldb.debugger.GetSelectedTarget().GetLaunchInfo().GetListener()
        # listener = lldb.debugger.GetSelectedTarget().GetLaunchInfo().GetShadowListener()

    print_class_name("SBListener")
    print_format("SBListener", listener)
    print_format("IsValid", listener.IsValid())


def pSBEvent(obj: Optional[lldb.SBEvent]) -> None:
    if obj is not None:
        event = obj
    else:
        event = lldb.SBEvent()

    print_class_name("SBEvent")
    print_format("IsValid", event.IsValid())
    print_format("GetDataFlavor", event.GetDataFlavor())
    event_type = event.GetType()
    print_format("GetType", event_type)
    print_format("GetBroadcaster", event.GetBroadcaster())  # SBBroadcaster
    print_format("GetBroadcasterClass", event.GetBroadcasterClass())
    print_format("GetCStringFromEvent", lldb.SBEvent.GetCStringFromEvent(event))


    is_process_event = lldb.SBProcess.EventIsProcessEvent(event)
    print_format("SBProcess.EventIsProcessEvent", is_process_event)
    if is_process_event:
        # print_format("SBProcess.GetProcessFromEvent", lldb.SBProcess.GetProcessFromEvent(event))  # SBProcess
        print_format("SBProcess.GetRestartedFromEvent", lldb.SBProcess.GetRestartedFromEvent(event))
        print_format("SBProcess.GetNumRestartedReasonsFromEvent", lldb.SBProcess.GetNumRestartedReasonsFromEvent(event))
        print_format("SBProcess.GetInterruptedFromEvent", lldb.SBProcess.GetInterruptedFromEvent(event))

        # StateType https://github.com/llvm/llvm-project/blob/master/lldb/include/lldb/lldb-enumerations.h
        state = lldb.SBProcess.GetStateFromEvent(event)  # lldb::StateType int
        state_string = lldb.SBDebugger.StateAsCString(state)
        print_format("SBProcess.GetStateFromEvent(raw)", state)
        print_format("SBProcess.GetStateFromEvent(resolved)", state_string)

        event_type_string = 'unknown'
        if event_type == lldb.SBProcess.eBroadcastBitStateChanged:
            event_type_string = 'eBroadcastBitStateChanged'
        elif event_type == lldb.SBProcess.eBroadcastBitInterrupt:
            event_type_string = 'eBroadcastBitInterrupt'
        elif event_type == lldb.SBProcess.eBroadcastBitSTDOUT:
            event_type_string = 'eBroadcastBitSTDOUT'
        elif event_type == lldb.SBProcess.eBroadcastBitSTDERR:
            event_type_string = 'eBroadcastBitSTDERR'
        elif event_type == lldb.SBProcess.eBroadcastBitProfileData:
            event_type_string = 'eBroadcastBitProfileData'
        elif event_type == lldb.SBProcess.eBroadcastBitStructuredData:
            event_type_string = 'eBroadcastBitStructuredData'
        print_format("GetType(resolved)", event_type_string)

    is_structured_data_event = lldb.SBProcess.EventIsStructuredDataEvent(event)
    print_format("SBProcess.EventIsStructuredDataEvent", is_structured_data_event)
    if is_structured_data_event:
        sd = lldb.SBProcess.GetStructuredDataFromEvent(event)  # SBStructuredData
        print_format("SBProcess.GetStructuredDataFromEvent", sd)


    is_target_event = lldb.SBTarget.EventIsTargetEvent(event)
    print_format("SBTarget.EventIsTargetEvent", is_target_event)
    if is_target_event:
        print_format("SBTarget.GetTargetFromEvent", lldb.SBTarget.GetTargetFromEvent(event))  # SBTarget
        print_format("SBTarget.GetNumModulesFromEvent", lldb.SBTarget.GetNumModulesFromEvent(event))
        event_type_string = 'unknown'
        if event_type == lldb.SBTarget.eBroadcastBitBreakpointChanged:
            event_type_string = 'eBroadcastBitBreakpointChanged'
        elif event_type == lldb.SBTarget.eBroadcastBitModulesLoaded:
            event_type_string = 'eBroadcastBitModulesLoaded'
        elif event_type == lldb.SBTarget.eBroadcastBitModulesUnloaded:
            event_type_string = 'eBroadcastBitModulesUnloaded'
        elif event_type == lldb.SBTarget.eBroadcastBitWatchpointChanged:
            event_type_string = 'eBroadcastBitWatchpointChanged'
        elif event_type == lldb.SBTarget.eBroadcastBitSymbolsLoaded:
            event_type_string = 'eBroadcastBitSymbolsLoaded'
        print_format("GetType(resolved)", event_type_string)


    is_breakpoint_event = lldb.SBBreakpoint.EventIsBreakpointEvent(event)
    print_format("SBBreakpoint.EventIsBreakpointEvent", is_breakpoint_event)
    if is_breakpoint_event:
        print_format("SBBreakpoint.GetBreakpointFromEvent", lldb.SBBreakpoint.GetBreakpointFromEvent(event))  # SBBreakpoint
        print_format("SBBreakpoint.GetNumBreakpointLocationsFromEvent", lldb.SBBreakpoint.GetNumBreakpointLocationsFromEvent(event))
        bp_event_type = lldb.SBBreakpoint.GetBreakpointEventTypeFromEvent(event)  # lldb::BreakpointEventType
        bp_event_type_string = 'unknown'
        if bp_event_type == lldb.eBreakpointEventTypeInvalidType:
            bp_event_type_string = 'eBreakpointEventTypeInvalidType'
        elif bp_event_type == lldb.eBreakpointEventTypeAdded:
            bp_event_type_string = 'eBreakpointEventTypeAdded'
        elif bp_event_type == lldb.eBreakpointEventTypeRemoved:
            bp_event_type_string = 'eBreakpointEventTypeRemoved'
        elif bp_event_type == lldb.eBreakpointEventTypeLocationsAdded:
            bp_event_type_string = 'eBreakpointEventTypeLocationsAdded'
        elif bp_event_type == lldb.eBreakpointEventTypeLocationsRemoved:
            bp_event_type_string = 'eBreakpointEventTypeLocationsRemoved'
        elif bp_event_type == lldb.eBreakpointEventTypeLocationsResolved:
            bp_event_type_string = 'eBreakpointEventTypeLocationsResolved'
        elif bp_event_type == lldb.eBreakpointEventTypeEnabled:
            bp_event_type_string = 'eBreakpointEventTypeEnabled'
        elif bp_event_type == lldb.eBreakpointEventTypeDisabled:
            bp_event_type_string = 'eBreakpointEventTypeDisabled'
        elif bp_event_type == lldb.eBreakpointEventTypeCommandChanged:
            bp_event_type_string = 'eBreakpointEventTypeCommandChanged'
        elif bp_event_type == lldb.eBreakpointEventTypeConditionChanged:
            bp_event_type_string = 'eBreakpointEventTypeConditionChanged'
        elif bp_event_type == lldb.eBreakpointEventTypeIgnoreChanged:
            bp_event_type_string = 'eBreakpointEventTypeIgnoreChanged'
        elif bp_event_type == lldb.eBreakpointEventTypeThreadChanged:
            bp_event_type_string = 'eBreakpointEventTypeThreadChanged'
        elif bp_event_type == lldb.eBreakpointEventTypeAutoContinueChanged:
            bp_event_type_string = 'eBreakpointEventTypeAutoContinueChanged'
        print_format("SBBreakpoint.GetBreakpointEventTypeFromEvent(raw)", bp_event_type)
        print_format("SBBreakpoint.GetBreakpointEventTypeFromEvent(resolved)", bp_event_type_string)


    is_command_interpreter_event = lldb.SBCommandInterpreter.EventIsCommandInterpreterEvent(event)
    print_format("SBCommandInterpreter.EventIsCommandInterpreterEvent", is_command_interpreter_event)
    if is_command_interpreter_event:
        event_type_string = 'unknown'
        if event_type == lldb.SBCommandInterpreter.eBroadcastBitThreadShouldExit:
            event_type_string = 'eBroadcastBitThreadShouldExit'
        elif event_type == lldb.SBCommandInterpreter.eBroadcastBitResetPrompt:
            event_type_string = 'eBroadcastBitResetPrompt'
        elif event_type == lldb.SBCommandInterpreter.eBroadcastBitQuitCommandReceived:
            event_type_string = 'eBroadcastBitQuitCommandReceived'
        elif event_type == lldb.SBCommandInterpreter.eBroadcastBitAsynchronousOutputData:
            event_type_string = 'eBroadcastBitAsynchronousOutputData'
        elif event_type == lldb.SBCommandInterpreter.eBroadcastBitAsynchronousErrorData:
            event_type_string = 'eBroadcastBitAsynchronousErrorData'
        print_format("GetType(resolved)", event_type_string)


    is_thread_event = lldb.SBThread.EventIsThreadEvent(event)
    print_format("SBThread.EventIsThreadEvent", is_thread_event)
    if is_thread_event:
        print_format("SBThread.GetThreadFromEvent", lldb.SBThread.GetThreadFromEvent(event))  # SBThread
        print_format("SBThread.GetStackFrameFromEvent", lldb.SBThread.GetStackFrameFromEvent(event))  # SBFrame
        event_type_string = 'unknown'
        if event_type == lldb.SBThread.eBroadcastBitStackChanged:
            event_type_string = 'eBroadcastBitStackChanged'
        elif event_type == lldb.SBThread.eBroadcastBitThreadSuspended:
            event_type_string = 'eBroadcastBitThreadSuspended'
        elif event_type == lldb.SBThread.eBroadcastBitThreadResumed:
            event_type_string = 'eBroadcastBitThreadResumed'
        elif event_type == lldb.SBThread.eBroadcastBitSelectedFrameChanged:
            event_type_string = 'eBroadcastBitSelectedFrameChanged'
        elif event_type == lldb.SBThread.eBroadcastBitThreadSelected:
            event_type_string = 'eBroadcastBitThreadSelected'
        print_format("GetType(resolved)", event_type_string)


    is_watchpoint_event = lldb.SBWatchpoint.EventIsWatchpointEvent(event)
    print_format("SBWatchpoint.EventIsWatchpointEvent", is_watchpoint_event)
    if is_watchpoint_event:
        print_format("SBWatchpoint.GetWatchpointFromEvent", lldb.SBWatchpoint.GetWatchpointFromEvent(event))  # SBWatchpoint
        wp_event_type = lldb.SBWatchpoint.GetWatchpointEventTypeFromEvent(event)  # lldb::WatchpointEventType
        wp_event_type_string = 'unknown'
        if wp_event_type == lldb.eWatchpointEventTypeInvalidType:
            wp_event_type_string = 'eWatchpointEventTypeInvalidType'
        elif wp_event_type == lldb.eWatchpointEventTypeAdded:
            wp_event_type_string = 'eWatchpointEventTypeAdded'
        elif wp_event_type == lldb.eWatchpointEventTypeRemoved:
            wp_event_type_string = 'eWatchpointEventTypeRemoved'
        elif wp_event_type == lldb.eWatchpointEventTypeEnabled:
            wp_event_type_string = 'eWatchpointEventTypeEnabled'
        elif wp_event_type == lldb.eWatchpointEventTypeDisabled:
            wp_event_type_string = 'eWatchpointEventTypeDisabled'
        elif wp_event_type == lldb.eWatchpointEventTypeCommandChanged:
            wp_event_type_string = 'eWatchpointEventTypeCommandChanged'
        elif wp_event_type == lldb.eWatchpointEventTypeConditionChanged:
            wp_event_type_string = 'eWatchpointEventTypeConditionChanged'
        elif wp_event_type == lldb.eWatchpointEventTypeIgnoreChanged:
            wp_event_type_string = 'eWatchpointEventTypeIgnoreChanged'
        elif wp_event_type == lldb.eWatchpointEventTypeThreadChanged:
            wp_event_type_string = 'eWatchpointEventTypeThreadChanged'
        elif wp_event_type == lldb.eWatchpointEventTypeTypeChanged:
            wp_event_type_string = 'eWatchpointEventTypeTypeChanged'
        print_format("SBWatchpoint.GetWatchpointEventTypeFromEvent(raw)", wp_event_type)
        print_format("SBWatchpoint.GetWatchpointEventTypeFromEvent(resolved)", wp_event_type_string)


def pSBStructuredData(obj: Optional[lldb.SBStructuredData]) -> None:
    if obj is not None:
        sd = obj
    else:
        sd = lldb.debugger.GetBuildConfiguration()
        # sd = lldb.debugger.GetSelectedTarget().GetStatistics()
        # sd = lldb.debugger.GetSetting()

    print_class_name("SBStructuredData")
    print_format("SBStructuredData", sd)
    print_format("IsValid", sd.IsValid())
    print_format("GetType(raw)", sd.GetType())  # StructuredDataType int
    print_format("GetType(resolved)", get_string_from_structured_data_type(sd.GetType()))
    print_format("GetSize", sd.GetSize())
    string_list = lldb.SBStringList()
    sd.GetKeys(string_list)
    print_format("GetKeys", get_string_from_SBStringList(string_list))
    print_format("GetUnsignedIntegerValue", sd.GetUnsignedIntegerValue())
    print_format("GetSignedIntegerValue", sd.GetSignedIntegerValue())
    print_format("GetIntegerValue", sd.GetIntegerValue())
    print_format("GetFloatValue", sd.GetFloatValue())
    print_format("GetBooleanValue", sd.GetBooleanValue())
    print_format("GetStringValue", sd.GetStringValue(1000))
    print_format("GetGenericValue", sd.GetGenericValue())  # SBScriptObject
    stream = lldb.SBStream()
    sd.GetAsJSON(stream)
    print_format("GetAsJSON", stream.GetData())


def pSBPlatform(obj: Optional[lldb.SBPlatform]) -> None:
    if obj is not None:
        platform = obj
    else:
        platform = lldb.debugger.GetSelectedPlatform()
        # platform = lldb.debugger.GetSelectedTarget().GetPlatform()
        # platform = lldb.SBPlatform.GetHostPlatform()

    print_class_name("SBPlatform")
    print_format("SBPlatform", platform)
    print_format("SBPlatform.GetHostPlatform", lldb.SBPlatform.GetHostPlatform())  # SBPlatform
    print_format("IsValid", platform.IsValid())
    print_format("GetWorkingDirectory", platform.GetWorkingDirectory())
    print_format("GetName", platform.GetName())
    print_format("IsConnected", platform.IsConnected())
    print_format("GetTriple", platform.GetTriple())
    print_format("GetHostname", platform.GetHostname())
    print_format("GetOSBuild", platform.GetOSBuild())
    print_format("GetOSDescription", platform.GetOSDescription())
    print_format("GetOSMajorVersion", platform.GetOSMajorVersion())
    print_format("GetOSMinorVersion", platform.GetOSMinorVersion())
    print_format("GetOSUpdateVersion", platform.GetOSUpdateVersion())
    error = lldb.SBError()
    print_format("GetAllProcesses", platform.GetAllProcesses(error))  # SBProcessInfoList
    print_format("GetUnixSignals", platform.GetUnixSignals())  # SBUnixSignals
    print_format("GetEnvironment", platform.GetEnvironment())  # SBEnvironment


def pSBSourceManager(obj: Optional[lldb.SBSourceManager]) -> None:
    if obj is not None:
        manager = obj
    else:
        manager = lldb.debugger.GetSourceManager()
        # manager = lldb.debugger.GetSelectedTarget().GetSourceManager()

    print_class_name("SBSourceManager")
    print_format("SBSourceManager", manager)


def pSBUnixSignals(obj: Optional[lldb.SBUnixSignals]) -> None:
    if obj is not None:
        signals = obj
    else:
        signals = lldb.debugger.GetSelectedPlatform().GetUnixSignals()
        # signals = lldb.debugger.GetSelectedTarget().GetProcess().GetUnixSignals()

    print_class_name("SBUnixSignals")
    print_format("SBUnixSignals", signals)
    print_format("IsValid", signals.IsValid())
    print_format("GetNumSignals", signals.GetNumSignals())

    print_traversal(signals, "GetNumSignals", "GetSignalAtIndex")  # [int]


def pSBLaunchInfo(obj: Optional[lldb.SBLaunchInfo]) -> None:
    if obj is not None:
        info = obj
    else:
        info = lldb.debugger.GetSelectedTarget().GetLaunchInfo()

    print_class_name("SBLaunchInfo")
    print_format("SBLaunchInfo", info)
    print_format("GetProcessID", info.GetProcessID())
    print_format("GetUserID", info.GetUserID())
    print_format("GetGroupID", info.GetGroupID())
    print_format("UserIDIsValid", info.UserIDIsValid())
    print_format("GroupIDIsValid", info.GroupIDIsValid())
    print_format("GetExecutableFile", info.GetExecutableFile())  # SBFileSpec
    print_format("GetListener", info.GetListener())  # SBListener
    print_format("GetShadowListener", info.GetShadowListener())  # SBListener
    print_format("GetNumArguments", info.GetNumArguments())
    print_format("GetNumEnvironmentEntries", info.GetNumEnvironmentEntries())
    print_format("GetEnvironment", info.GetEnvironment())  # SBEnvironment
    print_format("GetWorkingDirectory", info.GetWorkingDirectory())

    launch_flags = info.GetLaunchFlags()
    print_format("GetLaunchFlags", launch_flags)
    if launch_flags & lldb.eLaunchFlagExec:
        print(f"\teLaunchFlagExec ({lldb.eLaunchFlagExec})")
    if launch_flags & lldb.eLaunchFlagDebug:
        print(f"\teLaunchFlagDebug ({lldb.eLaunchFlagDebug})")
    if launch_flags & lldb.eLaunchFlagStopAtEntry:
        print(f"\teLaunchFlagStopAtEntry ({lldb.eLaunchFlagStopAtEntry})")
    if launch_flags & lldb.eLaunchFlagDisableASLR:
        print(f"\teLaunchFlagDisableASLR ({lldb.eLaunchFlagDisableASLR})")
    if launch_flags & lldb.eLaunchFlagDisableSTDIO:
        print(f"\teLaunchFlagDisableSTDIO ({lldb.eLaunchFlagDisableSTDIO})")
    if launch_flags & lldb.eLaunchFlagLaunchInTTY:
        print(f"\teLaunchFlagLaunchInTTY ({lldb.eLaunchFlagLaunchInTTY})")
    if launch_flags & lldb.eLaunchFlagLaunchInShell:
        print(f"\teLaunchFlagLaunchInShell ({lldb.eLaunchFlagLaunchInShell})")
    if launch_flags & lldb.eLaunchFlagLaunchInSeparateProcessGroup:
        print(f"\teLaunchFlagLaunchInSeparateProcessGroup ({lldb.eLaunchFlagLaunchInSeparateProcessGroup})")
    if launch_flags & lldb.eLaunchFlagDontSetExitStatus:
        print(f"\teLaunchFlagDontSetExitStatus ({lldb.eLaunchFlagDontSetExitStatus})")
    if launch_flags & lldb.eLaunchFlagDetachOnError:
        print(f"\teLaunchFlagDetachOnError ({lldb.eLaunchFlagDetachOnError})")
    if launch_flags & lldb.eLaunchFlagShellExpandArguments:
        print(f"\teLaunchFlagShellExpandArguments ({lldb.eLaunchFlagShellExpandArguments})")
    if launch_flags & lldb.eLaunchFlagCloseTTYOnExit:
        print(f"\teLaunchFlagCloseTTYOnExit ({lldb.eLaunchFlagCloseTTYOnExit})")
    if launch_flags & lldb.eLaunchFlagInheritTCCFromParent:
        print(f"\teLaunchFlagInheritTCCFromParent ({lldb.eLaunchFlagInheritTCCFromParent})")

    print_format("GetProcessPluginName", info.GetProcessPluginName())
    print_format("GetShell", info.GetShell())
    print_format("GetShellExpandArguments", info.GetShellExpandArguments())
    print_format("GetResumeCount", info.GetResumeCount())
    print_format("GetLaunchEventData", info.GetLaunchEventData())
    print_format("GetDetachOnError", info.GetDetachOnError())
    print_format("GetScriptedProcessClassName", info.GetScriptedProcessClassName())
    print_format("GetScriptedProcessDictionary", info.GetScriptedProcessDictionary())  # SBStructuredData

    print_traversal(info, "GetNumArguments", "GetArgumentAtIndex")  # [str]
    print_traversal(info, "GetNumEnvironmentEntries", "GetEnvironmentEntryAtIndex")  # [str]


def pSBEnvironment(obj: Optional[lldb.SBEnvironment]) -> None:
    if obj is not None:
        env = obj
    else:
        env = lldb.debugger.GetSelectedTarget().GetEnvironment()
        # env = lldb.debugger.GetSelectedTarget().GetLaunchInfo().GetEnvironment()

    print_class_name("SBEnvironment")
    print_format("SBEnvironment", env)
    print_format("GetNumValues", env.GetNumValues())
    entries_string_list = env.GetEntries()  # SBStringList
    print_format("GetEntries", entries_string_list)
    print_format("GetEntries(str)", get_string_from_SBStringList(entries_string_list))

    print_traversal(env, "GetNumValues", "GetNameAtIndex")
    print_traversal(env, "GetNumValues", "GetValueAtIndex")


def pSBCommandInterpreter(obj: Optional[lldb.SBCommandInterpreter]) -> None:
    if obj is not None:
        ci = obj
    else:
        ci = lldb.debugger.GetCommandInterpreter()

    print_class_name("SBCommandInterpreter")
    print_format("SBCommandInterpreter", ci)
    print_format("IsValid", ci.IsValid())
    print_format("GetPromptOnQuit", ci.GetPromptOnQuit())
    print_format("HasCustomQuitExitCode", ci.HasCustomQuitExitCode())
    print_format("GetQuitStatus", ci.GetQuitStatus())
    print_format("CommandExists", ci.CommandExists("breakpoint"))
    print_format("UserCommandExists", ci.UserCommandExists("plldbClassInfo"))
    print_format("AliasExists", ci.AliasExists('bt'))
    print_format("GetBroadcaster", ci.GetBroadcaster())  # SBBroadcaster
    print_format("GetBroadcasterClass", ci.GetBroadcasterClass())
    print_format("HasCommands", ci.HasCommands())
    print_format("HasAliases", ci.HasAliases())
    print_format("HasAliasOptions", ci.HasAliasOptions())
    print_format("IsInteractive", ci.IsInteractive())
    print_format("GetProcess", ci.GetProcess())  # SBProcess
    print_format("GetDebugger", ci.GetDebugger())  # SBDebugger
    print_format("IsActive", ci.IsActive())
    print_format("WasInterrupted", ci.WasInterrupted())
    print_format("InterruptCommand", ci.InterruptCommand())


def pSBCommandReturnObject(obj: Optional[lldb.SBCommandReturnObject]) -> None:
    if obj is not None:
        return_object = obj
    else:
        return_object = lldb.SBCommandReturnObject()
        lldb.debugger.GetCommandInterpreter().HandleCommand("breakpoint list", return_object)

    print_class_name("SBCommandReturnObject")
    print_format("SBCommandReturnObject", return_object)
    print_format("IsValid", return_object.IsValid())
    print_format("GetOutputSize", return_object.GetOutputSize())
    print_format("GetErrorSize", return_object.GetErrorSize())
    print_format("GetOutput", return_object.GetOutput())
    print_format("GetError", return_object.GetError())
    status = return_object.GetStatus()  # ReturnStatus int
    print_format("GetStatus(raw)", status)
    print_format("GetStatus(resolved)", get_string_from_return_status(status))
    print_format("Succeeded", return_object.Succeeded())
    print_format("HasResult", return_object.HasResult())


def pSBQueue(obj: Optional[lldb.SBQueue]) -> None:
    if obj is not None:
        queue = obj
    else:
        queue = lldb.debugger.GetSelectedTarget().GetProcess().GetSelectedThread().GetQueue()
        # queue = lldb.debugger.GetSelectedTarget().GetProcess().GetQueueAtIndex(0)

    print_class_name("SBQueue")
    print_format("SBQueue", queue)
    print_format("IsValid", queue.IsValid())
    print_format("GetProcess", queue.GetProcess())  # SBProcess
    print_format("GetQueueID", queue.GetQueueID())
    print_format("GetName", queue.GetName())
    queue_kind = queue.GetKind()  # lldb::QueueKind int
    print_format("GetKind(raw)", queue_kind)
    print_format("GetKind(resolved)", get_string_from_queue_kind(queue_kind))
    print_format("GetIndexID", queue.GetIndexID())
    print_format("GetNumThreads", queue.GetNumThreads())
    print_format("GetNumPendingItems", queue.GetNumPendingItems())
    print_format("GetNumRunningItems", queue.GetNumRunningItems())

    print_traversal(queue, "GetNumThreads", "GetThreadAtIndex")
    print_traversal(queue, "GetNumPendingItems", "GetPendingItemAtIndex")  # [SBQueueItem]


def pSBSection(obj: Optional[lldb.SBSection]) -> None:
    if obj is not None:
        section = obj
    else:
        section = lldb.debugger.GetSelectedTarget().GetProcess().GetSelectedThread().GetSelectedFrame().GetModule().FindSection("__TEXT")

    print_class_name("SBSection")
    print_format("SBSection", section)
    print_format("IsValid", section.IsValid())
    print_format("GetName", section.GetName())
    print_format("GetParent", section.GetParent())  # SBSection
    print_format("GetNumSubSections", section.GetNumSubSections())
    print_format("GetFileAddress", section.GetFileAddress())
    print_format("GetLoadAddress", section.GetLoadAddress(lldb.debugger.GetSelectedTarget()))
    print_format("GetByteSize", section.GetByteSize())
    print_format("GetFileOffset", section.GetFileOffset())
    print_format("GetFileByteSize", section.GetFileByteSize())
    # print_format("GetSectionData", section.GetSectionData())  # SBData
    section_type = section.GetSectionType()  # SectionType int
    print_format("GetSectionType(raw)", section_type)
    print_format("GetSectionType(resolved)", get_string_from_section_type(section_type))
    print_format("GetPermissions", section.GetPermissions())
    print_format("GetTargetByteSize", section.GetTargetByteSize())
    print_format("GetAlignment", section.GetAlignment())
    print_format("get_addr", section.get_addr())  # SBAddress

    print_traversal(section, "GetNumSubSections", "GetSubSectionAtIndex")  # [SBSection]


def pSBMemoryRegionInfoList(obj: Optional[lldb.SBMemoryRegionInfoList]) -> None:
    if obj is not None:
        memory_region_info_list = obj
    else:
        memory_region_info_list = lldb.debugger.GetSelectedTarget().GetProcess().GetMemoryRegions()

    print_class_name("SBMemoryRegionInfoList")
    print_format("SBMemoryRegionInfoList", memory_region_info_list)
    print_format("GetSize", memory_region_info_list.GetSize())

    size = memory_region_info_list.GetSize()
    global g_unlimited
    print(f"\n##### [GetMemoryRegionContainingAddress]({size}) #####")
    for i in range(size):
        if i == 100 and not g_unlimited:
            break
        info = lldb.SBMemoryRegionInfo()
        memory_region_info_list.GetMemoryRegionAtIndex(i, info)
        print(type(info))
        print(info)


def pSBMemoryRegionInfo(obj: Optional[lldb.SBMemoryRegionInfo]) -> None:
    if obj is not None:
        memoryRegionInfo = obj
    else:
        memoryRegionInfo = lldb.SBMemoryRegionInfo()
        index = 0
        lldb.debugger.GetSelectedTarget().GetProcess().GetMemoryRegions().GetMemoryRegionAtIndex(index, memoryRegionInfo)

    print_class_name("SBMemoryRegionInfo")
    print_format("SBMemoryRegionInfo", memoryRegionInfo)
    print_format("GetRegionBase", memoryRegionInfo.GetRegionBase())
    print_format("GetRegionEnd", memoryRegionInfo.GetRegionEnd())
    print_format("IsReadable", memoryRegionInfo.IsReadable())
    print_format("IsWritable", memoryRegionInfo.IsWritable())
    print_format("IsExecutable", memoryRegionInfo.IsExecutable())
    print_format("IsMapped", memoryRegionInfo.IsMapped())
    print_format("GetName", memoryRegionInfo.GetName())
    print_format("HasDirtyMemoryPageList", memoryRegionInfo.HasDirtyMemoryPageList())
    print_format("GetNumDirtyPages", memoryRegionInfo.GetNumDirtyPages())
    print_format("GetPageSize", memoryRegionInfo.GetPageSize())

    print_traversal(memoryRegionInfo, "GetNumDirtyPages", "GetDirtyPageAddressAtIndex")  # [int]


def pSBExpressionOptions(obj: Optional[lldb.SBExpressionOptions]) -> None:
    if obj is not None:
        options = obj
    else:
        options = lldb.SBExpressionOptions()

    print_class_name("SBExpressionOptions")
    print_format("SBExpressionOptions", options)
    print_format("GetCoerceResultToId", options.GetCoerceResultToId())
    print_format("GetUnwindOnError", options.GetUnwindOnError())
    print_format("GetIgnoreBreakpoints", options.GetIgnoreBreakpoints())
    print_format("GetFetchDynamicValue", options.GetFetchDynamicValue())
    print_format("GetTimeoutInMicroSeconds", options.GetTimeoutInMicroSeconds())
    print_format("GetOneThreadTimeoutInMicroSeconds", options.GetOneThreadTimeoutInMicroSeconds())
    print_format("GetTryAllThreads", options.GetTryAllThreads())
    print_format("GetStopOthers", options.GetStopOthers())
    print_format("GetTrapExceptions", options.GetTrapExceptions())
    print_format("GetPlaygroundTransformEnabled", options.GetPlaygroundTransformEnabled())
    print_format("GetPlaygroundTransformHighPerformance", options.GetPlaygroundTransformHighPerformance())
    print_format("GetREPLMode", options.GetREPLMode())
    print_format("GetGenerateDebugInfo", options.GetGenerateDebugInfo())
    print_format("GetSuppressPersistentResult", options.GetSuppressPersistentResult())
    print_format("GetPrefix", options.GetPrefix())
    print_format("GetAutoApplyFixIts", options.GetAutoApplyFixIts())
    print_format("GetRetriesWithFixIts", options.GetRetriesWithFixIts())
    print_format("GetTopLevel", options.GetTopLevel())
    print_format("GetAllowJIT", options.GetAllowJIT())
