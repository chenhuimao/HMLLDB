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
import HMLLDBHelpers as HM
import HMLLDBClassInfo
from datetime import datetime


def __lldb_init_module(debugger, internal_dict):
    debugger.HandleCommand('command script add -f HMStep.trace_function tracefunction -h "Trace functions"')


def trace_function(debugger, command, exe_ctx, result, internal_dict):
    """
    Syntax:
        tracefunction

    Examples:
        (lldb) tracefunction

    This command is implemented in HMStep.py
    """
    debugger.HandleCommand('thread step-scripted -C HMStep.TraceFunctionStep')


class TraceFunctionStep:

    def __init__(self, thread_plan, dict):
        HM.DPrint("==========Begin========================================================")
        self.start_time = datetime.now().strftime("%H:%M:%S")
        self.thread_plan = thread_plan

        stream = lldb.SBStream()
        self.thread_plan.GetThread().GetFrameAtIndex(0).GetPCAddress().GetDescription(stream)
        self.last_function: str = stream.GetData()
        print(self.last_function)  # first address

    def explains_stop(self, event: lldb.SBEvent) -> bool:
        stream = lldb.SBStream()
        self.thread_plan.GetThread().GetFrameAtIndex(0).GetPCAddress().GetDescription(stream)
        function_str = stream.GetData().split(" + ")[0]
        if function_str not in self.last_function:
            print(self.last_function)
        self.last_function = stream.GetData()
        return True

    def should_stop(self, event: lldb.SBEvent) -> bool:
        if self.thread_plan.GetThread().GetStopReason() != lldb.eStopReasonTrace:
            self.thread_plan.SetPlanComplete(True)
            stream = lldb.SBStream()
            self.thread_plan.GetThread().GetFrameAtIndex(0).GetPCAddress().GetDescription(stream)
            print(stream.GetData())  # current address

            HM.DPrint("==========End========================================================")
            HM.DPrint(f"start time = {self.start_time}")
            end_time = datetime.now().strftime("%H:%M:%S")
            HM.DPrint(f"end time = {end_time}")
            return True
        else:
            return False

    def should_step(self) -> bool:
        return True
