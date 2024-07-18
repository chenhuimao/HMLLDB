# The MIT License (MIT)
#
# Copyright (c) 2024 Huimao Chen
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
from enum import Enum
from typing import Dict, List, Tuple
import optparse
import os
import shlex
import HMCalculationHelper
import HMLLDBClassInfo
import HMLLDBHelpers as HM
import HMRegister
from HMRegister import HMRegisterList


g_image_address_target_dic: Dict[str, Dict[int, int]] = {}
g_image_address_ldr_dic: Dict[str, Dict[int, int]] = {}


class HMExtendOption(Enum):
    uxtw = 0b010
    lsl = 0b011
    sxtw = 0b110
    sxtx = 0b111
    unknow = 0b1000


class HMShift(Enum):
    lsl = 0b00
    lsr = 0b01
    asr = 0b10
    unknow = 0b11


def __lldb_init_module(debugger, internal_dict):
    debugger.HandleCommand('command script add -f HMReference.reference reference -h "Scan the image section to obtain all reference addresses of a certain address."')


def reference(debugger, command, exe_ctx, result, internal_dict):
    """
    Syntax:
        reference <address> <image_name>

    Examples:
        (lldb) reference 0x12345678 MyApp
        (lldb) reference 0x12345678 UIKitCore

    Notice:
        1.This command is expensive to scan large modules. For example, it takes 130 seconds to scan UIKitCore.
        2.This command will query the targets of all b/bl instructions and analyze most of the adr/adrp instructions and subsequent instructions.
        3.You should consider the "stub" function and "island" function when using it.

    This command is implemented in HMReference.py
    """

    if not HM.is_arm64(exe_ctx.GetTarget()):
        HM.DPrint("x86_64 architecture does not support the \"reference\" command.")
        return

    command_args: List[str] = command.split()
    if len(command_args) != 2:
        HM.DPrint("Error input. Please enter \"help reference\" for help.")
        return
    address_or_name = command_args[0]
    is_valid_address, target_address_int = HM.int_value_from_string(address_or_name)
    if not is_valid_address:
        HM.DPrint(f"Invalid address:{address_or_name}")
        return

    image_name = command_args[1]
    global g_image_address_target_dic, g_image_address_ldr_dic

    start_time = datetime.now().strftime("%H:%M:%S")
    is_first_scan_target_image = False
    # Find and scan module
    if image_name not in g_image_address_target_dic:
        is_first_scan_target_image = True
        # Find module
        target = exe_ctx.GetTarget()
        target_module: lldb.SBModule = None
        module_num = target.GetNumModules()
        for i in range(module_num):
            module = target.GetModuleAtIndex(i)
            if image_name == get_module_name(module):
                target_module = module
                break
        if target_module is None:
            HM.DPrint(f"Unable to find module:{image_name}. Please enter the \"image list\" command to view all modules.")
            return

        # Initialize variables corresponding to the module
        address_target_dic: Dict[int, int] = {}
        g_image_address_target_dic[image_name] = address_target_dic
        address_ldr_dic: Dict[int, int] = {}
        g_image_address_ldr_dic[image_name] = address_ldr_dic
        # Scan module
        section_num = target_module.GetNumSections()
        for i in range(section_num):
            section = target_module.GetSectionAtIndex(i)
            scan_section_code(exe_ctx, section, address_target_dic, address_ldr_dic)

    else:
        address_target_dic: Dict[int, int] = g_image_address_target_dic[image_name]
        address_ldr_dic: Dict[int, int] = g_image_address_ldr_dic[image_name]

    # Traverse records and print matching results
    result_count = 0
    for key, value in address_target_dic.items():
        if value == target_address_int:
            result_count += 1
            result_address: str = hex(key)
            if result_count == 1:
                HM.DPrint("These are the scan results:")
            print(f"{result_address}: {HM.get_image_lookup_summary_from_address(result_address)}")

    HM.DPrint(f"Scan result count:{result_count}")

    # Traverse memory records and print matching results
    result_count = 0
    for key, value in address_ldr_dic.items():
        if value == target_address_int:
            result_count += 1
            result_address: str = hex(key)
            if result_count == 1:
                HM.DPrint("These are the scan results in memory:")
            print(f"{result_address}: {HM.get_image_lookup_summary_from_address(result_address)}")

    HM.DPrint(f"Scan result count in memory:{result_count}")

    # Print time when scanning moudle for the first time
    if is_first_scan_target_image:
        stop_time = datetime.now().strftime("%H:%M:%S")
        HM.DPrint(f"Start time: {start_time}")
        HM.DPrint(f"Stop time: {stop_time}")


def scan_section_code(exe_ctx: lldb.SBExecutionContext, section: lldb.SBSection, address_target_dic: Dict[int, int], address_ldr_dic: Dict[int, int]) -> None:
    target: lldb.SBTarget = exe_ctx.GetTarget()
    section_type_int = section.GetSectionType()
    if section_type_int == lldb.eSectionTypeContainer:
        sub_sections_num = section.GetNumSubSections()
        for i in range(sub_sections_num):
            sub_section = section.GetSubSectionAtIndex(i)
            scan_section_code(exe_ctx, sub_section, address_target_dic, address_ldr_dic)
    elif section_type_int == lldb.eSectionTypeCode:
        HM.DPrint(f"Analyzing section:{get_description_of_section(section)}")
        section_load_address_start = section.GetLoadAddress(target)
        section_load_address_end = section.GetLoadAddress(target) + section.GetByteSize()
        current_address = section_load_address_start
        span = 4 * 10000
        snippet_count = int((section_load_address_end - section_load_address_start) / span)
        # print(f"snippet_count:{snippet_count}")
        analyzing_snippet_count = 0
        last_percentage: float = 0.0
        while current_address + span < section_load_address_end:
            instruction_analysis(exe_ctx, current_address, current_address + span, address_target_dic, address_ldr_dic)
            current_address = current_address + span
            # print percentage if necessary
            if snippet_count > 120:
                analyzing_snippet_count += 1
                percentage = (analyzing_snippet_count / snippet_count) * 100
                # Print every 5 percent
                if percentage - last_percentage > 5.0:
                    last_percentage = percentage
                    print(f"{percentage:.2f}%")

        # analysis last snippet
        if section_load_address_end - current_address >= 4:
            instruction_analysis(exe_ctx, current_address, section_load_address_end, address_target_dic, address_ldr_dic)


