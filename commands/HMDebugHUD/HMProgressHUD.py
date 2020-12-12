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
from typing import Optional
import HMLLDBHelpers as HM
import HMExpressionPrefix
import HMLLDBClassInfo


gClassName = "HMProgressHUD"


def register() -> None:

    if HM.existClass(gClassName):
        return

    # Register class
    HM.DPrint(f"Register {gClassName}...")
    classValue = HM.allocateClass(gClassName, "UIView")
    HM.addIvar(classValue.GetValue(), "_contentView", "UIView *")
    HM.addIvar(classValue.GetValue(), "_indicator", "UIActivityIndicatorView *")
    HM.addIvar(classValue.GetValue(), "_textLab", "UILabel *")
    HM.addIvar(classValue.GetValue(), "_hideDelayTimer", "NSTimer *")
    HM.registerClass(classValue.GetValue())

    # Add Class methods
    HM.DPrint(f"Add methods to {gClassName}...")
    sharedInstanceIMPValue = makeSharedInstanceIMP()
    if not HM.judgeSBValueHasValue(sharedInstanceIMPValue):
        return
    HM.addClassMethod(gClassName, "sharedInstance", sharedInstanceIMPValue.GetValue(), "@@:")

    showHUDIMPValue = makeShowHUDIMP()
    if not HM.judgeSBValueHasValue(showHUDIMPValue):
        return
    HM.addClassMethod(gClassName, "showHUD", showHUDIMPValue.GetValue(), "@@:")

    showOnlyTextIMPValue = makeShowOnlyTextHiddenAfterDelayIMP()
    if not HM.judgeSBValueHasValue(showOnlyTextIMPValue):
        return
    HM.addClassMethod(gClassName, "showOnlyText:hiddenAfterDelay:", showOnlyTextIMPValue.GetValue(), "@@:@i")

    hideHUDIMPValue = makeHideHUDIMP()
    if not HM.judgeSBValueHasValue(hideHUDIMPValue):
        return
    HM.addClassMethod(gClassName, "hideHUD", hideHUDIMPValue.GetValue(), "@@:")

    setTextIMPValue = makeSetTextIMP()
    if not HM.judgeSBValueHasValue(setTextIMPValue):
        return
    HM.addClassMethod(gClassName, "setText:", setTextIMPValue.GetValue(), "v@:@")

    # Add Instance methods
    HM.DPrint(f"Add methods to {gClassName}......")
    initWithFrameIMPValue = makeInitWithFrameIMP()
    if not HM.judgeSBValueHasValue(initWithFrameIMPValue):
        return
    HM.addInstanceMethod(gClassName, "initWithFrame:", initWithFrameIMPValue.GetValue(), "@@:{CGRect={CGPoint=dd}{CGSize=dd}}")

    layoutSubviewsIMPValue = makeLayoutSubviewsIMP()
    if not HM.judgeSBValueHasValue(layoutSubviewsIMPValue):
        return
    HM.addInstanceMethod(gClassName, "layoutSubviews", layoutSubviewsIMPValue.GetValue(), "v@:")

    HM.DPrint(f"Register {gClassName} done!")


def show(text: Optional[str]) -> None:

    register()

    command_script = f'''
        Class progressHUDCls = (Class)objc_lookUpClass("{gClassName}");
        (UIView *)[progressHUDCls performSelector:@selector(showHUD)];
    '''

    if len(text) > 0:
        command_script += f'(void)[progressHUDCls performSelector:@selector(setText:) withObject:@"{text}"];'

    command_script += "(void)[CATransaction flush];"
    HM.evaluateExpressionValue(command_script)


def hide() -> None:
    command_script = f'''
        Class progressHUDCls = (Class)objc_lookUpClass("{gClassName}");
        (UIView *)[progressHUDCls performSelector:@selector(hideHUD)];
        (void)[CATransaction flush];
    '''
    HM.evaluateExpressionValue(command_script)


def makeSharedInstanceIMP() -> lldb.SBValue:
    command_script = f'''
        UIView * (^IMPBlock)(id) = ^UIView *(id classSelf) {{
            static id {gClassName}Instance;
            static dispatch_once_t {gClassName}Token;
            _dispatch_once(&{gClassName}Token, ^{{
                {gClassName}Instance = (UIView *)[[(Class)objc_lookUpClass("{gClassName}") alloc] init];
            }});
            
            return {gClassName}Instance;
        }};

        imp_implementationWithBlock(IMPBlock);    
    '''

    return HM.evaluateExpressionValue(command_script)


