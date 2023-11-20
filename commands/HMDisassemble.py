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
from typing import Dict, List, Optional, Tuple
import HMCalculationHelper
import HMLLDBClassInfo
import HMLLDBHelpers as HM


def __lldb_init_module(debugger, internal_dict):
    debugger.HandleCommand('command script add -f HMDisassemble.enhanced_disassemble edisassemble -h "Enhanced disassemble"')


def enhanced_disassemble(debugger, command, exe_ctx, result, internal_dict):
    """
    Syntax:
        The syntax is the same as disassemble, please enter "help disassemble" for help.

    Examples:
        (lldb) edisassemble -s 0x107ad4504
        (lldb) edisassemble -a 0x107ad4504
        (lldb) edisassemble -n "-[NSArray objectAtIndex:]"

    This command is implemented in HMDisassemble.py
    """

    return_object = lldb.SBCommandReturnObject()
    debugger.GetCommandInterpreter().HandleCommand(f"disassemble {command}", exe_ctx, return_object)
    if return_object.GetErrorSize() > 0:
        print(return_object.GetError())
        return

    original_output = return_object.GetOutput()
    if not HM.is_arm64(exe_ctx.GetTarget()):
        if return_object.GetOutputSize() > 0:
            print(original_output)
        else:
            debugger.HandleCommand(f"disassemble {command}")
        return

    target = exe_ctx.GetTarget()
    assemble_lines = original_output.splitlines()
    address_comment_dict: Dict[int, str] = {}

    # Read continuous instructions
    first_address_int = lldb.LLDB_INVALID_ADDRESS
    continuous_instructions_count = 0
    for line in assemble_lines:
        address_int = get_address_from_assemble_line(line)
        if address_int == lldb.LLDB_INVALID_ADDRESS:
            if first_address_int != lldb.LLDB_INVALID_ADDRESS and continuous_instructions_count > 0:
                address: lldb.SBAddress = lldb.SBAddress(first_address_int, target)
                instruction_list: lldb.SBInstructionList = target.ReadInstructions(address, continuous_instructions_count)
                # Find instructions without comment
                set_my_comment_in_dict(address_comment_dict, instruction_list, exe_ctx)
            first_address_int = lldb.LLDB_INVALID_ADDRESS
            continuous_instructions_count = 0
            continue

        if first_address_int == lldb.LLDB_INVALID_ADDRESS:
            first_address_int = address_int
        continuous_instructions_count += 1

    # Read last continuous instructions
    if first_address_int != lldb.LLDB_INVALID_ADDRESS and continuous_instructions_count > 0:
        address: lldb.SBAddress = lldb.SBAddress(first_address_int, target)
        instruction_list: lldb.SBInstructionList = target.ReadInstructions(address, continuous_instructions_count)
        # Find instructions without comment
        set_my_comment_in_dict(address_comment_dict, instruction_list, exe_ctx)

    # Print result
    for line in assemble_lines:
        address_int = get_address_from_assemble_line(line)
        if address_int == lldb.LLDB_INVALID_ADDRESS:
            print(line)
            continue

        if address_int in address_comment_dict:
            print(f"{line}\t\t\t\t; {address_comment_dict[address_int]}")
        else:
            print(line)


def get_address_from_assemble_line(assemble_line: str) -> int:
    keywords = assemble_line.split()
    if len(keywords) < 2:
        return lldb.LLDB_INVALID_ADDRESS

    address_str = keywords[0].rstrip(':')
    if keywords[0] == '->':
        address_str = keywords[1].rstrip(':')

    is_valid, address_int = HM.int_value_from_string(address_str)
    if is_valid:
        return address_int
    return lldb.LLDB_INVALID_ADDRESS


