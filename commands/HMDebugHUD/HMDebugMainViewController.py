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
import HMDebugBaseViewController
import HMDebugInfoViewController
import HMExpressionPrefix
import HMInspectViewController
import HMLLDBClassInfo
import HMLLDBHelpers as HM
import HMProgressHUD
import HMSandboxViewController


gClassName = "HMDebugMainViewController"


def register() -> None:

    if HM.is_existing_class(gClassName):
        return

    HMDebugBaseViewController.register()

    # Register class
    HMProgressHUD.show(f"Register {gClassName}...")
    HM.DPrint(f"Register {gClassName}...")

    classValue = HM.allocate_class(gClassName, HMDebugBaseViewController.gClassName)
    HM.register_class(classValue.GetValue())

    # Add methods
    HM.DPrint(f"Add methods to {gClassName}...")
    presentIMPValue = makePresentIMP()
    if not HM.is_SBValue_has_value(presentIMPValue):
        HMProgressHUD.hide()
        return
    HM.add_class_method(gClassName, "present", presentIMPValue.GetValue(), "@@:")

    viewDidLoadIMPValue = makeViewDidLoadIMP()
    if not HM.is_SBValue_has_value(viewDidLoadIMPValue):
        HMProgressHUD.hide()
        return
    HM.add_instance_method(gClassName, "viewDidLoad", viewDidLoadIMPValue.GetValue(), "v@:")

    dismissSelfIMPValue = makeDismissSelfIMP()
    if not HM.is_SBValue_has_value(dismissSelfIMPValue):
        HMProgressHUD.hide()
        return
    HM.add_instance_method(gClassName, "dismissSelf", dismissSelfIMPValue.GetValue(), "v@:")

    # Methods related to tableView.
    HM.DPrint(f"Add methods to {gClassName}......")
    if not addTableViewMethods():
        HMProgressHUD.hide()
        return

    # Methods related to features.
    HM.DPrint(f"Add methods to {gClassName}.........")
    if not addFeatureMethods():
        HMProgressHUD.hide()
        return

    HM.DPrint(f"Register {gClassName} done!")
    HMProgressHUD.hide()


