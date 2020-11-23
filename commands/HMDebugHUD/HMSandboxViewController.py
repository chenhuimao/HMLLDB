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
import HMProgressHUD
import HMDebugBaseViewController


gClassName = "HMSandboxViewController"


def register() -> None:

    if HM.existClass(gClassName):
        return

    # Register class
    HMProgressHUD.show(f"Register {gClassName}...")
    HM.DPrint(f"Register {gClassName}...")

    classValue = HM.allocateClass(gClassName, HMDebugBaseViewController.gClassName)
    HM.addIvar(classValue.GetValue(), "_tableView", "UITableView *")
    HM.addIvar(classValue.GetValue(), "_currentPath", "NSString *")
    HM.addIvar(classValue.GetValue(), "_childPaths", "NSMutableArray *")
    HM.registerClass(classValue.GetValue())

    # Add methods
    HM.DPrint(f"Add methods to {gClassName}...")
    viewDidLoadIMPValue = makeViewDidLoadIMP()
    if not HM.judgeSBValueHasValue(viewDidLoadIMPValue):
        HMProgressHUD.hide()
        return
    HM.addInstanceMethod(gClassName, "viewDidLoad", viewDidLoadIMPValue.GetValue(), "v@:")

    loadPathIMPValue = makeLoadPathIMP()
    if not HM.judgeSBValueHasValue(loadPathIMPValue):
        HMProgressHUD.hide()
        return
    HM.addInstanceMethod(gClassName, "loadPath:", loadPathIMPValue.GetValue(), "v@:@")

    clickBackItemIMPValue = makeClickBackItemIMP()
    if not HM.judgeSBValueHasValue(clickBackItemIMPValue):
        HMProgressHUD.hide()
        return
    HM.addInstanceMethod(gClassName, "clickBackItem", clickBackItemIMPValue.GetValue(), "v@:")

    clickPopItemIMPValue = makeClickPopItemIMP()
    if not HM.judgeSBValueHasValue(clickPopItemIMPValue):
        HMProgressHUD.hide()
        return
    HM.addInstanceMethod(gClassName, "clickPopItem", clickPopItemIMPValue.GetValue(), "v@:")

    deleteFileOrDirIMPValue = makeDeleteFileOrDirIMP()
    if not HM.judgeSBValueHasValue(deleteFileOrDirIMPValue):
        HMProgressHUD.hide()
        return
    HM.addInstanceMethod(gClassName, "deleteFileOrDir:", deleteFileOrDirIMPValue.GetValue(), "v@:@")


    # Methods related to tableView.
    HM.DPrint(f"Add methods to {gClassName}......")
    if not addTableViewMethods():
        HMProgressHUD.hide()
        return


    HM.DPrint(f"Register {gClassName} done!")
    HMProgressHUD.hide()


def makeViewDidLoadIMP() -> lldb.SBValue:
    command_script = f'''
        void (^IMPBlock)(UIViewController *) = ^(UIViewController *vc) {{
            Class cls = objc_lookUpClass("{gClassName}");
            struct objc_super superInfo = {{
                .receiver = vc,
                .super_class = (Class)class_getSuperclass((Class)cls)
            }};

            ((void (*)(struct objc_super *, SEL))objc_msgSendSuper)(&superInfo, @selector(viewDidLoad));

            // initialize ivar and dataSource
            (void)[vc performSelector:@selector(loadPath:) withObject:NSHomeDirectory()];
            
            // property initialize
            (void)[vc.view setBackgroundColor:[[UIColor alloc] initWithRed:0.933 green:0.933 blue:0.961 alpha:1]];
            vc.navigationItem.title = @"SandBox";
            UIBarButtonItem *backItem = [[UIBarButtonItem alloc] initWithTitle:@"Back" style:(UIBarButtonItemStyle)UIBarButtonItemStylePlain target:vc action:@selector(clickBackItem)];
            UIBarButtonItem *popItem = [[UIBarButtonItem alloc] initWithTitle:@"Pop" style:(UIBarButtonItemStyle)UIBarButtonItemStylePlain target:vc action:@selector(clickPopItem)];
            (void)[vc.navigationItem setLeftBarButtonItems:@[popItem, backItem]];
            
            // tableView
            UITableView *tv = [[UITableView alloc] init];
            [vc setValue:tv forKey:@"_tableView"];
            tv.frame = vc.view.bounds;
            (void)[tv setBackgroundColor:(UIColor *)[vc.view backgroundColor]];
            tv.rowHeight = 56;
            tv.estimatedSectionHeaderHeight = 40;
            tv.tableFooterView = [[UIView alloc] init];
            tv.dataSource = (id)vc;
            tv.delegate = (id)vc;
            if ([tv respondsToSelector:@selector(setContentInsetAdjustmentBehavior:)]) {{
                // UIScrollViewContentInsetAdjustmentAutomatic
                ((void (*)(id, SEL, long)) objc_msgSend)((id)tv, @selector(setContentInsetAdjustmentBehavior:), 0);
            }}
            [vc.view addSubview:tv];            
        }};

        imp_implementationWithBlock(IMPBlock);

     '''
    return HM.evaluateExpressionValue(command_script)