def instruction_analysis(exe_ctx: lldb.SBExecutionContext, start_address: int, end_address: int, address_target_dic: Dict[int, int], address_ldr_dic: Dict[int, int]) -> None:
    target: lldb.SBTarget = exe_ctx.GetTarget()
    address: lldb.SBAddress = lldb.SBAddress(start_address, target)
    error = lldb.SBError()
    data: bytes = target.ReadMemory(address, end_address - start_address, error)
    if not error.Success():
        HM.DPrint(error)
        return
    for i in range(0, len(data), 4):
        instruction_data = data[i:i+4]
        if is_adrp_bytes(instruction_data) or is_adr_bytes(instruction_data):
            # Record all adr/adrp logic
            record_adrp_logic(exe_ctx, instruction_data, start_address + i, address_target_dic, address_ldr_dic)
        elif is_b_bytes(instruction_data) or is_bl_bytes(instruction_data):
            # Record all b/bl logic
            label = decode_b_bytes(instruction_data)
            address_target_dic[start_address + i] = start_address + i + label

        # For testing
        # if is_add_bytes_shifted_register(instruction_data):
        #     current_address: lldb.SBAddress = lldb.SBAddress(start_address + i, target)
        #     instruction_list: lldb.SBInstructionList = target.ReadInstructions(current_address, 1)
        #     instruction = instruction_list.GetInstructionAtIndex(0)
        #     HM.DPrint(f"{hex(start_address + i)}:{instruction} - {decode_add_bytes_shifted_register(instruction_data)}")

    # For testing
    # instruction_count = int((end_address - start_address) / 4)
    # instruction_list: lldb.SBInstructionList = target.ReadInstructions(address, instruction_count)
    # for i in range(instruction_count):
    #     instruction: lldb.SBInstruction = instruction_list.GetInstructionAtIndex(i)
    #     mnemonic: str = instruction.GetMnemonic(target)
    #     if mnemonic == 'add':
    #         step = i * 4
    #         instruction_data = data[step:step+4]
    #         if not (is_add_bytes_shifted_register(instruction_data) or is_add_bytes_extended_register(instruction_data) or is_add_bytes_immediate(instruction_data)):
    #             load_address_int = start_address + step
    #             HM.DPrint(f"{hex(load_address_int)}:{instruction}")


def is_adr_bytes(data: bytes) -> bool:
    # little endian
    # ADR <Xd>, <label>
    return (data[3] & 0x9f) == 0x10


def is_adrp_bytes(data: bytes) -> bool:
    # little endian
    # ADRP <Xd>, <label>
    return (data[3] & 0x9f) == 0x90


def is_b_bytes(data: bytes) -> bool:
    # little endian
    # B <label>
    return (data[3] & 0xfc) == 0x14


def is_bl_bytes(data: bytes) -> bool:
    # little endian
    # BL <label>
    return (data[3] & 0xfc) == 0x94


# ADD (extended register)
def is_add_bytes_extended_register(data: bytes) -> bool:
    # little endian
    # 32-bit: ADD <Wd|WSP>, <Wn|WSP>, <Wm>{, <extend> {#<amount>}}
    # 64-bit: ADD <Xd|SP>, <Xn|SP>, <Rm>{, <extend> {#<amount>}}
    # There are still a few cases that need to be excluded, which are omitted for efficiency.
    return ((data[3] & 0x7f) == 0x0b) and ((data[2] & 0xe0) == 0x20)


# ADD (immediate)
def is_add_bytes_immediate(data: bytes) -> bool:
    # little endian
    # This instruction is used by the alias MOV (to/from SP).
    # 32-bit: ADD <Wd|WSP>, <Wn|WSP>, #<imm>{, <shift>}
    # 64-bit: ADD <Xd|SP>, <Xn|SP>, #<imm>{, <shift>}
    return ((data[3] & 0x7f) == 0x11) and ((data[2] & 0x80) == 0x00)


# ADD (shifted register)
def is_add_bytes_shifted_register(data: bytes) -> bool:
    # little endian
    # 32-bit: ADD <Wd>, <Wn>, <Wm>{, <shift> #<amount>}
    # 64-bit: ADD <Xd>, <Xn>, <Xm>{, <shift> #<amount>}
    # There are still a few cases that need to be excluded, which are omitted for efficiency.(shift = 0b11, 32bit amount > 31)
    return ((data[3] & 0x7f) == 0x0b) and ((data[2] & 0x20) == 0x00)


# LDR (immediate) Post-index
def is_ldr_bytes_immediate_post_index(data: bytes) -> bool:
    # little endian
    # 32-bit: LDR <Wt>, [<Xn|SP>], #<simm>
    # 64-bit: LDR <Xt>, [<Xn|SP>], #<simm>
    return ((data[3] & 0xbf) == 0xb8) and ((data[2] & 0xe0) == 0x40) and ((data[1] & 0x0c) == 0x04)


# LDR (immediate) Pre-index
def is_ldr_bytes_immediate_pre_index(data: bytes) -> bool:
    # little endian
    # 32-bit: LDR <Wt>, [<Xn|SP>, #<simm>]!
    # 64-bit: LDR <Xt>, [<Xn|SP>, #<simm>]!
    return ((data[3] & 0xbf) == 0xb8) and ((data[2] & 0xe0) == 0x40) and ((data[1] & 0x0c) == 0x0c)


# LDR (immediate) Unsigned offset
def is_ldr_bytes_immediate_unsigned_offset(data: bytes) -> bool:
    # little endian
    # 32-bit: LDR <Wt>, [<Xn|SP>{, #<pimm>}]
    # 64-bit: LDR <Xt>, [<Xn|SP>{, #<pimm>}]
    return ((data[3] & 0xbf) == 0xb9) and ((data[2] & 0xc0) == 0x40)


# LDR (literal)
def is_ldr_bytes_literal(data: bytes) -> bool:
    # little endian
    # 32-bit: LDR <Wt>, <label>
    # 64-bit: LDR <Xt>, <label>
    return (data[3] & 0xbf) == 0x18


# LDR (register)
def is_ldr_bytes_register(data: bytes) -> bool:
    # little endian
    # 32-bit: LDR <Wt>, [<Xn|SP>, (<Wm>|<Xm>){, <extend> {<amount>}}]
    # 64-bit: LDR <Xt>, [<Xn|SP>, (<Wm>|<Xm>){, <extend> {<amount>}}]
    # There are still a few cases that need to be excluded, which are omitted for efficiency
    return ((data[3] & 0xbf) == 0xb8) and ((data[2] & 0xe0) == 0x60) and ((data[1] & 0x0c) == 0x08)


# LDRSW (immediate) Post-index
def is_ldrsw_bytes_immediate_post_index(data: bytes) -> bool:
    # little endian
    # LDRSW <Xt>, [<Xn|SP>], #<simm>
    return ((data[3] & 0xff) == 0xb8) and ((data[2] & 0xe0) == 0x80) and ((data[1] & 0x0c) == 0x04)


# LDRSW (immediate) Pre-index
def is_ldrsw_bytes_immediate_pre_index(data: bytes) -> bool:
    # little endian
    # LDRSW <Xt>, [<Xn|SP>, #<simm>]!
    return ((data[3] & 0xff) == 0xb8) and ((data[2] & 0xe0) == 0x80) and ((data[1] & 0x0c) == 0x0c)


# LDRSW (immediate) Unsigned offset
def is_ldrsw_bytes_immediate_unsigned_offset(data: bytes) -> bool:
    # little endian
    # LDRSW <Xt>, [<Xn|SP>{, #<pimm>}]
    return ((data[3] & 0xff) == 0xb9) and ((data[2] & 0xc0) == 0x80)


# LDRSW (literal)
def is_ldrsw_bytes_literal(data: bytes) -> bool:
    # little endian
    # LDRSW <Xt>, <label>
    return (data[3] & 0xff) == 0x98


# LDRSW (register)
def is_ldrsw_bytes_register(data: bytes) -> bool:
    # little endian
    # LDRSW <Xt>, [<Xn|SP>, (<Wm>|<Xm>){, <extend> {<amount>}}]
    # There are still a few cases that need to be excluded, which are omitted for efficiency.
    return ((data[3] & 0xff) == 0xb8) and ((data[2] & 0xe0) == 0xa0) and ((data[1] & 0x0c) == 0x08)


