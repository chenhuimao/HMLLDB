""" File: HMFileCommands.py

An lldb Python script about file.

"""

import lldb
import HMLLDBHelpers as HM
import os
import shlex
import optparse


def __lldb_init_module(debugger, internal_dict):
    debugger.HandleCommand('command script add -f HMFileCommands.pHomeDirectory phomedirectory -h "Print the path of the home directory."')
    debugger.HandleCommand('command script add -f HMFileCommands.pBundlePath pbundlepath -h "Print the path of the main bundle."')
    debugger.HandleCommand('command script add -f HMFileCommands.deleteFile deletefile -h "Delete the specified file in the sandbox."')


def pHomeDirectory(debugger, command, exe_ctx, result, internal_dict):
    """
    Syntax:
        phomedirectory [--open]

    Options:
        --open/-o; open in Finder

    Examples:
        (lldb) phomedirectory
        (lldb) phomedirectory -o

    This command is implemented in HMFileCommands.py
    """

    command_args = shlex.split(command)
    parser = generate_option_parser("phomedirectory")
    try:
        # options: optparse.Values
        # args: list
        (options, args) = parser.parse_args(command_args)
    except:
        result.SetError(parser.usage)
        return

    homeDirectoryValue = HM.evaluateExpressionValue('(NSString *)NSHomeDirectory()')
    path = homeDirectoryValue.GetObjectDescription()
    HM.DPrint(path)
    if options.open:
        os.system('open ' + path)


def pBundlePath(debugger, command, exe_ctx, result, internal_dict):
    """
    Syntax:
        pbundlepath [--open]

    Options:
        --open/-o; open in Finder

    Examples:
        (lldb) pbundlepath
        (lldb) pbundlepath -o

    This command is implemented in HMFileCommands.py
    """

    command_args = shlex.split(command)
    parser = generate_option_parser("pbundlepath")
    try:
        # options: optparse.Values
        # args: list
        (options, args) = parser.parse_args(command_args)
    except:
        result.SetError(parser.usage)
        return

    bundlePathValue = HM.evaluateExpressionValue('(NSString*)[[NSBundle mainBundle] bundlePath]')
    path = bundlePathValue.GetObjectDescription()
    HM.DPrint(path)
    if options.open:
        # Cannot open the bundle, so we open the directory where the bundle is located.
        directoryValue = HM.evaluateExpressionValue(f'(NSString *)[(NSString *){bundlePathValue.GetValue()} stringByDeletingLastPathComponent]')
        os.system('open ' + directoryValue.GetObjectDescription())


def deleteFile(debugger, command, exe_ctx, result, internal_dict):
    """
    Syntax:
        deletefile [--option]
        deletefile [--file] <path>

    Options:
        --all/-a; Delete all file in the sandbox
        --documents/-d; Delete documents's file
        --library/-l; Delete library's file
        --tmp/-t; Delete tmp's file
        --caches/-c; Delete caches's file
        --preferences/-p; Delete preferences's file
        --file/-f; Delete the file or directory

    Examples:
        (lldb) deletefile -a
        (lldb) deletefile -c -p
        (lldb) deletefile -f path/to/fileOrDirectory

    This command is implemented in HMFileCommands.py
    """

    command_args = shlex.split(command)
    parser = generate_DeleteFile_optionParser()
    try:
        # options: optparse.Values
        # args: list
        (options, args) = parser.parse_args(command_args)
    except:
        result.SetError(parser.usage)
        return

    hasOption = False

    if options.all:
        # Reserve the directory under the Home directory
        hasOption = True
        subFileArrayValue = HM.evaluateExpressionValue("[[NSFileManager defaultManager] contentsOfDirectoryAtPath:(NSString *)NSHomeDirectory() error:nil]")
        for i in range(subFileArrayValue.GetNumChildren()):
            subFileValue = subFileArrayValue.GetChildAtIndex(i)
            HM.DPrint("=============" + subFileValue.GetObjectDescription() + "=============")
            subFilePathValue = HM.evaluateExpressionValue(f"[(NSString *)NSHomeDirectory() stringByAppendingPathComponent:(NSString *){subFileValue.GetValue()}]")
            deleteAllFileInDirectory(subFilePathValue.GetObjectDescription())

    if options.documents:
        hasOption = True
        documentsDirectoryValue = HM.evaluateExpressionValue("(NSString *)[NSSearchPathForDirectoriesInDomains(NSDocumentDirectory, NSUserDomainMask, YES) firstObject]")
        deleteAllFileInDirectory(documentsDirectoryValue.GetObjectDescription())

    if options.library:
        hasOption = True
        libraryDirectoryValue = HM.evaluateExpressionValue("(NSString *)[NSSearchPathForDirectoriesInDomains(NSLibraryDirectory, NSUserDomainMask, YES) firstObject]")
        deleteAllFileInDirectory(libraryDirectoryValue.GetObjectDescription())

    if options.tmp:
        hasOption = True
        tmpDirectoryValue = HM.evaluateExpressionValue("(NSString *)NSTemporaryDirectory()")
        deleteAllFileInDirectory(tmpDirectoryValue.GetObjectDescription())

    if options.caches:
        hasOption = True
        cachesDirectoryValue = HM.evaluateExpressionValue("(NSString *)[NSSearchPathForDirectoriesInDomains(NSCachesDirectory, NSUserDomainMask, YES) firstObject]")
        deleteAllFileInDirectory(cachesDirectoryValue.GetObjectDescription())

    if options.preferences:
        hasOption = True
        libraryDirectoryValue = HM.evaluateExpressionValue("(NSString *)[NSSearchPathForDirectoriesInDomains(NSLibraryDirectory, NSUserDomainMask, YES) firstObject]")
        preferencesDirectoryValue = HM.evaluateExpressionValue(f"(NSString *)[(NSString *){libraryDirectoryValue.GetValue()} stringByAppendingPathComponent:@\"Preferences\"]")
        deleteAllFileInDirectory(preferencesDirectoryValue.GetObjectDescription())

    if options.file:
        hasOption = True
        deleteFileOrDirectory(options.file)

    if not hasOption:
        HM.DPrint("Requires at least one target file/directory, Please enter \"help deletefile\" for help.")


