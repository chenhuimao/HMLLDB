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
        addObjectScript = '[classNames appendString:name]; [classNames appendString:@"\\n"]; findCount += 1;'
    else:
        command = command.lower()
        addObjectScript = f'''
            if ([[name lowercaseString] containsString:@"{command}"]) {{
                [classNames appendString:name];
                [classNames appendString:@"\\n"];
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
            [classNames insertString:@"No class found." atIndex:0];
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
                [result appendString:name];
                [result appendString:@"\\n"];
                findCount += 1;
            }
        '''

    else:
        compareScript = '''
            for (Class superClass = class_getSuperclass(cls); superClass != nil; superClass = class_getSuperclass(superClass)) {
                if (superClass == inputClass) {
                    NSString *name = [[NSString alloc] initWithUTF8String:class_getName(cls)];
                    [result appendString:name];
                    [result appendString:@"\\n"];
                    findCount += 1;

                    break;
                }
            }
        '''

    command_script = f'''
        Class inputClass = objc_lookUpClass("{args[0]}");
        NSMutableString *result = [[NSMutableString alloc] init];

        if (inputClass == nil) {{
            [result appendString:@"Can't find {args[0]} class"];
        }} else {{
            unsigned int classCount;
            unsigned int findCount = 0;
            Class *classList = objc_copyClassList(&classCount);

            for (int i = 0; i < classCount; i++) {{
                Class cls = classList[i];
                {compareScript}
            }}

            if (findCount == 0) {{
                [result insertString:@"No subclass found." atIndex:0];
            }} else {{
                [result insertString:[[NSString alloc] initWithFormat:@"Subclass count: %u \\n", findCount] atIndex:0];
            }}
            
            free(classList);
        }}

        result;
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