# MOV (bitmask immediate)
def is_mov_bytes_bitmask_immediate(data: bytes) -> bool:
    # little endian
    # This is an alias of ORR (immediate)
    # 32-bit: MOV <Wd|WSP>, #<imm>    is equivalent to ORR <Wd|WSP>, WZR, #<imm>
    # 64-bit: MOV <Xd|SP>, #<imm>    is equivalent to ORR <Xd|SP>, XZR, #<imm>
    # There are still a few cases that need to be excluded, which are omitted for efficiency.
    return ((data[3] & 0x7f) == 0x32) and ((data[2] & 0x80) == 0x00) and ((data[1] & 0x03) == 0x03) and ((data[0] & 0xe0) == 0xe0)


# MOV (inverted wide immediate)
def is_mov_bytes_inverted_wide_immediate(data: bytes) -> bool:
    # little endian
    # This is an alias of MOVN
    # 32-bit: MOV <Wd>, #<imm>    is equivalent to MOVN <Wd>, #<imm16>, LSL #<shift>
    # 64-bit: MOV <Xd>, #<imm>    is equivalent to MOVN <Xd>, #<imm16>, LSL #<shift>
    # There are still a few cases that need to be excluded, which are omitted for efficiency.
    return ((data[3] & 0x7f) == 0x12) and ((data[2] & 0x80) == 0x80)


# MOV (register)
def is_mov_bytes_register(data: bytes) -> bool:
    # little endian
    # This is an alias of ORR (shifted register)
    # 32-bit: MOV <Wd>, <Wm>    is equivalent to ORR <Wd>, WZR, <Wm>
    # 64-bit: MOV <Xd>, <Xm>    is equivalent to ORR <Xd>, XZR, <Xm>
    return ((data[3] & 0x7f) == 0x2a) and ((data[2] & 0xe0) == 0x00) and ((data[1] & 0xff) == 0x03) and ((data[0] & 0xe0) == 0xe0)


# MOV (to/from SP)
def is_mov_bytes_to_from_sp(data: bytes) -> bool:
    # little endian
    # This is an alias of ADD (immediate)
    # 32-bit: MOV <Wd|WSP>, <Wn|WSP>    is equivalent to ADD <Wd|WSP>, <Wn|WSP>, #0
    # 64-bit: MOV <Xd|SP>, <Xn|SP>    is equivalent to ADD <Xd|SP>, <Xn|SP>, #0
    return ((data[3] & 0x7f) == 0x11) and ((data[2] & 0xff) == 0x00) and ((data[1] & 0xfc) == 0x00)


# MOV (wide immediate)
def is_mov_bytes_wide_immediate(data: bytes) -> bool:
    # little endian
    # This is an alias of MOVZ
    # 32-bit: MOV <Wd>, #<imm>    is equivalent to MOVZ <Wd>, #<imm16>, LSL #<shift>
    # 64-bit: MOV <Xd>, #<imm>    is equivalent to MOVZ <Xd>, #<imm16>, LSL #<shift>
    # There are still a few cases that need to be excluded, which are omitted for efficiency.
    return ((data[3] & 0x7f) == 0x52) and ((data[2] & 0x80) == 0x80)


# STR (immediate) Post-index
def is_str_bytes_immediate_post_index(data: bytes) -> bool:
    # little endian
    # 32-bit: STR <Wt>, [<Xn|SP>], #<simm>
    # 64-bit: STR <Xt>, [<Xn|SP>], #<simm>
    return ((data[3] & 0xbf) == 0xb8) and ((data[2] & 0xe0) == 0x00) and ((data[1] & 0x0c) == 0x04)


# STR (immediate) Pre-index
def is_str_bytes_immediate_pre_index(data: bytes) -> bool:
    # little endian
    # 32-bit: STR <Wt>, [<Xn|SP>, #<simm>]!
    # 64-bit: STR <Xt>, [<Xn|SP>, #<simm>]!
    return ((data[3] & 0xbf) == 0xb8) and ((data[2] & 0xe0) == 0x00) and ((data[1] & 0x0c) == 0x0c)


# STR (immediate) Unsigned offset
def is_str_bytes_immediate_unsigned_offset(data: bytes) -> bool:
    # little endian
    # 32-bit: STR <Wt>, [<Xn|SP>{, #<pimm>}]
    # 64-bit: STR <Xt>, [<Xn|SP>{, #<pimm>}]
    return ((data[3] & 0xbf) == 0xb9) and ((data[2] & 0xc0) == 0x00)


# STR (register)
def is_str_bytes_register(data: bytes) -> bool:
    # little endian
    # 32-bit: STR <Wt>, [<Xn|SP>, (<Wm>|<Xm>){, <extend> {<amount>}}]
    # 64-bit: STR <Xt>, [<Xn|SP>, (<Wm>|<Xm>){, <extend> {<amount>}}]
    # There are still a few cases that need to be excluded, which are omitted for efficiency.
    return ((data[3] & 0xbf) == 0xb8) and ((data[2] & 0xe0) == 0x20) and ((data[1] & 0x0c) == 0x08)


# NOP
def is_nop_bytes(data: bytes) -> bool:
    # little endian
    return (data[3] == 0xd5) and (data[2] == 0x03) and (data[1] == 0x20) and (data[0] == 0x1f)


# decode adr/adrp and return (Rd, offset)
def decode_adr_bytes(data: bytes) -> (int, int):
    # ADR <Xd>, <label>
    # ADRP <Xd>, <label> (label = offset * 4096)
    value = int.from_bytes(data, 'little')
    rd = value & 0b11111
    immhi = (value >> 5) & 0x7ffff
    immlo = (value >> 29) & 0b11
    imm21 = (immhi << 2) | immlo
    offset = HMRegister.twos_complement_to_int(imm21, 21)
    return rd, offset


# decode b/bl and return label
def decode_b_bytes(data: bytes) -> int:
    # B <label>
    # BL <label>
    value = int.from_bytes(data, 'little')
    imm26 = value & 0x3ffffff
    label = HMRegister.twos_complement_to_int(imm26, 26) * 4
    return label


# decode ADD (immediate) and return (Rd, Rn, is_64bit, final_immediate)
def decode_add_bytes_immediate(data: bytes) -> (int, int, bool, int):
    # 32-bit: ADD <Wd|WSP>, <Wn|WSP>, #<imm>{, <shift>}
    # 64-bit: ADD <Xd|SP>, <Xn|SP>, #<imm>{, <shift>}
    # mov x8, sp - (8, 31, True, 0)
    # add sp, sp, #0x70 - (31, 31, True, 0x70)
    # add w0, w22, #0x4 - (0, 22, False, 0x4)
    is_64bit = (data[3] & 0x80) == 0x80
    value = int.from_bytes(data, 'little')
    sh = (value >> 22) & 1
    imm12 = (value >> 10) & 0xfff
    rd = value & 0b11111
    rn = (value >> 5) & 0b11111
    final_immediate = imm12 if sh == 0 else imm12 << 12
    return rd, rn, is_64bit, final_immediate


