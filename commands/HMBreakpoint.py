# The MIT License (MIT)
#
# Copyright (c) 2022 Huimao Chen
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
from typing import List
import shlex
import optparse
import re
import time
import HMExpressionPrefix
import HMLLDBHelpers as HM
import HMLLDBClassInfo
import HMTrace


def __lldb_init_module(debugger, internal_dict):
    debugger.HandleCommand('command script add -f HMBreakpoint.breakpoint_frame bpframe -h "Set a breakpoint that stops only when the specified stack keyword is matched."')
    debugger.HandleCommand('command script add -f HMBreakpoint.breakpoint_next_oc_method bpmethod -h "Set a breakpoint that stops when the next OC method is called(via objc_msgSend) in the current thread."')
    debugger.HandleCommand('command script add -f HMBreakpoint.breakpoint_message bpmessage -h "Set a breakpoint for a selector on a class, even if the class itself doesn\'t override that selector."')


def breakpoint_frame(debugger, command, exe_ctx, result, internal_dict):
    """
    Syntax:
        bpframe [--one-shot] <symbol or address> <stack keyword 1> <stack keyword 2> ... <stack keyword n>

    Options:
        --one-shot/-o; The breakpoint is deleted the first time it stop.

    Examples:
        // Stop when "setupChildViewControllers:" is hit and the call stack contains "otherFunction"
        (lldb) bpframe setupChildViewControllers: otherFunction

        // Stop when "setupChildViewControllers:" is hit and the call stack contains "function_1" & "function_2"
        (lldb) bpframe setupChildViewControllers: function_1 function_2

        // Stop when "0x1025df6c0" is hit and the call stack contains "0x19261c1c0" & "0x19261bec0" addresses
        (lldb) bpframe 0x1025df6c0 0x19261c1c0 0x19261bec0

        // Stop when "0x1025df6c0" is hit and the call stack contains "otherFunction" & "0x19261bec0" address
        (lldb) bpframe 0x1025df6c0 otherFunction 0x19261bec0

        // --one-shot/-o; The breakpoint is deleted the first time it stop.
        (lldb) bpframe -o setupChildViewControllers: otherFunction
        (lldb) bpframe -o 0x1025df6c0 otherFunction

    Notice:
        1. Separate keywords with spaces.
        2. Match keywords in order.
        3. Hitting a breakpoint is expensive even if it doesn't stop. Do not set breakpoint on high frequency symbol or address.

    This command is implemented in HMBreakpoint.py
    """

    command_args = shlex.split(command)
    parser = generate_bpframe_option_parser()
    try:
        # options: optparse.Values
        # args: list
        (options, args_list) = parser.parse_args(command_args)
    except:
        result.SetError(parser.usage)
        return

    # HM.DPrint(args_list)
    if len(args_list) < 2:
        HM.DPrint("Error input. Requires at least 2 parameters. Please enter 'help bpframe' for more infomation")
        return

    target = lldb.debugger.GetSelectedTarget()
    is_address, address = HM.int_value_from_string(args_list[0])
    if is_address:
        # HM.DPrint(address)
        bp = target.BreakpointCreateByAddress(address)
    else:
        bp = target.BreakpointCreateByName(args_list[0])
    bp.AddName(f"HMLLDB_bpframe_{args_list[0]}")
    bp.SetOneShot(options.is_one_shot)

    # call stack symbols for script callback
    call_stack_symbols: str = ""
    for i in range(1, len(args_list)):
        if i == 1:
            call_stack_symbols += '"' + args_list[1] + '"'
        else:
            call_stack_symbols += ',"' + args_list[i] + '"'

    extra_args = lldb.SBStructuredData()
    stream = lldb.SBStream()
    stream.Print(f'[{call_stack_symbols}]')
    extra_args.SetFromJSON(stream)

    # set callback with extra_args
    time.sleep(0.1)
    error: lldb.SBError = bp.SetScriptCallbackFunction("HMBreakpoint.breakpoint_frame_handler", extra_args)
    if error.Success():
        HM.DPrint("Set breakpoint successfully")
        bp_id = bp.GetID()
        lldb.debugger.HandleCommand(f"breakpoint list {bp_id}")
    else:
        HM.DPrint(error)


