""" File: HMDebugHUD.py

An lldb Python script about HMDebugHUD.

"""

import lldb
import HMLLDBHelpers as HM
import HMLLDBClassInfo
import HMDebugMainViewController
import HMProgressHUD


def __lldb_init_module(debugger, internal_dict):
    debugger.HandleCommand('command script add -f HMDebugHUD.showDebugHUD showhud -h "Show debug HUD on key window.({arg})"'.format(arg=gClassName))
    debugger.HandleCommand('command script add -f HMDebugHUD.removeDebugHUD removehud -h "Remove debug HUD from key window.({arg})"'.format(arg=gClassName))


gClassName = "HMDebugHUD"


def showDebugHUD(debugger, command, exe_ctx, result, internal_dict):
    """
    Syntax:
        showhud

    Examples:
        (lldb) showhud

    Summary:
        Show debug HUD.
        1.Memory footprint.
        2.CPU utilization.
        3.FPS in main thread.
        The UI style refers to https://github.com/meitu/MTHawkeye

    This command is implemented in HMDebugHUD.py
    """

    HMProgressHUD.register()

    global gClassName
    if isDisplayingHUD():
        HM.DPrint("{arg} is already on display".format(arg=gClassName))
        return
    elif HM.existClass(gClassName):
        showHUDFunc()
        return

    # Register class
    HMProgressHUD.show("Register {arg}...".format(arg=gClassName))

    classValue = HM.allocateClass(gClassName, "UIView")
    HM.addIvar(classValue.GetValue(), "_link", "CADisplayLink *")
    HM.addIvar(classValue.GetValue(), "_count", "int")  # count in 1 second
    HM.addIvar(classValue.GetValue(), "_lastTime", "double")

    HM.addIvar(classValue.GetValue(), "_memoryLab", "UILabel *")
    HM.addIvar(classValue.GetValue(), "_cpuUtilizationLab", "UILabel *")
    HM.addIvar(classValue.GetValue(), "_fpsLab", "UILabel *")

    HM.registerClass(classValue.GetValue())

    # Add methods
    HMProgressHUD.show("Add methods to {arg}...".format(arg=gClassName))

    addToKeyWindowIMPValue = makeAddToKeyWindowIMP()
    if not HM.judgeSBValueHasValue(addToKeyWindowIMPValue):
        HMProgressHUD.hide()
        return
    HM.addClassMethod(gClassName, "addToKeyWindow", addToKeyWindowIMPValue.GetValue(), "@@:")

    tapSelfIMPValue = makeTapSelfIMP()
    if not HM.judgeSBValueHasValue(tapSelfIMPValue):
        HMProgressHUD.hide()
        return
    HM.addInstanceMethod(gClassName, "tapSelf", tapSelfIMPValue.GetValue(), "v@:")

    # Add methods(update)
    if not addUpdateMethods():
        HMProgressHUD.hide()
        return

    # Add methods(move)
    HMProgressHUD.show("Add methods to {arg}......".format(arg=gClassName))
    if not addMoveMethods():
        HMProgressHUD.hide()
        return

    # Add breakpoint in tapSelf
    HMProgressHUD.show("Add breakpoint to hook method...")
    HM.addOneShotBreakPointInIMP(tapSelfIMPValue, "HMDebugHUD.tapSelfBreakPointHandler", "HMDebugHUD_TapSelf_Breakpoint")

    HMProgressHUD.show("Register {arg} done!".format(arg=gClassName))

    # Show HUD command
    showHUDFunc()

    HMProgressHUD.hide()

    HM.processContinue()


def removeDebugHUD(debugger, command, exe_ctx, result, internal_dict) -> None:
    """
    Syntax:
        removehud

    Examples:
        (lldb) removehud

    This command is implemented in HMDebugHUD.py
    """

    global gClassName
    if not HM.existClass(gClassName):
        HM.DPrint("{arg} does not exist.".format(arg=gClassName))
        return

    command_script = '''
        UIView *keyWindow = [UIApplication sharedApplication].keyWindow;
        Class HUDClass = (Class)objc_getClass("{arg0}");
        UIView *objView = nil;
        for (UIView *subView in keyWindow.subviews) {{
            if ([subView isKindOfClass:HUDClass]) {{
                objView = subView;
                break;
            }}
        }}
        [objView removeFromSuperview];
        objView;
    '''.format(arg0=gClassName)

    val = HM.evaluateExpressionValue(command_script)
    if HM.judgeSBValueHasValue(val):
        HM.DPrint("remove done!")
    else:
        HM.DPrint("{arg} does not exist.".format(arg=gClassName))