def makeLoadPathIMP() -> lldb.SBValue:
    command_script = '''
        void (^IMPBlock)(UIViewController *, NSString *) = ^(UIViewController *vc, NSString *path) {
            [vc setValue:path forKey:@"_currentPath"];
            if ([path isEqual:(NSString *)NSHomeDirectory()]) {
                vc.navigationItem.title = @"SandBox";
            } else {
                vc.navigationItem.title = [path lastPathComponent];
            }
            
            NSMutableArray<NSString *> *childPaths = [[NSMutableArray alloc] init];
            NSArray<NSString *> *subpaths = [[NSFileManager defaultManager] contentsOfDirectoryAtPath:path error:NULL];
            for (NSString *subpath in subpaths) {
                [childPaths addObject:[path stringByAppendingPathComponent:subpath]];
            }
            [vc setValue:childPaths forKey:@"_childPaths"];
            
            UITableView *tableView = (UITableView *)[vc valueForKey:@"_tableView"];
            if ([tableView respondsToSelector:@selector(adjustedContentInset)]) {
                [tableView setContentOffset:(CGPoint){0, -tableView.adjustedContentInset.top} animated:NO];
            } else {
                [tableView setContentOffset:(CGPoint){0, -tableView.contentInset.top} animated:NO];
            }
            [tableView reloadData];
        };
        
        imp_implementationWithBlock(IMPBlock);

     '''
    return HM.evaluateExpressionValue(command_script)


def makeClickBackItemIMP() -> lldb.SBValue:
    command_script = '''
        void (^IMPBlock)(UIViewController *) = ^(UIViewController *vc) {
            NSString *currentPath = (NSString *)[vc valueForKey:@"_currentPath"];
            if ([currentPath isEqual:(NSString *)NSHomeDirectory()]) {
                [vc.navigationController popViewControllerAnimated:YES];
            } else {
                NSString *upperDirectory = [currentPath stringByDeletingLastPathComponent];
                (void)[vc performSelector:@selector(loadPath:) withObject:upperDirectory];
            }
        };

        imp_implementationWithBlock(IMPBlock);

     '''
    return HM.evaluateExpressionValue(command_script)


def makeClickPopItemIMP() -> lldb.SBValue:
    command_script = '''
        void (^IMPBlock)(UIViewController *) = ^(UIViewController *vc) {
            [vc.navigationController popViewControllerAnimated:YES];
        };
        imp_implementationWithBlock(IMPBlock);

     '''
    return HM.evaluateExpressionValue(command_script)


