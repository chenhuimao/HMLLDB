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
import HMRegister
from HMReference import HMExtendOption, HMShift
from HMRegister import HMRegisterList


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
            HM.DPrint("edisassemble only supports arm64 architecture.")
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
    # 0x102b8f544 <+0>:  sub    sp, sp, #0x20
    # -> 0x102b8f544 <+0>:  sub    sp, sp, #0x20

    # 0x1d8ebff50: adrp   x16, -243123
    # ->  0x1a31bc2f0: adrp   x16, 235058

    # DemoApp[0x102b8f544] <+0>:  sub    sp, sp, #0x20

    # DemoApp[0x10ed465e0]: adrp   x1, 15197

    keywords = assemble_line.split()
    if len(keywords) < 2:
        return lldb.LLDB_INVALID_ADDRESS

    address_str = keywords[0].rstrip(':')
    if keywords[0] == '->':
        address_str = keywords[1].rstrip(':')

    # Get the contents of []
    start = address_str.find('[')
    end = address_str.find(']')
    if 0 <= start < end:
        address_str = address_str[start + 1:end]

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
            # record_adrp_logic_orig(exe_ctx, instruction, address_comment_dict)


def record_branch_logic(exe_ctx: lldb.SBExecutionContext, branch_instruction: lldb.SBInstruction, address_comment_dict: Dict[int, str]) -> None:
    target = exe_ctx.GetTarget()
    comment = branch_instruction.GetComment(target)
    if len(comment) > 0:
        return
    my_comment = comment_for_branch(exe_ctx, branch_instruction)
    if len(my_comment) > 0:
        address_comment_dict[branch_instruction.GetAddress().GetLoadAddress(target)] = my_comment