def makePresentIMP() -> lldb.SBValue:
    command_script = f'''
        UIViewController * (^presentBlock)(id) = ^UIViewController *(id classSelf) {{
            UIViewController *vc = (UIViewController *)[[NSClassFromString(@"{gClassName}") alloc] init];
            UINavigationController *nv = [[UINavigationController alloc] initWithRootViewController:vc];
            ((void (*)(id, SEL, long)) objc_msgSend)((id)nv, @selector(setModalPresentationStyle:), 0); // UIModalPresentationFullScreen
            if ([nv.navigationBar respondsToSelector:@selector(setScrollEdgeAppearance:)]) {{
                NSObject *barAppearance = (NSObject *)[[NSClassFromString(@"UINavigationBarAppearance") alloc] init];
                ((void (*)(id, SEL, id)) objc_msgSend)((id)barAppearance, @selector(setBackgroundColor:), (id)[UIColor whiteColor]);
                (void)[nv.navigationBar setScrollEdgeAppearance:barAppearance];
                (void)[nv.navigationBar setStandardAppearance:barAppearance];
            }}
            UIViewController *rootVC = [UIApplication sharedApplication].keyWindow.rootViewController;
            if ([rootVC presentedViewController]) {{
                [[rootVC presentedViewController] presentViewController:nv animated:YES completion:nil];
            }} else {{
                [rootVC presentViewController:nv animated:YES completion:nil];
            }}
            return vc;
        }};

        imp_implementationWithBlock(presentBlock);
     '''

    return HM.evaluate_expression_value(expression=command_script, prefix=HMExpressionPrefix.gPrefix)


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
            vc.navigationItem.leftBarButtonItem = [[UIBarButtonItem alloc] initWithBarButtonSystemItem:UIBarButtonSystemItemDone target:vc action:@selector(dismissSelf)];
            vc.navigationItem.title = @"Tool";
            
            // tableView
            UITableView *tv = [[UITableView alloc] init];
            tv.frame = vc.view.bounds;
            tv.delegate = (id)vc;
            tv.dataSource = (id)vc;
            tv.rowHeight = 50;
            tv.tableFooterView = [[UIView alloc] init];
            if ([tv respondsToSelector:@selector(setContentInsetAdjustmentBehavior:)]) {{
                // UIScrollViewContentInsetAdjustmentAutomatic
                ((void (*)(id, SEL, long)) objc_msgSend)((id)tv, @selector(setContentInsetAdjustmentBehavior:), 0);
            }}
            [vc.view addSubview:tv];
        }};
        
        imp_implementationWithBlock(IMPBlock);

     '''
    return HM.evaluate_expression_value(expression=command_script, prefix=HMExpressionPrefix.gPrefix)


def makeDismissSelfIMP() -> lldb.SBValue:
    command_script = '''
        void (^dismissSelfBlock)(UIViewController *) = ^(UIViewController *vc) {
            [vc.navigationController dismissViewControllerAnimated:NO completion:nil];
        };
        
        imp_implementationWithBlock(dismissSelfBlock);

     '''
    return HM.evaluate_expression_value(expression=command_script, prefix=HMExpressionPrefix.gPrefix)


def addTableViewMethods() -> bool:
    global gClassName

    numberOfRowsInSectionIMPValue = makeNumberOfRowsInSectionIMP()
    if not HM.is_SBValue_has_value(numberOfRowsInSectionIMPValue):
        return False
    HM.add_instance_method(gClassName, "tableView:numberOfRowsInSection:", numberOfRowsInSectionIMPValue.GetValue(), "q@:@q")

    cellForRowAtIndexPathIMPValue = makeCellForRowAtIndexPathIMP()
    if not HM.is_SBValue_has_value(cellForRowAtIndexPathIMPValue):
        return False
    HM.add_instance_method(gClassName, "tableView:cellForRowAtIndexPath:", cellForRowAtIndexPathIMPValue.GetValue(), "@@:@@")

    didSelectRowAtIndexPathIMPValue = makeDidSelectRowAtIndexPathIMP()
    if not HM.is_SBValue_has_value(didSelectRowAtIndexPathIMPValue):
        return False
    HM.add_instance_method(gClassName, "tableView:didSelectRowAtIndexPath:", didSelectRowAtIndexPathIMPValue.GetValue(), "v@:@@")

    return True


def makeNumberOfRowsInSectionIMP() -> lldb.SBValue:
    command_script = '''
        long (^IMPBlock)(UIViewController *, UITableView *, long) = ^long(UIViewController *vc, UITableView *tv, long section) {
            return 3;
        };
        imp_implementationWithBlock(IMPBlock);    
    '''

    return HM.evaluate_expression_value(expression=command_script, prefix=HMExpressionPrefix.gPrefix)


def makeCellForRowAtIndexPathIMP() -> lldb.SBValue:
    command_script = '''
        UITableViewCell * (^IMPBlock)(UIViewController *, UITableView *, NSIndexPath *) = ^UITableViewCell *(UIViewController *vc, UITableView *tv, NSIndexPath *indexPath) {
            NSString * reuseIdentifier = @"Cell";
            UITableViewCell *cell = [tv dequeueReusableCellWithIdentifier:reuseIdentifier];
            if (cell == nil) {
                // UITableViewCellStyleDefault
                cell = [UITableViewCell alloc];
                cell = ((UITableViewCell * (*)(id, SEL, long, id)) objc_msgSend)((id)cell, @selector(initWithStyle:reuseIdentifier:), 0, reuseIdentifier);
                // UITableViewCellSelectionStyleNone
                ((void (*)(id, SEL, long)) objc_msgSend)((id)cell, @selector(setSelectionStyle:), 0);
                // UITableViewCellAccessoryDisclosureIndicator
                ((void (*)(id, SEL, long)) objc_msgSend)((id)cell, @selector(setAccessoryType:), 1);
            }
            
            long row = indexPath.row;
            if (row == 0) {
                cell.textLabel.text = @"App and system information";
            } else if (row == 1) {
                cell.textLabel.text = @"Sandbox";
            } else if (row == 2) {
                cell.textLabel.text = @"Inspect view";
            }
            return cell;
        };
        
        imp_implementationWithBlock(IMPBlock);    
    '''

    return HM.evaluate_expression_value(expression=command_script, prefix=HMExpressionPrefix.gPrefix)


def makeDidSelectRowAtIndexPathIMP() -> lldb.SBValue:
    command_script = '''
        void (^IMPBlock)(UIViewController *, UITableView *, NSIndexPath *) = ^(UIViewController *vc, UITableView *tv, NSIndexPath *indexPath) {
            long row = indexPath.row;
            if (row == 0) {
                (void)[vc performSelector:@selector(selectedAPPInfo)];
            } else if (row == 1) {
                (void)[vc performSelector:@selector(selectedSandbox)];
            } else if (row == 2) {
                (void)[vc performSelector:@selector(selectedInspectView)];
            }
        };

        imp_implementationWithBlock(IMPBlock);    
    '''

    return HM.evaluate_expression_value(expression=command_script, prefix=HMExpressionPrefix.gPrefix)


def addFeatureMethods() -> bool:
    global gClassName

    selectedAPPInfoIMPValue = makeSelectedAPPInfoIMP()
    if not HM.is_SBValue_has_value(selectedAPPInfoIMPValue):
        return False
    HM.add_instance_method(gClassName, "selectedAPPInfo", selectedAPPInfoIMPValue.GetValue(), "v@:")

    selectedSandboxIMPValue = makeSelectedSandboxIMP()
    if not HM.is_SBValue_has_value(selectedSandboxIMPValue):
        return False
    HM.add_instance_method(gClassName, "selectedSandbox", selectedSandboxIMPValue.GetValue(), "v@:")

    selectedInspectViewIMPValue = makeSelectedInspectViewIMP()
    if not HM.is_SBValue_has_value(selectedInspectViewIMPValue):
        return False
    HM.add_instance_method(gClassName, "selectedInspectView", selectedInspectViewIMPValue.GetValue(), "v@:")

    HM.DPrint("Add breakpoints to hook method...")
    HM.add_one_shot_breakpoint_in_imp(selectedAPPInfoIMPValue, "HMDebugMainViewController.selectedAPPInfoBreakPointHandler", "HMDebugMainViewController_selectedAPPInfo_Breakpoint")
    HM.add_one_shot_breakpoint_in_imp(selectedSandboxIMPValue, "HMDebugMainViewController.selectedSandboxBreakPointHandler", "HMDebugMainViewController_selectedSandbox_Breakpoint")
    HM.add_one_shot_breakpoint_in_imp(selectedInspectViewIMPValue, "HMDebugMainViewController.selectedInspectViewBreakPointHandler", "HMDebugMainViewController_selectedInspectView_Breakpoint")

    return True


def makeSelectedAPPInfoIMP() -> lldb.SBValue:
    command_script = f'''
        void (^IMPBlock)(UIViewController *) = ^(UIViewController *vc) {{
            Class objClass = (Class)objc_lookUpClass("{HMDebugInfoViewController.g_class_name}");
            UIViewController * objVC = (UIViewController *)[[objClass alloc] init];
            [vc.navigationController pushViewController:objVC animated:YES];
        }};

        imp_implementationWithBlock(IMPBlock);    
    '''

    return HM.evaluate_expression_value(expression=command_script, prefix=HMExpressionPrefix.gPrefix)


def makeSelectedSandboxIMP() -> lldb.SBValue:
    command_script = f'''
        void (^IMPBlock)(UIViewController *) = ^(UIViewController *vc) {{
            Class objClass = (Class)objc_lookUpClass("{HMSandboxViewController.gClassName}");
            UIViewController * objVC = (UIViewController *)[[objClass alloc] init];
            [vc.navigationController pushViewController:objVC animated:YES];
        }};

        imp_implementationWithBlock(IMPBlock);    
    '''

    return HM.evaluate_expression_value(expression=command_script, prefix=HMExpressionPrefix.gPrefix)


def makeSelectedInspectViewIMP() -> lldb.SBValue:
    command_script = f'''
        void (^IMPBlock)(UIViewController *) = ^(UIViewController *vc) {{
            [vc.navigationController dismissViewControllerAnimated:NO completion:nil];
            
            Class objClass = (Class)objc_lookUpClass("{HMInspectViewController.gClassName}");
            if ((BOOL)[(Class)objClass respondsToSelector:@selector(start)]) {{
                (void)[objClass performSelector:@selector(start)];
            }}
        }};

        imp_implementationWithBlock(IMPBlock);    
    '''

    return HM.evaluate_expression_value(expression=command_script, prefix=HMExpressionPrefix.gPrefix)


def selectedAPPInfoBreakPointHandler(frame, bp_loc, extra_args, internal_dict) -> bool:
    HMDebugInfoViewController.register()
    HM.process_continue()
    return True


def selectedSandboxBreakPointHandler(frame, bp_loc, extra_args, internal_dict) -> bool:
    HMSandboxViewController.register()
    HM.process_continue()
    return True


def selectedInspectViewBreakPointHandler(frame, bp_loc, extra_args, internal_dict) -> bool:
    HMInspectViewController.register()
    HM.process_continue()
    return True
