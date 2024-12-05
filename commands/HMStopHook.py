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
import re
from typing import Callable, List, Optional

import HMLLDBClassInfo
import HMLLDBHelpers as HM


# In the breakpoint's "ScriptCallbackFunction", adding another breakpoint and calling the "SetScriptCallbackFunction" function will cause an error.
# This class solves this problem by using the stop-hook method.
class HMAddressCallbackStopHook:
    idx: int = 0
    target_address: int = 0
    bp_id: int = 0
    callback: Callable[[lldb.SBFrame, lldb.SBBreakpointLocation, lldb.SBStructuredData, dict], bool]

    @staticmethod
    def add_address_callback_stop_hook(target: lldb.SBTarget, address: int, bp_id: int, callback: Callable[[lldb.SBFrame, lldb.SBBreakpointLocation, lldb.SBStructuredData, dict], bool]):
        return_object = lldb.SBCommandReturnObject()
        target.GetDebugger().GetCommandInterpreter().HandleCommand(f"target stop-hook add -P HMStopHook.HMAddressCallbackStopHook", return_object)

        if return_object.GetErrorSize() > 0:
            HM.DPrint(f"Adding stop-hook failed:{return_object.GetError()}")
            return

        match = re.search(r'#(\d+)', return_object.GetOutput())
        if match:
            idx = match.group(1)
            global g_address_callback_stop_hook_instance
            g_address_callback_stop_hook_instance.idx = idx
            g_address_callback_stop_hook_instance.target_address = address
            g_address_callback_stop_hook_instance.bp_id = bp_id
            g_address_callback_stop_hook_instance.callback = callback
            g_address_callback_stop_hook_instance = None

            global g_stop_hook_target_address_list
            g_stop_hook_target_address_list.append(address)
        else:
            HM.DPrint(f"Unable to find stop-hook id. Output:{return_object.GetOutput()}")

    def __init__(self, target, extra_args, internal_dict):
        global g_address_callback_stop_hook_instance
        g_address_callback_stop_hook_instance = self

    def handle_stop(self, exe_ctx, stream) -> bool:
        # Get breakpoint info
        bp = exe_ctx.GetTarget().FindBreakpointByID(self.bp_id)
        string_list = lldb.SBStringList()
        bp.GetCommandLineCommands(string_list)
        command_line_commands = HMLLDBClassInfo.get_string_from_SBStringList(string_list)
        bp_loc: lldb.SBBreakpointLocation = None
        if bp.GetNumLocations() > 0:
            bp_loc = bp.GetLocationAtIndex(0)

        # Try calling "SetScriptCallbackFunction", but it may fail
        if bp.IsValid() and len(command_line_commands) == 0:
            # Set script to breakpoint.
            bp.SetScriptCallbackFunction(f"{self.callback.__module__}.{self.callback.__name__}")

        # Deleting the hook will report an error, so use "disabled"
        current_pc_address = exe_ctx.GetFrame().GetPC()
        if current_pc_address == self.target_address or len(command_line_commands) > 0:
            # If current_pc_address == self.target_address, it is assumed that the call to "SetScriptCallbackFunction" is successful.
            return_object = lldb.SBCommandReturnObject()
            exe_ctx.GetTarget().GetDebugger().GetCommandInterpreter().HandleCommand(
                f"target stop-hook disable {self.idx}", return_object)

        # If the addresses are equal, the callback set by SetScriptCallbackFunction will not be executed immediately and needs to be simulated once
        if current_pc_address == self.target_address:
            should_stop = self.callback(exe_ctx.GetFrame(), bp_loc, None, None)
            return should_stop

        # It is necessary to judge whether the breakpoint is hit normally or hit in the "handle_stop" function
        global g_stop_hook_target_address_list
        if current_pc_address in g_stop_hook_target_address_list:
            return False
        else:
            return True


g_address_callback_stop_hook_instance: Optional[HMAddressCallbackStopHook] = None
g_stop_hook_target_address_list: List[int] = []