# decode ADD (shifted register) and return (Rd, Rn, Rm, is_64bit, shift, amount)
def decode_add_bytes_shifted_register(data: bytes) -> (int, int, int, bool, HMShift, int):
    # 32-bit: ADD <Wd>, <Wn>, <Wm>{, <shift> #<amount>}
    # 64-bit: ADD <Xd>, <Xn>, <Xm>{, <shift> #<amount>}
    # add x0, x20, x8 - (0, 20, 8, True, <HMShift.lsl: 0>, 0)
    # add x8, x8, x22, lsl #3 - (8, 8, 22, True, <HMShift.lsl: 0>, 3)
    # add x8, x8, x20, asr #32 - (8, 8, 20, True, <HMShift.asr: 2>, 32)
    # add w23, w8, w1 - (23, 8, 1, False, <HMShift.lsl: 0>, 0)
    # add w9, w9, w9, lsl #8 - (9, 9, 9, False, <HMShift.lsl: 0>, 8)
    # add w8, w9, w8, lsr #31 - (8, 9, 8, False, <HMShift.lsr: 1>, 31)
    # add xzr, x21, x8 - (31, 21, 8, True, <HMShift.lsl: 0>, 0)
    # add x8, xzr, x8 - (8, 31, 8, True, <HMShift.lsl: 0>, 0)
    # add x8, x21, xzr - (8, 21, 31, True, <HMShift.lsl: 0>, 0)
    is_64bit = (data[3] & 0x80) == 0x80
    value = int.from_bytes(data, 'little')
    rd = value & 0b11111
    rn = (value >> 5) & 0b11111
    rm = (value >> 16) & 0b11111
    shift_value = (value >> 22) & 0b11
    shift = HMShift(shift_value)
    imm6 = (value >> 10) & 0x3f
    return rd, rn, rm, is_64bit, shift, imm6


# decode LDR (immediate) Post-index and return (Rt, Rn, is_64bit, simm)
def decode_ldr_bytes_immediate_post_index(data: bytes) -> (int, int, bool, int):
    # 32-bit: LDR <Wt>, [<Xn|SP>], #<simm>
    # 64-bit: LDR <Xt>, [<Xn|SP>], #<simm>
    # ldr x10, [x9], #-0x18 - (10, 9, True, -0x18)
    # ldr w2, [x24], #0x4 - (2, 24, False, 0x4)
    # ldr x19, [sp], #0x20 - (19, 31, True, 32)
    # ldr xzr, [x20], #0x8 - (31, 20, True, 8)
    is_64bit = (data[3] & 0x40) == 0x40
    value = int.from_bytes(data, 'little')
    rt = value & 0b11111
    rn = (value >> 5) & 0b11111
    imm9 = (value >> 12) & 0x1ff
    simm = HMRegister.twos_complement_to_int(imm9, 9)
    return rt, rn, is_64bit, simm


# decode LDR (immediate) Pre-index and return (Rt, Rn, is_64bit, simm)
def decode_ldr_bytes_immediate_pre_index(data: bytes) -> (int, int, bool, int):
    # 32-bit: LDR <Wt>, [<Xn|SP>, #<simm>]!
    # 64-bit: LDR <Xt>, [<Xn|SP>, #<simm>]!
    # ldr x16, [x8, #-0x8]! - (16, 8, True, -8)
    # ldr w8, [x26, #0x38]! - (8, 26, False, 0x38)
    # ldr x9, [sp, #0x8]! - (9, 31, True, 8)
    # ldr wzr, [x16, #0xf6]! - (31, 16, False, 0xf6)
    is_64bit = (data[3] & 0x40) == 0x40
    value = int.from_bytes(data, 'little')
    rt = value & 0b11111
    rn = (value >> 5) & 0b11111
    imm9 = (value >> 12) & 0x1ff
    simm = HMRegister.twos_complement_to_int(imm9, 9)
    return rt, rn, is_64bit, simm


# decode LDR (immediate) Unsigned offset and return (Rt, Rn, is_64bit, pimm)
def decode_ldr_bytes_immediate_unsigned_offset(data: bytes) -> (int, int, bool, int):
    # 32-bit: LDR <Wt>, [<Xn|SP>{, #<pimm>}]
    # 64-bit: LDR <Xt>, [<Xn|SP>{, #<pimm>}]
    # ldr x2, [x8] - (2, 8, True, 0)
    # ldr w8, [x19, #0x8] - (8, 19, False, 8)
    # ldr x8, [sp, #0x98] - (8, 31, True, 0x98)
    # ldr xzr, [x8, #0x18] - (31, 8, True, 0x18)
    is_64bit = (data[3] & 0x40) == 0x40
    value = int.from_bytes(data, 'little')
    rt = value & 0b11111
    rn = (value >> 5) & 0b11111
    imm12 = (value >> 10) & 0xfff
    if is_64bit:
        pimm = imm12 * 8
    else:
        pimm = imm12 * 4
    return rt, rn, is_64bit, pimm


# decode LDR (literal), return (Rt, is_64bit, label)
def decode_ldr_bytes_literal(data: bytes) -> (int, bool, int):
    # 32-bit: LDR <Wt>, <label>
    # 64-bit: LDR <Xt>, <label>
    # 0x104d3307c: ldr w16, 0x104d33084 - (16, False, 8)
    # 0x10ec81160: ldr x20, #-0xf7c00 - (20, True, -0xf7c00)
    # 0x107c802e8: ldr wzr, 0x107c8a528 - (31, False, 41536)
    is_64bit = (data[3] & 0x40) == 0x40
    value = int.from_bytes(data, 'little')
    rt = value & 0b11111
    imm19 = (value >> 5) & 0x7ffff
    label = HMRegister.twos_complement_to_int(imm19, 19) * 4
    return rt, is_64bit, label


# decode LDR (register) and return (Rt, Rn, Rm, is_64bit, extend, amount)
def decode_ldr_bytes_register(data: bytes) -> (int, int, int, bool, HMExtendOption, int):
    # 32-bit: LDR <Wt>, [<Xn|SP>, (<Wm>|<Xm>){, <extend> {<amount>}}]
    # 64-bit: LDR <Xt>, [<Xn|SP>, (<Wm>|<Xm>){, <extend> {<amount>}}]
    # ldr x0, [x27, x8] - (0, 27, 8, True, <HMExtendOption.lsl: 3>, 0)
    # ldr w12, [x20, x9, lsl  #2] - (12, 20, 9, False, <HMExtendOption.lsl: 3>, 2)
    # ldr w2, [x8, w0, sxtw  #2] - (2, 8, 0, False, <HMExtendOption.sxtw: 6>, 2)
    # ldr x2, [x21, w8, uxtw] - (2, 21, 8, True, <HMExtendOption.uxtw: 2>, 0)
    # ldr wzr, [x19, x8] - (31, 19, 8, False, <HMExtendOption.lsl: 3>, 0)
    # ldr xzr, [sp, xzr] - (31, 31, 31, True, <HMExtendOption.lsl: 3>, 0)
    is_64bit = (data[3] & 0x40) == 0x40
    value = int.from_bytes(data, 'little')
    rt = value & 0b11111
    rn = (value >> 5) & 0b11111
    rm = (value >> 16) & 0b11111
    option = (value >> 13) & 0b111
    s = (value >> 12) & 0b1
    if is_64bit:
        amount = 0 if s == 0 else 3
    else:
        amount = 0 if s == 0 else 2

    if option == 0b10:
        extend = HMExtendOption.uxtw
    elif option == 0b11:
        extend = HMExtendOption.lsl
    elif option == 0b110:
        extend = HMExtendOption.sxtw
    elif option == 0b111:
        extend = HMExtendOption.sxtx
    else:
        extend = HMExtendOption.unknow
    return rt, rn, rm, is_64bit, extend, amount


