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
from typing import Dict, List
import optparse
import os
import shlex
import HMCalculationHelper
import HMLLDBClassInfo
import HMLLDBHelpers as HM


g_image_address_target_dic: Dict[str, Dict[int, int]] = {}


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
        1.This command is expensive to scan large modules. For example, it takes 100 seconds to scan UIKitCore.
        2.Currently, the query is only based on the b/bl instruction. You should consider the "stub" function and "island" function when using it.

    This command is implemented in HMReference.py
    """

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
    global g_image_address_target_dic

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

        # Scan module
        g_image_address_target_dic[image_name] = {}
        section_num = target_module.GetNumSections()
        for i in range(section_num):
            section = target_module.GetSectionAtIndex(i)
            scan_section_code(exe_ctx, image_name, section)

    # Traverse records and print matching results
    address_target_dic: Dict[int, int] = g_image_address_target_dic[image_name]
    # HM.DPrint(f"address_target_dic length:{len(address_target_dic)}")
    HM.DPrint("These are the scan results:")
    result_count = 0
    for key, value in address_target_dic.items():
        if value == target_address_int:
            result_count += 1
            result_address: str = hex(key)
            print(f"{result_address}: {HM.get_image_lookup_summary_from_address(result_address)}")

    HM.DPrint(f"Reference count:{result_count}")

    # Print time when scanning moudle for the first time
    if is_first_scan_target_image:
        stop_time = datetime.now().strftime("%H:%M:%S")
        HM.DPrint(f"Start time: {start_time}")
        HM.DPrint(f"Stop time: {stop_time}")


def scan_section_code(exe_ctx: lldb.SBExecutionContext, module_name: str, section: lldb.SBSection) -> None:
    target: lldb.SBTarget = exe_ctx.GetTarget()
    section_type_int = section.GetSectionType()
    if section_type_int == lldb.eSectionTypeContainer:
        sub_sections_num = section.GetNumSubSections()
        for i in range(sub_sections_num):
            sub_section = section.GetSubSectionAtIndex(i)
            scan_section_code(exe_ctx, module_name, sub_section)
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
            instruction_analysis(exe_ctx, module_name, current_address, current_address + span)
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
            instruction_analysis(exe_ctx, module_name, current_address, section_load_address_end)


def instruction_analysis(exe_ctx: lldb.SBExecutionContext, module_name: str, start_address: int, end_address: int) -> None:
    target: lldb.SBTarget = exe_ctx.GetTarget()
    instruction_count = int((end_address - start_address) / 4)
    address: lldb.SBAddress = lldb.SBAddress(start_address, target)
    instruction_list: lldb.SBInstructionList = target.ReadInstructions(address, instruction_count)
    global g_image_address_target_dic
    address_target_dic: Dict[int, int] = g_image_address_target_dic[module_name]
    for i in range(instruction_count):
        instruction: lldb.SBInstruction = instruction_list.GetInstructionAtIndex(i)
        # Record all b/bl logic
        if instruction.GetMnemonic(target) in ['b', 'bl']:
            target_address_str = instruction.GetOperands(target)
            is_valid_address, target_address_int = HM.int_value_from_string(target_address_str)
            if is_valid_address:
                address_target_dic[instruction.GetAddress().GetLoadAddress(target)] = target_address_int


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


