""" File: HMDebugMainViewController.py

Implementation of HMDebugMainViewController class.

"""

import lldb
import HMLLDBHelpers as HM
import HMLLDBClassInfo


gClassName = "HMDebugMainViewController"


def registerHMDebugMainViewController() -> None:

    if HM.existClass(gClassName):
        return

    # Register class
    HM.DPrint("Register {arg0}...".format(arg0=gClassName))
    classValue = HM.allocateClass(gClassName, "UIViewController")
    HM.registerClass(classValue.GetValue())

    # Add methods
    HM.DPrint("Add methods to {arg0}...".format(arg0=gClassName))
    presentIMPValue = makePresentIMP()
    if not HM.judgeSBValueHasValue(presentIMPValue):
        return
    HM.addClassMethod(gClassName, "present", presentIMPValue.GetValue(), "@@:")

    viewDidLoadIMPValue = makeViewDidLoadIMP()
    if not HM.judgeSBValueHasValue(viewDidLoadIMPValue):
        return
    HM.addInstanceMethod(gClassName, "viewDidLoad", viewDidLoadIMPValue.GetValue(), "v@:")

    dismissSelfIMPValue = makeDismissSelfIMP()
    if not HM.judgeSBValueHasValue(dismissSelfIMPValue):
        return
    HM.addInstanceMethod(gClassName, "dismissSelf", dismissSelfIMPValue.GetValue(), "v@:")

    HM.DPrint("Register {arg0} done!".format(arg0=gClassName))


def makePresentIMP() -> lldb.SBValue:
    command_script = '''
        UIViewController * (^presentBlock)(id) = ^UIViewController *(id classSelf) {{
            UIViewController *vc = (UIViewController *)[[NSClassFromString(@"{arg0}") alloc] init];
            UINavigationController *nv = [[UINavigationController alloc] initWithRootViewController:vc];
            nv.modalPresentationStyle = (UIModalPresentationStyle)UIModalPresentationFullScreen;
            [[UIApplication sharedApplication].keyWindow.rootViewController presentViewController:nv animated:YES completion:nil];
            
             return vc;
         }};

         (IMP)imp_implementationWithBlock(presentBlock);

     '''.format(arg0=gClassName)

    return HM.evaluateExpressionValue(command_script)


def makeViewDidLoadIMP() -> lldb.SBValue:
    command_script = '''
        void (^viewDidLoadBlock)(UIViewController *) = ^(UIViewController *vc) {
            struct objc_super superInfo = {
                .receiver = vc,
                .super_class = (Class)class_getSuperclass((Class)[vc class])
            };
    
            ((void (*)(struct objc_super *, SEL))objc_msgSendSuper)(&superInfo, @selector(viewDidLoad));
            
            (void)[vc.view setBackgroundColor:[UIColor whiteColor]];
            vc.navigationItem.leftBarButtonItem = [[UIBarButtonItem alloc] initWithBarButtonSystemItem:UIBarButtonSystemItemDone target:vc action:@selector(dismissSelf)];
            vc.navigationItem.title = @"Tool";
            
            UILabel *remindLab = [[UILabel alloc] initWithFrame:(CGRect){10, 100, 0, 0}];
            remindLab.text = @"New tools are being developed...";
            remindLab.textColor = [UIColor blackColor];
            [remindLab sizeToFit];
            [vc.view addSubview:remindLab];
        };
        
        (IMP)imp_implementationWithBlock(viewDidLoadBlock);

     '''
    return HM.evaluateExpressionValue(command_script)


def makeDismissSelfIMP() -> lldb.SBValue:
    command_script = '''
        void (^dismissSelfBlock)(UIViewController *) = ^(UIViewController *vc) {
            [vc.navigationController dismissViewControllerAnimated:NO completion:nil];
        };
        
        (IMP)imp_implementationWithBlock(dismissSelfBlock);

     '''
    return HM.evaluateExpressionValue(command_script)
