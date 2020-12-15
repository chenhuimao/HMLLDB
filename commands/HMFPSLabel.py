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
import HMExpressionPrefix
import HMLLDBClassInfo


def __lldb_init_module(debugger, internal_dict):
    debugger.HandleCommand('command script add -f HMFPSLabel.showFPS showfps -h "(deprecated)Show the FPS on key window(main thread)."')


def showFPS(debugger, command, exe_ctx, result, internal_dict):
    """
    Syntax:
        showfps

    Examples:
        (lldb) showfps

    Notice:
        showfps is deprecated. Use showhud instead.

    This command is implemented in HMFPSLabel.py
    """

    HM.DPrint("showfps is deprecated. Use showhud instead.")

    FPSClassName = "HMFPSLabel"
    if HM.existClass(FPSClassName):
        HM.DPrint("HMFPSLabel is already on display")
        return

    # Register class
    FPSLabelClassValue = HM.allocateClass(FPSClassName, "UILabel")
    HM.addIvar(FPSLabelClassValue.GetValue(), "_link", "CADisplayLink *")
    HM.addIvar(FPSLabelClassValue.GetValue(), "_count", "int")
    HM.addIvar(FPSLabelClassValue.GetValue(), "_lastTime", "double")
    HM.registerClass(FPSLabelClassValue.GetValue())

    addToKeyWindowIMPValue = makeAddToKeyWindowIMP()
    if not HM.judgeSBValueHasValue(addToKeyWindowIMPValue):
        return
    HM.addClassMethod(FPSClassName, "addToKeyWindow", addToKeyWindowIMPValue.GetValue(), "@@:")

    tickIMPValue = makeTickIMP()
    if not HM.judgeSBValueHasValue(tickIMPValue):
        return
    HM.addInstanceMethod(FPSClassName, "tick:", tickIMPValue.GetValue(), "v@:@")

    # Show fps command
    addToKeyWindowCommand = '''
        Class fps = NSClassFromString(@"HMFPSLabel");
        (UILabel *)[fps performSelector:@selector(addToKeyWindow)];
    '''
    HM.evaluateExpressionValue(addToKeyWindowCommand)

    HM.DPrint("showfps Done!")
    HM.processContinue()


def makeAddToKeyWindowIMP() -> lldb.SBValue:
    command_script = '''

        UILabel * (^addToKeyWindowBlock)(id) = ^UILabel *(id classSelf) {
            UILabel *fpsLabel = (UILabel *)[[NSClassFromString(@"HMFPSLabel") alloc] init];
            (void)[fpsLabel setFrame:(CGRect){60, [UIApplication sharedApplication].statusBarFrame.size.height, 58, 20}];
            fpsLabel.layer.zPosition = 100;
            fpsLabel.layer.cornerRadius = 5;
            fpsLabel.clipsToBounds = YES;
            fpsLabel.textAlignment = (NSTextAlignment)1;
            fpsLabel.userInteractionEnabled = NO;
            (void)[fpsLabel setBackgroundColor:[[UIColor blackColor] colorWithAlphaComponent:0.6]];
            fpsLabel.font = [UIFont systemFontOfSize:14];
    
            CADisplayLink *link = [CADisplayLink displayLinkWithTarget:fpsLabel selector:NSSelectorFromString(@"tick:")];
            [link addToRunLoop:[NSRunLoop mainRunLoop] forMode:NSRunLoopCommonModes];
            [fpsLabel setValue:link forKey:@"_link"];
    
            [[UIApplication sharedApplication].keyWindow addSubview:fpsLabel];
            
            return fpsLabel;
        };
        imp_implementationWithBlock(addToKeyWindowBlock);
        
    '''

    return HM.evaluateExpressionValue(expression=command_script, prefix=HMExpressionPrefix.gPrefix)


def makeTickIMP() -> lldb.SBValue:
    command_script = '''
        
        void (^tickBlock)(UILabel *, CADisplayLink *) = ^(UILabel *fpsLabel, CADisplayLink *link) {
            NSNumber *countNum = [fpsLabel valueForKey:@"_count"];
            int count = [countNum intValue] + 1;
            [fpsLabel setValue:@(count) forKey:@"_count"];
            
            NSNumber *lastTimeNum = [fpsLabel valueForKey:@"_lastTime"];
            double delta = link.timestamp - [lastTimeNum doubleValue];
            if (delta < 1) {
                return;
            }
    
            [fpsLabel setValue:@(link.timestamp) forKey:@"_lastTime"];
            
            int fps = (int)((count / delta) + 0.5);
            [fpsLabel setValue:@(0) forKey:@"_count"];
            
            UIColor *valueColor = [UIColor whiteColor];
            if (fps < 45) {
                valueColor = [[UIColor alloc] initWithRed:0.88 green:0.36 blue:0.36 alpha:1];
            } else if (fps < 52) {
                valueColor = [[UIColor alloc] initWithRed:0.91 green:0.73 blue:0.45 alpha:1];
            }
            UIColor *unitColor = [UIColor whiteColor];
            
            NSMutableAttributedString *text = [[NSMutableAttributedString alloc] initWithString:[NSString stringWithFormat:@"%d", fps] attributes:@{(id)NSFontAttributeName: fpsLabel.font, (id)NSForegroundColorAttributeName: valueColor}];
            NSAttributedString *FPSString = [[NSAttributedString alloc] initWithString:@" FPS" attributes:@{(id)NSFontAttributeName: fpsLabel.font, (id)NSForegroundColorAttributeName: unitColor}];
            [text appendAttributedString:FPSString];
            
            fpsLabel.attributedText = text;
        };
        imp_implementationWithBlock(tickBlock);

    '''

    return HM.evaluateExpressionValue(command_script)