def makeShowHUDIMP() -> lldb.SBValue:
    command_script = f'''
        UIView * (^IMPBlock)(id) = ^UIView *(id classSelf) {{
            
            UIView *HUD = (UIView *)[(Class)objc_lookUpClass("{gClassName}") performSelector:@selector(sharedInstance)];
            
            if ([HUD superview] == nil) {{
                [[UIApplication sharedApplication].keyWindow addSubview:HUD];
            }} else {{
                [[HUD superview] bringSubviewToFront:HUD];
            }}
                        
            UIActivityIndicatorView *indicator = (UIActivityIndicatorView *)[HUD valueForKey:@"_indicator"];
            [indicator setHidden:NO];
            [indicator startAnimating];

            [HUD setNeedsLayout];
            [HUD layoutIfNeeded];
            
            return HUD;
        }};

        imp_implementationWithBlock(IMPBlock);    
    '''

    return HM.evaluateExpressionValue(command_script)


def makeShowOnlyTextHiddenAfterDelayIMP() -> lldb.SBValue:
    command_script = f'''
        UIView * (^IMPBlock)(id, NSString *, int) = ^UIView *(id classSelf, NSString *text, int delay) {{
            
            UIView *HUD = (UIView *)[(Class)objc_lookUpClass("{gClassName}") performSelector:@selector(sharedInstance)];
            
            if ([HUD superview] == nil) {{
                [[UIApplication sharedApplication].keyWindow addSubview:HUD];
            }} else {{
                [[HUD superview] bringSubviewToFront:HUD];
            }}
            
            UIActivityIndicatorView *indicator = (UIActivityIndicatorView *)[HUD valueForKey:@"_indicator"];
            [indicator setHidden:YES];
            [indicator stopAnimating];

            UILabel *textLab = (UILabel *)[HUD valueForKey:@"_textLab"];
            [textLab setText:text];
            
            NSTimer * _hideDelayTimer = (NSTimer *)[HUD valueForKey:@"_hideDelayTimer"];
            [_hideDelayTimer invalidate];

            NSTimer *timer = [NSTimer timerWithTimeInterval:delay target:classSelf selector:@selector(hideHUD) userInfo:nil repeats:NO];
            [[NSRunLoop currentRunLoop] addTimer:timer forMode:NSRunLoopCommonModes];
            [HUD setValue:timer forKey:@"_hideDelayTimer"];

            [HUD setNeedsLayout];
            [HUD layoutIfNeeded];
            
            return HUD;
        }};

        imp_implementationWithBlock(IMPBlock);    
    '''

    return HM.evaluateExpressionValue(command_script)


def makeHideHUDIMP() -> lldb.SBValue:
    command_script = f'''
        UIView * (^IMPBlock)(id) = ^UIView *(id classSelf) {{
            
            UIView *HUD = (UIView *)[(Class)objc_lookUpClass("{gClassName}") performSelector:@selector(sharedInstance)];
            [HUD removeFromSuperview];
            UIActivityIndicatorView *indicator = [HUD valueForKey:@"_indicator"];
            [indicator stopAnimating];
            UILabel *textLab = (UILabel *)[HUD valueForKey:@"_textLab"];
            [textLab setText:@""];
            
            NSTimer * _hideDelayTimer = (NSTimer *)[HUD valueForKey:@"_hideDelayTimer"];
            [_hideDelayTimer invalidate];
            return HUD;
        }};

        imp_implementationWithBlock(IMPBlock);    
    '''

    return HM.evaluateExpressionValue(command_script)


def makeSetTextIMP() -> lldb.SBValue:
    command_script = f'''
        void (^IMPBlock)(id, NSString *) = ^(id classSelf, NSString *text) {{
            
            UIView *HUD = (UIView *)[(Class)objc_lookUpClass("{gClassName}") performSelector:@selector(sharedInstance)];
            UILabel *textLab = (UILabel *)[HUD valueForKey:@"_textLab"];
            [textLab setText:text];
            
            [HUD setNeedsLayout];
            [HUD layoutIfNeeded];
        }};

        imp_implementationWithBlock(IMPBlock);    
    '''

    return HM.evaluateExpressionValue(command_script)