def isDisplayingHUD() -> bool:
    if not HM.existClass(gClassName):
        return False

    command_script = '''
        BOOL isDisplaying = NO;
        UIView *keyWindow = [UIApplication sharedApplication].keyWindow;
        Class HUDClass = (Class)objc_getClass("{arg0}");
        for (UIView *subView in keyWindow.subviews) {{
            if ([subView isKindOfClass:HUDClass]) {{
                isDisplaying = YES;
                break;
            }}
        }}
        isDisplaying;
    '''.format(arg0=gClassName)

    val = HM.evaluateExpressionValue(command_script)
    return HM.boolOfSBValue(val)


def showHUDFunc() -> None:
    addToKeyWindowCommand = '''
        Class HUD = NSClassFromString(@"{arg0}");
        (UIView *)[HUD performSelector:@selector(addToKeyWindow)];
    '''.format(arg0=gClassName)
    HM.evaluateExpressionValue(addToKeyWindowCommand)


def currentTask() -> lldb.SBValue:
    taskValue = HM.evaluateExpressionValue("(unsigned int)(long)mach_task_self_")
    return taskValue


def addUpdateMethods() -> bool:
    global gClassName

    debugHUDtickIMPValue = makeDebugHUDtickIMP()
    if not HM.judgeSBValueHasValue(debugHUDtickIMPValue):
        HM.DPrint("Error debugHUDtickIMPValue, please fix it.")
        return False
    HM.addInstanceMethod(gClassName, "debugHUDtick:", debugHUDtickIMPValue.GetValue(), "v@:@")

    updateMemoryFootprintIMPValue = makeUpdateMemoryFootprintIMP()
    if not HM.judgeSBValueHasValue(updateMemoryFootprintIMPValue):
        HM.DPrint("Error updateMemoryFootprintIMPValue, please fix it.")
        return False
    HM.addInstanceMethod(gClassName, "updateMemoryFootprint", updateMemoryFootprintIMPValue.GetValue(), "v@:")

    updateCPUUtilizationIMPValue = makeUpdateCPUUtilizationIMP()
    if not HM.judgeSBValueHasValue(updateCPUUtilizationIMPValue):
        HM.DPrint("Error updateCPUUtilizationIMPValue, please fix it.")
        return False
    HM.addInstanceMethod(gClassName, "updateCPUUtilization", updateCPUUtilizationIMPValue.GetValue(), "v@:")

    updateFPSIMPValue = makeUpdateFPSIMP()
    if not HM.judgeSBValueHasValue(updateFPSIMPValue):
        HM.DPrint("Error updateFPSIMPValue, please fix it.")
        return False
    HM.addInstanceMethod(gClassName, "updateFPS:", updateFPSIMPValue.GetValue(), "v@:i")

    return True


