# The MIT License (MIT)
#
# Copyright (c) 2020 Huimao Chen
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

import HMLLDBClassInfo
import HMLLDBHelpers as HM
import optparse
import shlex


def __lldb_init_module(debugger, internal_dict):
    debugger.HandleCommand('command script add -f HMLifeCycle.print_lifecycle plifecycle -h "Print life cycle of UIViewController."')


def print_lifecycle(debugger, command, exe_ctx, result, internal_dict):
    """
    Syntax:
        plifecycle [-i/--ignore_system_classes]

    Options:
        --ignore_system_classes/-i; Ignore the system generated UIViewController classes

    Notice:
        You should use plifecycle in symbolic breakpoint(UIViewController's life cycle) for easier control.
        This command can ignore the system generated UIViewController classes, Otherwise you may use the following command directly.

        Method A: expression -l objc -O -- [[$arg1 description] stringByAppendingString:@"  dealloc/viewDidAppear:/..."]
        Method B: expression -l objc -O -- @import UIKit; [[NSString alloc] initWithFormat:@"%@  %s", (id)$arg1, (char *)$arg2]
        Method C: Add symbolic breakpoint of "UIApplicationMain" with command "expression -l objc -O -- @import UIKit",
                  then add symbolic breakpoint(UIViewController's life cycle) with command "expression -l objc -O -- [[NSString alloc] initWithFormat:@"%@  %s", (id)$arg1, (char *)$arg2]"

    This command is implemented in HMLifeCycle.py
    """

    command_args = shlex.split(command)
    parser = generate_option_parser()
    try:
        # options: optparse.Values
        # args: list
        (options, args) = parser.parse_args(command_args)
    except:
        result.SetError(parser.usage)
        return

    current_registers: lldb.SBValueList = exe_ctx.GetFrame().GetRegisters()
    general_purpose_registers: lldb.SBValue = current_registers.GetFirstValueByName("General Purpose Registers")
    children_num = general_purpose_registers.GetNumChildren()
    self_value: lldb.SBValue = 0
    selector_value: lldb.SBValue = 0
    for i in range(children_num):
        reg_value = general_purpose_registers.GetChildAtIndex(i)
        reg_name = reg_value.GetName()
        if reg_name == "x0" or reg_name == "rdi":
            self_value = reg_value
        if reg_name == "x1" or reg_name == "rsi":
            selector_value = reg_value
        if self_value and selector_value:
            break

    self_description = self_value.GetObjectDescription()

    ignore = False
    if options.ignore_system_classes:
        ignore_classes = ["UIAlertController",
                          "_UIAlertControllerTextFieldViewController",
                          "UIInputWindowController",
                          "UICompatibilityInputViewController",
                          "UIKeyboardCandidateGridCollectionViewController",
                          "UISystemKeyboardDockController",
                          "_UIRemoteInputViewController",
                          "UIApplicationRotationFollowingController",
                          "UISystemInputAssistantViewController",
                          "UIPredictionViewController",
                          "UICandidateViewController",
                          "_SFAppPasswordSavingViewController",
                          "SFPasswordSavingRemoteViewController"]

        for class_name in ignore_classes:
            if class_name in self_description:
                ignore = True
                break

    if not ignore:
        # address = lldb.SBAddress(selector_value.GetValueAsUnsigned(), exe_ctx.GetTarget())
        # error = lldb.SBError()
        # content: bytes = exe_ctx.GetTarget().ReadMemory(address, 128, error)
        # idx = content.index(b"\x00")
        # selector_description: str = content[:idx].decode("UTF-8")

        return_object = lldb.SBCommandReturnObject()
        debugger.GetCommandInterpreter().HandleCommand(f"memory read -f s {selector_value.GetValue()}", return_object)
        selector_description = return_object.GetOutput().split("\"")[1]
        HM.DPrint(self_description + '  ' + selector_description + '\n')


def generate_option_parser() -> optparse.OptionParser:
    usage = "usage: plifecycle [-i/--ignore_system_classes]"
    parser = optparse.OptionParser(usage=usage, prog="plifecycle")

    parser.add_option("-i", "--ignore_system_classes",
                      action="store_true",
                      default=False,
                      dest="ignore_system_classes",
                      help="Ignore system classes")

    return parser