def makeInitWithFrameIMP() -> lldb.SBValue:
    command_script = f'''
        UIView * (^IMPBlock)(UIView *, CGRect) = ^UIView *(UIView *HUD, CGRect frame) {{
            Class cls = objc_lookUpClass("{gClassName}");
            struct objc_super superInfo = {{
                .receiver = HUD,
                .super_class = (Class)class_getSuperclass((Class)cls)
            }};
    
            CGRect screenFrame = [UIScreen mainScreen].bounds;
            HUD = ((UIView * (*)(struct objc_super *, SEL, CGRect))objc_msgSendSuper)(&superInfo, @selector(initWithFrame:), screenFrame);
            
            if (HUD != nil) {{
                UIColor *color = [[UIColor alloc] initWithRed:0.24 green:0.24 blue:0.24 alpha:1];
                
                UIView *contentView = [[UIView alloc] init];
                [HUD setValue:contentView forKey:@"_contentView"];
                (void)[contentView setBackgroundColor:[[UIColor alloc] initWithRed:0.9 green:0.9 blue:0.9 alpha:1]];
                contentView.layer.cornerRadius = 5.0;
                [HUD addSubview:contentView];
    
                UIActivityIndicatorView *indicator = [[UIActivityIndicatorView alloc] initWithActivityIndicatorStyle:(UIActivityIndicatorViewStyle)0];
                [HUD setValue:indicator forKey:@"_indicator"];
                indicator.color = color;
                [contentView addSubview:indicator];
                
                UILabel *textLab = [[UILabel alloc] init];
                [HUD setValue:textLab forKey:@"_textLab"];
                textLab.font = [UIFont boldSystemFontOfSize:15];
                textLab.textColor = color;
                textLab.textAlignment = (NSTextAlignment)1;
                [contentView addSubview:textLab];
            }}
            
            return HUD;
        }};

        imp_implementationWithBlock(IMPBlock);    
    '''

    return HM.evaluateExpressionValue(expression=command_script, prefix=HMExpressionPrefix.gPrefix)


def makeLayoutSubviewsIMP() -> lldb.SBValue:
    command_script = f'''
        void (^IMPBlock)(UIView *) = ^(UIView *HUD) {{
            Class cls = objc_lookUpClass("{gClassName}");
            struct objc_super superInfo = {{
                .receiver = HUD,
                .super_class = (Class)class_getSuperclass((Class)cls)
            }};
            ((void * (*)(struct objc_super *, SEL))objc_msgSendSuper)(&superInfo, @selector(layoutSubviews));
            
            
            UILabel *textLab = (UILabel *)[HUD valueForKey:@"_textLab"];
            UIView *contentView = (UIView *)[HUD valueForKey:@"_contentView"];

            CGFloat contentViewHeight = 80;
            if ([textLab.text length] > 0) {{
                contentViewHeight = 100;
            }}
            CGFloat contentViewWidth = 80;
            if (textLab.intrinsicContentSize.width + 30 > contentViewWidth) {{
                contentViewWidth = textLab.intrinsicContentSize.width + 30;
            }}
            if (contentViewWidth > HUD.bounds.size.width) {{
                contentViewWidth = HUD.bounds.size.width;
            }}
                    
            (void)[contentView setBounds:(CGRect){{0, 0, contentViewWidth, contentViewHeight}}];
            (void)[contentView setCenter:(CGPoint){{HUD.bounds.size.width / 2, HUD.bounds.size.height / 2}}];
            
            UIActivityIndicatorView *indicator = (UIActivityIndicatorView *)[HUD valueForKey:@"_indicator"];
            CGFloat indicatorWidth = indicator.intrinsicContentSize.width;
            CGFloat indicatorHeight = indicator.intrinsicContentSize.height;
            if ([textLab.text length] > 0) {{
                (void)[indicator setFrame:(CGRect){{(contentViewWidth - indicatorWidth) / 2, 20, indicatorWidth, indicatorHeight}}];
            }} else {{
                (void)[indicator setFrame:(CGRect){{(contentViewWidth - indicatorWidth) / 2, (contentViewHeight - indicatorHeight) / 2, indicatorWidth, indicatorHeight}}];
            }}
            
            if ([textLab.text length] > 0) {{
                CGFloat textLabHeight = textLab.intrinsicContentSize.height;
                (void)[textLab setFrame:(CGRect){{0, contentViewHeight - 15 - textLabHeight, contentViewWidth, textLabHeight}}];
            }}

            if ([indicator isHidden]) {{
                contentView.bounds = (CGRect){{0, 0, contentViewWidth, textLab.intrinsicContentSize.height + 40}};
                (void)[textLab setFrame:contentView.bounds];
            }}
        }};

        imp_implementationWithBlock(IMPBlock);    
    '''

    return HM.evaluateExpressionValue(command_script)