def record_adrp_logic(exe_ctx: lldb.SBExecutionContext, adrp_instruction: lldb.SBInstruction, address_comment_dict: Dict[int, str]) -> None:
    # Analyze the specified instructions after adrp in sequence, and analyze up to 10 instructions.
    target = exe_ctx.GetTarget()
    register_list = HMRegisterList()

    # Calculate and save the value of adr/adrp instruction
    error = lldb.SBError()
    adrp_data: bytes = target.ReadMemory(adrp_instruction.GetAddress(), 4, error)
    if not error.Success():
        HM.DPrint(error)
        return
    adrp_instruction_load_address: int = adrp_instruction.GetAddress().GetLoadAddress(target)
    adrp_rd, adrp_offset = HMReference.decode_adr_bytes(adrp_data)
    if HMReference.is_adr_bytes(adrp_data):
        adrp_result = adrp_instruction_load_address + adrp_offset
    elif HMReference.is_adrp_bytes(adrp_data):
        adrp_result, _ = HMCalculationHelper.calculate_adrp_result_with_immediate_and_pc_address(adrp_offset, adrp_instruction_load_address)
    else:
        HM.DPrint("Not adr/adrp data.")
        return
    register_list.set_value(adrp_rd, adrp_result, True)
    adrp_comment = adrp_instruction.GetComment(target)
    if len(adrp_comment) == 0:
        my_comment = f"{HMRegister.get_register_name(adrp_rd, True)} = {hex(adrp_result)}"
        update_address_comment_dict(address_comment_dict, adrp_instruction_load_address, my_comment)

    # Analyze the specified instructions after adr/adrp
    instruction_count = 10
    address: lldb.SBAddress = lldb.SBAddress(adrp_instruction_load_address + 4, target)
    error = lldb.SBError()
    data: bytes = target.ReadMemory(address, 4 * instruction_count, error)
    if not error.Success():
        HM.DPrint(error)
        return
    instruction_list: lldb.SBInstructionList = target.ReadInstructions(address, instruction_count)
    for i in range(instruction_count):
        instruction_data = data[i*4:i*4+4]
        instruction: lldb.SBInstruction = instruction_list.GetInstructionAtIndex(i)
        instruction_load_address: int = instruction.GetAddress().GetLoadAddress(target)
        comment = instruction.GetComment(target)
        # adr/adrp
        if HMReference.is_adr_bytes(instruction_data):
            rd, offset = HMReference.decode_adr_bytes(instruction_data)
            rd_value = instruction_load_address + offset
            register_list.set_value(rd, rd_value, True)

            if len(comment) == 0:
                my_comment = f"{HMRegister.get_register_name(rd, True)} = {hex(rd_value)}"
                update_address_comment_dict(address_comment_dict, instruction_load_address, my_comment)
        elif HMReference.is_adrp_bytes(instruction_data):
            rd, offset = HMReference.decode_adr_bytes(instruction_data)
            rd_value, _ = HMCalculationHelper.calculate_adrp_result_with_immediate_and_pc_address(offset, instruction_load_address)
            register_list.set_value(rd, rd_value, True)

            if len(comment) == 0:
                my_comment = f"{HMRegister.get_register_name(rd, True)} = {hex(rd_value)}"
                update_address_comment_dict(address_comment_dict, instruction_load_address, my_comment)

        # add
        elif HMReference.is_add_bytes_immediate(instruction_data):
            rd, rn, is_64bit, final_immediate = HMReference.decode_add_bytes_immediate(instruction_data)
            if not register_list.has_value(rn):
                break
            rd_value = register_list.get_value(rn, is_64bit) + final_immediate
            register_list.set_value(rd, rd_value, is_64bit)

            if len(comment) == 0:
                result = register_list.get_value(rd, is_64bit)
                lookup_summary = HM.get_image_lookup_summary_from_address(result)
                my_comment = f"{HMRegister.get_register_name(rd, is_64bit)} = {hex(result)} {lookup_summary}"
                update_address_comment_dict(address_comment_dict, instruction_load_address, my_comment)
        elif HMReference.is_add_bytes_shifted_register(instruction_data):
            rd, rn, rm, is_64bit, shift, amount = HMReference.decode_add_bytes_shifted_register(instruction_data)
            if shift == HMShift.unknow:
                break
            if rd == 31:  # xzr
                continue
            if (not register_list.has_value(rn)) and rn != 31:
                break
            if (not register_list.has_value(rm)) and rm != 31:
                break
            rn_raw_value = 0 if rn == 31 else register_list.get_raw_value(rn, is_64bit)
            rm_raw_value = 0 if rm == 31 else register_list.get_raw_value(rm, is_64bit)
            bit_width = 64 if is_64bit else 32
            if amount == 0:
                rd_raw_value = rn_raw_value + rm_raw_value
            else:
                if shift == HMShift.lsl:
                    rm_value_shift = (rm_raw_value << amount) & ((1 << bit_width) - 1)
                elif shift == HMShift.lsr:
                    rm_value_shift = HMReference.logical_shift_right(rm_raw_value, amount, bit_width)
                elif shift == HMShift.asr:
                    rm_value_shift = (rm_raw_value >> amount) & ((1 << bit_width) - 1)
                else:  # HMShift.unknow
                    break
                rd_raw_value = rn_raw_value + rm_value_shift

            register_list.set_raw_value(rd, rd_raw_value, is_64bit)

            if len(comment) == 0:
                result = register_list.get_value(rd, is_64bit)
                lookup_summary = HM.get_image_lookup_summary_from_address(result)
                my_comment = f"{HMRegister.get_register_name(rd, is_64bit)} = {hex(result)} {lookup_summary}"
                update_address_comment_dict(address_comment_dict, instruction_load_address, my_comment)

        # ldr
        elif HMReference.is_ldr_bytes_immediate_post_index(instruction_data):
            rt, rn, is_64bit, simm = HMReference.decode_ldr_bytes_immediate_post_index(instruction_data)
            if not register_list.has_value(rn):
                break
            rn_value = register_list.get_value(rn, True)
            load_address = rn_value
            ldr_result = HM.load_address_value(exe_ctx, load_address)
            if ldr_result == -1:
                if len(comment) == 0:
                    my_comment = HM.get_image_lookup_summary_from_address(load_address)
                    update_address_comment_dict(address_comment_dict, instruction_load_address, my_comment)
                break
            if rt != 31:  # xzr
                register_list.set_raw_value(rt, ldr_result, is_64bit)
            rn_value += simm
            register_list.set_value(rn, rn_value, True)

            # lookup <ldr_result> first, if there is no result, lookup <load_address>
            if len(comment) == 0 and rt != 31:
                result = register_list.get_value(rt, is_64bit)
                lookup_summary = HM.get_image_lookup_summary_from_address(result)
                if len(lookup_summary) == 0:
                    lookup_summary = HM.get_image_lookup_summary_from_address(load_address)
                my_comment = f"{HMRegister.get_register_name(rt, is_64bit)} = {hex(result)} {lookup_summary}"
                update_address_comment_dict(address_comment_dict, instruction_load_address, my_comment)

        elif HMReference.is_ldr_bytes_immediate_pre_index(instruction_data):
            rt, rn, is_64bit, simm = HMReference.decode_ldr_bytes_immediate_pre_index(instruction_data)
            if not register_list.has_value(rn):
                break
            rn_value = register_list.get_value(rn, True)
            rn_value += simm
            register_list.set_value(rn, rn_value, True)
            ldr_result = HM.load_address_value(exe_ctx, rn_value)
            if ldr_result == -1:
                if len(comment) == 0:
                    my_comment = HM.get_image_lookup_summary_from_address(rn_value)
                    update_address_comment_dict(address_comment_dict, instruction_load_address, my_comment)
                break
            if rt != 31:  # xzr
                register_list.set_raw_value(rt, ldr_result, is_64bit)

            if len(comment) == 0 and rt != 31:
                result = register_list.get_value(rt, is_64bit)
                lookup_summary = HM.get_image_lookup_summary_from_address(result)
                if len(lookup_summary) == 0:
                    lookup_summary = HM.get_image_lookup_summary_from_address(rn_value)
                my_comment = f"{HMRegister.get_register_name(rt, is_64bit)} = {hex(result)} {lookup_summary}"
                update_address_comment_dict(address_comment_dict, instruction_load_address, my_comment)
        elif HMReference.is_ldr_bytes_immediate_unsigned_offset(instruction_data):
            rt, rn, is_64bit, pimm = HMReference.decode_ldr_bytes_immediate_unsigned_offset(instruction_data)
            if not register_list.has_value(rn):
                break
            rn_value = register_list.get_value(rn, True)
            load_address = rn_value + pimm
            ldr_result = HM.load_address_value(exe_ctx, load_address)
            if ldr_result == -1:
                if len(comment) == 0:
                    my_comment = HM.get_image_lookup_summary_from_address(load_address)
                    update_address_comment_dict(address_comment_dict, instruction_load_address, my_comment)
                break
            if rt != 31:  # xzr
                register_list.set_raw_value(rt, ldr_result, is_64bit)

            if len(comment) == 0 and rt != 31:
                result = register_list.get_value(rt, is_64bit)
                lookup_summary = HM.get_image_lookup_summary_from_address(result)
                if len(lookup_summary) == 0:
                    lookup_summary = HM.get_image_lookup_summary_from_address(load_address)
                my_comment = f"{HMRegister.get_register_name(rt, is_64bit)} = {hex(result)} {lookup_summary}"
                update_address_comment_dict(address_comment_dict, instruction_load_address, my_comment)
        elif HMReference.is_ldr_bytes_literal(instruction_data):
            rt, is_64bit, label = HMReference.decode_ldr_bytes_literal(instruction_data)
            load_address = label + instruction_load_address
            ldr_result = HM.load_address_value(exe_ctx, load_address)
            if ldr_result == -1:
                if len(comment) == 0:
                    my_comment = HM.get_image_lookup_summary_from_address(load_address)
                    update_address_comment_dict(address_comment_dict, instruction_load_address, my_comment)
                break
            if rt != 31:  # xzr
                register_list.set_raw_value(rt, ldr_result, is_64bit)

            if len(comment) == 0 and rt != 31:
                result = register_list.get_value(rt, is_64bit)
                lookup_summary = HM.get_image_lookup_summary_from_address(result)
                if len(lookup_summary) == 0:
                    lookup_summary = HM.get_image_lookup_summary_from_address(load_address)
                my_comment = f"{HMRegister.get_register_name(rt, is_64bit)} = {hex(result)} {lookup_summary}"
                update_address_comment_dict(address_comment_dict, instruction_load_address, my_comment)
        elif HMReference.is_ldr_bytes_register(instruction_data):
            rt, rn, rm, is_64bit, extend, amount = HMReference.decode_ldr_bytes_register(instruction_data)
            if rt == 31:  # xzr
                continue
            if extend == HMExtendOption.unknow or extend == HMExtendOption.sxtx:
                break
            if not register_list.has_value(rn):
                break
            if rm != 31 and (not register_list.has_value(rm)):
                break
            rn_raw_value = register_list.get_raw_value(rn, True)
            if extend == HMExtendOption.uxtw:
                rm_raw_value = 0 if rm == 31 else register_list.get_raw_value(rm, False)
                temp = HMReference.unsigned_extend_word(rm_raw_value) << amount
            elif extend == HMExtendOption.lsl:
                rm_raw_value = 0 if rm == 31 else register_list.get_raw_value(rm, True)
                temp = rm_raw_value << amount
            elif extend == HMExtendOption.sxtw:
                rm_raw_value = 0 if rm == 31 else register_list.get_value(rm, False)
                temp = HMReference.signed_extend_word(rm_raw_value) << amount
            else:
                break
            load_address = HMRegister.twos_complement_to_int(rn_raw_value + temp, 64)
            ldr_result = HM.load_address_value(exe_ctx, load_address)
            if ldr_result == -1:
                break
            register_list.set_raw_value(rt, ldr_result, is_64bit)

            if len(comment) == 0:
                result = register_list.get_value(rt, is_64bit)
                lookup_summary = HM.get_image_lookup_summary_from_address(result)
                if len(lookup_summary) == 0:
                    lookup_summary = HM.get_image_lookup_summary_from_address(load_address)
                my_comment = f"{HMRegister.get_register_name(rt, is_64bit)} = {hex(result)} {lookup_summary}"
                update_address_comment_dict(address_comment_dict, instruction_load_address, my_comment)

        # ldrsw
        elif HMReference.is_ldrsw_bytes_immediate_post_index(instruction_data):
            rt, rn, simm = HMReference.decode_ldrsw_bytes_immediate_post_index(instruction_data)
            if not register_list.has_value(rn):
                break
            rn_value = register_list.get_value(rn, True)
            load_address = rn_value
            ldrsw_result = HM.load_address_value_signed_word(exe_ctx, load_address)
            if ldrsw_result == -1:
                break
            if rt != 31:  # xzr
                register_list.set_raw_value(rt, ldrsw_result, True)
            rn_value += simm
            register_list.set_value(rn, rn_value, True)

            # The ldrsw instruction records the result address in memory
            if len(comment) == 0 and rt != 31:
                result = register_list.get_value(rt, True)
                my_comment = f"{HMRegister.get_register_name(rt, True)} = {hex(result)}"
                update_address_comment_dict(address_comment_dict, instruction_load_address, my_comment)
        elif HMReference.is_ldrsw_bytes_immediate_pre_index(instruction_data):
            rt, rn, simm = HMReference.decode_ldrsw_bytes_immediate_pre_index(instruction_data)
            if not register_list.has_value(rn):
                break
            rn_value = register_list.get_value(rn, True)
            rn_value += simm
            register_list.set_value(rn, rn_value, True)
            ldrsw_result = HM.load_address_value_signed_word(exe_ctx, rn_value)
            if ldrsw_result == -1:
                break
            if rt != 31:  # xzr
                register_list.set_raw_value(rt, ldrsw_result, True)

            if len(comment) == 0 and rt != 31:
                result = register_list.get_value(rt, True)
                my_comment = f"{HMRegister.get_register_name(rt, True)} = {hex(result)}"
                update_address_comment_dict(address_comment_dict, instruction_load_address, my_comment)
        elif HMReference.is_ldrsw_bytes_immediate_unsigned_offset(instruction_data):
            rt, rn, pimm = HMReference.decode_ldrsw_bytes_immediate_unsigned_offset(instruction_data)
            if not register_list.has_value(rn):
                break
            rn_value = register_list.get_value(rn, True)
            load_address = rn_value + pimm
            ldrsw_result = HM.load_address_value_signed_word(exe_ctx, load_address)
            if ldrsw_result == -1:
                break
            if rt != 31:  # xzr
                register_list.set_raw_value(rt, ldrsw_result, True)

            if len(comment) == 0 and rt != 31:
                result = register_list.get_value(rt, True)
                my_comment = f"{HMRegister.get_register_name(rt, True)} = {hex(result)}"
                update_address_comment_dict(address_comment_dict, instruction_load_address, my_comment)
        elif HMReference.is_ldrsw_bytes_register(instruction_data):
            rt, rn, rm, extend, amount = HMReference.decode_ldrsw_bytes_register(instruction_data)
            if rt == 31:  # xzr
                continue
            if extend == HMExtendOption.unknow or extend == HMExtendOption.sxtx:
                break
            if not register_list.has_value(rn):
                break
            if rm != 31 and (not register_list.has_value(rm)):
                break
            rn_raw_value = register_list.get_raw_value(rn, True)
            if extend == HMExtendOption.uxtw:
                rm_raw_value = 0 if rm == 31 else register_list.get_raw_value(rm, False)
                temp = HMReference.unsigned_extend_word(rm_raw_value) << amount
            elif extend == HMExtendOption.lsl:
                rm_raw_value = 0 if rm == 31 else register_list.get_raw_value(rm, True)
                temp = rm_raw_value << amount
            elif extend == HMExtendOption.sxtw:
                rm_raw_value = 0 if rm == 31 else register_list.get_value(rm, False)
                temp = HMReference.signed_extend_word(rm_raw_value) << amount
            else:
                break
            load_address = HMRegister.twos_complement_to_int(rn_raw_value + temp, 64)
            ldrsw_result = HM.load_address_value_signed_word(exe_ctx, load_address)
            if ldrsw_result == -1:
                break
            register_list.set_raw_value(rt, ldrsw_result, True)

            if len(comment) == 0:
                result = register_list.get_value(rt, True)
                my_comment = f"{HMRegister.get_register_name(rt, True)} = {hex(result)}"
                update_address_comment_dict(address_comment_dict, instruction_load_address, my_comment)

        # mov
        elif HMReference.is_mov_bytes_inverted_wide_immediate(instruction_data):
            rd, is_64bit, immediate = HMReference.decode_mov_bytes_inverted_wide_immediate(instruction_data)
            if rd == 31:  # xzr
                continue
            register_list.set_value(rd, immediate, is_64bit)
            if len(comment) == 0:
                result = register_list.get_value(rd, is_64bit)
                lookup_summary = HM.get_image_lookup_summary_from_address(result)
                my_comment = f"{HMRegister.get_register_name(rd, is_64bit)} = {hex(result)} {lookup_summary}"
                update_address_comment_dict(address_comment_dict, instruction_load_address, my_comment)
        elif HMReference.is_mov_bytes_register(instruction_data):
            rd, rm, is_64bit = HMReference.decode_mov_bytes_register(instruction_data)
            if rd == 31:  # xzr
                continue
            if rm != 31 and (not register_list.has_value(rm)):
                break
            rm_raw_value = 0 if rm == 31 else register_list.get_raw_value(rm, is_64bit)
            register_list.set_raw_value(rd, rm_raw_value, is_64bit)

            if len(comment) == 0:
                result = register_list.get_value(rd, is_64bit)
                lookup_summary = HM.get_image_lookup_summary_from_address(result)
                my_comment = f"{HMRegister.get_register_name(rd, is_64bit)} = {hex(result)} {lookup_summary}"
                update_address_comment_dict(address_comment_dict, instruction_load_address, my_comment)
        elif HMReference.is_mov_bytes_to_from_sp(instruction_data):
            rd, rn, is_64bit = HMReference.decode_mov_bytes_to_from_sp(instruction_data)
            if not register_list.has_value(rn):
                break
            rn_raw_value = register_list.get_raw_value(rn, is_64bit)
            register_list.set_raw_value(rd, rn_raw_value, is_64bit)

            if len(comment) == 0:
                result = register_list.get_value(rd, is_64bit)
                lookup_summary = HM.get_image_lookup_summary_from_address(result)
                my_comment = f"{HMRegister.get_register_name(rd, is_64bit)} = {hex(result)} {lookup_summary}"
                update_address_comment_dict(address_comment_dict, instruction_load_address, my_comment)
        elif HMReference.is_mov_bytes_wide_immediate(instruction_data):
            rd, is_64bit, immediate = HMReference.decode_mov_bytes_wide_immediate(instruction_data)
            if rd == 31:  # xzr
                continue
            register_list.set_value(rd, immediate, is_64bit)

            if len(comment) == 0:
                result = register_list.get_value(rd, is_64bit)
                lookup_summary = HM.get_image_lookup_summary_from_address(result)
                my_comment = f"{HMRegister.get_register_name(rd, is_64bit)} = {hex(result)} {lookup_summary}"
                update_address_comment_dict(address_comment_dict, instruction_load_address, my_comment)

        # str
        elif HMReference.is_str_bytes_immediate_post_index(instruction_data):
            rt, rn, is_64bit, simm = HMReference.decode_str_bytes_immediate_post_index(instruction_data)
            if not register_list.has_value(rn):
                break
            rn_value = register_list.get_value(rn, True)
            load_address = rn_value
            rn_value += simm
            register_list.set_value(rn, rn_value, is_64bit)
        elif HMReference.is_str_bytes_immediate_pre_index(instruction_data):
            rt, rn, is_64bit, simm = HMReference.decode_str_bytes_immediate_pre_index(instruction_data)
            if not register_list.has_value(rn):
                break
            rn_value = register_list.get_value(rn, True)
            rn_value += simm
            register_list.set_value(rn, rn_value, is_64bit)
        elif HMReference.is_str_bytes_immediate_unsigned_offset(instruction_data):
            continue
        elif HMReference.is_str_bytes_register(instruction_data):
            rt, rn, rm, is_64bit, extend, amount = HMReference.decode_str_bytes_register(instruction_data)
            if extend == HMExtendOption.unknow or extend == HMExtendOption.sxtx:
                break
            continue

        # stp
        elif HMReference.is_stp_bytes_signed_offset(instruction_data):
            continue

        # nop
        elif HMReference.is_nop_bytes(instruction_data):
            continue
        else:
            break


