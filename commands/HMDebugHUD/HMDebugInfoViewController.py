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
import sys
import HMDebugBaseViewController
import HMEnvironment
import HMExpressionPrefix
import HMLLDBClassInfo
import HMLLDBHelpers as HM
import HMProgressHUD


g_class_name = "HMDebugInfoViewController"


def register() -> None:
    global g_class_name

    if HM.is_existing_class(g_class_name):
        return

    # Register class
    HMProgressHUD.show(f"Register {g_class_name}...")
    HM.DPrint(f"Register {g_class_name}...")

    class_value = HM.allocate_class(g_class_name, HMDebugBaseViewController.gClassName)
    HM.add_ivar(class_value.GetValue(), "_leftTextArray", "NSMutableArray *")
    HM.add_ivar(class_value.GetValue(), "_rightTextArray", "NSMutableArray *")
    HM.register_class(class_value.GetValue())

    # Add methods
    HM.DPrint(f"Add methods to {g_class_name}...")
    viewDidLoad_imp_value = make_ViewDidLoad_IMP()
    if not HM.is_SBValue_has_value(viewDidLoad_imp_value):
        HMProgressHUD.hide()
        return
    HM.add_instance_method(g_class_name, "viewDidLoad", viewDidLoad_imp_value.GetValue(), "v@:")

    # Methods related to tableView.
    HM.DPrint(f"Add methods to {g_class_name}......")

    if not add_tableView_methods():
        HMProgressHUD.hide()
        return

    HM.DPrint(f"Register {g_class_name} done!")
    HMProgressHUD.hide()


