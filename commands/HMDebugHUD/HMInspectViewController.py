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
import HMProgressHUD
import HMDebugWindow
import HMDebugBaseViewController


gClassName = "HMInspectViewController"
gWindowTag = 10100


def register() -> None:

    if HM.existClass(gClassName):
        return

    HMDebugWindow.register()
    HMDebugBaseViewController.register()

    # Register class
    HMProgressHUD.show(f"Register {gClassName}...")
    HM.DPrint(f"Register {gClassName}...")

    classValue = HM.allocateClass(gClassName, HMDebugBaseViewController.gClassName)
    HM.addIvar(classValue.GetValue(), "_highlightView", "UIView *")
    HM.addIvar(classValue.GetValue(), "_targetView", "UIView *")
    HM.addIvar(classValue.GetValue(), "_exitBtn", "UIButton *")
    HM.addIvar(classValue.GetValue(), "_infoView", "UIView *")
    HM.registerClass(classValue.GetValue())

    HM.DPrint(f"Add methods to {gClassName}...")
    startIMPValue = makeStartIMP()
    if not HM.judgeSBValueHasValue(startIMPValue):
        HMProgressHUD.hide()
        return
    HM.addClassMethod(gClassName, "start", startIMPValue.GetValue(), "@@:")

    viewDidLoadIMPValue = makeViewDidLoadIMP()
    if not HM.judgeSBValueHasValue(viewDidLoadIMPValue):
        HMProgressHUD.hide()
        return
    HM.addInstanceMethod(gClassName, "viewDidLoad", viewDidLoadIMPValue.GetValue(), "v@:")

    viewDidLayoutSubviewsIMPValue = makeViewDidLayoutSubviewsIMP()
    if not HM.judgeSBValueHasValue(viewDidLayoutSubviewsIMPValue):
        HMProgressHUD.hide()
        return
    HM.addInstanceMethod(gClassName, "viewDidLayoutSubviews", viewDidLayoutSubviewsIMPValue.GetValue(), "v@:")

    # event
    HM.DPrint(f"Add methods to {gClassName}......")
    clickExitBtnIMPValue = makeClickExitBtnIMP()
    if not HM.judgeSBValueHasValue(clickExitBtnIMPValue):
        HMProgressHUD.hide()
        return
    HM.addInstanceMethod(gClassName, "clickExitBtn", clickExitBtnIMPValue.GetValue(), "v@:")

    handleTapRecognizerIMPValue = makeHandleTapRecognizerIMP()
    if not HM.judgeSBValueHasValue(handleTapRecognizerIMPValue):
        HMProgressHUD.hide()
        return
    HM.addInstanceMethod(gClassName, "handleTapRecognizer:", handleTapRecognizerIMPValue.GetValue(), "v@:@")

    refreshTargetViewIMPValue = makeRefreshTargetViewIMP()
    if not HM.judgeSBValueHasValue(refreshTargetViewIMPValue):
        HMProgressHUD.hide()
        return
    HM.addInstanceMethod(gClassName, "refreshTargetView:", refreshTargetViewIMPValue.GetValue(), "v@:@")

    HM.DPrint(f"Register {gClassName} done!")
    HMProgressHUD.hide()