# decode LDRSW (immediate) Post-index and return (Rt, Rn, simm)
def decode_ldrsw_bytes_immediate_post_index(data: bytes) -> (int, int, int):
    # LDRSW <Xt>, [<Xn|SP>], #<simm>
    # ldrsw x8, [x22], #0x4 - (8, 22, 4)
    # ldrsw x2, [x30], #-0x8 - (2, 30, -8)
    # ldrsw xzr, [sp], #0x1 - (31, 31, 1)
    value = int.from_bytes(data, 'little')
    rt = value & 0b11111
    rn = (value >> 5) & 0b11111
    imm9 = (value >> 12) & 0x1ff
    simm = HMRegister.twos_complement_to_int(imm9, 9)
    return rt, rn, simm


# decode LDRSW (immediate) Pre-index and return (Rt, Rn, simm)
def decode_ldrsw_bytes_immediate_pre_index(data: bytes) -> (int, int, int):
    # LDRSW <Xt>, [<Xn|SP>, #<simm>]!
    # ldrsw x20, [x24, #0x4]! - (20, 24, 4)
    # ldrsw x2, [x30, #-0x8]! - (2, 30, -8)
    # ldrsw xzr, [x20, #-0x7c]! - (31, 20, -124)
    # ldrsw x1, [sp, #0xc]! - (1, 31, 12)
    value = int.from_bytes(data, 'little')
    rt = value & 0b11111
    rn = (value >> 5) & 0b11111
    imm9 = (value >> 12) & 0x1ff
    simm = HMRegister.twos_complement_to_int(imm9, 9)
    return rt, rn, simm


# decode LDRSW (immediate) Unsigned offset and return (Rt, Rn, pimm)
def decode_ldrsw_bytes_immediate_unsigned_offset(data: bytes) -> (int, int, int):
    # LDRSW <Xt>, [<Xn|SP>{, #<pimm>}]
    # ldrsw x8, [x20] - (8, 20, 0)
    # ldrsw x23, [x8, #0xb0c] - (23, 8, 0xb0c)
    # ldrsw x8, [sp, #0x190] - (8, 31, 0x190)
    # ldrsw xzr, [x8, #0xc] - (31, 8, 12)
    value = int.from_bytes(data, 'little')
    rt = value & 0b11111
    rn = (value >> 5) & 0b11111
    imm12 = (value >> 10) & 0xfff
    pimm = imm12 * 4
    return rt, rn, pimm


# decode LDRSW (literal) and return (Rt, label)
def decode_ldrsw_bytes_literal(data: bytes) -> (int, int):
    # LDRSW <Xt>, <label>
    # 0x110e93dac: ldrsw x2, 0x110e9b194 - (2, 29672)
    # 0x110eed2d0: ldrsw xzr, 0x110ee36f4 - (31, -0x9bdc)
    value = int.from_bytes(data, 'little')
    rt = value & 0b11111
    imm19 = (value >> 5) & 0x7ffff
    label = HMRegister.twos_complement_to_int(imm19, 19) * 4
    return rt, label


# decode LDRSW (register) and return (Rt, Rn, Rm, extend, amount)
def decode_ldrsw_bytes_register(data: bytes) -> (int, int, int, HMExtendOption, int):
    # LDRSW <Xt>, [<Xn|SP>, (<Wm>|<Xm>){, <extend> {<amount>}}]
    # ldrsw x8, [x28, x8] - (8, 28, 8, <HMExtendOption.lsl: 3>, 0)
    # ldrsw x16, [x17, x16, lsl  #2] - (16, 17, 16, <HMExtendOption.lsl: 3>, 2)
    # ldrsw x8, [x8, w9, uxtw  #2] - (8, 8, 9, <HMExtendOption.uxtw: 2>, 2)
    # ldrsw  x19, [x26, w19, uxtw] - (19, 26, 19, <HMExtendOption.uxtw: 2>, 0)
    # ldrsw x28, [x24, w1, sxtw  #2] - (28, 24, 1, <HMExtendOption.sxtw: 6>, 2)
    # ldrsw  x28, [x24, w1, sxtw] - (28, 24, 1, <HMExtendOption.sxtw: 6>, 0)
    # ldrsw xzr, [sp, xzr, lsl  #2] - (31, 31, 31, <HMExtendOption.lsl: 3>, 2)
    value = int.from_bytes(data, 'little')
    rt = value & 0b11111
    rn = (value >> 5) & 0b11111
    rm = (value >> 16) & 0b11111
    option = (value >> 13) & 0b111
    s = (value >> 12) & 1
    amount = 0 if s == 0 else 2
    if option == 0b010:
        extend = HMExtendOption.uxtw
    elif option == 0b011:
        extend = HMExtendOption.lsl
    elif option == 0b110:
        extend = HMExtendOption.sxtw
    elif option == 0b111:
        extend = HMExtendOption.sxtx
    else:
        extend = HMExtendOption.unknow
    return rt, rn, rm, extend, amount


# decode MOV (inverted wide immediate) and return (rd, is_64bit, immediate)
def decode_mov_bytes_inverted_wide_immediate(data: bytes) -> (int, bool, int):
    # 32-bit: MOV <Wd>, #<imm>    is equivalent to MOVN <Wd>, #<imm16>, LSL #<shift>
    # 64-bit: MOV <Xd>, #<imm>    is equivalent to MOVN <Xd>, #<imm16>, LSL #<shift>
    # mov x8, #0x7fffffffffffffff - (8, True, 0x7fffffffffffffff)
    # mov x9, #-0x1 - (9, True, -1)
    # mov w8, #0x7f7fffff - (8, False, 0x7f7fffff)
    # mov xzr, #0x7fffffffffffffff - (31, True, 0x7fffffffffffffff)
    is_64bit = (data[3] & 0x80) == 0x80
    value = int.from_bytes(data, 'little')
    rd = value & 0b11111
    imm16 = (value >> 5) & 0xffff
    hw = (value >> 21) & 0b11
    pos = hw << 4
    result = imm16 << pos
    if is_64bit:
        result = ~result & 0xffffffffffffffff
        result = HMRegister.twos_complement_to_int(result, 64)
    else:
        result = ~result & 0xffffffff
        result = HMRegister.twos_complement_to_int(result, 32)
    return rd, is_64bit, result


# decode MOV (register) and return (rd, rm, is_64bit)
def decode_mov_bytes_register(data: bytes) -> (int, int, bool):
    # 32-bit: MOV <Wd>, <Wm>    is equivalent to ORR <Wd>, WZR, <Wm>
    # 64-bit: MOV <Xd>, <Xm>    is equivalent to ORR <Xd>, XZR, <Xm>
    # mov x20, x0 - (20, 0, True)
    # mov w2, w8 - (2, 8, False)
    # mov x0, xzr - (0, 31, True)
    # mov xzr, xzr - (31, 31, True)
    is_64bit = (data[3] & 0x80) == 0x80
    value = int.from_bytes(data, 'little')
    rd = value & 0b11111
    rm = (value >> 16) & 0b11111
    return rd, rm, is_64bit


# decode MOV (to/from SP) and return (rd, rn, is_64bit)
def decode_mov_bytes_to_from_sp(data: bytes) -> (int, int, bool):
    # 32-bit: MOV <Wd|WSP>, <Wn|WSP>    is equivalent to ADD <Wd|WSP>, <Wn|WSP>, #0
    # 64-bit: MOV <Xd|SP>, <Xn|SP>    is equivalent to ADD <Xd|SP>, <Xn|SP>, #0
    # mov x9, sp - (9, 31, True)
    # mov sp, x20 - (31, 20, True)
    # add w17, w1, #0x0 - (17, 1, False)
    is_64bit = (data[3] & 0x80) == 0x80
    value = int.from_bytes(data, 'little')
    rd = value & 0b11111
    rn = (value >> 5) & 0b11111
    return rd, rn, is_64bit