def generate_bpframe_option_parser() -> optparse.OptionParser:
    usage = '''usage: 
    bpframe [--one-shot] <symbol or address> <stack keyword 1> <stack keyword 2> ... <stack keyword n>
    '''
    parser = optparse.OptionParser(usage=usage, prog="bpframe")
    parser.add_option("-o", "--one-shot",
                      action="store_true",
                      default=False,
                      dest="is_one_shot",
                      help="The breakpoint is deleted the first time it stop.")

    return parser


def breakpoint_frame_handler(frame, bp_loc, extra_args, internal_dict) -> bool:
    if not extra_args.IsValid():
        return False
    if extra_args.GetType() != lldb.eStructuredDataTypeArray:
        return False

    # Get keywords
    keywords: List[str] = []
    for i in range(extra_args.GetSize()):
        arg: lldb.SBStructuredData = extra_args.GetItemAtIndex(i)
        if arg.GetType() != lldb.eStructuredDataTypeString:
            continue
        keyword = arg.GetStringValue(300)
        keywords.append(keyword)

    keywords_size = len(keywords)
    if keywords_size == 0:
        HM.DPrint("Error: Missing keywords.")
        return False
    keywords_index = 0

    # Get frame and match keywords in order
    result = False
    thread = frame.GetThread()
    for i in range(thread.GetNumFrames()):
        frame_in_stack = thread.GetFrameAtIndex(i)
        frame_pc_address = frame_in_stack.GetPC()
        current_keyword = keywords[keywords_index]
        is_address, address = HM.int_value_from_string(current_keyword)
        if is_address:
            # Increase compatibility (address + 4)
            if address == frame_pc_address or address + 4 == frame_pc_address:
                keywords_index += 1
        else:
            frame_display_name = frame_in_stack.GetDisplayFunctionName()
            if not frame_display_name:
                frame_display_name = hex(frame_pc_address)
            if current_keyword in frame_display_name:
                keywords_index += 1

        if keywords_index == keywords_size:
            result = True
            break

    if result:
        HM.DPrint(f"Hit breakpoint with bpframe command.")

    return result


def breakpoint_next_oc_method(debugger, command, exe_ctx, result, internal_dict):
    """
    Syntax:
        bpmethod [--continue]

    Options:
        --continue/-c; Continue program execution after executing bpmethod

    Examples:
        (lldb) bpmethod
        (lldb) bpmethod -c

    Notice:
        The breakpoint stops only for the thread whose TID matches the current thread's ID.

    This command is implemented in HMBreakpoint.py
    """

    command_args = shlex.split(command)
    parser = generate_bpmethod_option_parser()
    try:
        # options: optparse.Values
        # args: list
        (options, args) = parser.parse_args(command_args)
    except:
        result.SetError(parser.usage)
        return

    # Step:
    # 1. Add breakpoint in objc_msgSend.
    # 2. Get arguments(object & selector) by registers. Delete breakpoint(objc_msgSend).
    # 3. Get implementation via runtime.
    # 4. Set breakpoint(OneShot) in implementation.

    thread = exe_ctx.GetThread()
    thread_id = thread.GetThreadID()
    target = exe_ctx.GetTarget()
    bp = target.BreakpointCreateByName("objc_msgSend", "libobjc.A.dylib")
    bp.AddName("HMLLDB_bpmethod_objc_msgSend")
    bp.SetThreadID(thread_id)
    time.sleep(0.1)
    bp.SetScriptCallbackFunction("HMBreakpoint.breakpoint_next_oc_method_handler")

    HM.DPrint(f"Target thread index:{thread.GetIndexID()}, thread id:{thread_id}.")
    if options.is_continue:
        HM.process_continue()
    else:
        HM.DPrint("Done! You can continue program execution.")


def generate_bpmethod_option_parser() -> optparse.OptionParser:
    usage = "usage: bpmethod [--continue]"
    parser = optparse.OptionParser(usage=usage, prog="bpmethod")
    parser.add_option("-c", "--continue",
                      action="store_true",
                      default=False,
                      dest="is_continue",
                      help="Continue program execution after executing bpmethod")

    return parser