def makeDeleteFileOrDirIMP() -> lldb.SBValue:
    command_script = '''
        void (^IMPBlock)(UIViewController *, NSString *) = ^(UIViewController *vc, NSString *path) {
            NSString *title = [[NSString alloc] initWithFormat:@"Delete %@?", [path lastPathComponent]];
            UIAlertController *alertController = [UIAlertController alertControllerWithTitle:title message:nil preferredStyle:(UIAlertControllerStyle)UIAlertControllerStyleAlert];
    
            [alertController addAction:[UIAlertAction actionWithTitle:@"Delete" style:(UIAlertActionStyle)UIAlertActionStyleDefault handler:^(UIAlertAction * _Nonnull action) {
                NSFileManager *fileMgr = [NSFileManager defaultManager];
                [fileMgr removeItemAtPath:path error:nil];
                
                NSString *currentPath = (NSString *)[vc valueForKey:@"_currentPath"];
                (void)[vc performSelector:@selector(loadPath:) withObject:currentPath];
            }]];
            [alertController addAction:[UIAlertAction actionWithTitle:@"Cancel" style:(UIAlertActionStyle)UIAlertActionStyleCancel handler:nil]];
            
            [vc presentViewController:alertController animated:YES completion:nil];
        };
        imp_implementationWithBlock(IMPBlock);

     '''
    return HM.evaluateExpressionValue(command_script)


def addTableViewMethods() -> bool:
    global gClassName

    # data source
    numberOfRowsInSectionIMPValue = makeNumberOfRowsInSectionIMP()
    if not HM.judgeSBValueHasValue(numberOfRowsInSectionIMPValue):
        return False
    HM.addInstanceMethod(gClassName, "tableView:numberOfRowsInSection:", numberOfRowsInSectionIMPValue.GetValue(), "q@:@q")

    cellForRowAtIndexPathIMPValue = makeCellForRowAtIndexPathIMP()
    if not HM.judgeSBValueHasValue(cellForRowAtIndexPathIMPValue):
        return False
    HM.addInstanceMethod(gClassName, "tableView:cellForRowAtIndexPath:", cellForRowAtIndexPathIMPValue.GetValue(), "@@:@@")

    canEditRowAtIndexPathIMPValue = makeCanEditRowAtIndexPathIMP()
    if not HM.judgeSBValueHasValue(canEditRowAtIndexPathIMPValue):
        return False
    HM.addInstanceMethod(gClassName, "tableView:canEditRowAtIndexPath:", canEditRowAtIndexPathIMPValue.GetValue(), "B@:@@")

    commitEditingStyleForRowAtIndexPathIMPValue = makeCommitEditingStyleForRowAtIndexPathIMP()
    if not HM.judgeSBValueHasValue(commitEditingStyleForRowAtIndexPathIMPValue):
        return False
    HM.addInstanceMethod(gClassName, "tableView:commitEditingStyle:forRowAtIndexPath:", commitEditingStyleForRowAtIndexPathIMPValue.GetValue(), "v@:@q@")

    # delegate
    didSelectRowAtIndexPathIMPValue = makeDidSelectRowAtIndexPathIMP()
    if not HM.judgeSBValueHasValue(didSelectRowAtIndexPathIMPValue):
        return False
    HM.addInstanceMethod(gClassName, "tableView:didSelectRowAtIndexPath:", didSelectRowAtIndexPathIMPValue.GetValue(), "v@:@@")

    viewForHeaderInSectionIMPValue = makeViewForHeaderInSectionIMP()
    if not HM.judgeSBValueHasValue(viewForHeaderInSectionIMPValue):
        return False
    HM.addInstanceMethod(gClassName, "tableView:viewForHeaderInSection:", viewForHeaderInSectionIMPValue.GetValue(), "@@:@q")

    editingStyleForRowAtIndexPathIMPValue = makeEditingStyleForRowAtIndexPathIMP()
    if not HM.judgeSBValueHasValue(editingStyleForRowAtIndexPathIMPValue):
        return False
    HM.addInstanceMethod(gClassName, "tableView:editingStyleForRowAtIndexPath:", editingStyleForRowAtIndexPathIMPValue.GetValue(), "q@:@@")

    return True


