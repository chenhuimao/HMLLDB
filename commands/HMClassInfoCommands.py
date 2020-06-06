""" File: HMClassInfoCommands.py

An lldb Python script about class information.

"""

import lldb
import HMLLDBHelpers as HM
import HMLLDBClassInfo


def __lldb_init_module(debugger, internal_dict):
    debugger.HandleCommand('command script add -f HMClassInfoCommands.findClass fclass -h "Find the class containing the input name"')


def findClass(debugger, command, exe_ctx, result, internal_dict):
    """
    Syntax:
        fclass <className>

    Examples:
        (lldb) fclass
        (lldb) fclass UITabBarController
        (lldb) fclass controller

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