def makeStartIMP() -> lldb.SBValue:
    command_script = f'''
        UIViewController * (^IMPBlock)(id) = ^UIViewController *(id classSelf) {{
            UIWindow *window = (UIWindow *)[[(Class)objc_lookUpClass("{HMDebugWindow.gClassName}") alloc] init];
            (void)[window setBackgroundColor:[UIColor clearColor]];
            window.windowLevel = UIWindowLevelAlert - 1;
            window.tag = {gWindowTag};
            UIViewController *vc = (UIViewController *)[[(Class)objc_lookUpClass("{gClassName}") alloc] init];
            window.rootViewController = vc;
            [window makeKeyAndVisible];
            return vc;
        }};

        imp_implementationWithBlock(IMPBlock);
     '''
    return HM.evaluateExpressionValue(command_script)


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
            (void)[vc.view setBackgroundColor:[UIColor clearColor]];
            
            // highlightView
            UIView *_highlightView = [[UIView alloc] init];
            [vc setValue:_highlightView forKey:@"_highlightView"];
            [_highlightView setUserInteractionEnabled:NO];
            (void)[_highlightView setBackgroundColor:[UIColor colorWithRed:0.27 green:0.56 blue:0.82 alpha:0.5]];
            [vc.view addSubview:_highlightView];
    
            // infoView
            UIView *_infoView = [[UIView alloc] init];
            [vc setValue:_infoView forKey:@"_infoView"];
            [_infoView setUserInteractionEnabled:NO];
            _infoView.hidden = YES;
            (void)[_infoView setBackgroundColor:[[UIColor whiteColor] colorWithAlphaComponent:.9]];
            (void)[[_infoView layer] setBorderColor:[[UIColor lightGrayColor] CGColor]];
            (void)[[_infoView layer] setBorderWidth:0.5];
            (void)[[_infoView layer] setCornerRadius:5];
            [vc.view addSubview:_infoView];
    
            // exitBtn
            UIButton *_exitBtn = [[UIButton alloc] init];
            [vc setValue:_exitBtn forKey:@"_exitBtn"];
            (void)[_exitBtn setBackgroundColor:[UIColor colorWithRed:208/255.0 green:2/255.0 blue:27/255.0 alpha:.7]];
            ((void (*)(id, SEL, id, long)) objc_msgSend)((id)_exitBtn, @selector(setTitle:forState:), (id)@"Tap to inspect | Exit", 0); // UIControlStateNormal
            ((void (*)(id, SEL, id, long)) objc_msgSend)((id)_exitBtn, @selector(setTitleColor:forState:), (id)[UIColor whiteColor], 0); // UIControlStateNormal
            _exitBtn.titleLabel.font = [UIFont systemFontOfSize:13];
            _exitBtn.clipsToBounds = YES;
            ((void (*)(id, SEL, id, SEL, long)) objc_msgSend)((id)_exitBtn, @selector(addTarget:action:forControlEvents:), (id)vc, @selector(clickExitBtn), 64); // UIControlEventTouchUpInside
            [vc.view addSubview:_exitBtn];
            
            // tap
            UITapGestureRecognizer *tapRecognizer = [[UITapGestureRecognizer alloc] initWithTarget:vc action:@selector(handleTapRecognizer:)];
            [vc.view addGestureRecognizer:tapRecognizer];
        }};

        imp_implementationWithBlock(IMPBlock);
     '''
    return HM.evaluateExpressionValue(command_script)


def makeViewDidLayoutSubviewsIMP() -> lldb.SBValue:
    command_script = f'''
        void (^IMPBlock)(UIViewController *) = ^(UIViewController *vc) {{
            Class cls = objc_lookUpClass("{gClassName}");
            struct objc_super superInfo = {{
                .receiver = vc,
                .super_class = (Class)class_getSuperclass((Class)cls)
            }};
            ((void (*)(struct objc_super *, SEL))objc_msgSendSuper)(&superInfo, @selector(viewDidLayoutSubviews));
            
            UIEdgeInsets safeAreaInsets = UIEdgeInsetsZero;
            if ([UIApplication.sharedApplication.keyWindow respondsToSelector:@selector(safeAreaInsets)]) {{
                safeAreaInsets = [UIApplication.sharedApplication.keyWindow safeAreaInsets];
            }}

            UIButton *_exitBtn = (UIButton *)[vc valueForKey:@"_exitBtn"];
            CGSize exitBtnSize = CGSizeMake(_exitBtn.intrinsicContentSize.width + 20, _exitBtn.intrinsicContentSize.height);
            CGFloat exitBtnY = vc.view.frame.size.height - safeAreaInsets.bottom - 10 - exitBtnSize.height;
            (void)[_exitBtn setFrame:(CGRect){{(vc.view.frame.size.width - exitBtnSize.width) / 2, exitBtnY, exitBtnSize.width, exitBtnSize.height}}];
            _exitBtn.layer.cornerRadius = exitBtnSize.height / 2;
        }};

        imp_implementationWithBlock(IMPBlock);
     '''
    return HM.evaluateExpressionValue(command_script)


def makeClickExitBtnIMP() -> lldb.SBValue:
    command_script = '''
        void (^IMPBlock)(UIViewController *) = ^(UIViewController *vc) {
            [[vc.view window] setHidden:YES];
        };
        imp_implementationWithBlock(IMPBlock);
     '''
    return HM.evaluateExpressionValue(command_script)


def makeHandleTapRecognizerIMP() -> lldb.SBValue:
    command_script = '''
        void (^IMPBlock)(UIViewController *, UITapGestureRecognizer *) = ^(UIViewController *vc, UITapGestureRecognizer *tapRecognizer) {
            // find targetView
            CGPoint point = [tapRecognizer locationInView:vc.view];
            UIView *targetView = nil;
            for (UIWindow *window in [UIApplication sharedApplication].windows.reverseObjectEnumerator) {
    
                if (window == vc.view.window) {
                    continue;
                }
                if ([window isHidden]) {
                    continue;
                }
    
                CGPoint wPoint = [window convertPoint:point fromWindow:vc.view.window];
                targetView = [window hitTest:wPoint withEvent:nil];
            }
    
            (void)[vc performSelector:@selector(refreshTargetView:) withObject:(id)targetView];
        };
        imp_implementationWithBlock(IMPBlock);
     '''
    return HM.evaluateExpressionValue(command_script)


def makeRefreshTargetViewIMP() -> lldb.SBValue:
    command_script = '''
        void (^IMPBlock)(UIViewController *, UIView *) = ^(UIViewController *vc, UIView *targetView) {
            [vc setValue:targetView forKey:@"_targetView"];
            
            UIView *_highlightView = (UIView *)[vc valueForKey:@"_highlightView"];
            UIView *_infoView = (UIView *)[vc valueForKey:@"_infoView"];
            if (targetView == nil) {
                _highlightView.hidden = YES;
                _infoView.hidden = YES;
                return;
            }
            
            // highlightFrame
            _highlightView.hidden = NO;
            CGRect highlightFrame = [vc.view.window convertRect:targetView.frame fromView:[targetView superview]];
            (void)[_highlightView setFrame:(CGRect)highlightFrame];
            
            // infoView
            _infoView.hidden = NO;
            NSMutableArray *infoArr = [[NSMutableArray alloc] init]; // NSMutableArray<NSArray<NSString *> *> *infoArr
            NSString *address = [[NSString alloc] initWithFormat:@"%p", targetView];
            [infoArr addObject:@[@"Address", address]];
            NSString *frameStr = ({
                NSString *frameX = [[NSString alloc] initWithFormat:@"%.1f", targetView.frame.origin.x];
                if ([frameX hasSuffix:@".0"]) {
                    frameX = [frameX substringToIndex:[frameX length] - 2];
                }
                NSString *frameY = [[NSString alloc] initWithFormat:@"%.1f", targetView.frame.origin.y];
                if ([frameY hasSuffix:@".0"]) {
                    frameY = [frameY substringToIndex:[frameY length] - 2];
                }
                NSString *frameWidthStr = [[NSString alloc] initWithFormat:@"%.1f", targetView.frame.size.width];
                if ([frameWidthStr hasSuffix:@".0"]) {
                    frameWidthStr = [frameWidthStr substringToIndex:[frameWidthStr length] - 2];
                }
                NSString *frameHeightStr = [[NSString alloc] initWithFormat:@"%.1f", targetView.frame.size.height];
                if ([frameHeightStr hasSuffix:@".0"]) {
                    frameHeightStr = [frameHeightStr substringToIndex:[frameHeightStr length] - 2];
                }
                [[NSString alloc] initWithFormat:@"{%@, %@, %@, %@}", frameX, frameY, frameWidthStr, frameHeightStr];
            });
            [infoArr addObject:@[@"Frame", frameStr]];
            
            _infoView.hidden = targetView == nil;
            [_infoView.subviews makeObjectsPerformSelector:@selector(removeFromSuperview)];
            
            UILabel *clsNameLab = [[UILabel alloc] init];
            clsNameLab.text = NSStringFromClass([targetView class]);
            clsNameLab.textColor = [UIColor blackColor];
            clsNameLab.font = [UIFont systemFontOfSize:13 weight:(UIFontWeight)UIFontWeightBold];
            [_infoView addSubview:clsNameLab];
            
            UIView *separator = [[UIView alloc] init];
            (void)[separator setBackgroundColor:[[UIColor grayColor] colorWithAlphaComponent:0.4]];
            [_infoView addSubview:separator];
            
            // infoView width
            CGFloat marginX = 5;
            CGFloat maxWidth = clsNameLab.intrinsicContentSize.width;
            UIFont *infoFont = [UIFont systemFontOfSize:13];
            for (NSArray *info in infoArr) { // NSArray<NSString *> *info
                CGSize leftSize = (CGSize)[info.firstObject sizeWithAttributes:@{(id)NSFontAttributeName: infoFont}];
                CGSize rightSize = (CGSize)[info.lastObject sizeWithAttributes:@{(id)NSFontAttributeName: infoFont}];
                CGFloat labelPadding = 10;
                if (maxWidth < leftSize.width + rightSize.width + marginX * 2 + labelPadding) {
                    maxWidth = leftSize.width + rightSize.width + marginX * 2 + labelPadding;
                }
            }
            
            if (maxWidth > vc.view.bounds.size.width * 0.67) {
                maxWidth = vc.view.bounds.size.width * 0.67;
            }
            
            // infoView subviews and frame
            (void)[clsNameLab setFrame:(CGRect){marginX, 4, clsNameLab.intrinsicContentSize.width, clsNameLab.intrinsicContentSize.height}];
            (void)[separator setFrame:(CGRect){marginX, CGRectGetMaxY(clsNameLab.frame) + 4, maxWidth - marginX * 2, 0.5}];
    
            CGFloat maxHeight = 0;
            for (int i = 0; i< infoArr.count; ++i) {
                NSArray *info = infoArr[i]; // NSArray<NSString *> *info
                UILabel *leftLab = [[UILabel alloc] init];
                leftLab.text = info.firstObject;
                ((void (*)(id, SEL, long)) objc_msgSend)((id)leftLab, @selector(setTextAlignment:), 0); // NSTextAlignmentLeft
                leftLab.font = [UIFont systemFontOfSize:13];
                leftLab.textColor = [UIColor grayColor];
                (void)[leftLab setFrame:(CGRect){marginX, 30.0 + i * 30.0 , leftLab.intrinsicContentSize.width, leftLab.intrinsicContentSize.height}];
                [_infoView addSubview:leftLab];
    
                UILabel *rightLab = [[UILabel alloc] init];
                rightLab.text = info.lastObject;
                ((void (*)(id, SEL, long)) objc_msgSend)((id)rightLab, @selector(setTextAlignment:), 2); // NSTextAlignmentRight
                rightLab.font = [UIFont systemFontOfSize:13];
                rightLab.textColor = [UIColor blackColor];
                (void)[rightLab setFrame:(CGRect){maxWidth - marginX - rightLab.intrinsicContentSize.width, 30.0 + i * 30.0, rightLab.intrinsicContentSize.width, rightLab.intrinsicContentSize.height}];
                [_infoView addSubview:rightLab];
                
                if (maxHeight < CGRectGetMaxY(leftLab.frame) + 4) {
                    maxHeight = CGRectGetMaxY(leftLab.frame) + 4;
                }
            }
            
            if (60 + maxHeight > highlightFrame.origin.y) {
                UIButton *_exitBtn = (UIButton *)[vc valueForKey:@"_exitBtn"];
                (void)[_infoView setFrame:(CGRect){10, _exitBtn.frame.origin.y - 10 - maxHeight, maxWidth, maxHeight}];
            } else {
                (void)[_infoView setFrame:(CGRect){10, 60, maxWidth, maxHeight}];
            }
    
            [vc.view setNeedsLayout];
            [vc.view layoutIfNeeded];
        };
        
        imp_implementationWithBlock(IMPBlock);
     '''
    return HM.evaluateExpressionValue(command_script)
