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
import os
import HMLLDBHelpers as HM


def __lldb_init_module(debugger, internal_dict):
    debugger.HandleCommand('command script add -f HMSymbol.autodsym autodsym -h "Add a debug symbol file to the target\'s modules automatically."')


def autodsym(debugger, command, exe_ctx, result, internal_dict):
    """
    Syntax:
        autodsym

    Examples:
        (lldb) autodsym

    This command is implemented in HMSymbol.py
    """

    module_uuid = debugger.GetSelectedTarget().GetModuleAtIndex(0).GetUUIDString()
    HM.DPrint(f"module uuid:{module_uuid}")

    dsym_path = execute_system_command(f"mdfind \"com_apple_xcode_dsym_uuids == {module_uuid}\"")

    if not dsym_path.startswith("/"):
        HM.DPrint(f"Could not find the dSYM path of uuid:{module_uuid}.")
        HM.DPrint("Please execute this command: target symbol add /path/to/dSYM")
        return

    debugger.HandleCommand(f"target symbol add {dsym_path}")
    HM.DPrint(f"autodsym done!")


def execute_system_command(cmd) -> str:
    with os.popen(cmd) as fp:
        bf = fp.buffer.read()
        try:
            result = bf.decode().strip()
        except UnicodeDecodeError:
            result = bf.decode('utf8').strip()
    return result
