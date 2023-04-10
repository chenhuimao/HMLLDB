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
from typing import List
import HMLLDBHelpers as HM


def __lldb_init_module(debugger, internal_dict):
    debugger.HandleCommand('command script add -f HMInstructionsHelper.adrp adrp -h "Get the execution result of the adrp instruction."')


def adrp(debugger, command, exe_ctx, result, internal_dict):
    """
    Syntax:
        adrp <immediate> <pc address>

    Examples:
        (lldb) adrp 348413 0x189aef040
        (lldb) adrp 0x550fd 0x189aef040

    This command is implemented in HMInstructionsHelper.py
    """

    command_args: List[str] = command.split(" ")
    if len(command_args) != 2:
        HM.DPrint("Error input, this command requires two integer parameters.")
        return

    try:
        immediate_value: int = int_value_from_string(command_args[0])
        pc_address_value: int = int_value_from_string(command_args[1])
    except:
        HM.DPrint("Error input, this command requires two integer parameters.")
        return

    immediate_value_temp = immediate_value * 4096
    pc_address_value_temp = pc_address_value - pc_address_value % 4096

    result_value: int = immediate_value_temp + pc_address_value_temp
    HM.DPrint(f"result: {hex(result_value)}, {result_value}")


def int_value_from_string(integer_str: str) -> int:
    if integer_str.startswith("0x"):
        return int(integer_str, 16)

    return int(integer_str)

