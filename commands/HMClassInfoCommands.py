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
import shlex
import optparse
import HMExpressionPrefix
import HMLLDBHelpers as HM
import HMLLDBClassInfo


def __lldb_init_module(debugger, internal_dict):
    debugger.HandleCommand('command script add -f HMClassInfoCommands.methods methods -h "Execute [inputClass _methodDescription] or [inputClass _shortMethodDescription]."')
    debugger.HandleCommand('command script add -f HMClassInfoCommands.properties properties -h "Execute [inputClass _propertyDescription]."')

    debugger.HandleCommand('command script add -f HMClassInfoCommands.findClass fclass -h "Find the class containing the input name(Case insensitive)."')
    debugger.HandleCommand('command script add -f HMClassInfoCommands.findSubclass fsubclass -h "Find the subclass of the input."')
    debugger.HandleCommand('command script add -f HMClassInfoCommands.findSuperClass fsuperclass -h "Find the superclass of the input."')
    debugger.HandleCommand('command script add -f HMClassInfoCommands.findMethod fmethod -h "Find the specified method in the method list, you can also find the method list of the specified class."')

    debugger.HandleCommand('command script add -f HMClassInfoCommands.print_ivars_info ivarsinfo -h "Show ivars information of class."')


def methods(debugger, command, exe_ctx, result, internal_dict):
    """
    Syntax:
        methods [--short] <className/classInstance>

    Examples:
        (lldb) methods UIViewController
        (lldb) methods -s UIViewController
        (lldb) methods [UIView new]

        (lldb) expression -l objc -O -- [NSObject new]
        <NSObject: 0x60000375f9a0>
        (lldb) methods 0x60000375f9a0

    Options:
        --short/-s; Use [inputClass _shortMethodDescription] instead of [inputClass _methodDescription]

    This command is implemented in HMClassInfoCommands.py
    """

    command_args = shlex.split(command)
    parser = generate_methods_option_parser()
    try:
        # options: optparse.Values
        # args: list
        (options, args) = parser.parse_args(command_args)
    except:
        result.SetError(parser.usage)
        return

    inputStr: str = ""
    for string in args:
        inputStr += string + " "
    inputStr = inputStr.rstrip()

    if len(inputStr) == 0:
        HM.DPrint("Requires a argument, Please enter \"help methods\" for help.")
        return

    if options.short:
        selName = "_shortMethodDescription"
    else:
        selName = "_methodDescription"

    value = HM.evaluateExpressionValue(expression=f'(NSString *)[{inputStr} performSelector:NSSelectorFromString(@"{selName}")]', printErrors=False)
    if HM.successOfSBError(value.GetError()):
        HM.DPrint(value.GetObjectDescription())
        return

    clsPrefixesValue = HM.getClassPrefixes()[1]
    command_script = f'''
        Class inputClass = objc_lookUpClass("{inputStr}");

        if (inputClass == nil) {{   //  Find prefixed class
            for (NSString *prefix in (NSMutableArray *){clsPrefixesValue.GetValue()}) {{
                NSString *clsName = [prefix stringByAppendingString:@".{inputStr}"];
                inputClass = objc_lookUpClass((char *)[clsName UTF8String]);
                if (inputClass) {{
                    break;
                }}
            }}
        }}

        NSMutableString *result = [[NSMutableString alloc] init];
        if (inputClass == nil) {{
            [result appendString:@"Unable to resolve {inputStr} or find {inputStr} class, maybe {inputStr} is not a subclass of NSObject\\n"];
        }} else {{
            if ((BOOL)[(Class)inputClass respondsToSelector:(SEL)NSSelectorFromString(@"{selName}")]) {{
                [result appendString:(NSString *)[inputClass performSelector:NSSelectorFromString(@"{selName}")]];
            }} else {{
                [result appendString:@"{inputStr} is not a subclass of NSObject"];
            }}
        }}

        (NSMutableString *)result;
    '''

    result = HM.evaluateExpressionValue(command_script).GetObjectDescription()
    HM.DPrint(result)


def generate_methods_option_parser() -> optparse.OptionParser:
    usage = "usage: methods [-s] <className/classInstance>"
    parser = optparse.OptionParser(usage=usage, prog="fsubclass")
    parser.add_option("-s", "--short",
                      action="store_true",
                      default=False,
                      dest="short",
                      help="Use [inputClass _shortMethodDescription] instead of [inputClass _methodDescription]")

    return parser