def record_adrp_logic_orig(exe_ctx: lldb.SBExecutionContext, adrp_instruction: lldb.SBInstruction, address_comment_dict: Dict[int, str]) -> None:
    # Analyze the specified instructions after adrp in sequence, and analyze up to 10 instructions.
    # FIXME: x0 and w0 registers are independent and need to be merged.
    register_dic: Dict[str, int] = {}
    target = exe_ctx.GetTarget()

    # Calculate and save the value of adr/adrp instruction
    can_analyze_adrp, adrp_target_register, adrp_result = analyze_adrp(exe_ctx, adrp_instruction, register_dic)
    if not can_analyze_adrp:
        return

    adrp_instruction_load_address: int = adrp_instruction.GetAddress().GetLoadAddress(target)
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
            can_analyze_add, target_register_str, add_value = analyze_add(exe_ctx, instruction, register_dic)
            if not can_analyze_add:
                break
            if len(comment) == 0:
                lookup_summary = HM.get_image_lookup_summary_from_address(add_value)
                add_comment = f"{target_register_str} = {hex(add_value)} {lookup_summary}"
                address_comment_dict[instruction_load_address_int] = add_comment
        elif mnemonic == 'ldr':
            can_analyze_ldr, can_get_load_address, target_register_str, load_address_int, load_result_int = analyze_ldr(exe_ctx, instruction, register_dic)
            if not can_get_load_address:
                break
            if len(comment) == 0:
                lookup_summary = ""
                # lookup <load_result_int> first, if there is no result, lookup <load_address_int>
                if can_analyze_ldr:
                    lookup_summary = HM.get_image_lookup_summary_from_address(load_result_int)
                if len(lookup_summary) == 0:
                    lookup_summary = HM.get_image_lookup_summary_from_address(load_address_int)

                if can_analyze_ldr:
                    ldr_comment = f"{target_register_str} = {hex(load_result_int)} {lookup_summary}"
                else:
                    ldr_comment = lookup_summary

                if len(ldr_comment) > 0:
                    address_comment_dict[instruction_load_address_int] = ldr_comment

        elif mnemonic == 'ldrsw':
            can_analyze_ldrsw, _, target_register_str, _, load_result_int = analyze_ldr(exe_ctx, instruction, register_dic)
            if not can_analyze_ldrsw:
                break
            # The ldrsw instruction records the result address in memory
            if len(comment) == 0:
                lookup_summary = HM.get_image_lookup_summary_from_address(load_result_int)
                ldr_comment = f"{target_register_str} = {hex(load_result_int)} {lookup_summary}"
                address_comment_dict[instruction_load_address_int] = ldr_comment
        elif mnemonic == 'mov':
            can_analyze_mov, target_register_str, mov_value = analyze_mov(exe_ctx, instruction, register_dic)
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