def breakpoint_next_oc_method_handler(frame, bp_loc, extra_args, internal_dict) -> bool:
    # Delete current breakpoint
    bp = bp_loc.GetBreakpoint()
    target = frame.GetThread().GetProcess().GetTarget()
    target.BreakpointDelete(bp.GetID())

    # Get object and selector from registers
    registers: lldb.SBValueList = frame.GetRegisters()
    object_value: lldb.SBValue
    selector_value: lldb.SBValue
    for value in registers:
        if "General Purpose Registers" in value.GetName():
            children_num = value.GetNumChildren()
            for i in range(children_num):
                reg_value = value.GetChildAtIndex(i)
                if reg_value.GetName() in ["x0", "rdi"]:
                    object_value = reg_value
                elif reg_value.GetName() in ["x1", "rsi"]:
                    selector_value = reg_value

    # Set breakpoint with object and selector.
    set_breakpoint_with_object_and_selector(target, object_value, selector_value)

    return False


def set_breakpoint_with_object_and_selector(target: lldb.SBTarget, object_value: lldb.SBValue, selector_value: lldb.SBValue):
    command_script = f'''
        id object = (id){object_value.GetValue()};
        char *selName = (char *){selector_value.GetValue()};
        Class cls = object_getClass((id)object);
        SEL hm_selector = sel_registerName(selName);
        Method targetMethod = class_getInstanceMethod(cls, hm_selector);
        (IMP)method_getImplementation(targetMethod);
    '''
    imp_value = HM.evaluate_expression_value(expression=command_script, prefix=HMExpressionPrefix.gPrefix)
    if not HM.is_SBValue_has_value(imp_value):
        selector_desc = HM.evaluate_expression_value(f"(char *){selector_value.GetValue()};").GetSummary()
        HM.DPrint(f"Failed to find {selector_desc} implementation in object({object_value.GetValue()})")
        return

    HM.DPrint(f"Set a breakpoint on the implemented address:{imp_value.GetValue()}")
    bp = target.BreakpointCreateByAddress(imp_value.GetValueAsUnsigned())
    bp.AddName("HMLLDB_bpmethod_implementation")
    bp.SetOneShot(True)