def makeAddToKeyWindowIMP() -> lldb.SBValue:
    command_script = '''

        UIView * (^addToKeyWindowBlock)(id) = ^UIView *(id classSelf) {{
            UIView *HUD = (UIView *)[[NSClassFromString(@"{arg0}") alloc] init];
            HUD.frame = (CGRect){{60, [UIApplication sharedApplication].statusBarFrame.size.height, 42, 42}};
            (void)[HUD setBackgroundColor:[UIColor colorWithWhite:0.6 alpha:0.8]];

            CGFloat rowHeight = 14;
            CGFloat rowWidth = 40;
            UILabel *memoryLab = [[UILabel alloc] initWithFrame:(CGRect){{0, 0 * rowHeight, rowWidth, rowHeight}}];
            memoryLab.textAlignment = NSTextAlignmentRight;
            [HUD addSubview:memoryLab];
            [HUD setValue:memoryLab forKey:@"_memoryLab"];
            
            UILabel *cpuUtilizationLab = [[UILabel alloc] initWithFrame:(CGRect){{0, 1 * rowHeight, rowWidth, rowHeight}}];
            cpuUtilizationLab.textAlignment = NSTextAlignmentRight;
            [HUD addSubview:cpuUtilizationLab];
            [HUD setValue:cpuUtilizationLab forKey:@"_cpuUtilizationLab"];
            
            UILabel *fpsLab = [[UILabel alloc] initWithFrame:(CGRect){{0, 2 * rowHeight, rowWidth, rowHeight}}];
            fpsLab.textAlignment = NSTextAlignmentRight;
            [HUD addSubview:fpsLab];
            [HUD setValue:fpsLab forKey:@"_fpsLab"];

            CADisplayLink *link = [CADisplayLink displayLinkWithTarget:HUD selector:NSSelectorFromString(@"debugHUDtick:")];
            [link addToRunLoop:[NSRunLoop mainRunLoop] forMode:NSRunLoopCommonModes];
            [HUD setValue:link forKey:@"_link"];
            
            UITapGestureRecognizer *tap = [[UITapGestureRecognizer alloc] initWithTarget:HUD action:@selector(tapSelf)];
            [HUD addGestureRecognizer:tap];

            [[UIApplication sharedApplication].keyWindow addSubview:HUD];
            
            return HUD;
        }};

        (IMP)imp_implementationWithBlock(addToKeyWindowBlock);

    '''.format(arg0=gClassName)

    return HM.evaluateExpressionValue(command_script)


def makeTapSelfIMP() -> lldb.SBValue:
    command_script = '''
        void (^tapSelfBlock)(UIView *) = ^(UIView *HUD) {
            Class cls = (Class)objc_getClass("HMDebugMainViewController");
            (id)[cls performSelector:@selector(present)];
        };

        (IMP)imp_implementationWithBlock(tapSelfBlock);

    '''
    return HM.evaluateExpressionValue(command_script)


def makeDebugHUDtickIMP() -> lldb.SBValue:
    command_script = '''

        void (^debugHUDtickBlock)(UIView *, CADisplayLink *) = ^(UIView *HUD, CADisplayLink *link) {
            NSNumber *countNum = [HUD valueForKey:@"_count"];
            int count = [countNum intValue] + 1;
            [HUD setValue:@(count) forKey:@"_count"];

            NSNumber *lastTimeNum = [HUD valueForKey:@"_lastTime"];
            double delta = link.timestamp - [lastTimeNum doubleValue];
            if (delta < 1) {
                return;
            }

            [HUD setValue:@(link.timestamp) forKey:@"_lastTime"];
            [HUD setValue:@(0) forKey:@"_count"];

            int fps = (int)((count / delta) + 0.5);
            
            (void)[HUD updateMemoryFootprint];
            (void)[HUD updateCPUUtilization];
            (void)[HUD updateFPS:fps];
        };

        (IMP)imp_implementationWithBlock(debugHUDtickBlock);

    '''
    return HM.evaluateExpressionValue(command_script)


