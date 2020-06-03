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
    HM.addClassMethod(FPSClassName, "addToKeyWindow", addToKeyWindowIMPValue.GetValue(), "@@:")

    tickIMPValue = makeTickIMP()
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
        
        (IMP)imp_implementationWithBlock(tickBlock);

    '''

    return HM.evaluateExpressionValue(command_script)
