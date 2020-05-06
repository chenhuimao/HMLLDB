""" File: HMDebugMainViewController.py

Implementation of HMDebugMainViewController class.

"""

import lldb
import HMLLDBHelpers as HM
import HMLLDBClassInfo
import HMDebugInfoViewController
import HMProgressHUD


gClassName = "HMDebugMainViewController"


def register() -> None:

    if HM.existClass(gClassName):
        return

    # Register class
    HMProgressHUD.show("Register {arg0}...".format(arg0=gClassName))
    classValue = HM.allocateClass(gClassName, "UIViewController")
    HM.registerClass(classValue.GetValue())

    # Add methods
    HMProgressHUD.show("Add methods to {arg0}...".format(arg0=gClassName))
    presentIMPValue = makePresentIMP()
    if not HM.judgeSBValueHasValue(presentIMPValue):
        HMProgressHUD.hide()
        return
    HM.addClassMethod(gClassName, "present", presentIMPValue.GetValue(), "@@:")

    viewDidLoadIMPValue = makeViewDidLoadIMP()
    if not HM.judgeSBValueHasValue(viewDidLoadIMPValue):
        HMProgressHUD.hide()
        return
    HM.addInstanceMethod(gClassName, "viewDidLoad", viewDidLoadIMPValue.GetValue(), "v@:")

    dismissSelfIMPValue = makeDismissSelfIMP()
    if not HM.judgeSBValueHasValue(dismissSelfIMPValue):
        HMProgressHUD.hide()
        return
    HM.addInstanceMethod(gClassName, "dismissSelf", dismissSelfIMPValue.GetValue(), "v@:")

    # Methods related to tableView.
    HMProgressHUD.show("Add methods to {arg0}......".format(arg0=gClassName))
    if not addTableViewMethods():
        HMProgressHUD.hide()
        return

    # Methods related to features.
    HMProgressHUD.show("Add methods to {arg0}.........".format(arg0=gClassName))
    if not addFeatureMethods():
        HMProgressHUD.hide()
        return

    HMProgressHUD.show("Register {arg0} done!".format(arg0=gClassName))
    HMProgressHUD.hide()


def makePresentIMP() -> lldb.SBValue:
    command_script = '''
        UIViewController * (^presentBlock)(id) = ^UIViewController *(id classSelf) {{
            UIViewController *vc = (UIViewController *)[[NSClassFromString(@"{arg0}") alloc] init];
            UINavigationController *nv = [[UINavigationController alloc] initWithRootViewController:vc];
            nv.modalPresentationStyle = (UIModalPresentationStyle)0;
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
            
            // tableView
            UITableView *tv = [[UITableView alloc] init];
            tv.frame = vc.view.bounds;
            tv.delegate = vc;
            tv.dataSource = vc;
            tv.rowHeight = 50;
            tv.tableFooterView = [[UIView alloc] init];
            [vc.view addSubview:tv];
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


def addTableViewMethods() -> bool:
    global gClassName

    numberOfRowsInSectionIMPValue = makeNumberOfRowsInSectionIMP()
    if not HM.judgeSBValueHasValue(numberOfRowsInSectionIMPValue):
        return False
    HM.addInstanceMethod(gClassName, "tableView:numberOfRowsInSection:", numberOfRowsInSectionIMPValue.GetValue(), "l@:@l")

    cellForRowAtIndexPathIMPValue = makeCellForRowAtIndexPathIMP()
    if not HM.judgeSBValueHasValue(cellForRowAtIndexPathIMPValue):
        return False
    HM.addInstanceMethod(gClassName, "tableView:cellForRowAtIndexPath:", cellForRowAtIndexPathIMPValue.GetValue(), "@@:@@")

    didSelectRowAtIndexPathIMPValue = makeDidSelectRowAtIndexPathIMP()
    if not HM.judgeSBValueHasValue(didSelectRowAtIndexPathIMPValue):
        return False
    HM.addInstanceMethod(gClassName, "tableView:didSelectRowAtIndexPath:", didSelectRowAtIndexPathIMPValue.GetValue(), "v@:@@")

    return True


def makeNumberOfRowsInSectionIMP() -> lldb.SBValue:
    command_script = '''
        long (^IMPBlock)(UIViewController *, UITableView *, long) = ^long(UIViewController *vc, UITableView *tv, long section) {
            return 1;
        };
        (IMP)imp_implementationWithBlock(IMPBlock);    
    '''

    return HM.evaluateExpressionValue(command_script)


def makeCellForRowAtIndexPathIMP() -> lldb.SBValue:
    command_script = '''
        UITableViewCell * (^IMPBlock)(UIViewController *, UITableView *, NSIndexPath *) = ^UITableViewCell *(UIViewController *vc, UITableView *tv, NSIndexPath *indexPath) {
            NSString * reuseIdentifier = @"Cell";
            UITableViewCell *cell = [tv dequeueReusableCellWithIdentifier:reuseIdentifier];
            if (cell == nil) {
                cell = [[UITableViewCell alloc] initWithStyle:(UITableViewCellStyle)0 reuseIdentifier:reuseIdentifier];
                cell.selectionStyle = (UITableViewCellSelectionStyle)0;
                cell.accessoryType = (UITableViewCellAccessoryType)1;
            }
            
            long row = indexPath.row;
            if (row == 0) {
                cell.textLabel.text = @"APP and system information";
            }
            return cell;
        };
        
        (IMP)imp_implementationWithBlock(IMPBlock);    
    '''

    return HM.evaluateExpressionValue(command_script)


def makeDidSelectRowAtIndexPathIMP() -> lldb.SBValue:
    command_script = '''
        void (^IMPBlock)(UIViewController *, UITableView *, NSIndexPath *) = ^(UIViewController *vc, UITableView *tv, NSIndexPath *indexPath) {
            long row = indexPath.row;
            if (row == 0) {
                (void)[vc performSelector:@selector(selectedAPPInfo)];
            }
        };

        (IMP)imp_implementationWithBlock(IMPBlock);    
    '''

    return HM.evaluateExpressionValue(command_script)


def addFeatureMethods() -> bool:
    global gClassName

    selectedAPPInfoIMPValue = makeSelectedAPPInfoIMP()
    if not HM.judgeSBValueHasValue(selectedAPPInfoIMPValue):
        return False
    HM.addInstanceMethod(gClassName, "selectedAPPInfo", selectedAPPInfoIMPValue.GetValue(), "v@:")

    HM.DPrint("Add breakpoints to hook method...")
    HM.addOneShotBreakPointInIMP(selectedAPPInfoIMPValue, "HMDebugMainViewController.selectedAPPInfoBreakPointHandler", "HMDebugMainViewController_selectedAPPInfo_Breakpoint")

    return True


def makeSelectedAPPInfoIMP() -> lldb.SBValue:
    command_script = '''
        void (^IMPBlock)(UIViewController *) = ^(UIViewController *vc) {
            Class objClass = (Class)objc_getClass("HMDebugInfoViewController");
            UIViewController * objVC = (UIViewController *)[[objClass alloc] init];
            [vc.navigationController pushViewController:objVC animated:YES];
        };

        (IMP)imp_implementationWithBlock(IMPBlock);    
    '''

    return HM.evaluateExpressionValue(command_script)


def selectedAPPInfoBreakPointHandler(frame, bp_loc, internal_dict) -> bool:
    HMDebugInfoViewController.register()
    HM.processContinue()
    return True