def update_address_comment_dict(address_comment_dict: Dict[int, str], address_int: int, comment: str) -> bool:
    original_comment = address_comment_dict.get(address_int, "")
    if len(original_comment) >= len(comment):
        return False

    address_comment_dict[address_int] = comment
    return True


def comment_for_branch(exe_ctx: lldb.SBExecutionContext, branch_instruction: lldb.SBInstruction) -> str:
    target = exe_ctx.GetTarget()

    # Find the target address of the branch instruction
    branch_operands = branch_instruction.GetOperands(target)
    is_valid_address, address_int = HM.int_value_from_string(branch_operands)
    if not is_valid_address:
        return ""

    address: lldb.SBAddress = lldb.SBAddress(address_int, target)

    # Read 10 instructions of target address
    instruction_count = 10
    instruction_list: lldb.SBInstructionList = target.ReadInstructions(address, instruction_count)
    if instruction_count != instruction_list.GetSize():
        return ""

    # Analyze
    register_dic: Dict[str, int] = {}
    for i in range(instruction_count):
        instruction: lldb.SBInstruction = instruction_list.GetInstructionAtIndex(i)
        comment = instruction.GetComment(target)
        mnemonic: str = instruction.GetMnemonic(target)
        if mnemonic in ['br', 'blr']:
            # Get the comment of the target address of the next branch instruction
            operands = instruction.GetOperands(target)
            if operands not in register_dic:
                return ""
            target_result = register_dic[operands]
            lookup_summary = HM.get_image_lookup_summary_from_address(target_result)
            my_comment = f"{mnemonic} {operands}, {operands} = {hex(target_result)} {lookup_summary}"

            # resolve "x1" register when target is objc_msgSend
            if 'objc_msgSend' in lookup_summary and 'x1' in register_dic:
                x1_value = register_dic['x1']
                # Sometimes the summary is missing when using "image lookup", so use the "x/s" command instead.
                x1_str_return_object = lldb.SBCommandReturnObject()
                exe_ctx.GetTarget().GetDebugger().GetCommandInterpreter().HandleCommand(f"x/s {x1_value}", exe_ctx, x1_str_return_object)
                output_list = x1_str_return_object.GetOutput().split(" ")
                if len(output_list) >= 2:
                    x1_str_result = output_list[1]
                    my_comment = f"{my_comment}, sel = {x1_str_result}"
            return my_comment
        elif mnemonic in ['adr', 'adrp']:
            can_analyze_adrp, _, _ = analyze_adrp(exe_ctx, instruction, register_dic)
            if not can_analyze_adrp:
                return ""
        elif mnemonic == 'add':
            can_analyze_add, _, _ = analyze_add(exe_ctx, instruction, register_dic)
            if not can_analyze_add:
                return ""
        elif mnemonic in ['ldr', 'ldrsw']:
            can_analyze_ldr, _, _, _, _ = analyze_ldr(exe_ctx, instruction, register_dic)
            if not can_analyze_ldr:
                return ""
        elif mnemonic == 'mov':
            can_analyze_mov, _, _ = analyze_mov(exe_ctx, instruction, register_dic)
            if not can_analyze_mov:
                return ""
        elif mnemonic in ['str', 'nop']:
            continue
        else:
            return ""

    return ""