# Inspired by "bmessage" command in chisel: https://github.com/facebook/chisel/blob/main/commands/FBDebugCommands.py.
# "chisel" is implemented by conditional breakpoint. "HMLLDB" is implemented by runtime, it will add the method if the class itself doesn't override that selector.
def breakpoint_message(debugger, command, exe_ctx, result, internal_dict):
    """
    Syntax:
        bpmessage -[<class_name> <selector>]
        bpmessage +[<class_name> <selector>]

    Examples:
        (lldb) bpmessage -[MyModel release]
        (lldb) bpmessage -[MyModel dealloc]


    Notice:
        "bmessage"(in "chisel")is implemented by conditional breakpoint.
        "bpmessage"(in "HMLLDB") is implemented by runtime. It will add the method if the class itself doesn't override that selector, which reduces the loss of non-target classes hitting breakpoint.

    This command is implemented in HMBreakpoint.py
    """

    methodPattern = re.compile(
        r"""
  (?P<scope>[-+])?
  \[
    (?P<target>.*?)
    \s+
    (?P<selector>.*)
  \]
""",
        re.VERBOSE,
    )

    match = methodPattern.match(command)

    if not match:
        HM.DPrint("Failed to parse expression. Please enter \"help bpmessage\" for help.")
        return

    method_type_character = match.group("scope")
    class_name = match.group("target")
    method_name = match.group("selector")
    if method_type_character == '+':
        is_class_method = 1
        method_type = "class"
    elif method_type_character == '-':
        is_class_method = 0
        method_type = "instance"
    else:
        HM.DPrint("Failed to parse expression. Please enter \"help bpmessage\" for help.")
        return

    HM.DPrint("Waiting...")

    command_script = f'''
        NSMutableDictionary *resultDic = [[NSMutableDictionary alloc] init];
        SEL methodSelector = (SEL)sel_registerName("{method_name}");
        do {{
            Class cls = objc_lookUpClass("{class_name}");
            if (!cls) {{
                [resultDic setObject:@"Can't find {class_name} class." forKey:(id)@"failKey"];
                break;
            }}
            
            if ({is_class_method}) {{
                cls = (Class)object_getClass((id)cls);
                if (!cls) {{
                    [resultDic setObject:@"Can't find {class_name} meta class." forKey:(id)@"failKey"];
                    break;
                }}
            }}
            
            
            unsigned int instanceMethodCount;
            void (*originalIMP)(void) = 0;
    
            Method *instanceMethodList = class_copyMethodList(cls, &instanceMethodCount);
            for (int i = 0; i < instanceMethodCount; ++i) {{
                Method method = instanceMethodList[i];
                if (strcmp((const char *)sel_getName(methodSelector), (const char *)sel_getName(method_getName(method))) == 0) {{
                    originalIMP = (void (*)(void))method_getImplementation(method);
                    break;
                }}
            }}
            extern void free(void *f_address);
            free(instanceMethodList);
            
            if (originalIMP) {{
                NSString *adddressValue = [[NSString alloc] initWithFormat:@"0x%lx", (long)originalIMP];
                [resultDic setObject:adddressValue forKey:(id)@"addressKey"];
                [resultDic setObject:@"Find the implementation in the method list." forKey:(id)@"successKey"];
                break;
            }}
            

            Method originalMethod = class_getInstanceMethod(cls, methodSelector);
            if (!originalMethod) {{
                [resultDic setObject:@"The {method_name} {method_type} method does not exist in the {class_name} and its super class." forKey:(id)@"failKey"];
                break;
            }}
            
            originalIMP = (void (*)(void))method_getImplementation(originalMethod);
    
            void (^IMPBlock_hm)(id) = ^(id instance_hm) {{
                ((void (*)(id, char *)) originalIMP)(instance_hm, (char *)sel_getName(methodSelector));
            }};
            
            void (*newIMP)(void) = imp_implementationWithBlock(IMPBlock_hm);
            class_addMethod(cls, methodSelector, newIMP, method_getTypeEncoding(originalMethod));
            
            NSString *adddressValue = [[NSString alloc] initWithFormat:@"0x%lx", (long)newIMP];
            [resultDic setObject:adddressValue forKey:(id)@"addressKey"];
            [resultDic setObject:@"Find the implementation in the super class. HMLLDB added a new {method_name} {method_type} method to {class_name} class." forKey:(id)@"successKey"];
            
        }} while (0);
        
        
        (NSMutableDictionary *)resultDic;
    '''

    result_dic_value: lldb.SBValue = HM.evaluate_expression_value(expression=command_script, prefix=HMExpressionPrefix.gPrefix)

    HM.DPrint("Waiting......")
    # print result string
    command_get_desc = f'''
        NSMutableDictionary *resultDic = (NSMutableDictionary *)({result_dic_value.GetValueAsUnsigned()})
        NSString *desc_hm = (NSString *)[resultDic objectForKey:(id)@"failKey"];
        if (!desc_hm) {{
            desc_hm = (NSString *)[resultDic objectForKey:(id)@"successKey"];
        }}
        (NSString *)desc_hm; 
    '''

    desc_value = HM.evaluate_expression_value(command_get_desc)
    HM.DPrint(desc_value.GetObjectDescription())

    # get address
    command_get_address = f'''
        NSMutableDictionary *resultDic = (NSMutableDictionary *)({result_dic_value.GetValueAsUnsigned()})
        NSString *address_hm = (NSString *)[resultDic objectForKey:(id)@"addressKey"];
        (NSString *)address_hm; 
    '''
    address_value = HM.evaluate_expression_value(command_get_address)
    if not HM.is_SBValue_has_value(address_value):
        return
    target_address: str = address_value.GetObjectDescription()


    # set breakpoint
    HM.DPrint(f"Will add a breakpoint in address:{target_address}")

    target = lldb.debugger.GetSelectedTarget()
    bp = target.BreakpointCreateByAddress(int(target_address, 16))
    bp.AddName(f"bpmessage_{class_name}_{method_name}_{target_address}")

    extra_args = lldb.SBStructuredData()
    stream = lldb.SBStream()
    stream.Print(f"\"{command}\"")
    extra_args.SetFromJSON(stream)
    time.sleep(0.1)
    bp.SetScriptCallbackFunction("HMBreakpoint.bpmessage_breakpoint_handler", extra_args)

    bp_id = bp.GetID()
    debugger.HandleCommand(f"breakpoint list {bp_id}")
    HM.DPrint("Done!")


def bpmessage_breakpoint_handler(frame, bp_loc, extra_args, internal_dict) -> bool:
    if not extra_args.IsValid():
        return True
    if extra_args.GetType() != lldb.eStructuredDataTypeString:
        return True

    method: str = extra_args.GetStringValue(1000)
    HM.DPrint(f"Hit breakpoint in {method}.")

    if HM.is_arm64(frame.GetThread().GetProcess().GetTarget()):
        exe_ctx = lldb.SBExecutionContext(frame)
        HMTrace.complete_backtrace(None, None, exe_ctx, None, None)
    return True

