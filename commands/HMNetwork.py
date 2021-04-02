# The MIT License (MIT)
#
# Copyright (c) 2021 Huimao Chen
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
import optparse
import shlex


def __lldb_init_module(debugger, internal_dict):
    debugger.HandleCommand('command script add -f HMNetwork.request request -h "Print http/https request."')


def request(debugger, command, exe_ctx, result, internal_dict):
    """
    Syntax:
        request

    Examples:
        (lldb) request

    This command is implemented in HMNetwork.py
    """

    registerProtocol()
    HM.processContinue()


def registerProtocol():
    protocolName = "HMURLProtocolObserver"
    if HM.existClass(protocolName):
        return

    # Register class
    HM.DPrint(f"Register {protocolName}...")

    classValue = HM.allocateClass(protocolName, "NSURLProtocol")
    HM.registerClass(classValue.GetValue())

    # Add methods
    HM.DPrint(f"Add methods to {protocolName}...")

    canInitWithRequestIMPValue = makeCanInitWithRequestIMP()
    if not HM.judgeSBValueHasValue(canInitWithRequestIMPValue):
        return
    HM.addClassMethod(protocolName, "canInitWithRequest:", canInitWithRequestIMPValue.GetValue(), "B@:@")

    HM.DPrint(f"Register {protocolName} done!")

    # register NSURLProtocol
    registerClassExp = f"[NSURLProtocol registerClass:(Class){classValue.GetValue()}]"
    HM.evaluateExpressionValue(registerClassExp)


def makeCanInitWithRequestIMP() -> lldb.SBValue:
    command_script = '''
        BOOL (^IMPBlock)(id, NSURLRequest *) = ^BOOL(id classSelf, NSURLRequest *request) {
            printf("[HMLLDB]: %s\\n", (char *)[[request debugDescription] UTF8String]);
            return NO;
        };
        imp_implementationWithBlock(IMPBlock);
    '''
    return HM.evaluateExpressionValue(expression=command_script)