def make_ViewDidLoad_IMP() -> lldb.SBValue:
    lldb_version = lldb.debugger.GetVersionString().replace('\n', '\\n')
    target_triple = lldb.debugger.GetSelectedTarget().GetTriple()
    python_version = sys.version.replace('\n', '\\n')
    commit_hash = HMEnvironment.get_git_commit_hash()
    optimized_str = HMEnvironment.get_optimized_str()

    command_script = f'''
        void (^IMPBlock)(UIViewController *) = ^(UIViewController *vc) {{
            Class cls = objc_lookUpClass("{g_class_name}");
            struct objc_super superInfo = {{
                .receiver = vc,
                .super_class = (Class)class_getSuperclass((Class)cls)
            }};
    
            ((void (*)(struct objc_super *, SEL))objc_msgSendSuper)(&superInfo, @selector(viewDidLoad));
            
            // initialize ivar and dataSource
            NSMutableArray *leftTextArray = [[NSMutableArray alloc] init];
            [vc setValue:leftTextArray forKey:@"_leftTextArray"];
            NSMutableArray *rightTextArray = [[NSMutableArray alloc] init];
            [vc setValue:rightTextArray forKey:@"_rightTextArray"];
            
            // Model identifier
            // Target triple
            // System version
            // Bundle identifier
            // Bundle short version
            // Bundle version
            // Xcode version
            // Xcode Build version
            // LLDB version
            // Python version
            // (HM)commit hash
            // Optimized

            [leftTextArray addObject:@"Model identifier"];
            struct utsname systemInfo;
            (int)uname(&systemInfo);
            NSString *modelIdentifier = [NSString stringWithCString:systemInfo.machine encoding:(NSStringEncoding)4];
            [rightTextArray addObject:modelIdentifier];
    
            [leftTextArray addObject:@"Target triple"];
            NSString *targetTriple = @"{target_triple}";
            [rightTextArray addObject:targetTriple];

            [leftTextArray addObject:@"System version"];
            NSString *systemVersion = [[NSString alloc] initWithFormat:@"%@ %@", [[UIDevice currentDevice] systemName], [[UIDevice currentDevice] systemVersion]];
            [rightTextArray addObject:systemVersion];
            
            [leftTextArray addObject:@"Bundle identifier"];
            NSString *bundleID = [NSBundle mainBundle].infoDictionary[@"CFBundleIdentifier"] ?: @"-";
            [rightTextArray addObject:bundleID];
            
            [leftTextArray addObject:@"Bundle short version"];
            NSString *bundleShortVersion = [NSBundle mainBundle].infoDictionary[@"CFBundleShortVersionString"] ?: @"-";
            [rightTextArray addObject:bundleShortVersion];
            
            [leftTextArray addObject:@"Bundle version"];
            NSString *bundleVersion = [NSBundle mainBundle].infoDictionary[@"CFBundleVersion"] ?: @"-";
            [rightTextArray addObject:bundleVersion];
            
            [leftTextArray addObject:@"Xcode version"];
            NSString *XcodeVersion = [NSBundle mainBundle].infoDictionary[@"DTXcode"] ?: @"-";
            [rightTextArray addObject:XcodeVersion];
            
            [leftTextArray addObject:@"Xcode Build version"];
            NSString *XcodeBuildVersion = [NSBundle mainBundle].infoDictionary[@"DTXcodeBuild"] ?: @"-";
            [rightTextArray addObject:XcodeBuildVersion];
            
            [leftTextArray addObject:@"LLDB version"];
            NSString *LLDBVersion = @"{lldb_version}";
            [rightTextArray addObject:LLDBVersion];

            [leftTextArray addObject:@"Python version"];
            NSString *pythonVersion = @"{python_version}";
            [rightTextArray addObject:pythonVersion];
            
            [leftTextArray addObject:@"(HM)Commit hash"];
            NSString *commitHash = @"{commit_hash}";
            [rightTextArray addObject:commitHash];
            
            [leftTextArray addObject:@"Optimized"];
            NSString *optimized = @"{optimized_str}";
            [rightTextArray addObject:optimized];
            
            // property initialize
            (void)[vc.view setBackgroundColor:[UIColor whiteColor]];
            vc.navigationItem.title = @"Information";
            
            // tableView
            UITableView *tv = [[UITableView alloc] init];
            tv.frame = vc.view.bounds;
            tv.dataSource = (id)vc;
            tv.estimatedRowHeight = 50;
            tv.rowHeight = UITableViewAutomaticDimension;
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


def add_tableView_methods() -> bool:
    global g_class_name

    numberOfRowsInSection_imp_value = make_numberOfRowsInSection_imp()
    if not HM.is_SBValue_has_value(numberOfRowsInSection_imp_value):
        return False
    HM.add_instance_method(g_class_name, "tableView:numberOfRowsInSection:", numberOfRowsInSection_imp_value.GetValue(), "q@:@q")

    cellForRowAtIndexPath_imp_value = make_cellForRowAtIndexPath_imp()
    if not HM.is_SBValue_has_value(cellForRowAtIndexPath_imp_value):
        return False
    HM.add_instance_method(g_class_name, "tableView:cellForRowAtIndexPath:", cellForRowAtIndexPath_imp_value.GetValue(), "@@:@@")

    return True


def make_numberOfRowsInSection_imp() -> lldb.SBValue:
    command_script = '''
        long (^IMPBlock)(UIViewController *, UITableView *, long) = ^long(UIViewController *vc, UITableView *tv, long section) {
            NSMutableArray *leftTextArray = (NSMutableArray *)[vc valueForKey:@"_leftTextArray"];
            return [leftTextArray count];
        };
        
        imp_implementationWithBlock(IMPBlock);    
    '''

    return HM.evaluate_expression_value(expression=command_script, prefix=HMExpressionPrefix.gPrefix)


def make_cellForRowAtIndexPath_imp() -> lldb.SBValue:
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
                
                CGFloat marginX = 16;
                CGFloat marginY = 12;
                
                UILabel *leftLab = [[UILabel alloc] init];
                leftLab.tag = 1111;
                leftLab.font = [UIFont systemFontOfSize:16];
                leftLab.textColor = [UIColor blackColor];
                [cell.contentView addSubview:leftLab];
                
                leftLab.translatesAutoresizingMaskIntoConstraints = NO;
                [leftLab setContentCompressionResistancePriority:1000 forAxis:(UILayoutConstraintAxis)0];
                [[NSLayoutConstraint constraintWithItem:leftLab attribute:NSLayoutAttributeTop relatedBy:NSLayoutRelationEqual toItem:cell.contentView attribute:NSLayoutAttributeTop multiplier:1.0 constant:marginY] setActive:YES];
                [[NSLayoutConstraint constraintWithItem:leftLab attribute:NSLayoutAttributeLeft relatedBy:NSLayoutRelationEqual toItem:cell.contentView attribute:NSLayoutAttributeLeft multiplier:1.0 constant:marginX] setActive:YES];
                [[NSLayoutConstraint constraintWithItem:leftLab attribute:NSLayoutAttributeBottom relatedBy:NSLayoutRelationLessThanOrEqual toItem:cell.contentView attribute:NSLayoutAttributeBottom multiplier:1.0 constant:-marginY] setActive:YES];
    
                UILabel *rightLab = [[UILabel alloc] init];
                rightLab.tag = 2222;
                rightLab.font = [UIFont systemFontOfSize:16];
                rightLab.textColor = [UIColor grayColor];
                rightLab.textAlignment = (NSTextAlignment)2;
                rightLab.numberOfLines = 0;
                [cell.contentView addSubview:rightLab];
                
                rightLab.translatesAutoresizingMaskIntoConstraints = NO;
                [[NSLayoutConstraint constraintWithItem:rightLab attribute:NSLayoutAttributeTop relatedBy:NSLayoutRelationEqual toItem:cell.contentView attribute:NSLayoutAttributeTop multiplier:1.0 constant:marginY] setActive:YES];
                [[NSLayoutConstraint constraintWithItem:rightLab attribute:NSLayoutAttributeLeft relatedBy:NSLayoutRelationEqual toItem:leftLab attribute:NSLayoutAttributeRight multiplier:1.0 constant:20] setActive:YES];
                [[NSLayoutConstraint constraintWithItem:rightLab attribute:NSLayoutAttributeBottom relatedBy:NSLayoutRelationEqual toItem:cell.contentView attribute:NSLayoutAttributeBottom multiplier:1.0 constant:-marginY] setActive:YES];
                [[NSLayoutConstraint constraintWithItem:rightLab attribute:NSLayoutAttributeRight relatedBy:NSLayoutRelationEqual toItem:cell.contentView attribute:NSLayoutAttributeRight multiplier:1.0 constant:-marginX] setActive:YES];
            }
            
            NSArray *leftTextArray = [vc valueForKey:@"_leftTextArray"];
            NSArray *rightTextArray = [vc valueForKey:@"_rightTextArray"];
            
            UILabel *leftLab = (UILabel *)[cell.contentView viewWithTag:1111];
            UILabel *rightLab = (UILabel *)[cell.contentView viewWithTag:2222];
            leftLab.text = leftTextArray[indexPath.row];
            rightLab.text = rightTextArray[indexPath.row];
            
            return cell;
        };

        imp_implementationWithBlock(IMPBlock);    
    '''

    return HM.evaluate_expression_value(expression=command_script, prefix=HMExpressionPrefix.gPrefix)
