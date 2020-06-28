""" File: HMClassInfoCommands.py

An lldb Python script about class information.

"""

import lldb
import shlex
import optparse
import HMLLDBHelpers as HM
import HMLLDBClassInfo


def __lldb_init_module(debugger, internal_dict):
    debugger.HandleCommand('command script add -f HMClassInfoCommands.findClass fclass -h "Find the class containing the input name(Case insensitive)"')
    debugger.HandleCommand('command script add -f HMClassInfoCommands.findSubclass fsubclass -h "Find the subclass of the input"')
    debugger.HandleCommand('command script add -f HMClassInfoCommands.findMethod fmethod -h "Find the method"')


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
        addObjectScript = '[classNames appendFormat:@"%@\\n", name]; findCount += 1;'
    else:
        command = command.lower()
        addObjectScript = f'''
            if ([[name lowercaseString] containsString:@"{command}"]) {{
                [classNames appendFormat:@"%@\\n", name];
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
        classNames;
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
                [result appendFormat:@"%@\\n", name];
                findCount += 1;
            }
        '''

    else:
        compareScript = '''
            for (Class superClass = class_getSuperclass(cls); superClass != nil; superClass = class_getSuperclass(superClass)) {
                if (superClass == inputClass) {
                    NSString *name = [[NSString alloc] initWithUTF8String:class_getName(cls)];
                    [result appendFormat:@"%@\\n", name];
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

        result;
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
        elif len(args[0]) <= 5:
            HM.DPrint("Argument length must be greater than 5.")
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
                unsigned int methodCount;
                Method *methodList = class_copyMethodList(inputClass, &methodCount);
                for (int j = 0; j < methodCount; ++j) {{
                    Method method = methodList[j];
                    SEL sel = method_getName(method);
                    NSString *selName = [[NSString alloc] initWithUTF8String:sel_getName(sel)];
                    [result appendFormat:@"%@\\n\\tType encoding:%s\\n", selName, method_getTypeEncoding(method)];
                }}
                free(methodList);
                
                if (methodCount == 0) {{
                    [result insertString:@"No method found.\\n" atIndex:0];
                }} else {{
                    [result insertString:[[NSString alloc] initWithFormat:@"Methods count: %u \\n", methodCount] atIndex:0];
                }}
            }}
            
            result;
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
                unsigned int methodCount;
                Method *methodList = class_copyMethodList(cls, &methodCount);
        
                for (int j = 0; j < methodCount; ++j) {{
                    Method method = methodList[j];
                    SEL sel = method_getName(method);
                    NSString *selName = [[NSString alloc] initWithUTF8String:sel_getName(sel)];
                    if ([[selName lowercaseString] containsString:inputMethodName]) {{
                        NSString *clsName = [[NSString alloc] initWithUTF8String:class_getName(cls)];
                        [result appendFormat:@"%@\\n\\tType encoding:%s\\n\\tClass:%@\\n", selName, method_getTypeEncoding(method), clsName];
                        findCount += 1;
                    }}
                }}
                free(methodList);
            }}
            if (findCount == 0) {{
                [result insertString:@"No method found.\\n" atIndex:0];
            }} else {{
                [result insertString:[[NSString alloc] initWithFormat:@"Methods count: %u \\n", findCount] atIndex:0];
            }}

            free(classList);
            result;
        '''

    result = HM.evaluateExpressionValue(command_script).GetObjectDescription()
    HM.DPrint(result)



def generate_findSubclass_option_parser() -> optparse.OptionParser:
    usage = "usage: fsubclass [-n] <className>"
    parser = optparse.OptionParser(usage=usage, prog="fsubclass")
    parser.add_option("-n", "--nonrecursively",
                      action="store_true",
                      default=False,
                      dest="nonrecursively",
                      help="Find subclass non-recursively")

    return parser


def generate_findMethod_option_parser() -> optparse.OptionParser:
    usage = "usage: fmethod [-c] <className>"
    parser = optparse.OptionParser(usage=usage, prog="fmethod")
    parser.add_option("-c", "--class",
                      action="store",
                      default=None,
                      dest="cls",
                      help="Find all method in the class")

    return parser