def analyze_adrp(exe_ctx: lldb.SBExecutionContext, adrp_instruction: lldb.SBInstruction, register_dic: Dict[str, int]) -> Tuple[bool, str, int]:
    # return (analyze_result, target_register_str, adrp_value)
    target = exe_ctx.GetTarget()
    adrp_instruction_load_address: int = adrp_instruction.GetAddress().GetLoadAddress(target)
    adrp_instruction_mnemonic = adrp_instruction.GetMnemonic(target)
    adrp_target_register = ""
    adrp_result = -1
    if adrp_instruction_mnemonic == 'adr':
        # adr x17, #-0x8000
        operands = adrp_instruction.GetOperands(target).split(', ')
        if not (operands[1].startswith('#0x') or operands[1].startswith('#-0x')):
            # HM.DPrint(f"Error: Unsupported format in adr. Load address:{hex(adrp_instruction_load_address)}")
            return False, "", 0
        adrp_result = adrp_instruction_load_address + int(operands[1].lstrip('#'), 16)
        adrp_target_register = operands[0]
    elif adrp_instruction_mnemonic == 'adrp':
        # adrp x8, -24587
        operands = adrp_instruction.GetOperands(target).split(', ')
        adrp_result_tuple: Tuple[int, str] = HMCalculationHelper.calculate_adrp_result_with_immediate_and_pc_address(int(operands[1]), adrp_instruction_load_address)
        adrp_result = adrp_result_tuple[0]
        adrp_target_register = operands[0]
    else:
        return False, "", 0
    register_dic[adrp_target_register] = adrp_result
    return True, adrp_target_register, adrp_result


