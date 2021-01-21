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
import HMSandboxViewController


def __lldb_init_module(debugger, internal_dict):
    debugger.HandleCommand('command script add -f HMSandbox.sandbox sandbox -h "Presenting a view controller of sandbox browser."')


def sandbox(debugger, command, exe_ctx, result, internal_dict):
    """
    Syntax:
        sandbox

    Examples:
        (lldb) sandbox

    Summary:
        Presenting a view controller of sandbox browser.

    This command is implemented in HMSandbox.py
    """

    HMSandboxViewController.register()

    command_script = f'''
        UIViewController *vc = (UIViewController *)[[NSClassFromString(@"{HMSandboxViewController.gClassName}") alloc] init];
        UINavigationController *nv = [[UINavigationController alloc] initWithRootViewController:vc];
        ((void (*)(id, SEL, long)) objc_msgSend)((id)nv, @selector(setModalPresentationStyle:), 0); // UIModalPresentationFullScreen
        UIViewController *rootVC = [UIApplication sharedApplication].keyWindow.rootViewController;
        if ([rootVC presentedViewController]) {{
            [[rootVC presentedViewController] presentViewController:nv animated:YES completion:nil];
        }} else {{
            [rootVC presentViewController:nv animated:YES completion:nil];
        }}
    '''
    HM.evaluateExpressionValue(command_script)

    HM.processContinue()