def deleteAllFileInDirectory(directoryPath: str) -> None:
    command_script = f'''
        NSString *directoryPath = @"{directoryPath}";
        NSMutableString *result = [[NSMutableString alloc] init];
        NSFileManager *fileMgr = [NSFileManager defaultManager];
        if ([fileMgr fileExistsAtPath:directoryPath]) {{
            NSArray *subFileArray = [fileMgr contentsOfDirectoryAtPath:directoryPath error:nil];
            for (NSString *subFileName in subFileArray) {{
                NSString *subFilePath = [directoryPath stringByAppendingPathComponent:subFileName];
                if ([fileMgr removeItemAtPath:subFilePath error:nil]) {{
                    [result appendFormat:@"removed file: %@\\n", subFilePath];
                }} else {{
                    [result appendFormat:@"failed to remove file: %@\\n", subFilePath];
                }}
            }}
        }} else {{
            [result appendFormat:@"failed to remove non-existing file: %@\\n", directoryPath];
        }}

        if ([result length] == 0) {{
            [result appendString:@"There are no files in this directory.\\n"];
        }}
    
        result;
    '''

    result = HM.evaluateExpressionValue(command_script).GetObjectDescription()
    HM.DPrint(result)


def deleteFileOrDirectory(filePath: str) -> None:
    command_script = f'''
        NSString *filePath = @"{filePath}";
        NSMutableString *result = [[NSMutableString alloc] init];
        NSFileManager *fileMgr = [NSFileManager defaultManager];
        if ([fileMgr fileExistsAtPath:filePath]) {{
            if ([fileMgr removeItemAtPath:filePath error:nil]) {{
                [result appendFormat:@"removed file: %@\\n", filePath];
            }} else {{
                [result appendFormat:@"failed to remove file: %@\\n", filePath];
            }}
        }} else {{
            [result appendFormat:@"failed to remove non-existing file: %@\\n", filePath];
        }}

        result;
    '''
    result = HM.evaluateExpressionValue(command_script).GetObjectDescription()
    HM.DPrint(result)


def generate_option_parser(command: str) -> optparse.OptionParser:
    usage = f"usage: {command} [--open]"
    parser = optparse.OptionParser(usage=usage, prog=command)
    parser.add_option("-o", "--open",
                      action="store_true",
                      default=False,
                      dest="open",
                      help="Opens the path in Finder")

    return parser


def generate_DeleteFile_optionParser() -> optparse.OptionParser:
    usage = "usage: \ndeleteFile [--option] \ndeletefile [--file] <path>"
    parser = optparse.OptionParser(usage=usage, prog="deleteFile")

    parser.add_option("-a", "--all",
                      action="store_true",
                      default=False,
                      dest="all",
                      help="Delete all file in the sandbox")

    parser.add_option("-d", "--documents",
                      action="store_true",
                      default=False,
                      dest="documents",
                      help="Delete documents's file")

    parser.add_option("-l", "--library",
                      action="store_true",
                      default=False,
                      dest="library",
                      help="Delete library's file")

    parser.add_option("-t", "--tmp",
                      action="store_true",
                      default=False,
                      dest="tmp",
                      help="Delete tmp's file")

    parser.add_option("-c", "--caches",
                      action="store_true",
                      default=False,
                      dest="caches",
                      help="Delete caches's file")

    parser.add_option("-p", "--preferences",
                      action="store_true",
                      default=False,
                      dest="preferences",
                      help="Delete preferences's file")

    parser.add_option("-f", "--file",
                      action="store",
                      default=None,
                      dest="file",
                      help="Delete the file or directory")

    return parser