def properties(debugger, command, exe_ctx, result, internal_dict):
    """
    Syntax:
        properties <className/classInstance>

    Examples:
        (lldb) properties UIViewController
        (lldb) properties [NSObject new]

        (lldb) expression -l objc -O -- [NSObject new]
        <NSObject: 0x60000372f760>
        (lldb) properties 0x60000372f760

    This command is implemented in HMClassInfoCommands.py
    """

    if len(command) == 0:
        HM.DPrint("Requires a argument, Please enter \"help properties\" for help.")
        return

    value = HM.evaluateExpressionValue(expression=f'(NSString *)[{command} performSelector:NSSelectorFromString(@"_propertyDescription")]', printErrors=False)
    if HM.successOfSBError(value.GetError()):
        HM.DPrint(value.GetObjectDescription())
        return

    clsPrefixesValue = HM.getClassPrefixes()[1]
    command_script = f'''
        Class inputClass = objc_lookUpClass("{command}");

        if (inputClass == nil) {{   //  Find prefixed class
            for (NSString *prefix in (NSMutableArray *){clsPrefixesValue.GetValue()}) {{
                NSString *clsName = [prefix stringByAppendingString:@".{command}"];
                inputClass = objc_lookUpClass((char *)[clsName UTF8String]);
                if (inputClass) {{
                    break;
                }}
            }}
        }}

        NSMutableString *result = [[NSMutableString alloc] init];
        if (inputClass == nil) {{
            [result appendString:@"Unable to resolve {command} or find {command} class, maybe {command} is not a subclass of NSObject\\n"];
        }} else {{
            if ((BOOL)[(Class)inputClass respondsToSelector:(SEL)NSSelectorFromString(@"_propertyDescription")]) {{
                [result appendString:(NSString *)[inputClass performSelector:NSSelectorFromString(@"_propertyDescription")]];
            }} else {{
                [result appendString:@"{command} is not a subclass of NSObject"];
            }}
        }}

        (NSMutableString *)result;
    '''

    result = HM.evaluateExpressionValue(command_script).GetObjectDescription()
    HM.DPrint(result)


def findClass(debugger, command, exe_ctx, result, internal_dict):
    """
    Syntax:
        fclass <className>

    Examples:
        (lldb) fclass
        (lldb) fclass UITabBarController
        (lldb) fclass controller

    Notice:
        Case insensitive.

    This command is implemented in HMClassInfoCommands.py
    """

    HM.DPrint("Waiting...")

    if len(command) == 0:
        addObjectScript = '[classNames appendFormat:@"%@ (%p)\\n", name, classList[i]]; findCount += 1;'
    else:
        command = command.lower()
        addObjectScript = f'''
            if ([[name lowercaseString] containsString:@"{command}"]) {{
                [classNames appendFormat:@"%@ (%p)\\n", name, classList[i]];
                findCount += 1;
            }}
        '''

    command_script = f'''
        unsigned int findCount = 0;
        unsigned int classCount;
        Class *classList = objc_copyClassList(&classCount);
        NSMutableString *classNames = [[NSMutableString alloc] init];
        for (int i = 0; i < classCount; i++) {{
            NSString *name = [[NSString alloc] initWithUTF8String:class_getName(classList[i])];
            {addObjectScript}
        }}
        free(classList);

        if (findCount == 0) {{
            [classNames insertString:@"No class found.\\n" atIndex:0];
        }} else {{
            [classNames insertString:[[NSString alloc] initWithFormat:@"Count: %u \\n", findCount] atIndex:0];
        }}
        (NSMutableString *)classNames;
    '''

    classNames = HM.evaluateExpressionValue(command_script).GetObjectDescription()
    HM.DPrint(classNames)


