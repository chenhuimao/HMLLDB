""" File: HMDebugInfoViewController.py

Implementation of HMDebugInfoViewController class.

"""

import lldb
import HMLLDBHelpers as HM
import HMLLDBClassInfo


gClassName = "HMDebugInfoViewController"


def register() -> None:

    if HM.existClass(gClassName):
        return

    # Register class
    HM.DPrint("Register {arg0}...".format(arg0=gClassName))
    classValue = HM.allocateClass(gClassName, "UIViewController")
    HM.addIvar(classValue.GetValue(), "_leftTextArray", "NSMutableArray *")
    HM.addIvar(classValue.GetValue(), "_rightTextArray", "NSMutableArray *")
    HM.registerClass(classValue.GetValue())

    # Add methods
    HM.DPrint("Add methods to {arg0}...".format(arg0=gClassName))
    viewDidLoadIMPValue = makeViewDidLoadIMP()
    if not HM.judgeSBValueHasValue(viewDidLoadIMPValue):
        return
    HM.addInstanceMethod(gClassName, "viewDidLoad", viewDidLoadIMPValue.GetValue(), "v@:")

    # Methods related to tableView.
    HM.DPrint("Add methods to {arg0}......".format(arg0=gClassName))
    if not addTableViewMethods():
        return


    HM.DPrint("Register {arg0} done!".format(arg0=gClassName))


def makeViewDidLoadIMP() -> lldb.SBValue:
    lldbVersion = lldb.debugger.GetVersionString().replace('\n', '\\n')
    command_script = '''
        void (^IMPBlock)(UIViewController *) = ^(UIViewController *vc) {{
            struct objc_super superInfo = {{
                .receiver = vc,
                .super_class = (Class)class_getSuperclass((Class)[vc class])
            }};
    
            ((void (*)(struct objc_super *, SEL))objc_msgSendSuper)(&superInfo, @selector(viewDidLoad));
            
            // initialize ivar and dataSource
            NSMutableArray *leftTextArray = [[NSMutableArray alloc] init];
            [vc setValue:leftTextArray forKey:@"_leftTextArray"];
            NSMutableArray *rightTextArray = [[NSMutableArray alloc] init];
            [vc setValue:rightTextArray forKey:@"_rightTextArray"];
            
            // 0
            [leftTextArray addObject:@"Model identifier"];
            struct utsname systemInfo;
            (int)uname(&systemInfo);
            NSString *modelIdentifier = [NSString stringWithCString:systemInfo.machine encoding:NSUTF8StringEncoding];
            [rightTextArray addObject:modelIdentifier];
    
            //  1
            [leftTextArray addObject:@"System version"];
            NSString *systemVersion = [[NSString alloc] initWithFormat:@"%@ %@", [[UIDevice currentDevice] systemName], [[UIDevice currentDevice] systemVersion]];
            [rightTextArray addObject:systemVersion];
            
            // 2
            [leftTextArray addObject:@"Identifier for vendor"];
            NSString *idfv = [[[UIDevice currentDevice] identifierForVendor] UUIDString] ?: @"-";
            [rightTextArray addObject:idfv];
            
            // 3
            [leftTextArray addObject:@"Bundle identifier"];
            NSString *bundleID = [NSBundle mainBundle].infoDictionary[@"CFBundleIdentifier"] ?: @"-";
            [rightTextArray addObject:bundleID];
            
            // 4
            [leftTextArray addObject:@"Bundle short version"];
            NSString *bundleShortVersion = [NSBundle mainBundle].infoDictionary[@"CFBundleShortVersionString"] ?: @"-";
            [rightTextArray addObject:bundleShortVersion];
            
            // 5
            [leftTextArray addObject:@"Bundle version"];
            NSString *bundleVersion = [NSBundle mainBundle].infoDictionary[@"CFBundleVersion"] ?: @"-";
            [rightTextArray addObject:bundleVersion];
            
            // 6
            [leftTextArray addObject:@"Xcode version"];
            NSString *XcodeVersion = [NSBundle mainBundle].infoDictionary[@"DTXcode"] ?: @"-";
            [rightTextArray addObject:XcodeVersion];
            
            // 7
            [leftTextArray addObject:@"Xcode Build version"];
            NSString *XcodeBuildVersion = [NSBundle mainBundle].infoDictionary[@"DTXcodeBuild"] ?: @"-";
            [rightTextArray addObject:XcodeBuildVersion];
            
            // 8
            [leftTextArray addObject:@"LLDB version"];
            NSString *LLDBVersion = @"{arg0}";
            [rightTextArray addObject:LLDBVersion];
            
            // property initialize
            (void)[vc.view setBackgroundColor:[UIColor whiteColor]];
            vc.navigationItem.title = @"Information";
            
            // tableView
            UITableView *tv = [[UITableView alloc] init];
            tv.frame = vc.view.bounds;
            tv.dataSource = vc;
            tv.estimatedRowHeight = 50;
            tv.rowHeight = UITableViewAutomaticDimension;
            tv.tableFooterView = [[UIView alloc] init];
            [vc.view addSubview:tv];
        }};

        (IMP)imp_implementationWithBlock(IMPBlock);    
    '''.format(arg0=lldbVersion)

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

    return True