def analyze_add(exe_ctx: lldb.SBExecutionContext, add_instruction: lldb.SBInstruction, register_dic: Dict[str, int]) -> Tuple[bool, str, int]:
    # return (analyze_result, target_register_str, add_value)
    target = exe_ctx.GetTarget()
    operands = add_instruction.GetOperands(target).split(', ')
    if operands[1] in register_dic:
        op1_value = register_dic[operands[1]]
    else:
        is_valid_value, immediate_operand_value = HM.int_value_from_string(operands[1].lstrip("#"))
        if not is_valid_value:
            return False, "", 0
        op1_value = immediate_operand_value

    if operands[2] in register_dic:
        op2_value = register_dic[operands[2]]
    else:
        is_valid_value, immediate_operand_value = HM.int_value_from_string(operands[2].lstrip("#"))
        if not is_valid_value:
            return False, "", 0
        op2_value = immediate_operand_value

    register_dic[operands[0]] = op1_value + op2_value
    return True, operands[0], op1_value + op2_value


def analyze_ldr(exe_ctx: lldb.SBExecutionContext, ldr_instruction: lldb.SBInstruction, register_dic: Dict[str, int]) -> Tuple[bool, bool, str, int, int]:
    # return (analyze_result, can_get_load_address, target_register_str, load_address_int, load_result_int)
    target = exe_ctx.GetTarget()
    operand_tuple: Tuple[bool, str, str, str] = resolve_ldr_operands(ldr_instruction.GetOperands(target))
    if not operand_tuple[0]:
        return False, False, "", 0, 0
    if operand_tuple[2] not in register_dic:
        return False, False, "", 0, 0

    if operand_tuple[3] in register_dic:
        op3_value = register_dic[operand_tuple[3]]
    else:
        is_valid_value, immediate_operand_value = HM.int_value_from_string(operand_tuple[3].lstrip("#"))
        if not is_valid_value:
            return False, False, "", 0, 0
        op3_value = immediate_operand_value

    load_address: int = register_dic[operand_tuple[2]] + op3_value

    mnemonic = ldr_instruction.GetMnemonic(target)
    if mnemonic == 'ldr':
        ldr_result = HM.load_address_value(exe_ctx, load_address)
    elif mnemonic == 'ldrsw':
        ldr_result = HM.load_address_value_signed_word(exe_ctx, load_address)
    else:
        ldr_result = -1
        raise Exception("Parameter error, unsupported instruction type")

    if ldr_result == -1:
        # ldr_instruction_load_address_int: int = ldr_instruction.GetAddress().GetLoadAddress(target)
        # HM.DPrint(f"Invalid load address, instruction:{ldr_instruction}, instruction load address: {hex(ldr_instruction_load_address_int)}")
        return False, True, "", load_address, 0

    register_dic[operand_tuple[1]] = ldr_result
    return True, True, operand_tuple[1], load_address, ldr_result