def set_my_comment_in_dict(address_comment_dict: Dict[int, str], instruction_list: lldb.SBInstructionList, exe_ctx: lldb.SBExecutionContext):
    target = exe_ctx.GetTarget()
    instruction_count = instruction_list.GetSize()
    for i in range(instruction_count):
        instruction: lldb.SBInstruction = instruction_list.GetInstructionAtIndex(i)
        comment = instruction.GetComment(target)
        # HMLLDBClassInfo.pSBInstruction(instruction)
        if len(comment) > 0:
            continue

        # Get my comment
        if i == 0:
            my_comment = my_comment_for_instruction(instruction, None, exe_ctx)
        else:
            my_comment = my_comment_for_instruction(instruction, instruction_list.GetInstructionAtIndex(i - 1), exe_ctx)
        if len(my_comment) == 0:
            continue
        address_comment_dict[instruction.GetAddress().GetLoadAddress(target)] = my_comment


def my_comment_for_instruction(instruction: lldb.SBInstruction, previous_instruction: Optional[lldb.SBInstruction], exe_ctx: lldb.SBExecutionContext) -> str:
    # adr
    my_comment = comment_for_adr(instruction, exe_ctx)
    if len(my_comment) > 0:
        return my_comment

    # adrp
    my_comment = comment_for_adrp(instruction, exe_ctx)
    if len(my_comment) > 0:
        return my_comment

    # adrp next instruction
    if previous_instruction is not None:
        my_comment = comment_for_adrp_next_instruction(previous_instruction, instruction, exe_ctx)
        if len(my_comment) > 0:
            return my_comment

    # branch
    my_comment = comment_for_branch(instruction, exe_ctx)
    if len(my_comment) > 0:
        return my_comment
    return ""


def comment_for_adr(instruction: lldb.SBInstruction, exe_ctx: lldb.SBExecutionContext) -> str:
    target = exe_ctx.GetTarget()
    if instruction.GetMnemonic(target) != 'adr':
        return ""
    # adr x17, #-0x8000
    operands = instruction.GetOperands(target).split(', ')
    if not (operands[1].startswith('#0x') or operands[1].startswith('#-0x')):
        return ""
    adr_result = instruction.GetAddress().GetLoadAddress(target) + int(operands[1].lstrip('#'), 16)
    comment = f"{operands[0]} = {hex(adr_result)}, {adr_result}"
    return comment


def comment_for_adrp(instruction: lldb.SBInstruction, exe_ctx: lldb.SBExecutionContext) -> str:
    target = exe_ctx.GetTarget()
    if instruction.GetMnemonic(target) != 'adrp':
        return ""
    # # adrp x8, -24587
    operands = instruction.GetOperands(target).split(', ')
    adrp_result_tuple: Tuple[int, str] = HMCalculationHelper.calculate_adrp_result_with_immediate_and_pc_address(int(operands[1]), instruction.GetAddress().GetLoadAddress(target))
    comment = f"{operands[0]} = {adrp_result_tuple[1]}"
    return comment