def makeUpdateMemoryFootprintIMP() -> lldb.SBValue:

    command_script = '''
    
        void (^updateMemoryFootprintBlock)(UIView *) = ^(UIView *HUD) {{
            
            task_vm_info_data_t vmInfo;
            vmInfo.phys_footprint = 0;
            mach_msg_type_number_t count = ((mach_msg_type_number_t) (sizeof(task_vm_info_data_t) / sizeof(natural_t)));
            unsigned int task_vm_info = 22;
            unsigned int task = {arg0};
            kern_return_t result = (kern_return_t)task_info((unsigned int)task, (unsigned int)task_vm_info, (task_info_t)&vmInfo, &count);
            
            int kern_success = 0;
            if (result != kern_success) {{
                return;
            }}
        
            int megabyte = (int)(vmInfo.phys_footprint / 1024.0 / 1024.0 + 0.5);
            UIColor *valueColor = [UIColor whiteColor];
            UIFont *valueFont = [UIFont systemFontOfSize:12];
            UIColor *unitColor = [UIColor whiteColor];
            UIFont *unitFont = [UIFont systemFontOfSize:8];
            
            NSMutableAttributedString *valueText = [[NSMutableAttributedString alloc] initWithString:[NSString stringWithFormat:@"%d", megabyte] attributes:@{{(id)NSFontAttributeName: valueFont, (id)NSForegroundColorAttributeName: valueColor}}];
            NSAttributedString *unitText = [[NSAttributedString alloc] initWithString:@" MB" attributes:@{{(id)NSFontAttributeName: unitFont, (id)NSForegroundColorAttributeName: unitColor}}];
            [valueText appendAttributedString:unitText];
            
            UILabel *memoryLab = [HUD valueForKey:@"_memoryLab"];
            memoryLab.attributedText = valueText;
        }};

        (IMP)imp_implementationWithBlock(updateMemoryFootprintBlock);
        
    '''.format(arg0=currentTask().GetValue())

    return HM.evaluateExpressionValue(command_script)


def makeUpdateCPUUtilizationIMP() -> lldb.SBValue:
    command_script = '''

        void (^updateCPUUtilizationBlock)(UIView *) = ^(UIView *HUD) {{
            double totalUsageRatio = 0;
            double maxRatio = 0;
        
            thread_info_data_t thinfo;
            thread_act_array_t threads;
            thread_basic_info_t basic_info_t;
            mach_msg_type_number_t count = 0;
            
            mach_msg_type_number_t thread_info_count = 32;
            int kern_success = 0;
            int thread_basic_info = 3;
            int th_flags_idle = 2;
            double th_usage_scale = 1000.0;
            if ((kern_return_t)(task_threads({arg0}, &threads, &count)) == kern_success) {{
                for (int idx = 0; idx < count; idx++) {{
                    if ((kern_return_t)(thread_info(threads[idx], thread_basic_info, (thread_info_t)thinfo, &thread_info_count)) == kern_success) {{
                        basic_info_t = (thread_basic_info_t)thinfo;
        
                        if (!(basic_info_t->flags & th_flags_idle)) {{
                            double cpuUsage = basic_info_t->cpu_usage / th_usage_scale;
                            if (cpuUsage > maxRatio) {{
                                maxRatio = cpuUsage;
                            }}
                            totalUsageRatio += cpuUsage;
                        }}
                    }}
                }}
        
                if ((kern_return_t)(vm_deallocate({arg0}, (vm_address_t)threads, count * sizeof(thread_t))) != kern_success) {{
                    printf("[HMLLDB] vm_deallocate failed\\n");
                }}
            }}
            
            int cpuUtilization = (int)(totalUsageRatio * 100.0);
            UIColor *valueColor = [UIColor whiteColor];
            if (cpuUtilization >= 95) {{
                valueColor = [[UIColor alloc] initWithRed:0.88 green:0.36 blue:0.36 alpha:1];
            }} else if (cpuUtilization > 80) {{
                valueColor = [[UIColor alloc] initWithRed:0.91 green:0.73 blue:0.45 alpha:1];
            }}
            UIFont *valueFont = [UIFont systemFontOfSize:12];
            UIColor *unitColor = [UIColor whiteColor];
            UIFont *unitFont = [UIFont systemFontOfSize:8];
            
            NSMutableAttributedString *valueText = [[NSMutableAttributedString alloc] initWithString:[NSString stringWithFormat:@"%d", cpuUtilization] attributes:@{{(id)NSFontAttributeName: valueFont, (id)NSForegroundColorAttributeName: valueColor}}];
            NSAttributedString *unitText = [[NSAttributedString alloc] initWithString:@" %" attributes:@{{(id)NSFontAttributeName: unitFont, (id)NSForegroundColorAttributeName: unitColor}}];
            [valueText appendAttributedString:unitText];
            
            UILabel *cpuUtilizationLab = [HUD valueForKey:@"_cpuUtilizationLab"];
            cpuUtilizationLab.attributedText = valueText;
        }};

        (IMP)imp_implementationWithBlock(updateCPUUtilizationBlock);

    '''.format(arg0=currentTask().GetValue())

    return HM.evaluateExpressionValue(command_script)


