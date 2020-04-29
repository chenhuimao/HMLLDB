""" File: HMProgressHUD.py

Implementation of HMProgressHUD class.

"""

import lldb
from typing import Optional
import HMLLDBHelpers as HM
import HMLLDBClassInfo


gClassName = "HMProgressHUD"


def register() -> None:

    if HM.existClass(gClassName):
        return

    # Register class
    HM.DPrint("Register {arg0}...".format(arg0=gClassName))
    classValue = HM.allocateClass(gClassName, "UIView")
    HM.addIvar(classValue.GetValue(), "_contentView", "UIView *")
    HM.addIvar(classValue.GetValue(), "_indicator", "UIActivityIndicatorView *")
    HM.addIvar(classValue.GetValue(), "_textLab", "UILabel *")
    HM.registerClass(classValue.GetValue())

    # Add Class methods
    HM.DPrint("Add methods to {arg0}...".format(arg0=gClassName))
    sharedInstanceIMPValue = makeSharedInstanceIMP()
    if not HM.judgeSBValueHasValue(sharedInstanceIMPValue):
        return
    HM.addClassMethod(gClassName, "sharedInstance", sharedInstanceIMPValue.GetValue(), "@@:")

    showHUDIMPValue = makeShowHUDIMP()
    if not HM.judgeSBValueHasValue(showHUDIMPValue):
        return
    HM.addClassMethod(gClassName, "showHUD", showHUDIMPValue.GetValue(), "@@:")

    hideHUDIMPValue = makeHideHUDIMP()
    if not HM.judgeSBValueHasValue(hideHUDIMPValue):
        return
    HM.addClassMethod(gClassName, "hideHUD", hideHUDIMPValue.GetValue(), "@@:")

    setTextIMPValue = makeSetTextIMP()
    if not HM.judgeSBValueHasValue(setTextIMPValue):
        return
    HM.addClassMethod(gClassName, "setText:", setTextIMPValue.GetValue(), "v@:@")

    # Add Instance methods
    HM.DPrint("Add methods to {arg0}......".format(arg0=gClassName))
    initWithFrameIMPValue = makeInitWithFrameIMP()
    if not HM.judgeSBValueHasValue(initWithFrameIMPValue):
        return
    HM.addInstanceMethod(gClassName, "initWithFrame:", initWithFrameIMPValue.GetValue(), "@@:{CGRect={CGPoint=dd}{CGSize=dd}}")

    layoutSubviewsIMPValue = makeLayoutSubviewsIMP()
    if not HM.judgeSBValueHasValue(layoutSubviewsIMPValue):
        return
    HM.addInstanceMethod(gClassName, "layoutSubviews", layoutSubviewsIMPValue.GetValue(), "v@:")

    HM.DPrint("Register {arg0} done!".format(arg0=gClassName))


def show(text: Optional[str]) -> None:
    command_script = '''
        Class progressHUDCls = (Class)objc_getClass("{arg0}");
        (UIView *)[progressHUDCls performSelector:@selector(showHUD)];
    '''.format(arg0=gClassName)

    if len(text) > 0:
        command_script += '(void)[progressHUDCls performSelector:@selector(setText:) withObject:@"{arg1}"];'.format(arg1=text)
        HM.DPrint(text)

    command_script += "(void)[CATransaction flush];"
    HM.evaluateExpressionValue(command_script)


def hide() -> None:
    command_script = '''
        Class progressHUDCls = (Class)objc_getClass("{arg0}");
        (UIView *)[progressHUDCls performSelector:@selector(hideHUD)];
        (void)[CATransaction flush];
    '''.format(arg0=gClassName)
    HM.evaluateExpressionValue(command_script)


def makeSharedInstanceIMP() -> lldb.SBValue:
    command_script = '''
        UIView * (^IMPBlock)(id) = ^UIView *(id classSelf) {{
            static id {arg0}Instance;
            static dispatch_once_t {arg0}Token;
            _dispatch_once(&{arg0}Token, ^{{
                {arg0}Instance = (UIView *)[[(Class)objc_getClass("{arg0}") alloc] init];
            }});
            
            return {arg0}Instance;
        }};

        (IMP)imp_implementationWithBlock(IMPBlock);    
    '''.format(arg0=gClassName)

    return HM.evaluateExpressionValue(command_script)


def makeShowHUDIMP() -> lldb.SBValue:
    command_script = '''
        UIView * (^IMPBlock)(id) = ^UIView *(id classSelf) {{
            
            UIView *HUD = (UIView *)[(Class)objc_getClass("{arg0}") performSelector:@selector(sharedInstance)];
            
            if ([HUD superview] == nil) {{
                [[UIApplication sharedApplication].keyWindow addSubview:HUD];
            }} else {{
                [[HUD superview] bringSubviewToFront:HUD];
            }}
            
            UIActivityIndicatorView *indicator = [HUD valueForKey:@"_indicator"];
            [indicator startAnimating];
            
            [HUD setNeedsLayout];
            [HUD layoutIfNeeded];
            
            return HUD;
        }};

        (IMP)imp_implementationWithBlock(IMPBlock);    
    '''.format(arg0=gClassName)

    return HM.evaluateExpressionValue(command_script)


