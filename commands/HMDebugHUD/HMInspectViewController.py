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
import HMExpressionPrefix
import HMLLDBClassInfo


gClassName = "HMInspectViewController"
gWindowTag = 10100


def register() -> None:

    if HM.existClass(gClassName):
        return

    HMProgressHUD.register()
    HMDebugWindow.register()
    HMDebugBaseViewController.register()

    # Register class
    HMProgressHUD.show(f"Register {gClassName}...")
    HM.DPrint(f"Register {gClassName}...")

    classValue = HM.allocateClass(gClassName, HMDebugBaseViewController.gClassName)
    HM.addIvar(classValue.GetValue(), "_previousKeyWindow", "UIWindow *")
    HM.addIvar(classValue.GetValue(), "_highlightView", "UIView *")
    HM.addIvar(classValue.GetValue(), "_targetView", "UIView *")
    HM.addIvar(classValue.GetValue(), "_exitBtn", "UIButton *")

    HM.addIvar(classValue.GetValue(), "_infoView", "UIView *")
    HM.addIvar(classValue.GetValue(), "_actionView", "UIButton *")
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

    clickCloseBtnIMPValue = makeClickCloseBtnIMP()
    if not HM.judgeSBValueHasValue(clickCloseBtnIMPValue):
        HMProgressHUD.hide()
        return
    HM.addInstanceMethod(gClassName, "clickCloseBtn", clickCloseBtnIMPValue.GetValue(), "v@:")

    handleTapRecognizerIMPValue = makeHandleTapRecognizerIMP()
    if not HM.judgeSBValueHasValue(handleTapRecognizerIMPValue):
        HMProgressHUD.hide()
        return
    HM.addInstanceMethod(gClassName, "handleTapRecognizer:", handleTapRecognizerIMPValue.GetValue(), "v@:@")

    findSubviewAtPointInViewIMPValue = makeFindSubviewAtPointInViewIMP()
    if not HM.judgeSBValueHasValue(findSubviewAtPointInViewIMPValue):
        HMProgressHUD.hide()
        return
    HM.addInstanceMethod(gClassName, "findSubviewAtPoint:inView:", findSubviewAtPointInViewIMPValue.GetValue(), "@@:{CGPoint=dd}@")

    refreshTargetViewIMPValue = makeRefreshTargetViewIMP()
    if not HM.judgeSBValueHasValue(refreshTargetViewIMPValue):
        HMProgressHUD.hide()
        return
    HM.addInstanceMethod(gClassName, "refreshTargetView:", refreshTargetViewIMPValue.GetValue(), "v@:@")

    getInfoArrayFromTargetViewIMPValue = makeGetInfoArrayFromTargetViewIMP()
    if not HM.judgeSBValueHasValue(getInfoArrayFromTargetViewIMPValue):
        HMProgressHUD.hide()
        return
    HM.addInstanceMethod(gClassName, "getInfoArrayFromTargetView:", getInfoArrayFromTargetViewIMPValue.GetValue(), "@@:@")

    # function action
    HM.DPrint(f"Add methods to {gClassName}.........")
    if not addFunctionMethods():
        HMProgressHUD.hide()
        return

    HM.DPrint(f"Register {gClassName} done!")
    HMProgressHUD.hide()