def makeNumberOfRowsInSectionIMP() -> lldb.SBValue:
    command_script = '''
        long (^IMPBlock)(UIViewController *, UITableView *, long) = ^long(UIViewController *vc, UITableView *tv, long section) {
            NSMutableArray *leftTextArray = (NSMutableArray *)[vc valueForKey:@"_leftTextArray"];
            return [leftTextArray count];
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
                cell = [[UITableViewCell alloc] initWithStyle:(UITableViewCellStyle)UITableViewCellStyleDefault reuseIdentifier:reuseIdentifier];
                cell.selectionStyle = UITableViewCellSelectionStyleNone;
                
                CGFloat marginX = 16;
                CGFloat marginY = 12;
                
                UILabel *leftLab = [[UILabel alloc] init];
                leftLab.tag = 1111;
                leftLab.font = [UIFont systemFontOfSize:16];
                leftLab.textColor = [UIColor blackColor];
                [cell.contentView addSubview:leftLab];
                
                leftLab.translatesAutoresizingMaskIntoConstraints = NO;
                [leftLab setContentCompressionResistancePriority:1000 forAxis:(UILayoutConstraintAxis)UILayoutConstraintAxisHorizontal];
                [NSLayoutConstraint constraintWithItem:leftLab attribute:NSLayoutAttributeTop relatedBy:NSLayoutRelationEqual toItem:cell.contentView attribute:NSLayoutAttributeTop multiplier:1.0 constant:marginY].active = YES;
                [NSLayoutConstraint constraintWithItem:leftLab attribute:NSLayoutAttributeLeft relatedBy:NSLayoutRelationEqual toItem:cell.contentView attribute:NSLayoutAttributeLeft multiplier:1.0 constant:marginX].active = YES;
                [NSLayoutConstraint constraintWithItem:leftLab attribute:NSLayoutAttributeBottom relatedBy:NSLayoutRelationLessThanOrEqual toItem:cell.contentView attribute:NSLayoutAttributeBottom multiplier:1.0 constant:-marginY].active = YES;
    
                UILabel *rightLab = [[UILabel alloc] init];
                rightLab.tag = 2222;
                rightLab.font = [UIFont systemFontOfSize:16];
                rightLab.textColor = [UIColor grayColor];
                rightLab.textAlignment = NSTextAlignmentRight;
                rightLab.numberOfLines = 0;
                [cell.contentView addSubview:rightLab];
                
                rightLab.translatesAutoresizingMaskIntoConstraints = NO;
                [NSLayoutConstraint constraintWithItem:rightLab attribute:NSLayoutAttributeTop relatedBy:NSLayoutRelationEqual toItem:cell.contentView attribute:NSLayoutAttributeTop multiplier:1.0 constant:marginY].active = YES;
                [NSLayoutConstraint constraintWithItem:rightLab attribute:NSLayoutAttributeLeft relatedBy:NSLayoutRelationEqual toItem:leftLab attribute:NSLayoutAttributeRight multiplier:1.0 constant:20].active = YES;
                [NSLayoutConstraint constraintWithItem:rightLab attribute:NSLayoutAttributeBottom relatedBy:NSLayoutRelationEqual toItem:cell.contentView attribute:NSLayoutAttributeBottom multiplier:1.0 constant:-marginY].active = YES;
                [NSLayoutConstraint constraintWithItem:rightLab attribute:NSLayoutAttributeRight relatedBy:NSLayoutRelationEqual toItem:cell.contentView attribute:NSLayoutAttributeRight multiplier:1.0 constant:-marginX].active = YES;
            }
            
            NSArray *leftTextArray = [vc valueForKey:@"_leftTextArray"];
            NSArray *rightTextArray = [vc valueForKey:@"_rightTextArray"];
            
            UILabel *leftLab = (UILabel *)[cell.contentView viewWithTag:1111];
            UILabel *rightLab = (UILabel *)[cell.contentView viewWithTag:2222];
            leftLab.text = leftTextArray[indexPath.row];
            rightLab.text = rightTextArray[indexPath.row];
            
            return cell;
        };

        (IMP)imp_implementationWithBlock(IMPBlock);    
    '''

    return HM.evaluateExpressionValue(command_script)