def makeHideHUDIMP() -> lldb.SBValue:
    command_script = '''
        UIView * (^IMPBlock)(id) = ^UIView *(id classSelf) {{
            
            UIView *HUD = (UIView *)[(Class)objc_getClass("{arg0}") performSelector:@selector(sharedInstance)];
            [HUD removeFromSuperview];
            UIActivityIndicatorView *indicator = [HUD valueForKey:@"_indicator"];
            [indicator stopAnimating];
            UILabel *textLab = (UILabel *)[HUD valueForKey:@"_textLab"];
            [textLab setText:@""];
            
            return HUD;
        }};

        (IMP)imp_implementationWithBlock(IMPBlock);    
    '''.format(arg0=gClassName)

    return HM.evaluateExpressionValue(command_script)


def makeSetTextIMP() -> lldb.SBValue:
    command_script = '''
        void (^IMPBlock)(id, NSString *) = ^(id classSelf, NSString *text) {{
            
            UIView *HUD = (UIView *)[(Class)objc_getClass("{arg0}") performSelector:@selector(sharedInstance)];
            UILabel *textLab = (UILabel *)[HUD valueForKey:@"_textLab"];
            [textLab setText:text];
            
            [HUD setNeedsLayout];
            [HUD layoutIfNeeded];
        }};

        (IMP)imp_implementationWithBlock(IMPBlock);    
    '''.format(arg0=gClassName)

    return HM.evaluateExpressionValue(command_script)


def makeInitWithFrameIMP() -> lldb.SBValue:
    command_script = '''
        UIView * (^IMPBlock)(UIView *, CGRect) = ^UIView *(UIView *HUD, CGRect frame) {
            
            struct objc_super superInfo = {
                .receiver = HUD,
                .super_class = (Class)class_getSuperclass((Class)[HUD class])
            };
    
            CGRect screenFrame = [UIScreen mainScreen].bounds;
            HUD = ((UIView * (*)(struct objc_super *, SEL, CGRect))objc_msgSendSuper)(&superInfo, @selector(initWithFrame:), screenFrame);
            
            if (HUD != nil) {
                UIColor *color = [[UIColor alloc] initWithRed:0.24 green:0.24 blue:0.24 alpha:1];
                
                UIView *contentView = [[UIView alloc] init];
                [HUD setValue:contentView forKey:@"_contentView"];
                (void)[contentView setBackgroundColor:[[UIColor alloc] initWithRed:0.9 green:0.9 blue:0.9 alpha:1]];
                contentView.layer.cornerRadius = 5.0;
                [HUD addSubview:contentView];
    
                UIActivityIndicatorView *indicator = [[UIActivityIndicatorView alloc] initWithActivityIndicatorStyle:(UIActivityIndicatorViewStyle)UIActivityIndicatorViewStyleWhiteLarge];
                [HUD setValue:indicator forKey:@"_indicator"];
                indicator.color = color;
                [contentView addSubview:indicator];
                
                UILabel *textLab = [[UILabel alloc] init];
                [HUD setValue:textLab forKey:@"_textLab"];
                textLab.font = [UIFont boldSystemFontOfSize:15];
                textLab.textColor = color;
                textLab.textAlignment = NSTextAlignmentCenter;
                [contentView addSubview:textLab];
            }
            
            return HUD;
        };

        (IMP)imp_implementationWithBlock(IMPBlock);    
    '''

    return HM.evaluateExpressionValue(command_script)


def makeLayoutSubviewsIMP() -> lldb.SBValue:
    command_script = '''
        void (^IMPBlock)(UIView *) = ^(UIView *HUD) {
            
            struct objc_super superInfo = {
                .receiver = HUD,
                .super_class = (Class)class_getSuperclass((Class)[HUD class])
            };
            ((void * (*)(struct objc_super *, SEL))objc_msgSendSuper)(&superInfo, @selector(layoutSubviews));
            
            
            UILabel *textLab = (UILabel *)[HUD valueForKey:@"_textLab"];
            
            UIView *contentView = [HUD valueForKey:@"_contentView"];
            CGFloat contentViewHeight = 80;
            if ([textLab.text length] > 0) {
                contentViewHeight = 100;
            }
            CGFloat contentViewWidth = 80;
            if (textLab.intrinsicContentSize.width + 30 > contentViewWidth) {
                contentViewWidth = textLab.intrinsicContentSize.width + 30;
            }
            if (contentViewWidth > HUD.bounds.size.width) {
                contentViewWidth = HUD.bounds.size.width;
            }
                    
            contentView.bounds = (CGRect){0, 0, contentViewWidth, contentViewHeight};
            contentView.center = (CGPoint){HUD.bounds.size.width / 2, HUD.bounds.size.height / 2};
            
            UIActivityIndicatorView *indicator = [HUD valueForKey:@"_indicator"];
            CGFloat indicatorWidth = indicator.intrinsicContentSize.width;
            CGFloat indicatorHeight = indicator.intrinsicContentSize.height;
            if ([textLab.text length] > 0) {
                indicator.frame = (CGRect){(contentViewWidth - indicatorWidth) / 2, 20, indicatorWidth, indicatorHeight};
            } else {
                indicator.frame = (CGRect){(contentViewWidth - indicatorWidth) / 2, (contentViewHeight - indicatorHeight) / 2, indicatorWidth, indicatorHeight};
            }
            
            if ([textLab.text length] > 0) {
                CGFloat textLabHeight = textLab.intrinsicContentSize.height;
                textLab.frame = (CGRect){0, contentViewHeight - 15 - textLabHeight, contentViewWidth, textLabHeight};
            }
        };

        (IMP)imp_implementationWithBlock(IMPBlock);    
    '''

    return HM.evaluateExpressionValue(command_script)
