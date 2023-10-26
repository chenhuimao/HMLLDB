# The MIT License (MIT)
#
# Copyright (c) 2023 Huimao Chen
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
import time
import HMLLDBClassInfo
import HMLLDBHelpers as HM


def __lldb_init_module(debugger, internal_dict):
    debugger.HandleCommand('command script add -f HMTrace.trace_function tracefunction -h "Trace functions step by step until the next breakpoint is hit."')
    debugger.HandleCommand('command script add -f HMTrace.trace_instruction traceinstruction -h "Trace instructions step by step until the next breakpoint is hit."')
    debugger.HandleCommand('command script add -f HMTrace.trace_step_over_instruction trace-step-over-instruction -h "Trace step over instruction."')
    debugger.HandleCommand('command script add -f HMTrace.complete_backtrace cbt -h "Completely displays the current thread\'s call stack based on the fp/lr register."')


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
        if len(function_str) == 0:
            function_str = hex(pc_address.GetLoadAddress(target))
        if function_str not in self.last_function:
            if self.last_function.startswith("0x"):
                print(self.last_function)
            else:
                print(f"{self.last_function}\t({hex(self.last_pc_address_value)})")
            self.function_count += 1
        self.last_pc_address_value = pc_address.GetLoadAddress(target)
        self.last_function = stream.GetData()
        if len(self.last_function) == 0:
            self.last_function = hex(self.last_pc_address_value)
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


def print_instruction(frame: lldb.SBFrame, target: lldb.SBTarget):
    instructions: lldb.SBInstructionList = frame.GetSymbol().GetInstructions(target)
    instruction_str: str = ""
    pc_address_value: int = frame.GetPCAddress().GetLoadAddress(target)
    for instruction in instructions:
        if instruction.GetAddress() == frame.GetPCAddress():
            comment = instruction.GetComment(target)
            if len(comment) > 0:
                instruction_str = f"{instruction.GetMnemonic(target)}\t{instruction.GetOperands(target)}\t\t\t; {comment}"
            else:
                instruction_str = f"{instruction.GetMnemonic(target)}\t{instruction.GetOperands(target)}"
            break

    stream = lldb.SBStream()
    frame.GetPCAddress().GetDescription(stream)
    if len(instruction_str) == 0:
        print(hex(pc_address_value))
    else:
        print(f"{stream.GetData()}\t\t{instruction_str}\t({hex(pc_address_value)})")


class TraceInstructionStep:

    def __init__(self, thread_plan, dic):
        HM.DPrint("==========Begin========================================================")
        self.start_time = datetime.now().strftime("%H:%M:%S")
        self.thread_plan = thread_plan
        self.instruction_count = 1

        # first instruction
        frame = self.thread_plan.GetThread().GetFrameAtIndex(0)
        target = self.thread_plan.GetThread().GetProcess().GetTarget()
        print_instruction(frame, target)

    def explains_stop(self, event: lldb.SBEvent) -> bool:
        self.instruction_count += 1
        frame = self.thread_plan.GetThread().GetFrameAtIndex(0)
        target = self.thread_plan.GetThread().GetProcess().GetTarget()
        print_instruction(frame, target)
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

    def print_before_stop(self) -> None:
        self.thread_plan.SetPlanComplete(True)
        HM.DPrint("==========End========================================================")
        HM.DPrint(f"Instruction count: {self.instruction_count}")
        HM.DPrint(f"Start time: {self.start_time}")
        stop_time = datetime.now().strftime("%H:%M:%S")
        HM.DPrint(f"Stop time: {stop_time}")


def trace_step_over_instruction(debugger, command, exe_ctx, result, internal_dict):
    """
    Syntax:
        trace-step-over-instruction <count>

    Examples:
        (lldb) trace-step-over-instruction 20

    This command is implemented in HMTrace.py
    """

    if len(command) == 0:
        HM.DPrint("Error input, this command requires an integer parameter.")
        return

    try:
        count = int(command)
    except:
        HM.DPrint("Error input, this command requires an integer parameter.")
        return

    if count <= 1:
        HM.DPrint("Error input, the integer parameter must be greater than or equal to 2.")
        return

    breakpoint_name = "HMLLDB_trace_step_over_instruction"
    thread = exe_ctx.GetThread()
    target = exe_ctx.GetTarget()

    print_instruction(thread.GetSelectedFrame(), target)
    last_bp_id: int = set_breakpoint_at_next_pc_address(target, thread.GetSelectedFrame(), breakpoint_name)

    for i in range(count - 1):
        is_step_over = should_step_over(target, thread.GetSelectedFrame())
        thread.StepInstruction(is_step_over)
        delete_breakpoint_with_id(target, last_bp_id)
        frame = thread.GetSelectedFrame()
        print_instruction(frame, target)
        last_bp_id = set_breakpoint_at_next_pc_address(target, frame, breakpoint_name)

    is_step_over = should_step_over(target, thread.GetSelectedFrame())
    async_state = debugger.GetAsync()
    debugger.SetAsync(True)
    thread.StepInstruction(is_step_over)
    debugger.SetAsync(async_state)

    time.sleep(1)
    print_instruction(thread.GetSelectedFrame(), target)
    delete_breakpoint_with_id(target, last_bp_id)