# decode MOV (wide immediate) and return (rd, is_64bit, immediate)
def decode_mov_bytes_wide_immediate(data: bytes) -> (int, bool, int):
    # 32-bit: MOV <Wd>, #<imm>    is equivalent to MOVZ <Wd>, #<imm16>, LSL #<shift>
    # 64-bit: MOV <Xd>, #<imm>    is equivalent to MOVZ <Xd>, #<imm16>, LSL #<shift>
    # mov w8, #0x1 - (8, False, 1)
    # mov x0, #0x2 - (0, True, 2)
    # mov w10, #-0x80000000 - (10, False, -0x80000000)
    # mov x9, #-0x8000000000000000 - (9, True, -0x8000000000000000)
    # mov xzr, #0x1 - (31, True, 1)
    is_64bit = (data[3] & 0x80) == 0x80
    value = int.from_bytes(data, 'little')
    rd = value & 0b11111
    imm16 = (value >> 5) & 0xffff
    hw = (value >> 21) & 0b11
    pos = hw << 4
    result = imm16 << pos
    bit_width = 64 if is_64bit else 32
    result = HMRegister.twos_complement_to_int(result, bit_width)
    return rd, is_64bit, result


# decode STR (immediate) Post-index and return (rt, rn, is_64bit, simm)
def decode_str_bytes_immediate_post_index(data: bytes) -> (int, int, bool, int):
    # 32-bit: STR <Wt>, [<Xn|SP>], #<simm>
    # 64-bit: STR <Xt>, [<Xn|SP>], #<simm>
    # str x8, [x22], #0x8 - (8, 22, True, 0x8)
    # str w0, [x21], #0x4 - (0, 21, False, 0x4)
    # str x11, [x10], #-0x8 - (11, 10, True, -8)
    # str wzr, [x22], #0x8 - (31, 22, False, 0x8)
    # str x21, [sp], #0x10 - (21, 31, True, 0x10)
    is_64bit = (data[3] & 0x40) == 0x40
    value = int.from_bytes(data, 'little')
    rt = value & 0b11111
    rn = (value >> 5) & 0b11111
    imm9 = (value >> 12) & 0x1ff
    simm = HMRegister.twos_complement_to_int(imm9, 9)
    return rt, rn, is_64bit, simm


# decode STR (immediate) Pre-index and return (rt, rn, is_64bit, simm)
def decode_str_bytes_immediate_pre_index(data: bytes) -> (int, int, bool, int):
    # 32-bit: STR <Wt>, [<Xn|SP>, #<simm>]!
    # 64-bit: STR <Xt>, [<Xn|SP>, #<simm>]!
    # str wzr, [sp, #-0x10]! - (31, 31, False, -0x10)
    # str xzr, [x23, #0x60]! - (31, 23, True, 0x60)
    # str w8, [x1, #0x60]! - (8, 1, False, 0x60)
    is_64bit = (data[3] & 0x40) == 0x40
    value = int.from_bytes(data, 'little')
    rt = value & 0b11111
    rn = (value >> 5) & 0b11111
    imm9 = (value >> 12) & 0x1ff
    simm = HMRegister.twos_complement_to_int(imm9, 9)
    return rt, rn, is_64bit, simm


# decode STR (immediate) Unsigned offset and return (rt, rn, is_64bit, pimm)
def decode_str_bytes_immediate_unsigned_offset(data: bytes) -> (int, int, bool, int):
    # 32-bit: STR <Wt>, [<Xn|SP>{, #<pimm>}]
    # 64-bit: STR <Xt>, [<Xn|SP>{, #<pimm>}]
    # str xzr, [sp, #0x58] - (31, 31, True, 0x58)
    # str x8, [sp] - (8, 31, True, 0x0)
    # str w0, [x19, #0x560] - (0, 19, False, 0x560)
    # str wzr, [x8, #0x50] - (31, 8, False, 0x50)
    is_64bit = (data[3] & 0x40) == 0x40
    value = int.from_bytes(data, 'little')
    rt = value & 0b11111
    rn = (value >> 5) & 0b11111
    imm12 = (value >> 10) & 0xfff
    if is_64bit:
        pimm = imm12 * 8
    else:
        pimm = imm12 * 4
    return rt, rn, is_64bit, pimm


# decode STR (register) and return (Rt, Rn, Rm, is_64bit, extend, amount)
def decode_str_bytes_register(data: bytes) -> (int, int, int, bool, HMExtendOption, int):
    # 32-bit: STR <Wt>, [<Xn|SP>, (<Wm>|<Xm>){, <extend> {<amount>}}]
    # 64-bit: STR <Xt>, [<Xn|SP>, (<Wm>|<Xm>){, <extend> {<amount>}}]
    # str x0, [x20, x8] - (0, 20, 8, True, <HMExtendOption.lsl: 3>, 0)
    # str w9, [x0, x8] - (9, 0, 8, False, <HMExtendOption.lsl: 3>, 0)
    # str x9, [x8, w20, uxtw  #3] - (9, 8, 20, True, <HMExtendOption.uxtw: 2>, 3)
    # str x0, [x20, w27, sxtw] - (0, 20, 27, True, <HMExtendOption.sxtw: 6>, 0)
    is_64bit = (data[3] & 0x40) == 0x40
    value = int.from_bytes(data, 'little')
    rt = value & 0b11111
    rn = (value >> 5) & 0b11111
    rm = (value >> 16) & 0b11111
    s = (value >> 12) & 1
    option = (value >> 13) & 0b111
    if is_64bit:
        amount = 0 if s == 0 else 3
    else:
        amount = 0 if s == 0 else 2
    if option == 0b10:
        extend = HMExtendOption.uxtw
    elif option == 0b11:
        extend = HMExtendOption.lsl
    elif option == 0b110:
        extend = HMExtendOption.sxtw
    elif option == 0b111:
        extend = HMExtendOption.sxtx
    else:
        extend = HMExtendOption.unknow
    return rt, rn, rm, is_64bit, extend, amount


def logical_shift_right(raw_value: int, amount: int, bit_width: int) -> int:
    raw_value &= (1 << bit_width) - 1
    result = raw_value >> amount
    result &= (1 << (bit_width - amount)) - 1
    return result


# uxtw
def unsigned_extend_word(raw_value: int) -> int:
    raw_value = raw_value & 0xffffffff
    return raw_value


# sxtw
def signed_extend_word(raw_value: int) -> int:
    raw_value = raw_value & 0xffffffff
    sign_bit = (raw_value >> 31) & 1
    if sign_bit == 1:
        result = raw_value | 0xffffffff00000000
    else:
        result = raw_value
    return result


def get_description_of_section(section: lldb.SBSection) -> str:
    stream = lldb.SBStream()
    section.GetDescription(stream)
    description = stream.GetData()
    description_list = description.split(')', 1)
    if len(description_list) == 2:
        return description_list[1].strip()

    return description


def get_module_name(module: lldb.SBModule) -> str:
    return os.path.basename(module.GetFileSpec().GetFilename())


