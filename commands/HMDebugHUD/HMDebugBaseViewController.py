""" File: HMDebugBaseViewController.py

Implementation of HMDebugBaseViewController class.

"""

import lldb
import HMLLDBHelpers as HM
import HMLLDBClassInfo
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

        (IMP)imp_implementationWithBlock(IMPBlock);

     '''

    return HM.evaluateExpressionValue(command_script)