def makeStartIMP() -> lldb.SBValue:
    command_script = f'''
        UIViewController * (^IMPBlock)(id) = ^UIViewController *(id classSelf) {{
            UIViewController *vc = (UIViewController *)[[(Class)objc_lookUpClass("{gClassName}") alloc] init];
            [vc setValue:[UIApplication sharedApplication].keyWindow forKey:@"_previousKeyWindow"];

            UIWindow *window = (UIWindow *)[[(Class)objc_lookUpClass("{HMDebugWindow.gClassName}") alloc] init];
            if ((BOOL)[[UIApplication sharedApplication] respondsToSelector:@selector(connectedScenes)]) {{
                NSSet *scenes = [[UIApplication sharedApplication] connectedScenes]; // NSSet<UIScene *> *scenes
                for (id scene in scenes) {{
                    if ((long)[scene activationState] == 0 && (BOOL)[scene isKindOfClass:NSClassFromString(@"UIWindowScene")]) {{
                        // UISceneActivationStateForegroundActive
                        (void)[window setWindowScene:scene];
                        break;
                    }}
                }}
            }}
            (void)[window setFrame:(CGRect)UIScreen.mainScreen.bounds];
            (void)[window setBackgroundColor:[UIColor clearColor]];
            window.windowLevel = UIWindowLevelAlert - 1;
            window.tag = {gWindowTag};
            window.rootViewController = vc;
            [window makeKeyAndVisible];
            return vc;
        }};

        imp_implementationWithBlock(IMPBlock);
     '''
    return HM.evaluateExpressionValue(command_script, prefix=HMExpressionPrefix.gPrefix)


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
    
            // actionView
            CGFloat actionViewHeight = 120;
            CGFloat actionViewWidth = vc.view.bounds.size.width - 10;
            UIButton *_actionView = [[UIButton alloc] init];
            (void)[_actionView setFrame:(CGRect){{(vc.view.bounds.size.width - actionViewWidth) / 2, 0, actionViewWidth, actionViewHeight}}];
            [vc setValue:_actionView forKey:@"_actionView"];
            _actionView.hidden = YES;
            (void)[_actionView setBackgroundColor:[[UIColor whiteColor] colorWithAlphaComponent:.9]];
            (void)[[_actionView layer] setBorderColor:[[UIColor lightGrayColor] CGColor]];
            (void)[[_actionView layer] setBorderWidth:0.5];
            (void)[[_actionView layer] setCornerRadius:5];
            [vc.view addSubview:_actionView];
            
            // actionView-moveBtn
            UIButton *(^makeMoveBtnBlock)(NSInteger, NSString *) = ^UIButton *(NSInteger tag, NSString *text) {{
                UIButton *moveBtn = [[UIButton alloc] init];
                moveBtn.tag = tag;
                (void)[moveBtn setBackgroundColor:[[UIColor grayColor] colorWithAlphaComponent:0.2]];
                moveBtn.layer.cornerRadius = 18;
                ((void (*)(id, SEL, id, long)) objc_msgSend)((id)moveBtn, @selector(setTitle:forState:), (id)text, 0); // UIControlStateNormal
                ((void (*)(id, SEL, id, long)) objc_msgSend)((id)moveBtn, @selector(setTitleColor:forState:), (id)[UIColor blackColor], 0); // UIControlStateNormal
                ((void (*)(id, SEL, id, long)) objc_msgSend)((id)moveBtn, @selector(setTitleColor:forState:), (id)[[UIColor blackColor] colorWithAlphaComponent:0.2], 1); // UIControlStateHighlighted
                ((void (*)(id, SEL, id, SEL, long)) objc_msgSend)((id)moveBtn, @selector(addTarget:action:forControlEvents:), (id)vc, @selector(clickMoveBtn:), 64); // UIControlEventTouchUpInside
                moveBtn.titleLabel.font = [UIFont systemFontOfSize:18 weight:(UIFontWeight)UIFontWeightBold];
                return moveBtn;
            }};

            CGFloat moveBtnSideLength = 36;
            UIButton *moveTopBtn = makeMoveBtnBlock(1, @"↑");
            (void)[moveTopBtn setFrame:(CGRect){{32, 6, moveBtnSideLength, moveBtnSideLength}}];
            [_actionView addSubview:moveTopBtn];

            UIButton *moveLeftBtn = makeMoveBtnBlock(2, @"←");
            (void)[moveLeftBtn setFrame:(CGRect){{4, CGRectGetMaxY(moveTopBtn.frame), moveBtnSideLength, moveBtnSideLength}}];
            [_actionView addSubview:moveLeftBtn];

            UIButton *moveRightBtn = makeMoveBtnBlock(4, @"→");
            (void)[moveRightBtn setFrame:(CGRect){{CGRectGetMaxX(moveLeftBtn.frame) + 20, moveLeftBtn.frame.origin.y, moveBtnSideLength, moveBtnSideLength}}];
            [_actionView addSubview:moveRightBtn];

            UIButton *moveBottomBtn = makeMoveBtnBlock(3, @"↓");
            (void)[moveBottomBtn setFrame:(CGRect){{moveTopBtn.frame.origin.x, CGRectGetMaxY(moveLeftBtn.frame), moveBtnSideLength, moveBtnSideLength}}];
            [_actionView addSubview:moveBottomBtn];

            // actionView-other btns
            // 1. ivars   properties  methods
            // 2. superview  subviews.first
            // 3. next sibling  close
            UIButton *(^makeBtnBlock)(NSString *) = ^UIButton *(NSString *text) {{
                UIButton *btn = [[UIButton alloc] init];
                (void)[btn setBackgroundColor:[[UIColor grayColor] colorWithAlphaComponent:0.2]];
                btn.layer.cornerRadius = 3;
                ((void (*)(id, SEL, id, long)) objc_msgSend)((id)btn, @selector(setTitle:forState:), (id)text, 0); // UIControlStateNormal
                ((void (*)(id, SEL, id, long)) objc_msgSend)((id)btn, @selector(setTitleColor:forState:), (id)[UIColor blackColor], 0); // UIControlStateNormal
                ((void (*)(id, SEL, id, long)) objc_msgSend)((id)btn, @selector(setTitleColor:forState:), (id)[[UIColor blackColor] colorWithAlphaComponent:0.2], 1); // UIControlStateHighlighted
                btn.titleLabel.font = [UIFont systemFontOfSize:13 weight:(UIFontWeight)UIFontWeightBold];
                return btn;
            }};

            CGFloat beginX = CGRectGetMaxX(moveRightBtn.frame);
            CGFloat btnHeight = 30;
            CGFloat btnWidth1 = 80;
            CGFloat btnWidth2 = 100;
            CGFloat marginX = 8;
            CGFloat offsetY = 6;
            CGFloat offsetX = (actionViewWidth - beginX - marginX * 2 - btnWidth1 * 3) / 2;

            UIButton *ivarsBtn = makeBtnBlock(@"ivars");
            (void)[ivarsBtn setFrame:(CGRect){{beginX + marginX, 8, btnWidth1, btnHeight}}];
            ((void (*)(id, SEL, id, SEL, long)) objc_msgSend)((id)ivarsBtn, @selector(addTarget:action:forControlEvents:), (id)vc, @selector(ivarsAction), 64); // UIControlEventTouchUpInside
            [_actionView addSubview:ivarsBtn];

            UIButton *propertiesBtn = makeBtnBlock(@"properties");
            (void)[propertiesBtn setFrame:(CGRect){{CGRectGetMaxX(ivarsBtn.frame) + offsetX, ivarsBtn.frame.origin.y, btnWidth1, btnHeight}}];
            ((void (*)(id, SEL, id, SEL, long)) objc_msgSend)((id)propertiesBtn, @selector(addTarget:action:forControlEvents:), (id)vc, @selector(propertiesAction), 64); // UIControlEventTouchUpInside
            [_actionView addSubview:propertiesBtn];

            UIButton *methodsBtn = makeBtnBlock(@"methods");
            (void)[methodsBtn setFrame:(CGRect){{CGRectGetMaxX(propertiesBtn.frame) + offsetX, ivarsBtn.frame.origin.y, btnWidth1, btnHeight}}];
            ((void (*)(id, SEL, id, SEL, long)) objc_msgSend)((id)methodsBtn, @selector(addTarget:action:forControlEvents:), (id)vc, @selector(methodsAction), 64); // UIControlEventTouchUpInside
            [_actionView addSubview:methodsBtn];

            UIButton *siblingPreviousBtn = makeBtnBlock(@"sibling.previous");
            (void)[siblingPreviousBtn setFrame:(CGRect){{beginX + marginX, CGRectGetMaxY(ivarsBtn.frame) + offsetY, 120, btnHeight}}];
            ((void (*)(id, SEL, id, SEL, long)) objc_msgSend)((id)siblingPreviousBtn, @selector(addTarget:action:forControlEvents:), (id)vc, @selector(siblingPreviousAction), 64); // UIControlEventTouchUpInside
            [_actionView addSubview:siblingPreviousBtn];
            
            UIButton *siblingNextBtn = makeBtnBlock(@"sibling.next");
            (void)[siblingNextBtn setFrame:(CGRect){{CGRectGetMaxX(siblingPreviousBtn.frame) + offsetX, siblingPreviousBtn.frame.origin.y, btnWidth2, btnHeight}}];
            ((void (*)(id, SEL, id, SEL, long)) objc_msgSend)((id)siblingNextBtn, @selector(addTarget:action:forControlEvents:), (id)vc, @selector(siblingNextAction), 64); // UIControlEventTouchUpInside
            [_actionView addSubview:siblingNextBtn];
            
            UIButton *superviewBtn = makeBtnBlock(@"superview");
            (void)[superviewBtn setFrame:(CGRect){{beginX + marginX, CGRectGetMaxY(siblingNextBtn.frame) + offsetY, btnWidth1, btnHeight}}];
            ((void (*)(id, SEL, id, SEL, long)) objc_msgSend)((id)superviewBtn, @selector(addTarget:action:forControlEvents:), (id)vc, @selector(superviewAction), 64); // UIControlEventTouchUpInside
            [_actionView addSubview:superviewBtn];
            
            UIButton *subviewBtn = makeBtnBlock(@"subviews.first");
            (void)[subviewBtn setFrame:(CGRect){{CGRectGetMaxX(superviewBtn.frame) + offsetX, superviewBtn.frame.origin.y, btnWidth2, btnHeight}}];
            ((void (*)(id, SEL, id, SEL, long)) objc_msgSend)((id)subviewBtn, @selector(addTarget:action:forControlEvents:), (id)vc, @selector(subviewAction), 64); // UIControlEventTouchUpInside
            [_actionView addSubview:subviewBtn];

            UIButton *closeBtn = [[UIButton alloc] init];
            (void)[closeBtn setFrame:(CGRect){{actionViewWidth - marginX - 50, superviewBtn.frame.origin.y, 50, btnHeight}}];
            (void)[closeBtn setBackgroundColor:[UIColor colorWithRed:208/255.0 green:2/255.0 blue:27/255.0 alpha:.7]];
            ((void (*)(id, SEL, id, long)) objc_msgSend)((id)closeBtn, @selector(setTitle:forState:), (id)@"Close", 0); // UIControlStateNormal
            ((void (*)(id, SEL, id, long)) objc_msgSend)((id)closeBtn, @selector(setTitleColor:forState:), (id)[UIColor whiteColor], 0); // UIControlStateNormal

            closeBtn.titleLabel.font = [UIFont systemFontOfSize:13];
            closeBtn.layer.cornerRadius = 3;
            ((void (*)(id, SEL, id, SEL, long)) objc_msgSend)((id)closeBtn, @selector(addTarget:action:forControlEvents:), (id)vc, @selector(clickCloseBtn), 64); // UIControlEventTouchUpInside
            [_actionView addSubview:closeBtn];

            // exitBtn
            UIButton *_exitBtn = [[UIButton alloc] init];
            [vc setValue:_exitBtn forKey:@"_exitBtn"];
            (void)[_exitBtn setBackgroundColor:[UIColor colorWithRed:208/255.0 green:2/255.0 blue:27/255.0 alpha:.7]];
            ((void (*)(id, SEL, id, long)) objc_msgSend)((id)_exitBtn, @selector(setTitle:forState:), (id)@"Tap to exit", 0); // UIControlStateNormal
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
            CGSize exitBtnSize = (CGSize){{_exitBtn.intrinsicContentSize.width + 20, _exitBtn.intrinsicContentSize.height}}; 
            CGFloat exitBtnY = vc.view.frame.size.height - safeAreaInsets.bottom - 10 - exitBtnSize.height;
            (void)[_exitBtn setFrame:(CGRect){{(vc.view.frame.size.width - exitBtnSize.width) / 2, exitBtnY, exitBtnSize.width, exitBtnSize.height}}];
            _exitBtn.layer.cornerRadius = exitBtnSize.height / 2;
        }};

        imp_implementationWithBlock(IMPBlock);
     '''
    return HM.evaluateExpressionValue(expression=command_script, prefix=HMExpressionPrefix.gPrefix)


def makeClickExitBtnIMP() -> lldb.SBValue:
    command_script = '''
        void (^IMPBlock)(UIViewController *) = ^(UIViewController *vc) {
            UIWindow *_previousKeyWindow = (UIWindow *)[vc valueForKey:@"_previousKeyWindow"];
            [vc setValue:nil forKey:@"_previousKeyWindow"];
            
            [[vc.view window] setHidden:YES];
            [_previousKeyWindow makeKeyWindow];
        };
        imp_implementationWithBlock(IMPBlock);
     '''
    return HM.evaluateExpressionValue(command_script)


def makeClickCloseBtnIMP() -> lldb.SBValue:
    command_script = '''
        void (^IMPBlock)(UIViewController *) = ^(UIViewController *vc) {
            UIView *_highlightView = (UIView *)[vc valueForKey:@"_highlightView"];
            UIView *_infoView = (UIView *)[vc valueForKey:@"_infoView"];
            UIButton *_actionView = (UIButton *)[vc valueForKey:@"_actionView"];
            _highlightView.hidden = YES;
            _infoView.hidden = YES;
            _actionView.hidden = YES;
        };
        imp_implementationWithBlock(IMPBlock);
     '''
    return HM.evaluateExpressionValue(command_script)


def makeHandleTapRecognizerIMP() -> lldb.SBValue:
    command_script = '''
        void (^IMPBlock)(UIViewController *, UITapGestureRecognizer *) = ^(UIViewController *vc, UITapGestureRecognizer *tapRecognizer) {
            // find targetView
            CGPoint point = [tapRecognizer locationInView:vc.view];
            UIView *_targetView = nil;
            UIWindow *_previousKeyWindow = (UIWindow *)[vc valueForKey:@"_previousKeyWindow"];
            for (UIWindow *window in [UIApplication sharedApplication].windows.reverseObjectEnumerator) {
                if (_targetView) {
                    break;
                }
                if (window == vc.view.window) {
                    continue;
                }
                if ([window isHidden]) {
                    continue;
                }
    
                CGPoint wPoint = [window convertPoint:point fromWindow:vc.view.window];
                if (window == _previousKeyWindow) {
                    _targetView = ((id (*)(id, SEL, CGPoint, id)) objc_msgSend)((id)vc, @selector(findSubviewAtPoint:inView:), wPoint, (id)window);
                } else {
                    _targetView = [window hitTest:wPoint withEvent:nil];
                }
            }
    
            printf("\\n[HMLLDB]: %s\\n", (char *)[[_targetView description] UTF8String]);
            (void)[vc performSelector:@selector(refreshTargetView:) withObject:(id)_targetView];
        };
        imp_implementationWithBlock(IMPBlock);
     '''
    return HM.evaluateExpressionValue(expression=command_script, prefix=HMExpressionPrefix.gPrefix)


def makeFindSubviewAtPointInViewIMP() -> lldb.SBValue:
    command_script = '''
        UIView * (^IMPBlock)(UIViewController *, CGPoint, UIView *) = ^UIView *(UIViewController *vc, CGPoint point, UIView *view) {
            NSArray *clsArr = @[[UITextField class], [UITextView class], [UIProgressView class], [UIActivityIndicatorView class], [UISlider class], [UISwitch class], [UIPageControl class], [UIStepper class]];
            for (Class cls in clsArr) {
                if ([view isKindOfClass:cls]) {
                    return view;
                }
            }
            
            UIView *targetView = nil;
            for (UIView *sView in view.subviews.reverseObjectEnumerator) {
                if ([sView isHidden] || sView.alpha <= 0.01) {
                    continue;
                }
                
                if (CGRectContainsPoint(sView.frame, point)) {
                    targetView = sView;
                    break;;
                }
            }
            
            if (!targetView) {
                return view;
            }
            
            CGPoint tPoint = [targetView convertPoint:point fromView:view];
            targetView = ((id (*)(id, SEL, CGPoint, id)) objc_msgSend)((id)vc, @selector(findSubviewAtPoint:inView:), tPoint, (id)targetView);
            return targetView;
        };  
        imp_implementationWithBlock(IMPBlock);
     '''
    return HM.evaluateExpressionValue(expression=command_script, prefix=HMExpressionPrefix.gPrefix)


def makeRefreshTargetViewIMP() -> lldb.SBValue:
    command_script = '''
        void (^IMPBlock)(UIViewController *, UIView *) = ^(UIViewController *vc, UIView *targetView) {
            [vc setValue:targetView forKey:@"_targetView"];
            
            UIView *_highlightView = (UIView *)[vc valueForKey:@"_highlightView"];
            UIView *_infoView = (UIView *)[vc valueForKey:@"_infoView"];
            UIButton *_actionView = (UIButton *)[vc valueForKey:@"_actionView"];
            if (targetView == nil) {
                _highlightView.hidden = YES;
                _infoView.hidden = YES;
                _actionView.hidden = YES;
                return;
            }
            
            _highlightView.hidden = NO;
            _infoView.hidden = NO;
            _actionView.hidden = NO;
        
            // highlightFrame
            CGRect highlightFrame = [vc.view.window convertRect:targetView.frame fromView:[targetView superview]];
            (void)[_highlightView setFrame:(CGRect)highlightFrame];
            
            // infoView. NSArray<NSArray<NSString *> *> *infoArr
            NSArray *infoArr = (NSArray *)[vc performSelector:@selector(getInfoArrayFromTargetView:) withObject:targetView];
            
            _infoView.hidden = targetView == nil;
            [_infoView.subviews makeObjectsPerformSelector:@selector(removeFromSuperview)];
            
            UILabel *clsNameLab = [[UILabel alloc] init];
            clsNameLab.numberOfLines = 0;
            clsNameLab.text = NSStringFromClass([targetView class]);
            clsNameLab.textColor = [UIColor blackColor];
            clsNameLab.font = [UIFont systemFontOfSize:13 weight:(UIFontWeight)UIFontWeightBold];
            [_infoView addSubview:clsNameLab];
            
            UIView *separator = [[UIView alloc] init];
            (void)[separator setBackgroundColor:[[UIColor grayColor] colorWithAlphaComponent:0.4]];
            [_infoView addSubview:separator];
            
            // infoView width
            CGFloat marginX = 5;
            CGFloat infoViewWidth = clsNameLab.intrinsicContentSize.width + marginX * 2;
            UIFont *infoFont = [UIFont systemFontOfSize:13];
            for (NSArray *infos in infoArr) { // NSArray<NSString *> *infos
                CGSize leftSize = (CGSize)[infos.firstObject sizeWithAttributes:@{(id)NSFontAttributeName: infoFont}];
                CGSize rightSize = (CGSize)[infos.lastObject sizeWithAttributes:@{(id)NSFontAttributeName: infoFont}];
                CGFloat labelPadding = 10;
                if (infoViewWidth < leftSize.width + rightSize.width + marginX * 2 + labelPadding) {
                    infoViewWidth = leftSize.width + rightSize.width + marginX * 2 + labelPadding;
                }
            }
            
            if (infoViewWidth > vc.view.bounds.size.width - 10) {
                infoViewWidth = vc.view.bounds.size.width - 10;
            }
            
            // infoView subviews and frame
            CGSize clsNameLabSize = (CGSize)[clsNameLab sizeThatFits:(CGSize){infoViewWidth - marginX * 2, 1000}];
            (void)[clsNameLab setFrame:(CGRect){marginX, 4, clsNameLabSize.width, clsNameLabSize.height}];
            (void)[separator setFrame:(CGRect){marginX, CGRectGetMaxY(clsNameLab.frame) + 4, infoViewWidth - marginX * 2, 0.5}];
    
            CGFloat infoViewHeight = 0;
            for (int i = 0; i< infoArr.count; ++i) {
                NSArray *infos = infoArr[i]; // NSArray<NSString *> *infos
                CGFloat rowHeight = 25;
                CGFloat beginY = CGRectGetMaxY(separator.frame) + 4;
            
                UILabel *leftLab = [[UILabel alloc] init];
                leftLab.text = infos.firstObject;
                ((void (*)(id, SEL, long)) objc_msgSend)((id)leftLab, @selector(setTextAlignment:), 0); // NSTextAlignmentLeft
                leftLab.font = [UIFont systemFontOfSize:13];
                leftLab.textColor = [UIColor grayColor];
                (void)[leftLab setFrame:(CGRect){marginX, beginY + i * rowHeight , leftLab.intrinsicContentSize.width, leftLab.intrinsicContentSize.height}];
                [_infoView addSubview:leftLab];
    
                UILabel *rightLab = [[UILabel alloc] init];
                rightLab.text = infos.lastObject;
                ((void (*)(id, SEL, long)) objc_msgSend)((id)rightLab, @selector(setTextAlignment:), 2); // NSTextAlignmentRight
                rightLab.font = [UIFont systemFontOfSize:13];
                rightLab.textColor = [UIColor blackColor];
                (void)[rightLab setFrame:(CGRect){infoViewWidth - marginX - rightLab.intrinsicContentSize.width, beginY + i * rowHeight, rightLab.intrinsicContentSize.width, rightLab.intrinsicContentSize.height}];
                [_infoView addSubview:rightLab];
                
                if (infoViewHeight < CGRectGetMaxY(leftLab.frame) + 4) {
                    infoViewHeight = CGRectGetMaxY(leftLab.frame) + 4;
                }
            }
            
            UIButton *_exitBtn = (UIButton *)[vc valueForKey:@"_exitBtn"];
            CGFloat actionViewOffsetY = 6;
            CGFloat infoViewY = _exitBtn.frame.origin.y - 10 - _actionView.bounds.size.height - actionViewOffsetY - infoViewHeight;
            BOOL canFrameInTop = (60 + infoViewHeight + actionViewOffsetY + _actionView.bounds.size.height) <= CGRectGetMinY(highlightFrame);
            if (infoViewY < CGRectGetMaxY(highlightFrame) && canFrameInTop) {
                infoViewY = 60;
            }
            (void)[_infoView setFrame:(CGRect){(vc.view.bounds.size.width - infoViewWidth) / 2, infoViewY, infoViewWidth, infoViewHeight}];
    
            CGRect actionViewFrame = _actionView.frame;
            actionViewFrame.origin.y = CGRectGetMaxY(_infoView.frame) + actionViewOffsetY;
            (void)[_actionView setFrame:(CGRect)actionViewFrame];
    
            [vc.view setNeedsLayout];
            [vc.view layoutIfNeeded];
        };
        
        imp_implementationWithBlock(IMPBlock);
     '''
    return HM.evaluateExpressionValue(expression=command_script, prefix=HMExpressionPrefix.gPrefix)


# The "infoView" is based on https://github.com/QMUI/LookinServer
def makeGetInfoArrayFromTargetViewIMP() -> lldb.SBValue:
    command_script = '''
        NSArray * (^IMPBlock)(UIViewController *, UIView *) = ^NSArray *(UIViewController *vc, UIView *targetView) {
            NSMutableArray *infoArray = [[NSMutableArray alloc] init]; // NSMutableArray<NSArray<NSString *> *> *infoArr
            
            // helper block
            NSString *(^makeColorStringBlock)(UIColor *) = ^NSString *(UIColor *color) {
                CGFloat r, g, b, a;
                [color getRed:&r green:&g blue:&b alpha:&a];
                
                if (a >= 1) {
                    return [[NSString alloc] initWithFormat:@"(%.0lf, %.0lf, %.0lf)", r * 255.0, g * 255.0, b * 255.0];
                } else {
                    return [[NSString alloc] initWithFormat:@"(%.0lf, %.0lf, %.0lf, %.2lf)", r * 255.0, g * 255.0, b * 255.0, a];
                }
            };
            
            NSString *(^getAssetNameBlock)(UIImage *) = ^NSString *(UIImage *img) {
                UIImageAsset *imageAsset = (UIImageAsset *)[img imageAsset];
                if ((BOOL)[imageAsset respondsToSelector:@selector(assetName)] && (BOOL)[imageAsset respondsToSelector:@selector(_assetManager)]) {
                    id assetManager = (id)[imageAsset performSelector:@selector(_assetManager)];
                    if (assetManager) {
                        return (NSString *)[imageAsset performSelector:@selector(assetName)];
                    }
                }
                return @"";
            };
            
            // Address
            NSString *address = [[NSString alloc] initWithFormat:@"%p", targetView];
            [infoArray addObject:@[@"Address", address]];
            // Frame
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
            [infoArray addObject:@[@"Frame", frameStr]];
            
            // BackgroundColor
            if ((UIColor *)[targetView backgroundColor]) {
                NSString *colorString = makeColorStringBlock((UIColor *)[targetView backgroundColor]);
                [infoArray addObject:@[@"BackgroundColor", colorString]];
            }
            
            // Alpha
            if (targetView.alpha < 1) {
                NSString *alphaString = [[NSString alloc] initWithFormat:@"%.2lf", targetView.alpha];
                [infoArray addObject:@[@"Alpha", alphaString]];
            }
            
            // CornerRadius
            if (targetView.layer.cornerRadius > 0) {
                NSString *radiusString = [[NSString alloc] initWithFormat:@"%.2lf", targetView.layer.cornerRadius];
                [infoArray addObject:@[@"CornerRadius", radiusString]];
            }
            
            // BorderColor & BorderWidth
            if (targetView.layer.borderColor && targetView.layer.borderWidth > 0) {
                UIColor *borderColor = [[UIColor alloc] initWithCGColor:targetView.layer.borderColor];
                NSString *colorString = makeColorStringBlock(borderColor);
                [infoArray addObject:@[@"BorderColor", colorString]];
                NSString *widthString = [[NSString alloc] initWithFormat:@"%.2lf", targetView.layer.borderWidth];
                [infoArray addObject:@[@"BorderWidth", widthString]];
            }
            
            // Shadow
            if (targetView.layer.shadowColor && targetView.layer.shadowOpacity > 0) {
                UIColor *shadowColor = [[UIColor alloc] initWithCGColor:targetView.layer.shadowColor];
                [infoArray addObject:@[@"ShadowColor", makeColorStringBlock(shadowColor)]];
                [infoArray addObject:@[@"ShadowOpacity", [[NSString alloc] initWithFormat:@"%.2lf", targetView.layer.shadowOpacity]]];
                [infoArray addObject:@[@"ShadowOffset", [[NSString alloc] initWithFormat:@"%@", NSStringFromCGSize(targetView.layer.shadowOffset)]]];
                [infoArray addObject:@[@"ShadowRadius", [[NSString alloc] initWithFormat:@"%.2lf", targetView.layer.shadowRadius]]];
            }
            
            // UIImageView
            // UIButton
            // UILabel
            // UIScrollView
            // UITextView
            // UITextField
            if ([targetView isKindOfClass:[UIImageView class]]) {
                UIImageView *imageView = (UIImageView *)targetView;
                NSString *assetName = getAssetNameBlock([imageView image]);
                if ([assetName length] > 0) {
                    [infoArray addObject:@[@"AssetName", assetName]];
                }
            } else if ([targetView isKindOfClass:[UIButton class]]) {
                UIButton *btn = (UIButton *)targetView;
                if ([btn titleForState:0].length) { // UIControlStateNormal
                    [infoArray addObject:@[@"FontSize", [[NSString alloc] initWithFormat:@"%.2lf", btn.titleLabel.font.pointSize]]];
                    [infoArray addObject:@[@"FontName", btn.titleLabel.font.fontName]];
                    [infoArray addObject:@[@"TextColor", makeColorStringBlock(btn.titleLabel.textColor)]];
                }
                NSString *assetName = getAssetNameBlock([btn imageForState:0]); // UIControlStateNormal
                if ([assetName length] > 0) {
                    [infoArray addObject:@[@"AssetName.normal", assetName]];
                }
            } else if ([targetView isKindOfClass:[UILabel class]]) {
                UILabel *label = (UILabel *)targetView;
                [infoArray addObject:@[@"FontSize", [[NSString alloc] initWithFormat:@"%.2lf", label.font.pointSize]]];
                [infoArray addObject:@[@"FontName", label.font.fontName]];
                [infoArray addObject:@[@"TextColor", makeColorStringBlock(label.textColor)]];
                [infoArray addObject:@[@"NumberOfLines", [NSString stringWithFormat:@"%ld", label.numberOfLines]]];
            } else if ([targetView isKindOfClass:[UIScrollView class]]) {
                UIScrollView *scrollView = (UIScrollView *)targetView;
                [infoArray addObject:@[@"ContentSize", NSStringFromCGSize(scrollView.contentSize)]];
                [infoArray addObject:@[@"ContentOffset", NSStringFromCGPoint(scrollView.contentOffset)]];
                [infoArray addObject:@[@"ContentInset", NSStringFromUIEdgeInsets(scrollView.contentInset)]];
                if ([scrollView respondsToSelector:@selector(adjustedContentInset)]) {
                    [infoArray addObject:@[@"AdjustedContentInset", NSStringFromUIEdgeInsets(scrollView.adjustedContentInset)]];
                }
                
                if ([scrollView isKindOfClass:[UITextView class]]) {
                    UITextView *textView = (UITextView *)scrollView;
                    [infoArray addObject:@[@"FontSize", [[NSString alloc] initWithFormat:@"%.2lf", textView.font.pointSize]]];
                    [infoArray addObject:@[@"FontName", textView.font.fontName]];
                    [infoArray addObject:@[@"TextColor", makeColorStringBlock(textView.textColor)]];
                }
            } else if ([targetView isKindOfClass:[UITextField class]]) {
                UITextField *textField = (UITextField *)targetView;
                [infoArray addObject:@[@"FontSize", [[NSString alloc] initWithFormat:@"%.2lf", textField.font.pointSize]]];
                [infoArray addObject:@[@"FontName", textField.font.fontName]];
                [infoArray addObject:@[@"TextColor", makeColorStringBlock(textField.textColor)]];
            }
            
            return [infoArray copy];
        };
    
        imp_implementationWithBlock(IMPBlock);
     '''
    return HM.evaluateExpressionValue(command_script)


def addFunctionMethods() -> bool:
    clickMoveBtnIMPValue = makeClickMoveBtnIMP()
    if not HM.judgeSBValueHasValue(clickMoveBtnIMPValue):
        return False
    HM.addInstanceMethod(gClassName, "clickMoveBtn:", clickMoveBtnIMPValue.GetValue(), "v@:@")

    ivarsActionIMPValue = makeIvarsActionIMP()
    if not HM.judgeSBValueHasValue(ivarsActionIMPValue):
        return False
    HM.addInstanceMethod(gClassName, "ivarsAction", ivarsActionIMPValue.GetValue(), "v@:")

    propertiesActionIMPValue = makePropertiesActionIMP()
    if not HM.judgeSBValueHasValue(propertiesActionIMPValue):
        return False
    HM.addInstanceMethod(gClassName, "propertiesAction", propertiesActionIMPValue.GetValue(), "v@:")

    methodsActionIMPValue = makeMethodsActionIMP()
    if not HM.judgeSBValueHasValue(methodsActionIMPValue):
        return False
    HM.addInstanceMethod(gClassName, "methodsAction", methodsActionIMPValue.GetValue(), "v@:")

    siblingNextActionIMPValue = makeSiblingNextActionIMP()
    if not HM.judgeSBValueHasValue(siblingNextActionIMPValue):
        return False
    HM.addInstanceMethod(gClassName, "siblingNextAction", siblingNextActionIMPValue.GetValue(), "v@:")

    siblingPreviousActionIMPValue = makeSiblingPreviousActionIMP()
    if not HM.judgeSBValueHasValue(siblingPreviousActionIMPValue):
        return False
    HM.addInstanceMethod(gClassName, "siblingPreviousAction", siblingPreviousActionIMPValue.GetValue(), "v@:")

    superviewActionIMPValue = makeSuperviewActionIMP()
    if not HM.judgeSBValueHasValue(superviewActionIMPValue):
        return False
    HM.addInstanceMethod(gClassName, "superviewAction", superviewActionIMPValue.GetValue(), "v@:")

    subviewActionIMPValue = makeSubviewActionIMP()
    if not HM.judgeSBValueHasValue(subviewActionIMPValue):
        return False
    HM.addInstanceMethod(gClassName, "subviewAction", subviewActionIMPValue.GetValue(), "v@:")

    return True


def makeClickMoveBtnIMP() -> lldb.SBValue:
    command_script = '''
        void (^IMPBlock)(UIViewController *, UIButton *) = ^(UIViewController *vc, UIButton *btn) {
            UIView *_targetView = (UIView *)[vc valueForKey:@"_targetView"];
            CGRect targetFrame = [_targetView frame];
            if (btn.tag == 1) {
                targetFrame.origin.y = targetFrame.origin.y - 1;
            } else if (btn.tag == 2) {
                targetFrame.origin.x = targetFrame.origin.x - 1;
            } else if (btn.tag == 3) {
                targetFrame.origin.y = targetFrame.origin.y + 1;
            } else if (btn.tag == 4) {
                targetFrame.origin.x = targetFrame.origin.x + 1;
            }
            
            (void)[_targetView setFrame:(CGRect)targetFrame];
            (void)[vc performSelector:@selector(refreshTargetView:) withObject:(id)_targetView];
        };
        imp_implementationWithBlock(IMPBlock);
     '''
    return HM.evaluateExpressionValue(expression=command_script, prefix=HMExpressionPrefix.gPrefix)


def makeIvarsActionIMP() -> lldb.SBValue:
    command_script = f'''
        void (^IMPBlock)(UIViewController *) = ^(UIViewController *vc) {{
            UIView *_targetView = (UIView *)[vc valueForKey:@"_targetView"];
            NSString *desc = (NSString *)[_targetView performSelector:NSSelectorFromString(@"_ivarDescription")];
            printf("\\n[HMLLDB]: _ivarDescription:\\n%s\\n", (char *)[desc UTF8String]);
            
            Class progressHUDCls = (Class)objc_lookUpClass("{HMProgressHUD.gClassName}");
            ((id (*)(id, SEL, id, int)) objc_msgSend)((id)progressHUDCls, @selector(showOnlyText:hiddenAfterDelay:), @"Please check the Xcode console output", 4);
        }};
        imp_implementationWithBlock(IMPBlock);
     '''
    return HM.evaluateExpressionValue(command_script)


def makePropertiesActionIMP() -> lldb.SBValue:
    command_script = f'''
        void (^IMPBlock)(UIViewController *) = ^(UIViewController *vc) {{
            UIView *_targetView = (UIView *)[vc valueForKey:@"_targetView"];
            NSString *desc = (NSString *)[_targetView performSelector:NSSelectorFromString(@"_propertyDescription")];
            printf("\\n[HMLLDB]: _propertyDescription:\\n%s\\n", (char *)[desc UTF8String]);
            
            Class progressHUDCls = (Class)objc_lookUpClass("{HMProgressHUD.gClassName}");
            ((id (*)(id, SEL, id, int)) objc_msgSend)((id)progressHUDCls, @selector(showOnlyText:hiddenAfterDelay:), @"Please check the Xcode console output", 4);
        }};
        imp_implementationWithBlock(IMPBlock);
     '''
    return HM.evaluateExpressionValue(command_script)


def makeMethodsActionIMP() -> lldb.SBValue:
    command_script = f'''
        void (^IMPBlock)(UIViewController *) = ^(UIViewController *vc) {{
            UIView *_targetView = (UIView *)[vc valueForKey:@"_targetView"];
            NSString *desc = (NSString *)[_targetView performSelector:NSSelectorFromString(@"_methodDescription")];
            printf("\\n[HMLLDB]: _methodDescription:\\n%s\\n", (char *)[desc UTF8String]);
            
            Class progressHUDCls = (Class)objc_lookUpClass("{HMProgressHUD.gClassName}");
            ((id (*)(id, SEL, id, int)) objc_msgSend)((id)progressHUDCls, @selector(showOnlyText:hiddenAfterDelay:), @"Please check the Xcode console output", 4);
        }};
        imp_implementationWithBlock(IMPBlock);
     '''
    return HM.evaluateExpressionValue(command_script)


def makeSiblingNextActionIMP() -> lldb.SBValue:
    command_script = '''
        void (^IMPBlock)(UIViewController *) = ^(UIViewController *vc) {
            UIView *_targetView = (UIView *)[vc valueForKey:@"_targetView"];
            NSArray *siblings = [[_targetView superview] subviews];
            if (siblings != nil) {
                NSInteger index = [siblings indexOfObject:_targetView];
                index = index + 1;
                if (index >= [siblings count]) {
                    index = 0;
                }
                UIView *targetSibling = [siblings objectAtIndex:index];
                printf("\\n[HMLLDB]: %s\\n", (char *)[[targetSibling description] UTF8String]);
                (void)[vc performSelector:@selector(refreshTargetView:) withObject:(id)targetSibling];
            }
        };
        imp_implementationWithBlock(IMPBlock);
     '''
    return HM.evaluateExpressionValue(command_script)


def makeSiblingPreviousActionIMP() -> lldb.SBValue:
    command_script = '''
        void (^IMPBlock)(UIViewController *) = ^(UIViewController *vc) {
            UIView *_targetView = (UIView *)[vc valueForKey:@"_targetView"];
            NSArray *siblings = [[_targetView superview] subviews];
            if (siblings != nil) {
                NSInteger index = [siblings indexOfObject:_targetView];
                index = index - 1;
                if (index < 0) {
                    index = [siblings count] - 1;
                }
                UIView *targetSibling = [siblings objectAtIndex:index];
                printf("\\n[HMLLDB]: %s\\n", (char *)[[targetSibling description] UTF8String]);
                (void)[vc performSelector:@selector(refreshTargetView:) withObject:(id)targetSibling];
            }
        };        
        imp_implementationWithBlock(IMPBlock);
     '''
    return HM.evaluateExpressionValue(command_script)


def makeSuperviewActionIMP() -> lldb.SBValue:
    command_script = '''
        void (^IMPBlock)(UIViewController *) = ^(UIViewController *vc) {
            UIView *_targetView = (UIView *)[vc valueForKey:@"_targetView"];
            UIView *targetSuperView = [_targetView superview];
            if (targetSuperView != nil) {
                printf("\\n[HMLLDB]: %s\\n", (char *)[[targetSuperView description] UTF8String]);
                (void)[vc performSelector:@selector(refreshTargetView:) withObject:(id)targetSuperView];
            }
        };       
        imp_implementationWithBlock(IMPBlock);
     '''
    return HM.evaluateExpressionValue(command_script)


def makeSubviewActionIMP() -> lldb.SBValue:
    command_script = '''
        void (^IMPBlock)(UIViewController *) = ^(UIViewController *vc) {
            UIView *_targetView = (UIView *)[vc valueForKey:@"_targetView"];
            UIView *targetSubview = [[_targetView subviews] firstObject];
            if (targetSubview != nil) {
                printf("\\n[HMLLDB]: %s\\n", (char *)[[targetSubview description] UTF8String]);
                (void)[vc performSelector:@selector(refreshTargetView:) withObject:(id)targetSubview];
            }
        };     
        imp_implementationWithBlock(IMPBlock);
     '''
    return HM.evaluateExpressionValue(command_script)

