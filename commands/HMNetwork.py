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

gProtocolName = "HMLLDBURLProtocolObserver"
gCustomizedSELString = "HMLLDBProtocolClasses"


def __lldb_init_module(debugger, internal_dict):
    debugger.HandleCommand('command script add -f HMNetwork.request request -h "Print http/https request automatically."')


def request(debugger, command, exe_ctx, result, internal_dict):
    """
    Syntax:
        request

    Examples:
        (lldb) request

    Notice:
        Except WKWebView

    This command is implemented in HMNetwork.py
    """

    global gProtocolName
    if HM.existClass(gProtocolName):
        return

    registerProtocol()
    swizzlingProtocolClasses()
    HM.processContinue()


def registerProtocol():
    global gProtocolName
    if HM.existClass(gProtocolName):
        return

    # Register class
    HM.DPrint(f"Register {gProtocolName}...")

    classValue = HM.allocateClass(gProtocolName, "NSURLProtocol")
    HM.registerClass(classValue.GetValue())

    # Add methods
    HM.DPrint(f"Add methods to {gProtocolName}...")

    canInitWithRequestIMPValue = makeCanInitWithRequestIMP()
    if not HM.judgeSBValueHasValue(canInitWithRequestIMPValue):
        return
    HM.addClassMethod(gProtocolName, "canInitWithRequest:", canInitWithRequestIMPValue.GetValue(), "B@:@")

    HM.DPrint(f"Register {gProtocolName} done!")

    # register NSURLProtocol
    registerClassExp = f"[NSURLProtocol registerClass:(Class){classValue.GetValue()}]"
    HM.evaluateExpressionValue(registerClassExp)


def makeCanInitWithRequestIMP() -> lldb.SBValue:
    command_script = '''
        BOOL (^IMPBlock)(id, NSURLRequest *) = ^BOOL(id classSelf, NSURLRequest *request) {
            printf("\\n[HMLLDB]: %s\\n", (char *)[[request debugDescription] UTF8String]);
            return NO;
        };
        imp_implementationWithBlock(IMPBlock);
    '''
    return HM.evaluateExpressionValue(expression=command_script)


def swizzlingProtocolClasses():
    global gCustomizedSELString

    # add customized method
    clsName = "__NSCFURLSessionConfiguration"
    if not HM.existClass(clsName):
        clsName = "NSURLSessionConfiguration"

    HMLLDBProtocolClassesIMPValue = makeHMLLDBProtocolClassesIMP()
    if not HM.judgeSBValueHasValue(HMLLDBProtocolClassesIMPValue):
        return
    HM.addInstanceMethod(clsName, gCustomizedSELString, HMLLDBProtocolClassesIMPValue.GetValue(), "@@:")

    # exchange implementation
    command_script = f'''
        Class cls = NSClassFromString(@"{clsName}");
        Method m1 = class_getInstanceMethod(cls, NSSelectorFromString(@"protocolClasses"));
        Method m2 = class_getInstanceMethod(cls, NSSelectorFromString(@"{gCustomizedSELString}"));
        method_exchangeImplementations(m1, m2);
    '''
    HM.evaluateExpressionValue(command_script)


def makeHMLLDBProtocolClassesIMP() -> lldb.SBValue:
    global gProtocolName
    command_script = f'''
        NSArray *(^IMPBlock)(id) = ^NSArray *(id conf) {{
            NSMutableArray *classes = (NSMutableArray *)[[conf performSelector:NSSelectorFromString(@"{gCustomizedSELString}")] mutableCopy];
            BOOL isContain = NO;
            for (Class cls in classes) {{
                if ((BOOL)[cls isKindOfClass:[{gProtocolName} class]]) {{
                    isContain = YES;
                    break;
                }}
            }}
            if (!isContain) {{
                [classes insertObject:[{gProtocolName} class] atIndex:0];
            }}
            return classes;
        }};
        imp_implementationWithBlock(IMPBlock);
    '''
    return HM.evaluateExpressionValue(expression=command_script)