def makeNumberOfRowsInSectionIMP() -> lldb.SBValue:
    command_script = '''
        long (^IMPBlock)(UIViewController *, UITableView *, long) = ^long(UIViewController *vc, UITableView *tv, long section) {
            NSMutableArray *childPaths = (NSMutableArray *)[vc valueForKey:@"childPaths"];
            return [childPaths count];
        };
        imp_implementationWithBlock(IMPBlock);
     '''
    return HM.evaluateExpressionValue(command_script)


def makeCellForRowAtIndexPathIMP() -> lldb.SBValue:
    command_script = '''
        UITableViewCell * (^IMPBlock)(UIViewController *, UITableView *, NSIndexPath *) = ^UITableViewCell *(UIViewController *vc, UITableView *tv, NSIndexPath *indexPath) {
            NSString * reuseIdentifier = @"Cell";
            UITableViewCell *cell = [tv dequeueReusableCellWithIdentifier:reuseIdentifier];
            if (cell == nil) {
                cell = [[UITableViewCell alloc] initWithStyle:(UITableViewCellStyle)UITableViewCellStyleDefault reuseIdentifier:reuseIdentifier];
                cell.accessoryType = (UITableViewCellAccessoryType)UITableViewCellAccessoryDisclosureIndicator;
                (void)[cell setBackgroundColor:[UIColor whiteColor]];
                            
                UILabel *topLeftLab = [[UILabel alloc] init];
                topLeftLab.tag = 1111;
                topLeftLab.font = [UIFont systemFontOfSize:18];
                topLeftLab.textColor = [UIColor blackColor];
                [cell.contentView addSubview:topLeftLab];
                
                UILabel *bottomLeftLab = [[UILabel alloc] init];
                bottomLeftLab.tag = 2222;
                bottomLeftLab.font = [UIFont systemFontOfSize:12];
                bottomLeftLab.textColor = [UIColor grayColor];
                [cell.contentView addSubview:bottomLeftLab];
                
                UILabel *rightLab = [[UILabel alloc] init];
                rightLab.tag = 3333;
                rightLab.font = [UIFont systemFontOfSize:15];
                rightLab.textColor = [UIColor grayColor];
                ((void (*)(id, SEL, long)) objc_msgSend)((id)rightLab, @selector(setTextAlignment:), 2); // NSTextAlignmentRight
                rightLab.numberOfLines = 0;
                [cell.contentView addSubview:rightLab];
            }
            
            // data
            NSMutableArray *childPaths = (NSMutableArray *)[vc valueForKey:@"childPaths"];
            NSString *path = childPaths[indexPath.row];
    
            UILabel *topLeftLab = (UILabel *)[cell.contentView viewWithTag:1111];
            UILabel *bottomLeftLab = (UILabel *)[cell.contentView viewWithTag:2222];
            UILabel *rightLab = (UILabel *)[cell.contentView viewWithTag:3333];
    
            // topLeftLab
            topLeftLab.text = [path lastPathComponent];
            
            // bottomLeftLab
            NSFileManager *fileManager =[NSFileManager defaultManager];
            NSDictionary *attributes = [fileManager attributesOfItemAtPath:path error:NULL];
            BOOL isDirectory = [[attributes fileType] isEqual:NSFileTypeDirectory];
            NSString *bottomLeftText = nil;
            if (isDirectory) {
                unsigned long count = [[fileManager contentsOfDirectoryAtPath:path error:NULL] count];
                bottomLeftText = [[NSString alloc] initWithFormat:@"%lu item%@", count, (count == 1 ? @"" : @"s")];
            } else {
                if (attributes) {
                    bottomLeftText = [[NSString alloc] initWithFormat:@"%@", [attributes fileModificationDate]];
                } else {
                    bottomLeftText = @"You don’t have permission to access it";
                }
            }
            bottomLeftLab.text = bottomLeftText;
            
            // rightLab, file size
            if (isDirectory) {
                rightLab.text = @"";
            } else {
                NSNumber *fileSize = @([attributes fileSize]);
                rightLab.text = [NSByteCountFormatter stringFromByteCount:[fileSize longLongValue] countStyle:NSByteCountFormatterCountStyleFile];
            }
            
            // layout
            CGFloat marginX = 16;
            CGFloat rightLabX = vc.view.bounds.size.width - 32 - rightLab.intrinsicContentSize.width;
            (void)[rightLab setFrame:(CGRect){rightLabX, 0, rightLab.intrinsicContentSize.width, tv.rowHeight}];
            CGFloat bottomLeftLabY = tv.rowHeight - 8 - bottomLeftLab.intrinsicContentSize.height;
            (void)[bottomLeftLab setFrame:(CGRect){marginX, bottomLeftLabY, bottomLeftLab.intrinsicContentSize.width, bottomLeftLab.intrinsicContentSize.height}];
            CGFloat topLeftLabWidth = rightLab.frame.origin.x - marginX - 10;
            (void)[topLeftLab setFrame:(CGRect){marginX, 8, topLeftLabWidth, topLeftLab.intrinsicContentSize.height}];
    
            return cell;
        };
        
        imp_implementationWithBlock(IMPBlock);
     '''
    return HM.evaluateExpressionValue(command_script)