def findSubclass(debugger, command, exe_ctx, result, internal_dict):
    """
    Syntax:
        fsubclass [--nonrecursively] <className>

    Options:
        --nonrecursively/-n; Find subclass non-recursively

    Examples:
        (lldb) fsubclass UIViewController
        (lldb) fsubclass -n UIViewController


    This command is implemented in HMClassInfoCommands.py
    """

    command_args = shlex.split(command)
    parser = generate_findSubclass_option_parser()
    try:
        # options: optparse.Values
        # args: list
        (options, args) = parser.parse_args(command_args)
    except:
        result.SetError(parser.usage)
        return

    if len(args) != 1:
        HM.DPrint("Requires a argument, Please enter \"help fsubclass\" for help.")
        return

    HM.DPrint("Waiting...")

    if options.nonrecursively:
        compareScript = '''
            if (class_getSuperclass(cls) == inputClass){
                NSString *name = [[NSString alloc] initWithUTF8String:class_getName(cls)];
                [result appendFormat:@"%@ (%p)\\n", name, cls];
                findCount += 1;
            }
        '''

    else:
        compareScript = '''
            for (Class superClass = class_getSuperclass(cls); superClass != nil; superClass = class_getSuperclass(superClass)) {
                if (superClass == inputClass) {
                    NSString *name = [[NSString alloc] initWithUTF8String:class_getName(cls)];
                    [result appendFormat:@"%@ (%p)\\n", name, cls];
                    findCount += 1;

                    break;
                }
            }
        '''

    clsPrefixesValue = HM.getClassPrefixes()[1]
    command_script = f'''
        Class inputClass = objc_lookUpClass("{args[0]}");

        if (inputClass == nil) {{   //  Find prefixed class
            for (NSString *prefix in (NSMutableArray *){clsPrefixesValue.GetValue()}) {{
                NSString *clsName = [prefix stringByAppendingString:@".{args[0]}"];
                inputClass = objc_lookUpClass((char *)[clsName UTF8String]);
                if (inputClass) {{
                    break;
                }}
            }}
        }}

        NSMutableString *result = [[NSMutableString alloc] init];
        if (inputClass == nil) {{
            [result appendString:@"Can't find {args[0]} class\\n"];
        }} else {{
            unsigned int classCount;
            unsigned int findCount = 0;
            Class *classList = objc_copyClassList(&classCount);

            for (int i = 0; i < classCount; i++) {{
                Class cls = classList[i];
                {compareScript}
            }}

            if (findCount == 0) {{
                [result insertString:@"No subclass found.\\n" atIndex:0];
            }} else {{
                [result insertString:[[NSString alloc] initWithFormat:@"Subclass count: %u \\n", findCount] atIndex:0];
            }}
            
            free(classList);
        }}

        (NSMutableString *)result;
    '''

    classNames = HM.evaluateExpressionValue(command_script).GetObjectDescription()
    HM.DPrint(classNames)


def generate_findSubclass_option_parser() -> optparse.OptionParser:
    usage = "usage: fsubclass [-n] <className>"
    parser = optparse.OptionParser(usage=usage, prog="fsubclass")
    parser.add_option("-n", "--nonrecursively",
                      action="store_true",
                      default=False,
                      dest="nonrecursively",
                      help="Find subclass non-recursively")

    return parser


def findSuperClass(debugger, command, exe_ctx, result, internal_dict):
    """
    Syntax:
        fsuperclass <className>

    Examples:
        (lldb) fsuperclass UIButton

    This command is implemented in HMClassInfoCommands.py
    """

    if len(command) == 0:
        HM.DPrint("Requires a argument, Please enter \"help fsuperclass\" for help.")
        return

    clsPrefixesValue = HM.getClassPrefixes()[1]
    command_script = f'''
        Class inputClass = objc_lookUpClass("{command}");

        if (inputClass == nil) {{   //  Find prefixed class
            for (NSString *prefix in (NSMutableArray *){clsPrefixesValue.GetValue()}) {{
                NSString *clsName = [prefix stringByAppendingString:@".{command}"];
                inputClass = objc_lookUpClass((char *)[clsName UTF8String]);
                if (inputClass) {{
                    break;
                }}
            }}
        }}

        NSMutableString *result = [[NSMutableString alloc] init];
        if (inputClass == nil) {{
            [result appendString:@"Can't find {command} class\\n"];
        }} else {{
            [result appendString:[[NSString alloc] initWithUTF8String:class_getName(inputClass)]];
            for (Class superClass = class_getSuperclass(inputClass); superClass != nil; superClass = class_getSuperclass(superClass)) {{
                NSString *name = [[NSString alloc] initWithUTF8String:class_getName(superClass)];
                [result appendFormat:@" : %@", name];
            }}
        }}

        (NSMutableString *)result;
    '''

    classNames = HM.evaluateExpressionValue(command_script).GetObjectDescription()
    HM.DPrint(classNames)


