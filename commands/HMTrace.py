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
from datetime import datetime
import optparse
import shlex
import HMLLDBClassInfo
import HMLLDBHelpers as HM


def __lldb_init_module(debugger, internal_dict):
    debugger.HandleCommand('command script add -f HMTrace.trace_function tracefunction -h "Trace functions step by step until the next breakpoint is hit."')
    debugger.HandleCommand('command script add -f HMTrace.trace_instruction traceinstruction -h "Trace instructions step by step until the next breakpoint is hit."')


g_function_limit: int = -1
g_instruction_limit: int = -1


def trace_function(debugger, command, exe_ctx, result, internal_dict):
    """
    Syntax:
        tracefunction [-m <count>]

    Options:
        --max/-m; Maximum number of functions to print

    Examples:
        (lldb) tracefunction
        (lldb) tracefunction -m 500

    This command is implemented in HMTrace.py
    """

    command_args = shlex.split(command)
    parser = generate_trace_function_option_parser()
    try:
        # options: optparse.Values
        # args: list
        (options, args_list) = parser.parse_args(command_args)
    except:
        result.SetError(parser.usage)
        return

    global g_function_limit
    if options.max_count:
        g_function_limit = int(options.max_count)
        if g_function_limit <= 0:
            HM.DPrint("Error input, Please enter \"help tracefunction\" for help.")
            return
    else:
        g_function_limit = -1

    debugger.HandleCommand('thread step-scripted -C HMTrace.TraceFunctionStep')


def generate_trace_function_option_parser() -> optparse.OptionParser:
    usage = "usage: tracefunction [--max <count>]"
    parser = optparse.OptionParser(usage=usage, prog="tracefunction")
    parser.add_option("-m", "--max",
                      action="store",
                      default=None,
                      dest="max_count",
                      help="")
    return parser


class TraceFunctionStep:

    def __init__(self, thread_plan, dic):
        HM.DPrint("==========Begin========================================================")
        self.start_time = datetime.now().strftime("%H:%M:%S")
        self.thread_plan = thread_plan
        self.instruction_count = 1
        self.function_count = 1

        target = self.thread_plan.GetThread().GetProcess().GetTarget()
        stream = lldb.SBStream()
        pc_address = self.thread_plan.GetThread().GetFrameAtIndex(0).GetPCAddress()
        pc_address.GetDescription(stream)
        self.last_pc_address_value = pc_address.GetLoadAddress(target)
        self.last_function: str = stream.GetData()
        print(f"{self.last_function}\t({hex(self.last_pc_address_value)})")  # first address

    def explains_stop(self, event: lldb.SBEvent) -> bool:
        self.instruction_count += 1

        target = self.thread_plan.GetThread().GetProcess().GetTarget()
        stream = lldb.SBStream()
        pc_address = self.thread_plan.GetThread().GetFrameAtIndex(0).GetPCAddress()
        pc_address.GetDescription(stream)
        function_str = stream.GetData().split(" + ")[0]
        if function_str not in self.last_function:
            print(f"{self.last_function}\t({hex(self.last_pc_address_value)})")
            self.function_count += 1
        self.last_pc_address_value = pc_address.GetLoadAddress(target)
        self.last_function = stream.GetData()
        return True

    def should_stop(self, event: lldb.SBEvent) -> bool:
        global g_function_limit
        if 0 < g_function_limit <= self.function_count + 1:
            self.print_before_stop()
            return True

        if self.thread_plan.GetThread().GetStopReason() != lldb.eStopReasonTrace:
            self.print_before_stop()
            return True
        else:
            return False

    def should_step(self) -> bool:
        return True

    def print_before_stop(self) -> None:
        self.thread_plan.SetPlanComplete(True)
        target = self.thread_plan.GetThread().GetProcess().GetTarget()
        stream = lldb.SBStream()
        pc_address = self.thread_plan.GetThread().GetFrameAtIndex(0).GetPCAddress()
        pc_address.GetDescription(stream)
        print(f"{stream.GetData()}\t({hex(pc_address.GetLoadAddress(target))})")  # current address
        self.function_count += 1

        HM.DPrint("==========End========================================================")
        HM.DPrint(f"Instruction count: {self.instruction_count}")
        HM.DPrint(f"Function count: {self.function_count}")
        HM.DPrint(f"Start time: {self.start_time}")
        stop_time = datetime.now().strftime("%H:%M:%S")
        HM.DPrint(f"Stop time: {stop_time}")