def makeCanEditRowAtIndexPathIMP() -> lldb.SBValue:
    command_script = '''
        BOOL (^IMPBlock)(UIViewController *, UITableView *, NSIndexPath *) = ^BOOL(UIViewController *vc, UITableView *tv, NSIndexPath * indexPath) {
            return YES;
        };
        imp_implementationWithBlock(IMPBlock);
     '''
    return HM.evaluateExpressionValue(command_script)


def makeCommitEditingStyleForRowAtIndexPathIMP() -> lldb.SBValue:
    command_script = '''
        void (^IMPBlock)(UIViewController *, UITableView *, UITableViewCellEditingStyle, NSIndexPath *) = ^(UIViewController *vc, UITableView *tv, UITableViewCellEditingStyle editingStyle, NSIndexPath *indexPath) {
            if (editingStyle == UITableViewCellEditingStyleDelete) {
                NSMutableArray *childPaths = (NSMutableArray *)[vc valueForKey:@"childPaths"];
                NSString *path = childPaths[indexPath.row];
                (void)[vc performSelector:@selector(deleteFileOrDir:) withObject:path];
            }
        };
        imp_implementationWithBlock(IMPBlock);
     '''
    return HM.evaluateExpressionValue(command_script)


def makeDidSelectRowAtIndexPathIMP() -> lldb.SBValue:
    command_script = '''
        void (^IMPBlock)(UIViewController *, UITableView *, NSIndexPath *) = ^(UIViewController *vc, UITableView *tv, NSIndexPath *indexPath) {
            [tv deselectRowAtIndexPath:indexPath animated:YES];
    
            NSMutableArray *childPaths = (NSMutableArray *)[vc valueForKey:@"childPaths"];
            NSString *path = childPaths[indexPath.row];
            
            BOOL isDirectory = NO;
            BOOL exist = [[NSFileManager defaultManager] fileExistsAtPath:path isDirectory:&isDirectory];
    
            if (!exist) {
                UIAlertController *alertController = [UIAlertController alertControllerWithTitle:nil message:@"You don’t have permission to access it, or this file no longer exists." preferredStyle:(UIAlertControllerStyle)UIAlertControllerStyleAlert];
                [alertController addAction:[UIAlertAction actionWithTitle:@"Cancel" style:(UIAlertActionStyle)UIAlertActionStyleCancel handler:nil]];
                [vc presentViewController:alertController animated:YES completion:nil];
                return;
            }
            
            if (isDirectory) {
                (void)[vc performSelector:@selector(loadPath:) withObject:path];
            } else {
                UIAlertController *alertController = [UIAlertController alertControllerWithTitle:nil message:nil preferredStyle:(UIAlertControllerStyle)UIAlertControllerStyleActionSheet];
                
                [alertController addAction:[UIAlertAction actionWithTitle:@"Delete" style:UIAlertActionStyleDestructive handler:^(UIAlertAction * _Nonnull action) {
                    (void)[vc performSelector:@selector(deleteFileOrDir:) withObject:path];
                }]];
                
                [alertController addAction:[UIAlertAction actionWithTitle:@"Share" style:UIAlertActionStyleDefault handler:^(UIAlertAction * _Nonnull action) {
                    NSURL *url = [[NSURL alloc] initFileURLWithPath:path];
                    if (url) {
                        NSArray *items = @[url];    // NSString、NSURL、UIImage
                        UIActivityViewController *controller = [[UIActivityViewController alloc] initWithActivityItems:items applicationActivities:nil];
                        [vc presentViewController:controller animated:YES completion:nil];
                    }
                }]];
                
                [alertController addAction:[UIAlertAction actionWithTitle:@"Cancel" style:UIAlertActionStyleCancel handler:nil]];
                
                [vc presentViewController:alertController animated:YES completion:nil];
            }
        };
        imp_implementationWithBlock(IMPBlock);
     '''
    return HM.evaluateExpressionValue(command_script)