def record_adrp_logic(exe_ctx: lldb.SBExecutionContext, adrp_data: bytes, adrp_instruction_load_address: int, address_target_dic: Dict[int, int], address_ldr_dic: Dict[int, int]) -> None:
    # Analyze the specified instructions after adrp in sequence, and analyze up to 5 instructions.
    register_list = HMRegisterList()
    target = exe_ctx.GetTarget()

    # Calculate and save the value of adr/adrp instruction
    adrp_rd, adrp_offset = decode_adr_bytes(adrp_data)
    if is_adr_bytes(adrp_data):
        adrp_result = adrp_instruction_load_address + adrp_offset
    else:
        adrp_result, _ = HMCalculationHelper.calculate_adrp_result_with_immediate_and_pc_address(adrp_offset, adrp_instruction_load_address)
    register_list.set_value(adrp_rd, adrp_result, True)

    # Analyze the specified instructions after adr/adrp
    instruction_count = 5

    address: lldb.SBAddress = lldb.SBAddress(adrp_instruction_load_address + 4, target)
    error = lldb.SBError()
    data: bytes = target.ReadMemory(address, 4 * instruction_count, error)
    if not error.Success():
        HM.DPrint(error)
        return
    for i in range(0, len(data), 4):
        instruction_data = data[i:i+4]
        instruction_load_address = adrp_instruction_load_address + 4 + i
        # add
        if is_add_bytes_immediate(instruction_data):
            rd, rn, is_64bit, final_immediate = decode_add_bytes_immediate(instruction_data)
            if not register_list.has_value(rn):
                break
            rd_value = register_list.get_value(rn, is_64bit) + final_immediate
            register_list.set_value(rd, rd_value, is_64bit)
            address_target_dic[instruction_load_address] = register_list.get_value(rd, is_64bit)
        elif is_add_bytes_shifted_register(instruction_data):
            rd, rn, rm, is_64bit, shift, amount = decode_add_bytes_shifted_register(instruction_data)
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
                    rm_value_shift = logical_shift_right(rm_raw_value, amount, bit_width)
                elif shift == HMShift.asr:
                    rm_value_shift = (rm_raw_value >> amount) & ((1 << bit_width) - 1)
                else:  # HMShift.unknow
                    break
                rd_raw_value = rn_raw_value + rm_value_shift

            register_list.set_raw_value(rd, rd_raw_value, is_64bit)
            address_target_dic[instruction_load_address] = HMRegister.twos_complement_to_int(rd_raw_value, bit_width)

        # ldr
        elif is_ldr_bytes_immediate_post_index(instruction_data):
            rt, rn, is_64bit, simm = decode_ldr_bytes_immediate_post_index(instruction_data)
            if not register_list.has_value(rn):
                break
            rn_value = register_list.get_value(rn, True)
            load_address = rn_value
            ldr_result = HM.load_address_value(exe_ctx, load_address)
            if rt != 31:  # xzr
                register_list.set_raw_value(rt, ldr_result, is_64bit)
            rn_value += simm
            register_list.set_value(rn, rn_value, True)
            # The ldr instruction records the loading address, and records the result address in memory
            bit_width = 64 if is_64bit else 32
            address_target_dic[instruction_load_address] = load_address
            address_ldr_dic[instruction_load_address] = HMRegister.twos_complement_to_int(ldr_result, bit_width)
        elif is_ldr_bytes_immediate_pre_index(instruction_data):
            rt, rn, is_64bit, simm = decode_ldr_bytes_immediate_pre_index(instruction_data)
            if not register_list.has_value(rn):
                break
            rn_value = register_list.get_value(rn, True)
            rn_value += simm
            register_list.set_value(rn, rn_value, True)
            ldr_result = HM.load_address_value(exe_ctx, rn_value)
            if rt != 31:  # xzr
                register_list.set_raw_value(rt, ldr_result, is_64bit)

            bit_width = 64 if is_64bit else 32
            address_target_dic[instruction_load_address] = rn_value
            address_ldr_dic[instruction_load_address] = HMRegister.twos_complement_to_int(ldr_result, bit_width)
        elif is_ldr_bytes_immediate_unsigned_offset(instruction_data):
            rt, rn, is_64bit, pimm = decode_ldr_bytes_immediate_unsigned_offset(instruction_data)
            if not register_list.has_value(rn):
                break
            rn_value = register_list.get_value(rn, True)
            load_address = rn_value + pimm
            ldr_result = HM.load_address_value(exe_ctx, load_address)
            if rt != 31:  # xzr
                register_list.set_raw_value(rt, ldr_result, is_64bit)

            bit_width = 64 if is_64bit else 32
            address_target_dic[instruction_load_address] = load_address
            address_ldr_dic[instruction_load_address] = HMRegister.twos_complement_to_int(ldr_result, bit_width)
        elif is_ldr_bytes_literal(instruction_data):
            rt, is_64bit, label = decode_ldr_bytes_literal(instruction_data)
            load_address = label + instruction_load_address
            ldr_result = HM.load_address_value(exe_ctx, load_address)
            if rt != 31:  # xzr
                register_list.set_raw_value(rt, ldr_result, is_64bit)

            bit_width = 64 if is_64bit else 32
            address_target_dic[instruction_load_address] = load_address
            address_ldr_dic[instruction_load_address] = HMRegister.twos_complement_to_int(ldr_result, bit_width)
        elif is_ldr_bytes_register(instruction_data):
            rt, rn, rm, is_64bit, extend, amount = decode_ldr_bytes_register(instruction_data)
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
                temp = unsigned_extend_word(rm_raw_value) << amount
            elif extend == HMExtendOption.lsl:
                rm_raw_value = 0 if rm == 31 else register_list.get_raw_value(rm, True)
                temp = rm_raw_value << amount
            elif extend == HMExtendOption.sxtw:
                rm_raw_value = 0 if rm == 31 else register_list.get_value(rm, False)
                temp = signed_extend_word(rm_raw_value) << amount
            else:
                break
            load_address = HMRegister.twos_complement_to_int(rn_raw_value + temp, 64)
            ldr_result = HM.load_address_value(exe_ctx, load_address)
            register_list.set_raw_value(rt, ldr_result, is_64bit)

            bit_width = 64 if is_64bit else 32
            address_target_dic[instruction_load_address] = load_address
            address_ldr_dic[instruction_load_address] = HMRegister.twos_complement_to_int(ldr_result, bit_width)

        # ldrsw
        elif is_ldrsw_bytes_immediate_post_index(instruction_data):
            rt, rn, simm = decode_ldrsw_bytes_immediate_post_index(instruction_data)
            if not register_list.has_value(rn):
                break
            rn_value = register_list.get_value(rn, True)
            load_address = rn_value
            ldrsw_result = HM.load_address_value_signed_word(exe_ctx, load_address)
            if rt != 31:  # xzr
                register_list.set_raw_value(rt, ldrsw_result, True)
            rn_value += simm
            register_list.set_value(rn, rn_value, True)

            address_target_dic[instruction_load_address] = load_address
            address_ldr_dic[instruction_load_address] = HMRegister.twos_complement_to_int(ldrsw_result, 64)

        elif is_ldrsw_bytes_immediate_pre_index(instruction_data):
            rt, rn, simm = decode_ldrsw_bytes_immediate_pre_index(instruction_data)
            if not register_list.has_value(rn):
                break
            rn_value = register_list.get_value(rn, True)
            rn_value += simm
            register_list.set_value(rn, rn_value, True)
            ldrsw_result = HM.load_address_value_signed_word(exe_ctx, rn_value)
            if rt != 31:  # xzr
                register_list.set_raw_value(rt, ldrsw_result, True)

            address_target_dic[instruction_load_address] = rn_value
            address_ldr_dic[instruction_load_address] = HMRegister.twos_complement_to_int(ldrsw_result, 64)
        elif is_ldrsw_bytes_immediate_unsigned_offset(instruction_data):
            rt, rn, pimm = decode_ldrsw_bytes_immediate_unsigned_offset(instruction_data)
            if not register_list.has_value(rn):
                break
            rn_value = register_list.get_value(rn, True)
            load_address = rn_value + pimm
            ldrsw_result = HM.load_address_value_signed_word(exe_ctx, load_address)
            if rt != 31:  # xzr
                register_list.set_raw_value(rt, ldrsw_result, True)

            address_target_dic[instruction_load_address] = load_address
            address_ldr_dic[instruction_load_address] = HMRegister.twos_complement_to_int(ldrsw_result, 64)
        elif is_ldrsw_bytes_register(instruction_data):
            rt, rn, rm, extend, amount = decode_ldrsw_bytes_register(instruction_data)
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
                temp = unsigned_extend_word(rm_raw_value) << amount
            elif extend == HMExtendOption.lsl:
                rm_raw_value = 0 if rm == 31 else register_list.get_raw_value(rm, True)
                temp = rm_raw_value << amount
            elif extend == HMExtendOption.sxtw:
                rm_raw_value = 0 if rm == 31 else register_list.get_value(rm, False)
                temp = signed_extend_word(rm_raw_value) << amount
            else:
                break
            load_address = HMRegister.twos_complement_to_int(rn_raw_value + temp, 64)
            ldrsw_result = HM.load_address_value_signed_word(exe_ctx, load_address)
            register_list.set_raw_value(rt, ldrsw_result, True)

            address_target_dic[instruction_load_address] = load_address
            address_ldr_dic[instruction_load_address] = HMRegister.twos_complement_to_int(ldrsw_result, 64)

        # mov
        elif is_mov_bytes_inverted_wide_immediate(instruction_data):
            rd, is_64bit, immediate = decode_mov_bytes_inverted_wide_immediate(instruction_data)
            if rd == 31:  # xzr
                address_target_dic[instruction_load_address] = immediate
                continue
            register_list.set_value(rd, immediate, is_64bit)
            address_target_dic[instruction_load_address] = register_list.get_value(rd, is_64bit)
        elif is_mov_bytes_register(instruction_data):
            rd, rm, is_64bit = decode_mov_bytes_register(instruction_data)
            if rd == 31:  # xzr
                continue
            if rm != 31 and (not register_list.has_value(rm)):
                break
            rm_raw_value = 0 if rm == 31 else register_list.get_raw_value(rm, is_64bit)
            register_list.set_raw_value(rd, rm_raw_value, is_64bit)
            bit_width = 64 if is_64bit else 32
            address_target_dic[instruction_load_address] = HMRegister.twos_complement_to_int(rm_raw_value, bit_width)
        elif is_mov_bytes_to_from_sp(instruction_data):
            rd, rn, is_64bit = decode_mov_bytes_to_from_sp(instruction_data)
            if not register_list.has_value(rn):
                break
            rn_raw_value = register_list.get_raw_value(rn, is_64bit)
            register_list.set_raw_value(rd, rn_raw_value, is_64bit)
            bit_width = 64 if is_64bit else 32
            address_target_dic[instruction_load_address] = HMRegister.twos_complement_to_int(rn_raw_value, bit_width)
        elif is_mov_bytes_wide_immediate(instruction_data):
            rd, is_64bit, immediate = decode_mov_bytes_wide_immediate(instruction_data)
            if rd == 31:  # xzr
                address_target_dic[instruction_load_address] = immediate
                continue
            register_list.set_value(rd, immediate, is_64bit)
            address_target_dic[instruction_load_address] = register_list.get_value(rd, is_64bit)

        # str
        elif is_str_bytes_immediate_post_index(instruction_data):
            rt, rn, is_64bit, simm = decode_str_bytes_immediate_post_index(instruction_data)
            if not register_list.has_value(rn):
                break
            rn_value = register_list.get_value(rn, True)
            load_address = rn_value
            rn_value += simm
            register_list.set_value(rn, rn_value, is_64bit)
            address_target_dic[instruction_load_address] = load_address
        elif is_str_bytes_immediate_pre_index(instruction_data):
            rt, rn, is_64bit, simm = decode_str_bytes_immediate_pre_index(instruction_data)
            if not register_list.has_value(rn):
                break
            rn_value = register_list.get_value(rn, True)
            rn_value += simm
            register_list.set_value(rn, rn_value, is_64bit)
            address_target_dic[instruction_load_address] = rn_value
        elif is_str_bytes_immediate_unsigned_offset(instruction_data):
            rt, rn, is_64bit, pimm = decode_str_bytes_immediate_unsigned_offset(instruction_data)
            if not register_list.has_value(rn):
                continue
            rn_value = register_list.get_value(rn, True)
            load_address = rn_value + pimm
            address_target_dic[instruction_load_address] = load_address
        elif is_str_bytes_register(instruction_data):
            rt, rn, rm, is_64bit, extend, amount = decode_str_bytes_register(instruction_data)
            if extend == HMExtendOption.unknow or extend == HMExtendOption.sxtx:
                break
            if not register_list.has_value(rn):
                continue
            if rm != 31 and (not register_list.has_value(rm)):
                continue
            rn_raw_value = register_list.get_raw_value(rn, True)
            if extend == HMExtendOption.uxtw:
                rm_raw_value = 0 if rm == 31 else register_list.get_raw_value(rm, False)
                temp = unsigned_extend_word(rm_raw_value) << amount
            elif extend == HMExtendOption.lsl:
                rm_raw_value = 0 if rm == 31 else register_list.get_raw_value(rm, True)
                temp = rm_raw_value << amount
            elif extend == HMExtendOption.sxtw:
                rm_raw_value = 0 if rm == 31 else register_list.get_value(rm, False)
                temp = signed_extend_word(rm_raw_value) << amount
            else:
                continue
            load_address = HMRegister.twos_complement_to_int(rn_raw_value + temp, 64)

            address_target_dic[instruction_load_address] = load_address
            continue

        # nop
        elif is_nop_bytes(instruction_data):
            continue
        else:
            break


    # If the next instruction is nop, record the current adr/adrp result
    next_instruction_data = data[0:4]
    if is_nop_bytes(next_instruction_data):
        address_target_dic[adrp_instruction_load_address] = adrp_result



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


def analyze_str(exe_ctx: lldb.SBExecutionContext, str_instruction: lldb.SBInstruction, register_dic: Dict[str, int], address_target_dic: Dict[int, int]) -> None:
    # It always returns true if the register is not modified.
    target = exe_ctx.GetTarget()
    operand_tuple: Tuple[bool, str, str, str] = resolve_ldr_operands(str_instruction.GetOperands(target))
    if not operand_tuple[0]:
        return True
    if operand_tuple[2] not in register_dic:
        return True

    if operand_tuple[3] in register_dic:
        op3_value = register_dic[operand_tuple[3]]
    else:
        is_valid_value, immediate_operand_value = HM.int_value_from_string(operand_tuple[3].lstrip("#"))
        if not is_valid_value:
            return True
        op3_value = immediate_operand_value

    save_address: int = register_dic[operand_tuple[2]] + op3_value
    # The str instruction records the saving address
    address_target_dic[str_instruction.GetAddress().GetLoadAddress(target)] = save_address
    return True


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