def trace_instruction(debugger, command, exe_ctx, result, internal_dict):
    """
    Syntax:
        traceinstruction [-m <count>]

    Options:
        --max/-m; Maximum number of instructions to print

    Examples:
        (lldb) traceinstruction
        (lldb) traceinstruction -m 6000

    This command is implemented in HMTrace.py
    """
    command_args = shlex.split(command)
    parser = generate_trace_instruction_option_parser()
    try:
        # options: optparse.Values
        # args: list
        (options, args_list) = parser.parse_args(command_args)
    except:
        result.SetError(parser.usage)
        return

    global g_instruction_limit
    if options.max_count:
        g_instruction_limit = int(options.max_count)
        if g_instruction_limit <= 0:
            HM.DPrint("Error input, Please enter \"help traceinstruction\" for help.")
            return
    else:
        g_instruction_limit = -1

    debugger.HandleCommand('thread step-scripted -C HMTrace.TraceInstructionStep')


def generate_trace_instruction_option_parser() -> optparse.OptionParser:
    usage = "usage: traceinstruction [--max <count>]"
    parser = optparse.OptionParser(usage=usage, prog="traceinstruction")
    parser.add_option("-m", "--max",
                      action="store",
                      default=None,
                      dest="max_count",
                      help="")
    return parser


class TraceInstructionStep:

    def __init__(self, thread_plan, dic):
        HM.DPrint("==========Begin========================================================")
        self.start_time = datetime.now().strftime("%H:%M:%S")
        self.thread_plan = thread_plan
        self.instruction_count = 1

        self.print_instruction()  # first instruction

    def explains_stop(self, event: lldb.SBEvent) -> bool:
        self.instruction_count += 1
        self.print_instruction()
        return True

    def should_stop(self, event: lldb.SBEvent) -> bool:
        global g_instruction_limit
        if 0 < g_instruction_limit <= self.instruction_count:
            self.print_before_stop()
            return True

        if self.thread_plan.GetThread().GetStopReason() != lldb.eStopReasonTrace:
            self.print_before_stop()
            return True
        else:
            return False

    def should_step(self) -> bool:
        return True

    def print_instruction(self) -> None:
        frame = self.thread_plan.GetThread().GetFrameAtIndex(0)
        target = self.thread_plan.GetThread().GetProcess().GetTarget()
        instructions = frame.GetSymbol().GetInstructions(target)
        instruction_str: str = ""
        pc_address_value: int = 0
        for instruction in instructions:
            if instruction.GetAddress() == frame.GetPCAddress():
                pc_address_value = instruction.GetAddress().GetLoadAddress(target)
                comment = instruction.GetComment(target)
                if len(comment) > 0:
                    instruction_str = f"{instruction.GetMnemonic(target)}\t{instruction.GetOperands(target)}\t\t\t; {instruction.GetComment(target)}"
                else:
                    instruction_str = f"{instruction.GetMnemonic(target)}\t{instruction.GetOperands(target)}"
                break

        stream = lldb.SBStream()
        frame.GetPCAddress().GetDescription(stream)
        print(f"{stream.GetData()}\t\t{instruction_str}\t({hex(pc_address_value)})")

    def print_before_stop(self) -> None:
        self.thread_plan.SetPlanComplete(True)
        HM.DPrint("==========End========================================================")
        HM.DPrint(f"Instruction count: {self.instruction_count}")
        HM.DPrint(f"Start time: {self.start_time}")
        stop_time = datetime.now().strftime("%H:%M:%S")
        HM.DPrint(f"Stop time: {stop_time}")

