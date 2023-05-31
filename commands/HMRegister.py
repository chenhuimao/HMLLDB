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
import math
import optparse
import shlex
from typing import Dict, List, Tuple
import HMLLDBClassInfo
import HMLLDBHelpers as HM


# [register_name, register_value]
g_last_registers_dict: Dict[str, str] = {}
last_disassemble: str = ""


def __lldb_init_module(debugger, internal_dict):
    debugger.HandleCommand('command script add -f HMRegister.register_change rc -h "Show general purpose registers changes."')
    debugger.HandleCommand('command script add -f HMRegister.register_read rr -h "Alias for \'register read\' with additional -s/--sp arguments."')


def register_change(debugger, command, exe_ctx, result, internal_dict):
    """
    Syntax:
        rc

    Examples:
        (lldb) rc
        [HMLLDB] Get register for the first time.

        // Step over instruction
        (lldb) rc
        0x10431a3cc <+16>:  mov    x1, x2
                x1:0x000000010431aa94 -> 0x000000010490be50
                pc:0x000000010431a3cc -> 0x000000010431a3d0  Demo`-[ViewController clickBtn:] + 20 at ViewController.m:24

    This command is implemented in HMRegister.py
    """

    frame = exe_ctx.GetFrame()
    global g_last_registers_dict
    if len(g_last_registers_dict) == 0:
        HM.DPrint("Get registers for the first time.")

    # Is it repeated?
    if is_executed_repeatedly(frame):
        HM.DPrint("Executed repeatedly!")
        return

    # When the pc register differ by 4
    print_last_instruction_if_needed(frame)

    # Print and save registers
    current_registers: lldb.SBValueList = frame.GetRegisters()
    general_purpose_registers: lldb.SBValue = current_registers.GetFirstValueByName("General Purpose Registers")
    children_num = general_purpose_registers.GetNumChildren()
    for i in range(children_num):
        reg_value = general_purpose_registers.GetChildAtIndex(i)
        reg_name = reg_value.GetName()
        reg_value_str: str = reg_value.GetValue()

        # Ignore w0 ~ w28
        if reg_name.startswith("w"):
            continue

        if reg_name not in g_last_registers_dict:
            g_last_registers_dict[reg_name] = reg_value_str
            continue

        last_register_value: str = g_last_registers_dict[reg_name]
        if reg_value_str != last_register_value:
            address: lldb.SBAddress = lldb.SBAddress(reg_value.GetValueAsUnsigned(), exe_ctx.GetTarget())
            address_desc = ""
            if address.GetSymbol().IsValid():
                desc_stream = lldb.SBStream()
                address.GetDescription(desc_stream)
                address_desc = desc_stream.GetData()

            # x16:0x0000000300982fd4 -> 0x00000001c7a6f508  libobjc.A.dylib`objc_release
            print(f"\t\t{reg_name}:{last_register_value} -> {reg_value_str}  {address_desc}")

        g_last_registers_dict[reg_name] = reg_value_str

    # Record last disassemble
    global last_disassemble
    last_disassemble = frame.Disassemble()


def is_executed_repeatedly(frame: lldb.SBFrame) -> bool:
    last_pc_value: int = 0
    if "rip" in g_last_registers_dict:
        last_pc_value = int(g_last_registers_dict["rip"], 16)
    if "pc" in g_last_registers_dict:
        last_pc_value = int(g_last_registers_dict["pc"], 16)
    return frame.GetPC() == last_pc_value


def print_last_instruction_if_needed(frame: lldb.SBFrame) -> None:
    pc_key = "pc"
    global g_last_registers_dict
    if pc_key not in g_last_registers_dict:
        return
    last_pc_value = int(g_last_registers_dict[pc_key], 16)
    if frame.GetPC() - last_pc_value != 4:
        return

    global last_disassemble
    instruction_list: List[str] = last_disassemble.splitlines(False)
    for instruction_line in instruction_list:
        instruction_line_strip = instruction_line.lstrip("->").strip()
        instruction_line_split: List[str] = instruction_line_strip.split(" ")
        address: str = ""
        for element in instruction_line_split:
            if element.startswith("0x"):
                address = element
                break
        if not address.startswith("0x"):
            continue
        address = address.rstrip(":")
        if int(address, 16) == last_pc_value:
            print(instruction_line_strip)
            break


def register_read(debugger, command, exe_ctx, result, internal_dict):
    """
    Syntax:
        Alias for 'register read' with additional -s/--sp arguments
        rr [-s <offset>]

    Options:
        --sp/-s; Show [sp, (sp + offset)] address value.

    Examples:
        // Alias for 'register read'
        (lldb)rr

        // Alias for 'register read -a'
        (lldb)rr -a

        // Show [sp, (sp + offset)] address value after execute 'register read'
        (lldb)rr -s 64
        (lldb)rr -s 0x40
        (lldb)rr -s 0x40 -a

        (lldb)rr x0 sp -s 0x10
        [HMLLDB] register read x0 sp
            x0 = 0x0000000000000000
            sp = 0x000000016fb2cdf0
        0x16fb2cdf0: 0x000000010110b8b0
        0x16fb2cdf8: 0x00000001002e5008 "clickBtn:"
        0x16fb2ce00: 0x0000000101137b80

    This command is implemented in HMRegister.py
    """

    command_args: list[str] = shlex.split(command)
    # Find the offset value of the sp register
    sp_offset: str = ""
    for i in range(len(command_args)):
        if i == 0:
            continue
        current_arg = command_args[i]
        previous_arg = command_args[i-1]
        if previous_arg == "--sp" or previous_arg == "-s":
            sp_offset = current_arg
            if sp_offset.startswith('-'):
                HM.DPrint("Error input. Please enter \"help rr\" for help.")
                return
            break

    if len(sp_offset) > 0:
        sp_offset_is_valid, sp_offset_value = HM.int_value_from_string(sp_offset)
        if not sp_offset_is_valid:
            HM.DPrint("Error input. The <offset> parameter does not support being converted to an integer. Please enter \"help rr\" for help.")
            return

    # Concatenate other parameters
    args_for_system: str = ""
    for i in range(len(command_args)):
        current_arg = command_args[i]
        if i == 0 and current_arg != "--sp" and current_arg != "-s":
            args_for_system += current_arg + ' '
            continue

        previous_arg = command_args[i-1]
        if previous_arg == "--sp" or previous_arg == "-s" or current_arg == "--sp" or current_arg == "-s":
            continue
        args_for_system += current_arg + ' '

    args_for_system = args_for_system.rstrip()
    HM.DPrint(f"register read {args_for_system}")
    debugger.HandleCommand(f"register read {args_for_system}")
    if len(sp_offset) > 0:
        number_of_address = math.ceil(sp_offset_value / 8) + 1
        sp_address = exe_ctx.GetFrame().GetSP()
        debugger.HandleCommand(f"x/{number_of_address}a {sp_address}")


def generate_rr_option_parser() -> optparse.OptionParser:
    usage = "usage: rr [--all] [--sp <offset>]"
    parser = optparse.OptionParser(usage=usage, prog="rr")
    parser.add_option("-a", "--all",
                      action="store_true",
                      default=False,
                      dest="all",
                      help="Show all register sets")
    parser.add_option("-s", "--sp",
                      action="store",
                      default=None,
                      dest="sp",
                      help="Show [sp, (sp + offset)] address value")
    return parser

