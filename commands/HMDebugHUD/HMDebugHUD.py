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

# https://github.com/chenhuimao/HMLLDB

import lldb
import HMDebugMainViewController
import HMExpressionPrefix
import HMLLDBClassInfo
import HMLLDBHelpers as HM
import HMProgressHUD


def __lldb_init_module(debugger, internal_dict):
    debugger.HandleCommand(f'command script add -f HMDebugHUD.showDebugHUD showhud -h "Show debug HUD on key window.({gClassName})"')
    debugger.HandleCommand(f'command script add -f HMDebugHUD.removeDebugHUD removehud -h "Remove debug HUD from key window.({gClassName})"')


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
        The UI style is based on https://github.com/meitu/MTHawkeye

    This command is implemented in HMDebugHUD.py
    """

    global gClassName
    if isDisplayingHUD():
        HM.DPrint(f"{gClassName} is already on display")
        HM.process_continue()
        return
    elif HM.is_existing_class(gClassName):
        showHUDFunc()
        HM.process_continue()
        return

    # Register class
    HMProgressHUD.show(f"Register {gClassName}...")
    HM.DPrint(f"Register {gClassName}...")

    classValue = HM.allocate_class(gClassName, "UIView")
    HM.add_ivar(classValue.GetValue(), "_link", "CADisplayLink *")
    HM.add_ivar(classValue.GetValue(), "_count", "int")  # count in 1 second
    HM.add_ivar(classValue.GetValue(), "_lastTime", "double")

    HM.add_ivar(classValue.GetValue(), "_memoryLab", "UILabel *")
    HM.add_ivar(classValue.GetValue(), "_cpuUtilizationLab", "UILabel *")
    HM.add_ivar(classValue.GetValue(), "_fpsLab", "UILabel *")

    HM.register_class(classValue.GetValue())

    # Add methods
    HM.DPrint(f"Add methods to {gClassName}...")

    addToKeyWindowIMPValue = makeAddToKeyWindowIMP()
    if not HM.is_SBValue_has_value(addToKeyWindowIMPValue):
        HMProgressHUD.hide()
        return
    HM.add_class_method(gClassName, "addToKeyWindow", addToKeyWindowIMPValue.GetValue(), "@@:")

    tapSelfIMPValue = makeTapSelfIMP()
    if not HM.is_SBValue_has_value(tapSelfIMPValue):
        HMProgressHUD.hide()
        return
    HM.add_instance_method(gClassName, "tapSelf", tapSelfIMPValue.GetValue(), "v@:")

    # Add methods(update)
    if not addUpdateMethods():
        HMProgressHUD.hide()
        return

    # Add methods(move)
    HM.DPrint(f"Add methods to {gClassName}......")
    if not addMoveMethods():
        HMProgressHUD.hide()
        return

    # Add breakpoint in tapSelf
    HM.DPrint("Add breakpoint to hook method...")
    HM.add_one_shot_breakpoint_in_imp(tapSelfIMPValue, "HMDebugHUD.tapSelfBreakPointHandler", "HMDebugHUD_TapSelf_Breakpoint")

    HM.DPrint(f"Register {gClassName} done!")

    # Show HUD command
    showHUDFunc()

    HMProgressHUD.hide()

    HM.process_continue()


def removeDebugHUD(debugger, command, exe_ctx, result, internal_dict) -> None:
    """
    Syntax:
        removehud

    Examples:
        (lldb) removehud

    This command is implemented in HMDebugHUD.py
    """

    global gClassName
    if not HM.is_existing_class(gClassName):
        HM.DPrint(f"{gClassName} does not exist.")
        return

    command_script = f'''
        UIView *keyWindow = [UIApplication sharedApplication].keyWindow;
        Class HUDClass = (Class)objc_lookUpClass("{gClassName}");
        UIView *objView = nil;
        for (UIView *subView in keyWindow.subviews) {{
            if ([subView isKindOfClass:HUDClass]) {{
                objView = subView;
                break;
            }}
        }}
        [objView removeFromSuperview];
        objView;
    '''

    val = HM.evaluate_expression_value(expression=command_script, prefix=HMExpressionPrefix.gPrefix)
    if HM.is_SBValue_has_value(val):
        HM.DPrint("remove done!")
    else:
        HM.DPrint(f"{gClassName} does not exist.")


def isDisplayingHUD() -> bool:
    if not HM.is_existing_class(gClassName):
        return False

    command_script = f'''
        BOOL isDisplaying = NO;
        UIView *keyWindow = [UIApplication sharedApplication].keyWindow;
        UIView *HUD = nil;
        Class HUDClass = (Class)objc_lookUpClass("{gClassName}");
        for (UIView *subView in keyWindow.subviews) {{
            if ([subView isKindOfClass:HUDClass]) {{
                isDisplaying = YES;
                HUD = subView;
                break;
            }}
        }}
        if (HUD) {{
            [keyWindow bringSubviewToFront:HUD];
        }}
        (BOOL)isDisplaying;
    '''

    val = HM.evaluate_expression_value(expression=command_script, prefix=HMExpressionPrefix.gPrefix)
    return HM.bool_of_SBValue(val)


def showHUDFunc() -> None:
    addToKeyWindowCommand = f'''
        Class HUD = NSClassFromString(@"{gClassName}");
        (UIView *)[HUD performSelector:@selector(addToKeyWindow)];
    '''
    HM.evaluate_expression_value(expression=addToKeyWindowCommand, prefix=HMExpressionPrefix.gPrefix)


def currentTask() -> lldb.SBValue:
    taskValue = HM.evaluate_expression_value("(unsigned int)(long)mach_task_self_")
    return taskValue


def addUpdateMethods() -> bool:
    global gClassName

    debugHUDtickIMPValue = makeDebugHUDtickIMP()
    if not HM.is_SBValue_has_value(debugHUDtickIMPValue):
        return False
    HM.add_instance_method(gClassName, "debugHUDtick:", debugHUDtickIMPValue.GetValue(), "v@:@")

    updateMemoryFootprintIMPValue = makeUpdateMemoryFootprintIMP()
    if not HM.is_SBValue_has_value(updateMemoryFootprintIMPValue):
        return False
    HM.add_instance_method(gClassName, "updateMemoryFootprint", updateMemoryFootprintIMPValue.GetValue(), "v@:")

    updateCPUUtilizationIMPValue = makeUpdateCPUUtilizationIMP()
    if not HM.is_SBValue_has_value(updateCPUUtilizationIMPValue):
        return False
    HM.add_instance_method(gClassName, "updateCPUUtilization", updateCPUUtilizationIMPValue.GetValue(), "v@:")

    updateFPSIMPValue = makeUpdateFPSIMP()
    if not HM.is_SBValue_has_value(updateFPSIMPValue):
        return False
    HM.add_instance_method(gClassName, "updateFPS:", updateFPSIMPValue.GetValue(), "v@:i")

    return True


def makeAddToKeyWindowIMP() -> lldb.SBValue:
    command_script = f'''

        UIView * (^addToKeyWindowBlock)(id) = ^UIView *(id classSelf) {{
            UIView *HUD = (UIView *)[[NSClassFromString(@"{gClassName}") alloc] init];
            (void)[HUD setFrame:(CGRect){{60, [UIApplication sharedApplication].statusBarFrame.size.height, 42, 42}}];
            (void)[HUD setBackgroundColor:[UIColor colorWithWhite:0.6 alpha:0.8]];

            CGFloat rowHeight = 14;
            CGFloat rowWidth = 40;
            UILabel *memoryLab = [[UILabel alloc] initWithFrame:(CGRect){{0, 0 * rowHeight, rowWidth, rowHeight}}];
            memoryLab.textAlignment = (NSTextAlignment)2;
            [HUD addSubview:memoryLab];
            [HUD setValue:memoryLab forKey:@"_memoryLab"];
            
            UILabel *cpuUtilizationLab = [[UILabel alloc] initWithFrame:(CGRect){{0, 1 * rowHeight, rowWidth, rowHeight}}];
            cpuUtilizationLab.textAlignment = (NSTextAlignment)2;
            [HUD addSubview:cpuUtilizationLab];
            [HUD setValue:cpuUtilizationLab forKey:@"_cpuUtilizationLab"];
            
            UILabel *fpsLab = [[UILabel alloc] initWithFrame:(CGRect){{0, 2 * rowHeight, rowWidth, rowHeight}}];
            fpsLab.textAlignment = (NSTextAlignment)2;
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

        imp_implementationWithBlock(addToKeyWindowBlock);

    '''

    return HM.evaluate_expression_value(expression=command_script, prefix=HMExpressionPrefix.gPrefix)


def makeTapSelfIMP() -> lldb.SBValue:
    command_script = f'''
        void (^tapSelfBlock)(UIView *) = ^(UIView *HUD) {{
            Class cls = (Class)objc_lookUpClass("{HMDebugMainViewController.gClassName}");
            (id)[cls performSelector:@selector(present)];
        }};

        imp_implementationWithBlock(tapSelfBlock);

    '''
    return HM.evaluate_expression_value(expression=command_script, prefix=HMExpressionPrefix.gPrefix)


def makeDebugHUDtickIMP() -> lldb.SBValue:
    command_script = '''

        void (^debugHUDtickBlock)(UIView *, CADisplayLink *) = ^(UIView *HUD, CADisplayLink *link) {
            NSNumber *countNum = [HUD valueForKey:@"_count"];
            int hm_count = [countNum intValue] + 1;
            [HUD setValue:@(hm_count) forKey:@"_count"];

            NSNumber *lastTimeNum = [HUD valueForKey:@"_lastTime"];
            double delta = link.timestamp - [lastTimeNum doubleValue];
            if (delta < 1) {
                return;
            }

            [HUD setValue:@(link.timestamp) forKey:@"_lastTime"];
            [HUD setValue:@(0) forKey:@"_count"];

            int fps = (int)((hm_count / delta) + 0.5);
            
            (void)[HUD updateMemoryFootprint];
            (void)[HUD updateCPUUtilization];
            (void)[HUD updateFPS:fps];
        };

        imp_implementationWithBlock(debugHUDtickBlock);

    '''
    return HM.evaluate_expression_value(expression=command_script, prefix=HMExpressionPrefix.gPrefix)


def makeUpdateMemoryFootprintIMP() -> lldb.SBValue:

    command_script = f'''
    
        void (^updateMemoryFootprintBlock)(UIView *) = ^(UIView *HUD) {{
            
            task_vm_info_data_t vmInfo;
            vmInfo.phys_footprint = 0;
            mach_msg_type_number_t hm_count = ((mach_msg_type_number_t) (sizeof(task_vm_info_data_t) / sizeof(natural_t)));
            unsigned int task_vm_info = 22;
            unsigned int task = {currentTask().GetValue()};
            kern_return_t result = (kern_return_t)task_info((unsigned int)task, (unsigned int)task_vm_info, (task_info_t)&vmInfo, &hm_count);
            
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

        imp_implementationWithBlock(updateMemoryFootprintBlock);
        
    '''

    return HM.evaluate_expression_value(expression=command_script, prefix=HMExpressionPrefix.gPrefix)


def makeUpdateCPUUtilizationIMP() -> lldb.SBValue:
    command_script = f'''

        void (^updateCPUUtilizationBlock)(UIView *) = ^(UIView *HUD) {{
            double totalUsageRatio = 0;
            double maxRatio = 0;
        
            thread_info_data_t thinfo;
            thread_act_array_t threads;
            thread_basic_info_t basic_info_t;
            mach_msg_type_number_t hm_count = 0;
            
            mach_msg_type_number_t thread_info_count = 32;
            int kern_success = 0;
            int thread_basic_info = 3;
            int th_flags_idle = 2;
            double th_usage_scale = 1000.0;
            if ((kern_return_t)(task_threads({currentTask().GetValue()}, &threads, &hm_count)) == kern_success) {{
                for (int idx = 0; idx < hm_count; idx++) {{
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
        
                if ((kern_return_t)(vm_deallocate({currentTask().GetValue()}, (vm_address_t)threads, hm_count * sizeof(thread_t))) != kern_success) {{
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

        imp_implementationWithBlock(updateCPUUtilizationBlock);

    '''

    return HM.evaluate_expression_value(expression=command_script, prefix=HMExpressionPrefix.gPrefix)


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

        imp_implementationWithBlock(updateFPSBlock);

    '''
    return HM.evaluate_expression_value(expression=command_script, prefix=HMExpressionPrefix.gPrefix)


def addMoveMethods() -> bool:
    global gClassName

    touchesMovedWithEventIMPValue = makeTouchesMovedWithEventIMP()
    if not HM.is_SBValue_has_value(touchesMovedWithEventIMPValue):
        return False
    HM.add_instance_method(gClassName, "touchesMoved:withEvent:", touchesMovedWithEventIMPValue.GetValue(), "v@:@@")

    touchesEndedWithEventIMPValue = makeTouchesEndedWithEventIMP()
    if not HM.is_SBValue_has_value(touchesEndedWithEventIMPValue):
        return False
    HM.add_instance_method(gClassName, "touchesEnded:withEvent:", touchesEndedWithEventIMPValue.GetValue(), "v@:@@")

    touchesCancelledWithEventIMPValue = makeTouchesCancelledWithEventIMP()
    if not HM.is_SBValue_has_value(touchesCancelledWithEventIMPValue):
        return False
    HM.add_instance_method(gClassName, "touchesCancelled:withEvent:", touchesCancelledWithEventIMPValue.GetValue(), "v@:@@")

    attachToEdgeIMPValue = makeAttachToEdgeIMP()
    if not HM.is_SBValue_has_value(attachToEdgeIMPValue):
        return False
    HM.add_instance_method(gClassName, "attachToEdge", attachToEdgeIMPValue.GetValue(), "v@:")

    return True


def makeTouchesMovedWithEventIMP() -> lldb.SBValue:
    command_script = f'''

        void (^touchesMovedWithEventBlock)(UIView *, NSSet *, UIEvent *) = ^(UIView *HUD, NSSet * touches, UIEvent *event) {{
            Class cls = objc_lookUpClass("{gClassName}");
            struct objc_super superInfo = {{
                .receiver = HUD,
                .super_class = (Class)class_getSuperclass((Class)cls)
            }};

            ((void (*)(struct objc_super *, SEL, id, id))objc_msgSendSuper)(&superInfo, @selector(touchesMoved:withEvent:), touches, event);
        
            UIView *superView = HUD.superview;
            if (!superView) {{
                return;
            }}
        
            UITouch *touch = [touches anyObject];
            CGPoint previousPoint = [touch previousLocationInView:HUD];
            CGPoint currentPoint = [touch locationInView:HUD];
            CGPoint targetCenter = HUD.center;
            CGFloat offsetX = currentPoint.x - previousPoint.x;
            CGFloat offsetY = currentPoint.y - previousPoint.y;
        
            if ((offsetX * offsetX < 1) && (offsetY * offsetY < 1)) {{
                return;
            }}
            targetCenter.x = ceil(HUD.center.x + offsetX);
            targetCenter.y = ceil(HUD.center.y + offsetY);
        
            HUD.center = targetCenter;
        }};

        imp_implementationWithBlock(touchesMovedWithEventBlock);

    '''
    return HM.evaluate_expression_value(expression=command_script, prefix=HMExpressionPrefix.gPrefix)


def makeTouchesEndedWithEventIMP() -> lldb.SBValue:
    command_script = f'''

        void (^touchesEndedWithEventBlock)(UIView *, NSSet *, UIEvent *) = ^(UIView *HUD, NSSet * touches, UIEvent *event) {{
            Class cls = objc_lookUpClass("{gClassName}");
            struct objc_super superInfo = {{
                .receiver = HUD,
                .super_class = (Class)class_getSuperclass((Class)cls)
            }};

            ((void (*)(struct objc_super *, SEL, id, id))objc_msgSendSuper)(&superInfo, @selector(touchesEnded:withEvent:), touches, event);

            (void)[HUD attachToEdge];
        }};

        imp_implementationWithBlock(touchesEndedWithEventBlock);

    '''
    return HM.evaluate_expression_value(expression=command_script, prefix=HMExpressionPrefix.gPrefix)


def makeTouchesCancelledWithEventIMP() -> lldb.SBValue:
    command_script = f'''

        void (^touchesCancelledWithEventBlock)(UIView *, NSSet *, UIEvent *) = ^(UIView *HUD, NSSet * touches, UIEvent *event) {{
            Class cls = objc_lookUpClass("{gClassName}");
            struct objc_super superInfo = {{
                .receiver = HUD,
                .super_class = (Class)class_getSuperclass((Class)cls)
            }};

            ((void (*)(struct objc_super *, SEL, id, id))objc_msgSendSuper)(&superInfo, @selector(touchesCancelled:withEvent:), touches, event);

            (void)[HUD attachToEdge];
        }};

        imp_implementationWithBlock(touchesCancelledWithEventBlock);

    '''
    return HM.evaluate_expression_value(expression=command_script, prefix=HMExpressionPrefix.gPrefix)


def makeAttachToEdgeIMP() -> lldb.SBValue:
    command_script = '''

        void (^attachToEdgeBlock)(UIView *, NSSet *, UIEvent *) = ^(UIView *HUD, NSSet * touches, UIEvent *event) {
            
            if (!HUD.window) {
                return;
            }
        
            UIEdgeInsets hm_safeAreaInsets = {0.0, 0.0, 0.0, 0.0};   
            hm_safeAreaInsets = [HUD.window safeAreaInsets];   
            CGFloat minX = hm_safeAreaInsets.left;
            CGFloat maxX = HUD.window.bounds.size.width - hm_safeAreaInsets.right;
            CGFloat minY = hm_safeAreaInsets.top;
            CGFloat maxY = HUD.window.bounds.size.height - hm_safeAreaInsets.bottom;
            
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
        
            CGRect targetFrame = (CGRect)[HUD frame];
            targetFrame.origin = (CGPoint){x, y};
            
            [UIView animateWithDuration:0.2 animations:^{
                HUD.frame = targetFrame;
            }];
            
        };

        imp_implementationWithBlock(attachToEdgeBlock);

    '''
    return HM.evaluate_expression_value(expression=command_script, prefix=HMExpressionPrefix.gPrefix)


def tapSelfBreakPointHandler(frame, bp_loc, extra_args, internal_dict) -> bool:
    HMDebugMainViewController.register()
    HM.process_continue()
    return True