def makeUpdateFPSIMP() -> lldb.SBValue:
    command_script = '''

        void (^updateFPSBlock)(UIView *, int) = ^(UIView *HUD, int fps) {
            UIColor *valueColor = [UIColor whiteColor];
            if (fps < 45) {
                valueColor = [[UIColor alloc] initWithRed:0.88 green:0.36 blue:0.36 alpha:1];
            } else if (fps < 52) {
                valueColor = [[UIColor alloc] initWithRed:0.91 green:0.73 blue:0.45 alpha:1];
            }
            UIFont *valueFont = [UIFont systemFontOfSize:12];
            UIColor *unitColor = [UIColor whiteColor];
            UIFont *unitFont = [UIFont systemFontOfSize:8];

            NSMutableAttributedString *valueText = [[NSMutableAttributedString alloc] initWithString:[NSString stringWithFormat:@"%d", fps] attributes:@{(id)NSFontAttributeName: valueFont, (id)NSForegroundColorAttributeName: valueColor}];
            NSAttributedString *unitText = [[NSAttributedString alloc] initWithString:@" FPS" attributes:@{(id)NSFontAttributeName: unitFont, (id)NSForegroundColorAttributeName: unitColor}];
            [valueText appendAttributedString:unitText];

            UILabel *fpsLab = [HUD valueForKey:@"_fpsLab"];
            fpsLab.attributedText = valueText;
        };

        (IMP)imp_implementationWithBlock(updateFPSBlock);

    '''
    return HM.evaluateExpressionValue(command_script)


def addMoveMethods() -> bool:
    global gClassName

    touchesMovedWithEventIMPValue = makeTouchesMovedWithEventIMP()
    if not HM.judgeSBValueHasValue(touchesMovedWithEventIMPValue):
        HM.DPrint("Error touchesMovedWithEventIMPValue, please fix it.")
        return False
    HM.addInstanceMethod(gClassName, "touchesMoved:withEvent:", touchesMovedWithEventIMPValue.GetValue(), "v@:@@")

    touchesEndedWithEventIMPValue = makeTouchesEndedWithEventIMP()
    if not HM.judgeSBValueHasValue(touchesEndedWithEventIMPValue):
        HM.DPrint("Error touchesEndedWithEventIMPValue, please fix it.")
        return False
    HM.addInstanceMethod(gClassName, "touchesEnded:withEvent:", touchesEndedWithEventIMPValue.GetValue(), "v@:@@")

    touchesCancelledWithEventIMPValue = makeTouchesCancelledWithEventIMP()
    if not HM.judgeSBValueHasValue(touchesCancelledWithEventIMPValue):
        HM.DPrint("Error touchesCancelledWithEventIMPValue, please fix it.")
        return False
    HM.addInstanceMethod(gClassName, "touchesCancelled:withEvent:", touchesCancelledWithEventIMPValue.GetValue(), "v@:@@")

    attachToEdgeIMPValue = makeAttachToEdgeIMP()
    if not HM.judgeSBValueHasValue(attachToEdgeIMPValue):
        HM.DPrint("Error attachToEdgeIMPValue, please fix it.")
        return False
    HM.addInstanceMethod(gClassName, "attachToEdge", attachToEdgeIMPValue.GetValue(), "v@:")

    return True