def analyze_mov(exe_ctx: lldb.SBExecutionContext, mov_instruction: lldb.SBInstruction, register_dic: Dict[str, int]) -> Tuple[bool, str, int]:
    # return (analyze_result, target_register_str, mov_value)
    target = exe_ctx.GetTarget()
    operands = mov_instruction.GetOperands(target).split(', ')
    if operands[1] in register_dic:
        op1_value = register_dic[operands[1]]
    else:
        is_valid_value, immediate_operand_value = HM.int_value_from_string(operands[1].lstrip("#"))
        if not is_valid_value:
            return False, "", 0
        op1_value = immediate_operand_value

    register_dic[operands[0]] = op1_value
    return True, operands[0], op1_value


# resolve ldr/ldrsw/str
def resolve_ldr_operands(operands: str) -> Tuple[bool, str, str, str]:
    # ldr x1, [x2, #0x9c8] -> (True, x1, x2, 0x9c8)
    # ldr x1, [x2] -> (True, x1, x2, 0)
    # ldr x8, [x0, x20] -> (True, x8, x0, x20)
    operand_list = operands.split(', ')
    if len(operand_list) == 2:
        return True, operand_list[0], operand_list[1].lstrip('[').rstrip(']'), "0"
    elif len(operand_list) == 3:
        operand_list[1] = operand_list[1].lstrip('[')
        operand_list[2] = operand_list[2].rstrip(']')
        return True, operand_list[0], operand_list[1], operand_list[2]

    # return False
    # ldr x21, [x8, x23, lsl #3] -> (False, "", "", "0")
    return False, "", "", "0"