def findMethod(debugger, command, exe_ctx, result, internal_dict):
    """
    Syntax:
        fmethod <methodName>  (Case insensitive.)
        fmethod [--class] <className>

    Options:
        --class/-c; Find all method in the class

    Examples:
        (lldb) fmethod viewdid
        (lldb) fmethod viewDidLayoutSubviews
        (lldb) fmethod -c UITableViewController

    This command is implemented in HMClassInfoCommands.py
    """

    command_args = shlex.split(command)
    parser = generate_findMethod_option_parser()
    try:
        # options: optparse.Values
        # args: list
        (options, args) = parser.parse_args(command_args)
    except:
        result.SetError(parser.usage)
        return

    if not options.cls:
        if len(args) != 1:
            HM.DPrint("Error input, Please enter \"help fmethod\" for help.")
            return
        elif len(args[0]) <= 4:
            HM.DPrint("Argument length must be greater than 4.")
            return


    HM.DPrint("Waiting...")

    if options.cls:
        clsPrefixesValue = HM.getClassPrefixes()[1]
        command_script = f'''
            NSMutableString *result = [[NSMutableString alloc] init];
            Class inputClass = objc_lookUpClass("{options.cls}");
            if (inputClass == nil) {{   //  Find prefixed class
                for (NSString *prefix in (NSMutableArray *){clsPrefixesValue.GetValue()}) {{
                    NSString *clsName = [prefix stringByAppendingString:@".{options.cls}"];
                    inputClass = objc_lookUpClass((char *)[clsName UTF8String]);
                    if (inputClass) {{
                        break;
                    }}
                }}
            }}

            if (inputClass == nil) {{
                [result appendString:@"Can't find {options.cls} class\\n"];
            }} else {{
                unsigned int instanceMethodCount;
                Method *instanceMethodList = class_copyMethodList(inputClass, &instanceMethodCount);
                for (int j = 0; j < instanceMethodCount; ++j) {{
                    Method method = instanceMethodList[j];
                    NSString *selName = [[NSString alloc] initWithUTF8String:sel_getName(method_getName(method))];
                    void (*impl_hm)() = (void (*)())method_getImplementation(method);
                    [result appendFormat:@"(-) %@ (%p)\\n\\tType encoding:%s\\n", selName, impl_hm, method_getTypeEncoding(method)];
                }}
                free(instanceMethodList);
                
                unsigned int classMethodCount = 0;
                Class metaCls = object_getClass(inputClass);
                if (class_isMetaClass(metaCls)) {{
                    Method *classMethodList = class_copyMethodList(metaCls, &classMethodCount);
                    for (int j = 0; j < classMethodCount; ++j) {{
                        Method method = classMethodList[j];
                        NSString *selName = [[NSString alloc] initWithUTF8String:sel_getName(method_getName(method))];
                        void (*impl_hm)() = (void (*)())method_getImplementation(method);
                        [result appendFormat:@"(+) %@ (%p)\\n\\tType encoding:%s\\n", selName, impl_hm, method_getTypeEncoding(method)];
                    }}
                    free(classMethodList);
                }}
                
                if (instanceMethodCount + classMethodCount == 0) {{
                    [result insertString:@"No method found.\\n" atIndex:0];
                }} else {{
                    [result insertString:[[NSString alloc] initWithFormat:@"Instance methods count: %u. Class method count: %u.\\n", instanceMethodCount, classMethodCount] atIndex:0];
                    NSString *clsName = [[NSString alloc] initWithUTF8String:class_getName(inputClass)];
                    [result insertString:[[NSString alloc] initWithFormat:@"Class: %@ (%p)\\n", clsName, inputClass] atIndex:0];
                }}
            }}
            
            (NSMutableString *)result;
        '''

    else:
        inputMethodName = args[0].lower()
        command_script = f'''
            NSString *inputMethodName = [[NSString alloc] initWithUTF8String:"{inputMethodName}"];
            
            NSMutableString *result = [[NSMutableString alloc] init];
        
            unsigned int classCount;
            unsigned int findCount = 0;
            Class *classList = objc_copyClassList(&classCount);
        
            for (int i = 0; i < classCount; ++i) {{
                Class cls = classList[i];
                // Instance Methods
                unsigned int instanceMethodCount;
                Method *instanceMethodList = class_copyMethodList(cls, &instanceMethodCount);
        
                for (int j = 0; j < instanceMethodCount; ++j) {{
                    Method method = instanceMethodList[j];
                    NSString *selName = [[NSString alloc] initWithUTF8String:sel_getName(method_getName(method))];
                    if ([[selName lowercaseString] containsString:inputMethodName]) {{
                        NSString *clsName = [[NSString alloc] initWithUTF8String:class_getName(cls)];
                        void (*impl_hm)() = (void (*)())method_getImplementation(method);
                        [result appendFormat:@"(-) %@ (%p)\\n\\tType encoding:%s\\n\\tClass:%@\\n", selName, impl_hm, method_getTypeEncoding(method), clsName];
                        findCount += 1;
                    }}
                }}
                free(instanceMethodList);
                
                // Class Methods
                Class metaCls = object_getClass(cls);
                if (!class_isMetaClass(metaCls)) {{
                    continue;
                }}
                unsigned int classMethodCount;
                Method *classMethodList = class_copyMethodList(metaCls, &classMethodCount);
        
                for (int j = 0; j < classMethodCount; ++j) {{
                    Method method = classMethodList[j];
                    NSString *selName = [[NSString alloc] initWithUTF8String:sel_getName(method_getName(method))];
                    if ([[selName lowercaseString] containsString:inputMethodName]) {{
                        NSString *clsName = [[NSString alloc] initWithUTF8String:class_getName(cls)];
                        void (*impl_hm)() = (void (*)())method_getImplementation(method);
                        [result appendFormat:@"(+) %@ (%p)\\n\\tType encoding:%s\\n\\tClass:%@\\n", selName, impl_hm, method_getTypeEncoding(method), clsName];
                        findCount += 1;
                    }}
                }}
                free(classMethodList);
            }}
            if (findCount == 0) {{
                [result insertString:@"No method found.\\n" atIndex:0];
            }} else {{
                [result insertString:[[NSString alloc] initWithFormat:@"Methods count: %u \\n", findCount] atIndex:0];
            }}

            free(classList);
            (NSMutableString *)result;
        '''

    result = HM.evaluateExpressionValue(expression=command_script, prefix=HMExpressionPrefix.gPrefix).GetObjectDescription()
    HM.DPrint(result)


