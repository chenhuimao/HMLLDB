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
import sys
import os
import HMLLDBHelpers as HM


def __lldb_init_module(debugger, internal_dict):
    debugger.HandleCommand('command script add -f HMEnvironment.environment environment -h "Show diagnostic environment."')


def environment(debugger, command, exe_ctx, result, internal_dict):
    """
    Syntax:
        environment

    Examples:
        (lldb) environment

    This command is implemented in HMEnvironment.py
    """

    # Python version
    # LLDB version
    # Host program path
    # Target triple
    # Git commit hash
    # Optimized
    # Xcode version
    # Xcode build version
    # Model identifier
    # System version

    HM.DPrint('[Python version] ' + sys.version.replace('\n', '\n\t\t'))

    HM.DPrint('[LLDB version] ' + debugger.GetVersionString().replace('\n', '\n\t\t'))

    host_program_file_path = lldb.SBHostOS.GetProgramFileSpec().fullpath
    HM.DPrint('[Host program path] ' + host_program_file_path)

    HM.DPrint('[Target triple] ' + debugger.GetSelectedTarget().GetTriple())

    HM.DPrint('[Git commit hash] ' + get_git_commit_hash())

    HM.DPrint('[Optimized] ' + get_optimized_str())

    xcode_version_value = HM.evaluate_expression_value('(NSString *)([NSBundle mainBundle].infoDictionary[@"DTXcode"] ?: @"-")')
    HM.DPrint('[Xcode version] ' + xcode_version_value.GetObjectDescription())

    xcode_build_version_value = HM.evaluate_expression_value('(NSString *)([NSBundle mainBundle].infoDictionary[@"DTXcodeBuild"] ?: @"-")')
    HM.DPrint('[Xcode build version] ' + xcode_build_version_value.GetObjectDescription())

    HM.DPrint('[Model identifier] ' + get_model_identifier())

    system_version_value = HM.evaluate_expression_value('(NSString *)[[NSString alloc] initWithFormat:@"%@ %@", [[UIDevice currentDevice] systemName], [[UIDevice currentDevice] systemVersion]]')
    HM.DPrint('[iOS version] ' + system_version_value.GetObjectDescription())


def get_git_commit_hash() -> str:
    file_path = os.path.realpath(__file__)  # Absolute path
    dir_name = os.path.dirname(file_path)
    git_commit = os.popen(f"git -C {dir_name} log --pretty=format:'%H'").readline()
    return git_commit.replace('\n', '')


def get_optimized_str() -> str:
    optimized_false_count = 0
    optimized_true_count = 0
    symbol_context_list: lldb.SBSymbolContextList = lldb.debugger.GetSelectedTarget().FindFunctions("viewDidLoad")
    for i in range(symbol_context_list.GetSize()):
        if i == 800:
            break
        ctx = symbol_context_list.GetContextAtIndex(i)
        if ctx.GetFunction().IsValid():
            if ctx.GetFunction().GetIsOptimized():
                optimized_true_count += 1
            else:
                optimized_false_count += 1

    return f'False: {optimized_false_count}  True: {optimized_true_count}'


def get_model_identifier() -> str:
    command_script = '''
        struct hmlldb_utsname {
            char    sysname[256];
            char    nodename[256];
            char    release[256];
            char    version[256];
            char    machine[256];
        };
        struct hmlldb_utsname systemInfo;
        (int)uname(&systemInfo);
        NSString *modelIdentifier = [NSString stringWithCString:systemInfo.machine encoding:(NSStringEncoding)4];
        modelIdentifier;
    '''
    model_id_value = HM.evaluate_expression_value(command_script)
    return model_id_value.GetObjectDescription()