def makeTouchesMovedWithEventIMP() -> lldb.SBValue:
    command_script = '''

        void (^touchesMovedWithEventBlock)(UIView *, NSSet *, UIEvent *) = ^(UIView *HUD, NSSet * touches, UIEvent *event) {
            struct objc_super superInfo = {
                .receiver = HUD,
                .super_class = (Class)class_getSuperclass((Class)[HUD class])
            };

            ((void (*)(struct objc_super *, SEL, id, id))objc_msgSendSuper)(&superInfo, @selector(touchesMoved:withEvent:), touches, event);
        
            UIView *superView = HUD.superview;
            if (!superView) {
                return;
            }
        
            UITouch *touch = [touches anyObject];
            CGPoint previousPoint = [touch previousLocationInView:HUD];
            CGPoint currentPoint = [touch locationInView:HUD];
            CGPoint targetCenter = HUD.center;
            CGFloat offsetX = currentPoint.x - previousPoint.x;
            CGFloat offsetY = currentPoint.y - previousPoint.y;
        
            if ((offsetX * offsetX < 1) && (offsetY * offsetY < 1)) {
                return;
            }
            targetCenter.x = ceil(HUD.center.x + offsetX);
            targetCenter.y = ceil(HUD.center.y + offsetY);
        
            HUD.center = targetCenter;
        };

        (IMP)imp_implementationWithBlock(touchesMovedWithEventBlock);

    '''
    return HM.evaluateExpressionValue(command_script)


def makeTouchesEndedWithEventIMP() -> lldb.SBValue:
    command_script = '''

        void (^touchesEndedWithEventBlock)(UIView *, NSSet *, UIEvent *) = ^(UIView *HUD, NSSet * touches, UIEvent *event) {
            struct objc_super superInfo = {
                .receiver = HUD,
                .super_class = (Class)class_getSuperclass((Class)[HUD class])
            };

            ((void (*)(struct objc_super *, SEL, id, id))objc_msgSendSuper)(&superInfo, @selector(touchesEnded:withEvent:), touches, event);

            (void)[HUD attachToEdge];
        };

        (IMP)imp_implementationWithBlock(touchesEndedWithEventBlock);

    '''
    return HM.evaluateExpressionValue(command_script)


def makeTouchesCancelledWithEventIMP() -> lldb.SBValue:
    command_script = '''

        void (^touchesCancelledWithEventBlock)(UIView *, NSSet *, UIEvent *) = ^(UIView *HUD, NSSet * touches, UIEvent *event) {
            struct objc_super superInfo = {
                .receiver = HUD,
                .super_class = (Class)class_getSuperclass((Class)[HUD class])
            };

            ((void (*)(struct objc_super *, SEL, id, id))objc_msgSendSuper)(&superInfo, @selector(touchesCancelled:withEvent:), touches, event);

            (void)[HUD attachToEdge];
        };

        (IMP)imp_implementationWithBlock(touchesCancelledWithEventBlock);

    '''
    return HM.evaluateExpressionValue(command_script)


def makeAttachToEdgeIMP() -> lldb.SBValue:
    command_script = '''

        void (^attachToEdgeBlock)(UIView *, NSSet *, UIEvent *) = ^(UIView *HUD, NSSet * touches, UIEvent *event) {
            
            if (!HUD.window) {
                return;
            }
        
            UIEdgeInsets safeAreaInsets = UIEdgeInsetsZero;
            if ([HUD.window respondsToSelector:@selector(safeAreaInsets)]) {
                safeAreaInsets = [HUD.window safeAreaInsets];
            }
            
            CGFloat minX = safeAreaInsets.left;
            CGFloat maxX = HUD.window.bounds.size.width - safeAreaInsets.right;
            CGFloat minY = safeAreaInsets.top;
            CGFloat maxY = HUD.window.bounds.size.height - safeAreaInsets.bottom;
        
            
            CGFloat x = HUD.frame.origin.x;
            if (x < minX) {
                x = minX;
            }
            if (x > maxX - HUD.frame.size.width) {
                x = maxX - HUD.frame.size.width;
            }
            
            CGFloat y = HUD.frame.origin.y;
            if (y < minY) {
                y = minY;
            }
            if (y > maxY - HUD.frame.size.height) {
                y = maxY - HUD.frame.size.height;
            }
        
            CGRect targetFrame = HUD.frame;
            targetFrame.origin = (CGPoint){x, y};
            
            [UIView animateWithDuration:0.2 animations:^{
                HUD.frame = targetFrame;
            }];
            
        };

        (IMP)imp_implementationWithBlock(attachToEdgeBlock);

    '''
    return HM.evaluateExpressionValue(command_script)


def tapSelfBreakPointHandler(frame, bp_loc, internal_dict) -> bool:
    HMDebugMainViewController.register()
    HM.processContinue()
    return True
