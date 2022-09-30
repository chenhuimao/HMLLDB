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
import HMExpressionPrefix
import HMLLDBClassInfo
import HMLLDBHelpers as HM
import HMProgressHUD


gClassName = "HMDebugBaseViewController"


def register() -> None:
    if HM.existClass(gClassName):
        return

    # Register class
    HMProgressHUD.show(f"Register {gClassName}...")
    HM.DPrint(f"Register {gClassName}...")

    classValue = HM.allocateClass(gClassName, "UIViewController")
    HM.registerClass(classValue.GetValue())

    # Add methods
    HM.DPrint(f"Add methods to {gClassName}...")
    viewDidLoadIMPValue = makeViewDidLoadIMP()
    if not HM.judgeSBValueHasValue(viewDidLoadIMPValue):
        return
    HM.addInstanceMethod(gClassName, "viewDidLoad", viewDidLoadIMPValue.GetValue(), "v@:")

    HM.DPrint(f"Register {gClassName} done!")


def makeViewDidLoadIMP() -> lldb.SBValue:
    command_script = f'''
        void (^IMPBlock)(UIViewController *) = ^(UIViewController *vc) {{
            Class cls = objc_lookUpClass("{gClassName}");
            struct objc_super superInfo = {{
                .receiver = vc,
                .super_class = (Class)class_getSuperclass((Class)cls)
            }};

            ((void (*)(struct objc_super *, SEL))objc_msgSendSuper)(&superInfo, @selector(viewDidLoad));

            // property initialize
            (void)[vc.view setBackgroundColor:[UIColor whiteColor]];
            (void)[vc setExtendedLayoutIncludesOpaqueBars:YES];
            (void)[vc setAutomaticallyAdjustsScrollViewInsets:YES];
            
            if ([vc respondsToSelector:@selector(setOverrideUserInterfaceStyle:)]) {{
                [vc setOverrideUserInterfaceStyle:UIUserInterfaceStyleLight];
            }}
        }};

        imp_implementationWithBlock(IMPBlock);

     '''

    return HM.evaluateExpressionValue(expression=command_script, prefix=HMExpressionPrefix.gPrefix)
