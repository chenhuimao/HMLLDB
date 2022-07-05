# The MIT License (MIT)
#
# Copyright (c) 2022 Huimao Chen
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
from typing import List
import HMLLDBHelpers as HM
import HMLLDBClassInfo


def __lldb_init_module(debugger, internal_dict):
    debugger.HandleCommand('command script add -f HMBreakpoint.breakpoint_frame bpframe -h "Set a symbolic breakpoint that stops only when the specified stack keyword is matched"')


def breakpoint_frame(debugger, command, exe_ctx, result, internal_dict):
    """
    Syntax:
        bpframe <symbol or function> <stack keyword 1> <stack keyword 2> ... <stack keyword n>

    Examples:
        // Stop when "viewDidAppear:" is hit and the call stack contains "customMethod"
        (lldb) bpframe viewDidAppear: customMethod

    Notice:
        1. Separate keywords with spaces.
        2. Match keywords in order.
        3. Hitting a breakpoint is expensive even if it doesn't stop. Do not use symbolic breakpoint to set high-frequency symbols.

    This command is implemented in HMBreakpoint.py
    """

    parameters_list: List[str] = command.split(" ")
    # HM.DPrint(parameters_list)

    if len(parameters_list) < 2:
        HM.DPrint("Error input. Requires at least 2 parameters. Please enter 'help bpframe' for more infomation")
        return

    target = lldb.debugger.GetSelectedTarget()
    breakpoint = target.BreakpointCreateByName(parameters_list[0])
    breakpoint.AddName(f"HMLLDB_bpframe_{parameters_list[0]}")

    # call stack symbols for script callback
    call_stack_symbols: str = ""
    for i in range(1, len(parameters_list)):
        if i == 1:
            call_stack_symbols += '"' + parameters_list[1] + '"'
        else:
            call_stack_symbols += ',"' + parameters_list[i] + '"'

    extra_args = lldb.SBStructuredData()
    stream = lldb.SBStream()
    stream.Print(f'[{call_stack_symbols}]')
    extra_args.SetFromJSON(stream)

    # set callback with extra_args
    error: lldb.SBError = breakpoint.SetScriptCallbackFunction("HMBreakpoint.breakpoint_frame_handler", extra_args)
    if error.Success():
        HM.DPrint("Set breakpoint successfully")
        breakpoint_id = breakpoint.GetID()
        lldb.debugger.HandleCommand(f"breakpoint list {breakpoint_id}")
    else:
        HM.DPrint(error)


def breakpoint_frame_handler(frame, bp_loc, extra_args, internal_dict) -> bool:
    if not extra_args.IsValid():
        return False
    if extra_args.GetType() != lldb.eStructuredDataTypeArray:
        return False

    # Get keywords
    keywords: List[str] = []
    for i in range(extra_args.GetSize()):
        arg: lldb.SBStructuredData = extra_args.GetItemAtIndex(i)
        if arg.GetType() != lldb.eStructuredDataTypeString:
            continue
        keyword = arg.GetStringValue(100)
        keywords.append(keyword)

    keywords_size = len(keywords)
    if keywords_size == 0:
        HM.DPrint("Error: Missing keywords.")
        return False
    keywords_index = 0

    # Get frame and match keywords in order
    result = False
    thread = frame.GetThread()
    for i in range(thread.GetNumFrames()):
        frame_in_stack = thread.GetFrameAtIndex(i)
        frame_display_name = frame_in_stack.GetDisplayFunctionName()
        if keywords[keywords_index] in frame_display_name:
            keywords_index += 1
            if keywords_index == keywords_size:
                result = True
                break
    return result