def set_breakpoint_at_next_pc_address(target: lldb.SBTarget, frame: lldb.SBFrame, name: str) -> int:
    instructions: lldb.SBInstructionList = frame.GetSymbol().GetInstructions(target)
    instructions_count = instructions.GetSize()
    for i in range(instructions_count - 1):
        instruction: lldb.SBInstruction = instructions.GetInstructionAtIndex(i)
        if instruction.GetAddress() == frame.GetPCAddress():
            next_instruction = instructions.GetInstructionAtIndex(i + 1)
            next_address: int = next_instruction.GetAddress().GetLoadAddress(target)
            bp = target.BreakpointCreateByAddress(next_address)
            bp.AddName(name)
            return bp.GetID()

    return 0


def delete_breakpoint_with_id(target: lldb.SBTarget, bp_id: int) -> bool:
    if bp_id != 0:
        return target.BreakpointDelete(bp_id)
    return False


def should_step_over(target: lldb.SBTarget, frame: lldb.SBFrame) -> bool:
    instruction_list: lldb.SBInstructionList = frame.GetSymbol().GetInstructions(target)
    for instruction in instruction_list:
        if instruction.GetAddress() == frame.GetPCAddress():
            opcode = instruction.GetMnemonic(target)
            if "ret" in opcode:
                return False

    return True


def complete_backtrace(debugger, command, exe_ctx, result, internal_dict):
    """
    Syntax:
        cbt

    Examples:
        (lldb) cbt

    This command is implemented in HMTrace.py
    """

    if not HM.is_arm64(exe_ctx.GetTarget()):
        HM.DPrint("x86_64 architecture does not require the \"cbt\" command, please use the \"bt\" command.")
        return

    # print current thread
    print(exe_ctx.GetThread())

    # always get the first frame
    current_registers: lldb.SBValueList = exe_ctx.GetThread().GetFrameAtIndex(0).GetRegisters()
    general_purpose_registers: lldb.SBValue = current_registers.GetFirstValueByName("General Purpose Registers")

    # print pc register information
    pc_value_int = general_purpose_registers.GetChildMemberWithName('pc').GetValueAsUnsigned()
    first_lr_desc = HM.get_image_lookup_summary_from_address(str(pc_value_int))
    frame_count = 0
    print(f"\tframe #{frame_count}:\t{hex(pc_value_int)}\t{first_lr_desc}")
    frame_count += 1

    # print current lr register information
    lr_value_int = general_purpose_registers.GetChildMemberWithName('lr').GetValueAsUnsigned()
    first_lr_desc = HM.get_image_lookup_summary_from_address(str(lr_value_int))
    print(f"\tframe #{frame_count}:\t{hex(lr_value_int)}\t{first_lr_desc}")
    frame_count += 1

    # print information about remaining frames
    current_fp_value_int = general_purpose_registers.GetChildMemberWithName('fp').GetValueAsUnsigned()
    previous_fp_value_int = HM.load_address_value(str(current_fp_value_int), exe_ctx)
    while previous_fp_value_int > 0:
        current_lr_value_int = HM.load_address_value(str(current_fp_value_int + 8), exe_ctx)
        current_lr_value_int = HM.strip_pac_sign_address(current_lr_value_int, exe_ctx.GetProcess())
        current_lr_desc = HM.get_image_lookup_summary_from_address(str(current_lr_value_int))
        print(f"\tframe #{frame_count}:\t{hex(current_lr_value_int)}\t{current_lr_desc}")
        frame_count += 1
        current_fp_value_int = previous_fp_value_int
        previous_fp_value_int = HM.load_address_value(str(current_fp_value_int), exe_ctx)