def comment_for_adrp_next_instruction(adrp_instruction: lldb.SBInstruction, next_instruction: lldb.SBInstruction, exe_ctx: lldb.SBExecutionContext) -> str:
    target = exe_ctx.GetTarget()
    if adrp_instruction.GetMnemonic(target) != 'adrp':
        return ""
    adrp_operands = adrp_instruction.GetOperands(target).split(', ')
    adrp_result_tuple: Tuple[int, str] = HMCalculationHelper.calculate_adrp_result_with_immediate_and_pc_address(int(adrp_operands[1]), adrp_instruction.GetAddress().GetLoadAddress(target))
    comment = ''
    mnemonic = next_instruction.GetMnemonic(target)
    operands = next_instruction.GetOperands(target).split(', ')
    if mnemonic == 'ldr':
        # adrp x2, 325020
        # ldr x2, [x2, #0x9c8]
        operands[1] = operands[1].lstrip('[')
        operands[2] = operands[2].rstrip(']')
        if adrp_operands[0] == operands[1] and operands[2].startswith('#0x'):
            load_address_int = adrp_result_tuple[0] + int(operands[2].lstrip('#'), 16)
            ldr_return_object = lldb.SBCommandReturnObject()
            lldb.debugger.GetCommandInterpreter().HandleCommand(f"x/a {load_address_int}", exe_ctx, ldr_return_object)
            load_address_output = ldr_return_object.GetOutput()
            if len(load_address_output) > 0:
                ldr_result_list = load_address_output.split(": ", 1)
                ldr_result = ldr_result_list[1]
                comment = f"{operands[0]} = {ldr_result}"

    elif mnemonic == 'ldrsw':
        # adrp x8, 61167
        # ldrsw x8, [x8, #0xaac]
        operands[1] = operands[1].lstrip('[')
        operands[2] = operands[2].rstrip(']')
        if adrp_operands[0] == operands[1] and operands[2].startswith('#0x'):
            load_address_int = adrp_result_tuple[0] + int(operands[2].lstrip('#'), 16)
            ldrsw_return_object = lldb.SBCommandReturnObject()
            lldb.debugger.GetCommandInterpreter().HandleCommand(f"x/a {load_address_int}", exe_ctx, ldrsw_return_object)
            load_address_output = ldrsw_return_object.GetOutput()
            if len(load_address_output) > 0:
                ldrsw_result_list = load_address_output.split()
                ldrsw_result = int(ldrsw_result_list[1], 16) & 0xFFFFFFFF
                if ldrsw_result & 0x80000000 > 0:
                    ldrsw_result += 0xFFFFFFFF00000000
                comment = f"{operands[0]} = {hex(ldrsw_result)}"

    elif mnemonic == 'add':
        # adrp x8, -24587
        # add x1, x8, #0xbbb
        if adrp_operands[0] == operands[1] and operands[2].startswith('#0x'):
            add_result = adrp_result_tuple[0] + int(operands[2].lstrip('#'), 16)
            comment = f"{operands[0]} = {hex(add_result)}"

    return comment


def comment_for_branch(instruction: lldb.SBInstruction, exe_ctx: lldb.SBExecutionContext) -> str:
    target = exe_ctx.GetTarget()
    if not instruction.GetMnemonic(target).startswith('b'):
        return ""

    # Find the 3 instructions of the branch address
    operands = instruction.GetOperands(target)
    is_valid_address, address_int = HM.int_value_from_string(operands)
    if not is_valid_address:
        return ""

    address: lldb.SBAddress = lldb.SBAddress(address_int, target)
    instruction_list: lldb.SBInstructionList = target.ReadInstructions(address, 3)
    instruction_count = instruction_list.GetSize()
    if instruction_count != 3:
        return ""

    first_instruction = instruction_list.GetInstructionAtIndex(0)
    second_instruction = instruction_list.GetInstructionAtIndex(1)
    third_instruction = instruction_list.GetInstructionAtIndex(2)

    # Calculate the actual branch address and comments
    comment = ""
    third_mnemonic = third_instruction.GetMnemonic(target)
    if first_instruction.GetMnemonic(target) == 'adrp' and third_mnemonic.startswith('b'):
        if second_instruction.GetMnemonic(target) == 'add':
            # adrp x16, -51447
            # add x16, x16, #0x4e0          ; objc_claimAutoreleasedReturnValue
            # br x16
            adrp_operands = first_instruction.GetOperands(target).split(', ')
            adrp_result_tuple: Tuple[int, str] = HMCalculationHelper.calculate_adrp_result_with_immediate_and_pc_address(int(adrp_operands[1]), first_instruction.GetAddress().GetLoadAddress(target))
            add_operands = second_instruction.GetOperands(target).split(', ')
            if adrp_operands[0] == add_operands[1] and add_operands[2].startswith('#0x'):
                add_result = adrp_result_tuple[0] + int(add_operands[2].lstrip('#'), 16)
                branch_operands = third_instruction.GetOperands(target)
                if branch_operands == add_operands[0]:
                    comment = f"{third_mnemonic} {hex(add_result)} {second_instruction.GetComment(target)}"

    return comment

