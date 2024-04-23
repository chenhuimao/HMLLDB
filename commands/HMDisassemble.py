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
import HMReference


def __lldb_init_module(debugger, internal_dict):
    debugger.HandleCommand('command script add -f HMDisassemble.enhanced_disassemble edisassemble -h "Enhanced disassemble"')


def enhanced_disassemble(debugger, command, exe_ctx, result, internal_dict):
    """
    Syntax:
        The syntax is the same as disassemble, please enter "help disassemble" for help.

    Examples:
        (lldb) edisassemble -s 0x107ad4504
        (lldb) edis -a 0x107ad4504
        (lldb) edis -n "-[UIDevice systemVersion]"

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
    original_comment_index = -1
    max_assemble_line_length = 0

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
                set_my_comment_in_dict(exe_ctx, address_comment_dict, instruction_list)
            # Reset variables
            first_address_int = lldb.LLDB_INVALID_ADDRESS
            continuous_instructions_count = 0
            continue

        if first_address_int == lldb.LLDB_INVALID_ADDRESS:
            first_address_int = address_int
        continuous_instructions_count += 1

        # Get comment index
        if original_comment_index == -1 and line.rfind(';') >= 0:
            original_comment_index = line.rfind(';')
        max_assemble_line_length = max(max_assemble_line_length, len(line))

    # Set comment index if needed
    if original_comment_index == -1:
        original_comment_index = max_assemble_line_length + 4

    # Read last continuous instructions
    if first_address_int != lldb.LLDB_INVALID_ADDRESS and continuous_instructions_count > 0:
        address: lldb.SBAddress = lldb.SBAddress(first_address_int, target)
        instruction_list: lldb.SBInstructionList = target.ReadInstructions(address, continuous_instructions_count)
        # Find instructions without comment
        set_my_comment_in_dict(exe_ctx, address_comment_dict, instruction_list)

    # Print result
    for line in assemble_lines:
        address_int = get_address_from_assemble_line(line)
        if address_int == lldb.LLDB_INVALID_ADDRESS:
            result.AppendMessage(line)
            continue
        is_contain_comment = ';' in line
        if is_contain_comment:
            # Sometimes instruction.GetComment(target) cannot obtain the comment, so it needs to be judged again.
            result.AppendMessage(line)
        elif address_int in address_comment_dict:
            result.AppendMessage(f"{line.ljust(original_comment_index)}; {address_comment_dict[address_int]}")
        else:
            result.AppendMessage(line)


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


def set_my_comment_in_dict(exe_ctx: lldb.SBExecutionContext, address_comment_dict: Dict[int, str], instruction_list: lldb.SBInstructionList):
    target = exe_ctx.GetTarget()
    instruction_count = instruction_list.GetSize()
    for i in range(instruction_count):
        instruction: lldb.SBInstruction = instruction_list.GetInstructionAtIndex(i)
        mnemonic: str = instruction.GetMnemonic(target)
        if mnemonic in ['b', 'bl']:
            # Record all branch logic
            record_branch_logic(exe_ctx, instruction, address_comment_dict)
        elif mnemonic in ['adr', 'adrp']:
            # Record all adr/adrp logic
            record_adrp_logic(exe_ctx, instruction, address_comment_dict)


def record_branch_logic(exe_ctx: lldb.SBExecutionContext, branch_instruction: lldb.SBInstruction, address_comment_dict: Dict[int, str]) -> None:
    target = exe_ctx.GetTarget()
    comment = branch_instruction.GetComment(target)
    if len(comment) > 0:
        return
    my_comment = comment_for_branch(exe_ctx, branch_instruction)
    if len(my_comment) > 0:
        address_comment_dict[branch_instruction.GetAddress().GetLoadAddress(target)] = my_comment


def record_adrp_logic(exe_ctx: lldb.SBExecutionContext, adrp_instruction: lldb.SBInstruction, address_comment_dict: Dict[int, str]) -> None:
    # Analyze the specified instructions after adrp in sequence, and analyze up to 8 instructions.
    # FIXME: x0 and w0 registers are independent and need to be merged.
    register_dic: Dict[str, int] = {}
    target = exe_ctx.GetTarget()

    # Calculate and save the value of adr/adrp instruction
    adrp_instruction_load_address: int = adrp_instruction.GetAddress().GetLoadAddress(target)
    adrp_instruction_mnemonic = adrp_instruction.GetMnemonic(target)
    adrp_target_register = ""
    adrp_result = -1
    if adrp_instruction_mnemonic == 'adr':
        # adr x17, #-0x8000
        operands = adrp_instruction.GetOperands(target).split(', ')
        if not (operands[1].startswith('#0x') or operands[1].startswith('#-0x')):
            # HM.DPrint(f"Error: Unsupported format in adr. Load address:{hex(adrp_instruction_load_address)}")
            return
        adrp_result = adrp_instruction_load_address + int(operands[1].lstrip('#'), 16)
        adrp_target_register = operands[0]
    elif adrp_instruction_mnemonic == 'adrp':
        # adrp x8, -24587
        operands = adrp_instruction.GetOperands(target).split(', ')
        adrp_result_tuple: Tuple[int, str] = HMCalculationHelper.calculate_adrp_result_with_immediate_and_pc_address(int(operands[1]), adrp_instruction_load_address)
        adrp_result = adrp_result_tuple[0]
        adrp_target_register = operands[0]
    else:
        return
    register_dic[adrp_target_register] = adrp_result
    comment = adrp_instruction.GetComment(target)
    if len(comment) == 0:
        adrp_comment = f"{adrp_target_register} = {hex(adrp_result)}"
        address_comment_dict[adrp_instruction_load_address] = adrp_comment

    # Analyze the specified instructions after adr/adrp
    instruction_count = 8
    address: lldb.SBAddress = lldb.SBAddress(adrp_instruction_load_address + 4, target)
    instruction_list: lldb.SBInstructionList = target.ReadInstructions(address, instruction_count)
    for i in range(instruction_count):
        instruction: lldb.SBInstruction = instruction_list.GetInstructionAtIndex(i)
        comment = instruction.GetComment(target)
        mnemonic: str = instruction.GetMnemonic(target)
        instruction_load_address_int: int = instruction.GetAddress().GetLoadAddress(target)
        if mnemonic == 'add':
            can_analyze_add, target_register_str, add_value = HMReference.analyze_add(exe_ctx, instruction, register_dic)
            if not can_analyze_add:
                break
            if len(comment) == 0:
                lookup_summary = HM.get_image_lookup_summary_from_address(hex(add_value))
                add_comment = f"{target_register_str} = {hex(add_value)} {lookup_summary}"
                address_comment_dict[instruction_load_address_int] = add_comment
        elif mnemonic == 'ldr':
            can_analyze_ldr, can_load_address, target_register_str, load_address_int, load_result_int = HMReference.analyze_ldr(exe_ctx, instruction, register_dic)
            # TODO: image lookup -a <load_address_int>
            # if can_load_address:

            if not can_analyze_ldr:
                break
            # The ldr instruction records the result address in memory
            if len(comment) == 0:
                lookup_summary = HM.get_image_lookup_summary_from_address(hex(load_result_int))
                ldr_comment = f"{target_register_str} = {hex(load_result_int)} {lookup_summary}"
                address_comment_dict[instruction_load_address_int] = ldr_comment

        elif mnemonic == 'ldrsw':
            can_analyze_ldrsw, _, target_register_str, _, load_result_int = HMReference.analyze_ldr(exe_ctx, instruction, register_dic)
            if not can_analyze_ldrsw:
                break
            # The ldrsw instruction records the result address in memory
            if len(comment) == 0:
                lookup_summary = HM.get_image_lookup_summary_from_address(hex(load_result_int))
                ldr_comment = f"{target_register_str} = {hex(load_result_int)} {lookup_summary}"
                address_comment_dict[instruction_load_address_int] = ldr_comment
        elif mnemonic == 'mov':
            can_analyze_mov, target_register_str, mov_value = HMReference.analyze_mov(exe_ctx, instruction, register_dic)
            if not can_analyze_mov:
                break
            if len(comment) == 0:
                mov_comment = f"{target_register_str} = {hex(mov_value)}"
                address_comment_dict[instruction_load_address_int] = mov_comment
        elif mnemonic == 'str':
            continue
        elif mnemonic == 'nop':
            continue
        else:
            break

    return


def comment_for_branch(exe_ctx: lldb.SBExecutionContext, instruction: lldb.SBInstruction) -> str:
    target = exe_ctx.GetTarget()
    if not is_b_branch_instruction(instruction, target):
        return ""

    # Find the 3 instructions of the branch address
    operands = instruction.GetOperands(target)
    is_valid_address, address_int = HM.int_value_from_string(operands)
    if not is_valid_address:
        return ""

    address: lldb.SBAddress = lldb.SBAddress(address_int, target)
    instruction_list: lldb.SBInstructionList = target.ReadInstructions(address, 5)
    instruction_count = instruction_list.GetSize()
    if instruction_count != 5:
        return ""

    first_instruction = instruction_list.GetInstructionAtIndex(0)
    second_instruction = instruction_list.GetInstructionAtIndex(1)
    third_instruction = instruction_list.GetInstructionAtIndex(2)
    fourth_instruction = instruction_list.GetInstructionAtIndex(3)
    fifth_instruction = instruction_list.GetInstructionAtIndex(4)

    # Calculate the actual branch address and comments
    comment = ""
    if is_b_branch_instruction(third_instruction, target) and first_instruction.GetMnemonic(target) == 'adrp':
        if second_instruction.GetMnemonic(target) == 'add':
            # adrp x16, -51447
            # add x16, x16, #0x4e0          ; objc_claimAutoreleasedReturnValue
            # br x16
            adrp_operands = first_instruction.GetOperands(target).split(', ')
            adrp_result_tuple: Tuple[int, str] = HMCalculationHelper.calculate_adrp_result_with_immediate_and_pc_address(int(adrp_operands[1]), first_instruction.GetAddress().GetLoadAddress(target))
            add_operand_tuple: Tuple[str, str, int] = resolve_add_operands(second_instruction.GetOperands(target))
            if adrp_operands[0] == add_operand_tuple[1]:
                add_result = adrp_result_tuple[0] + add_operand_tuple[2]
                branch_operands = third_instruction.GetOperands(target)
                if branch_operands == add_operand_tuple[0]:
                    third_mnemonic = third_instruction.GetMnemonic(target)
                    comment = f"{third_mnemonic} {branch_operands}, {branch_operands} = {hex(add_result)} {second_instruction.GetComment(target)}"

        # TODO: second_instruction.GetMnemonic(target) == 'ldr'
        
    if len(comment) > 0:
        return comment

    if is_b_branch_instruction(fifth_instruction, target) and first_instruction.GetMnemonic(target) == 'adrp' and third_instruction.GetMnemonic(target) == 'adrp':
        if second_instruction.GetMnemonic(target) == 'ldr' and fourth_instruction.GetMnemonic(target) == 'ldr':
            # adrp   x1, 13437
            # ldr    x1, [x1, #0x2b0]
            # adrp   x16, 1731
            # ldr    x16, [x16, #0xf98]
            # br     x16

            # resolve "br 16"
            third_adrp_operands = third_instruction.GetOperands(target).split(', ')
            third_adrp_result_tuple: Tuple[int, str] = HMCalculationHelper.calculate_adrp_result_with_immediate_and_pc_address(int(third_adrp_operands[1]), third_instruction.GetAddress().GetLoadAddress(target))
            fourth_ldr_operand_tuple: Tuple[str, str, int] = resolve_ldr_operands(fourth_instruction.GetOperands(target))
            if third_adrp_operands[0] == fourth_ldr_operand_tuple[1]:
                fourth_ldr_load_address_int = third_adrp_result_tuple[0] + fourth_ldr_operand_tuple[2]
                fourth_ldr_return_object = lldb.SBCommandReturnObject()
                lldb.debugger.GetCommandInterpreter().HandleCommand(f"x/a {fourth_ldr_load_address_int}", exe_ctx, fourth_ldr_return_object)
                fourth_ldr_load_address_output = fourth_ldr_return_object.GetOutput()
                fourth_ldr_result_list = fourth_ldr_load_address_output.split(": ", 1)
                fourth_ldr_load_result = fourth_ldr_result_list[1]

                fifth_branch_operands = fifth_instruction.GetOperands(target)
                if fifth_branch_operands == fourth_ldr_operand_tuple[0]:
                    fifth_mnemonic = fifth_instruction.GetMnemonic(target)
                    comment = f"{fifth_mnemonic} {fifth_branch_operands}, {fifth_branch_operands} = {fourth_ldr_load_result}"

            # resolve "x1" register when target is objc_msgSend
            if 'objc_msgSend' in comment and second_instruction.GetOperands(target).split(', ')[0] == 'x1':
                first_adrp_operands = first_instruction.GetOperands(target).split(', ')
                first_adrp_result_tuple: Tuple[int, str] = HMCalculationHelper.calculate_adrp_result_with_immediate_and_pc_address(int(first_adrp_operands[1]), first_instruction.GetAddress().GetLoadAddress(target))
                second_ldr_operand_tuple: Tuple[str, str, int] = resolve_ldr_operands(second_instruction.GetOperands(target))
                if first_adrp_operands[0] == second_ldr_operand_tuple[1]:
                    second_ldr_load_address_int = first_adrp_result_tuple[0] + second_ldr_operand_tuple[2]
                    second_ldr_return_object = lldb.SBCommandReturnObject()
                    lldb.debugger.GetCommandInterpreter().HandleCommand(f"x/a {second_ldr_load_address_int}", exe_ctx, second_ldr_return_object)
                    second_ldr_load_address_output = second_ldr_return_object.GetOutput()
                    second_ldr_result_list = second_ldr_load_address_output.split(" ")
                    second_ldr_load_result = second_ldr_result_list[1]

                    x1_str_return_object = lldb.SBCommandReturnObject()
                    lldb.debugger.GetCommandInterpreter().HandleCommand(f"x/s {second_ldr_load_result}", exe_ctx, x1_str_return_object)
                    x1_str_result = x1_str_return_object.GetOutput().split(" ")[1]
                    comment = f"{comment.rstrip()}, sel = {x1_str_result}"

    return comment


def is_b_branch_instruction(instruction: lldb.SBInstruction, target: lldb.SBTarget) -> bool:
    mnemonic = instruction.GetMnemonic(target)
    return mnemonic in ['b', 'br', 'bl', 'blr']


def resolve_ldr_operands(operands: str) -> Tuple[str, str, int]:
    # ldr x1, [x2, #0x9c8] -> (x1, x2, 0x9c8)
    # ldr x1, [x2] -> (x1, x2, 0)
    operand_list = operands.split(', ')
    if len(operand_list) == 2:
        return operand_list[0], operand_list[1].lstrip('[').rstrip(']'), 0
    elif len(operand_list) == 3:
        operand_list[1] = operand_list[1].lstrip('[')
        operand_list[2] = operand_list[2].rstrip(']')
        return operand_list[0], operand_list[1], int_value_from_string(operand_list[2])

    raise Exception("Mismatched ldr instruction format")


def resolve_add_operands(operands: str) -> Tuple[str, str, int]:
    # add x1, x8, #0xbbb -> (x1, x8, 0xbbb)
    operand_list = operands.split(', ')
    if len(operand_list) == 3:
        return operand_list[0], operand_list[1], int_value_from_string(operand_list[2])

    raise Exception("Mismatched add instruction format")


def int_value_from_string(integer_str: str) -> int:
    integer_str = integer_str.lstrip("#")
    if integer_str.startswith("0x") or integer_str.startswith("-0x"):
        integer_value = int(integer_str, 16)
    else:
        integer_value = int(integer_str)

    return integer_value