def makeViewForHeaderInSectionIMP() -> lldb.SBValue:
    command_script = '''
        UIView * (^IMPBlock)(UIViewController *, UITableView *, long) = ^UIView *(UIViewController *vc, UITableView *tv, long section) {
            UITableViewHeaderFooterView *header = [tv dequeueReusableHeaderFooterViewWithIdentifier:@"Header"];
            if (header == nil) {
                header = [[UITableViewHeaderFooterView alloc] initWithReuseIdentifier:@"Header"];
                UIView *backgroundView = [[UIView alloc] init];
                (void)[backgroundView setBackgroundColor:(UIColor *)[vc.view backgroundColor]];
                [header setBackgroundView:backgroundView];
                
                UILabel *titleLab = [[UILabel alloc] init];
                titleLab.tag = 11111;
                titleLab.font = [UIFont systemFontOfSize:16];
                titleLab.textColor = [UIColor grayColor];
                titleLab.numberOfLines = 0;
                [header.contentView addSubview:titleLab];
                
                titleLab.translatesAutoresizingMaskIntoConstraints = NO;
                [[NSLayoutConstraint constraintWithItem:titleLab attribute:NSLayoutAttributeTop relatedBy:NSLayoutRelationEqual toItem:header.contentView attribute:NSLayoutAttributeTop multiplier:1.0 constant:8] setActive:YES];
                [[NSLayoutConstraint constraintWithItem:titleLab attribute:NSLayoutAttributeLeft relatedBy:NSLayoutRelationEqual toItem:header.contentView attribute:NSLayoutAttributeLeft multiplier:1.0 constant:16] setActive:YES];
                [[NSLayoutConstraint constraintWithItem:titleLab attribute:NSLayoutAttributeBottom relatedBy:NSLayoutRelationEqual toItem:header.contentView attribute:NSLayoutAttributeBottom multiplier:1.0 constant:-8] setActive:YES];
                [[NSLayoutConstraint constraintWithItem:titleLab attribute:NSLayoutAttributeRight relatedBy:NSLayoutRelationEqual toItem:header.contentView attribute:NSLayoutAttributeRight multiplier:1.0 constant:-16] setActive:YES];
            }
            
            UILabel *titleLab = (UILabel *)[header.contentView viewWithTag:11111];
            NSString *currentPath = (NSString *)[vc valueForKey:@"_currentPath"];
            titleLab.text = [currentPath stringByAbbreviatingWithTildeInPath];
    
            return header;
        };
        imp_implementationWithBlock(IMPBlock);
     '''
    return HM.evaluateExpressionValue(command_script)


def makeEditingStyleForRowAtIndexPathIMP() -> lldb.SBValue:
    command_script = '''
        UITableViewCellEditingStyle (^IMPBlock)(UIViewController *, UITableView *, NSIndexPath *) = ^UITableViewCellEditingStyle(UIViewController *vc, UITableView *tv, NSIndexPath *indexPath) {
            return UITableViewCellEditingStyleDelete;
        };
        imp_implementationWithBlock(IMPBlock);
     '''
    return HM.evaluateExpressionValue(command_script)