def generate_findMethod_option_parser() -> optparse.OptionParser:
    usage = "usage: fmethod [-c] <className>"
    parser = optparse.OptionParser(usage=usage, prog="fmethod")
    parser.add_option("-c", "--class",
                      action="store",
                      default=None,
                      dest="cls",
                      help="Find all method in the class")

    return parser


def print_ivars_info(debugger, command, exe_ctx, result, internal_dict):
    """
    Syntax:
        ivarsinfo <className>

    Examples:
        (lldb) ivarsinfo UIView
        (lldb) ivarsinfo MYModel

    This command is implemented in HMClassInfoCommands.py
    """

    if len(command) == 0:
        HM.DPrint("Requires a argument, Please enter \"help ivarsinfo\" for help.")
        return

    if not HM.existClass(command):
        HM.DPrint(f"{command} does not exist.")
        return

    command_script = f'''        
        Class inputClass = objc_lookUpClass("{command}");
        
        NSMutableString *result = [[NSMutableString alloc] init];
        [result appendString:[[NSString alloc] initWithFormat:@"%s (%p)", class_getName(inputClass), inputClass]];
        
        unsigned int ivarsCount = 0;
        Ivar *ivarList = class_copyIvarList(inputClass, &ivarsCount);
        for (int i = 0; i < ivarsCount; ++i) {{
            Ivar ivar = ivarList[i];
            const char *ivarName = ivar_getName(ivar);
            const char *ivarTypeEncoding = ivar_getTypeEncoding(ivar);
            long ivarOffset = ivar_getOffset(ivar);
            
            NSString *ivarInfo = [[NSString alloc] initWithFormat:@"\\n%s\\n\\ttypeEncoding:%s\\n\\toffset:%ld hex:0x%lx", ivarName, ivarTypeEncoding, ivarOffset, ivarOffset];
            [result appendString:ivarInfo];
        }}
        if (ivarsCount == 0) {{
            [result appendString:@"\\n[HMLLDB] No ivar found."];
        }}
        free(ivarList);
        (NSMutableString *)result;
    '''

    result = HM.evaluateExpressionValue(command_script).GetObjectDescription()
    HM.DPrint(result)

