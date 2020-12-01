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

import lldb
import HMLLDBHelpers as HM
import HMLLDBClassInfo
import HMInspectViewController


def __lldb_init_module(debugger, internal_dict):
    debugger.HandleCommand('command script add -f HMInspectView.inspect inspect -h "Inspect UIView"')


def inspect(debugger, command, exe_ctx, result, internal_dict):
    """
    Syntax:
        inspect

    Examples:
        (lldb) inspect

    Summary:
        Inspect UIView.
        The "infoView" is based on https://github.com/QMUI/LookinServer

    This command is implemented in HMInspectView.py
    """

    HMInspectViewController.register()

    command_script = f'''
        Class objClass = (Class)objc_lookUpClass("{HMInspectViewController.gClassName}");
        if ((BOOL)[(Class)objClass respondsToSelector:@selector(start)]) {{
            (void)[objClass performSelector:@selector(start)];
        }}
    '''
    HM.evaluateExpressionValue(command_script)

    HM.processContinue()

