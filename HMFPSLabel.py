""" File: HMFPSLabel.py

An lldb Python script about HMFPSLabel.

"""

import lldb
import HMLLDBHelpers as HM


def __lldb_init_module(debugger, internal_dict):
    debugger.HandleCommand('command script add -f HMFPSLabel.showFPS showfps -h "(deprecated)Show the FPS on key window(main thread)."')


def showFPS(debugger, command, exe_ctx, result, internal_dict):
    """
    Syntax:
        showfps

    Examples:
        (lldb) showfps

    Notice:
        showfps is deprecated. Use showdebughud instead.

    This command is implemented in HMFPSLabel.py
    """

    HM.DPrint("showfps is deprecated. Use showdebughud instead.")

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
    HM.addClassMethod(FPSClassName, "addToKeyWindow", addToKeyWindowIMPValue.GetValue(), "@@:")

    tickIMPValue = makeTickIMP()
    HM.addInstanceMethod(FPSClassName, "tick:", tickIMPValue.GetValue(), "v@:@")

    # Show fps command
    addToKeyWindowCommand = '''
        Class fps = NSClassFromString(@"HMFPSLabel");
        (UILabel *)[fps performSelector:@selector(addToKeyWindow)];
    '''
    HM.evaluateExpressionValue(addToKeyWindowCommand)


def makeAddToKeyWindowIMP() -> lldb.SBValue:
    command_script = '''

        UILabel * (^addToKeyWindowBlock)(id) = ^UILabel *(id classSelf) {
            UILabel *fpsLabel = (UILabel *)[[NSClassFromString(@"HMFPSLabel") alloc] init];
            fpsLabel.frame = CGRectMake(60, [UIApplication sharedApplication].statusBarFrame.size.height, 58, 20);
            fpsLabel.layer.zPosition = 100;
            fpsLabel.layer.cornerRadius = 5;
            fpsLabel.clipsToBounds = YES;
            fpsLabel.textAlignment = NSTextAlignmentCenter;
            fpsLabel.userInteractionEnabled = NO;
            (void)[fpsLabel setBackgroundColor:[[UIColor blackColor] colorWithAlphaComponent:0.6]];
            fpsLabel.font = [UIFont systemFontOfSize:14];
    
            CADisplayLink *link = [CADisplayLink displayLinkWithTarget:fpsLabel selector:NSSelectorFromString(@"tick:")];
            [link addToRunLoop:[NSRunLoop mainRunLoop] forMode:NSRunLoopCommonModes];
            [fpsLabel setValue:link forKey:@"_link"];
    
            [[UIApplication sharedApplication].keyWindow addSubview:fpsLabel];
            
            return fpsLabel;
        };
        
        (IMP)imp_implementationWithBlock(addToKeyWindowBlock);
        
    '''

    return HM.evaluateExpressionValue(command_script)


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
            
            double fps = count / delta;
            [fpsLabel setValue:@(0) forKey:@"_count"];
            
            CGFloat progress = fps / 60.0;
            UIColor *color = [UIColor colorWithHue:0.27 * (progress - 0.2) saturation:1 brightness:0.9 alpha:1];
            
            NSMutableAttributedString *text = [[NSMutableAttributedString alloc] initWithString:[NSString stringWithFormat:@"%d",(int)(fps + 0.5)] attributes:@{(id)NSFontAttributeName: fpsLabel.font, (id)NSForegroundColorAttributeName: color}];
            NSAttributedString *FPSString = [[NSAttributedString alloc] initWithString:@" FPS" attributes:@{(id)NSFontAttributeName: fpsLabel.font, (id)NSForegroundColorAttributeName: [UIColor whiteColor]}];
            [text appendAttributedString:FPSString];
            
            fpsLabel.attributedText = text;
        };
        
        (IMP)imp_implementationWithBlock(tickBlock);

    '''

    return HM.evaluateExpressionValue(command_script)
