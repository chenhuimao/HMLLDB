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
    # Target triple
    # Git commit hash
    # Optimized
    # Xcode version
    # Xcode build version
    # Model identifier
    # System version

    HM.DPrint('[Python version] ' + sys.version.replace('\n', '\n\t\t'))

    HM.DPrint('[LLDB version] ' + debugger.GetVersionString().replace('\n', '\n\t\t'))

    HM.DPrint('[Target triple] ' + debugger.GetSelectedTarget().GetTriple())

    HM.DPrint('[Git commit hash] ' + getGitCommitHash())

    HM.DPrint('[Optimized] ' + getOptimizedStr())

    XcodeVersionValue = HM.evaluate_expression_value('(NSString *)([NSBundle mainBundle].infoDictionary[@"DTXcode"] ?: @"-")')
    HM.DPrint('[Xcode version] ' + XcodeVersionValue.GetObjectDescription())

    XcodeBuildVersionValue = HM.evaluate_expression_value('(NSString *)([NSBundle mainBundle].infoDictionary[@"DTXcodeBuild"] ?: @"-")')
    HM.DPrint('[Xcode build version] ' + XcodeBuildVersionValue.GetObjectDescription())

    HM.DPrint('[Model identifier] ' + getModelIdentifier())

    SystemVersionValue = HM.evaluate_expression_value('(NSString *)[[NSString alloc] initWithFormat:@"%@ %@", [[UIDevice currentDevice] systemName], [[UIDevice currentDevice] systemVersion]]')
    HM.DPrint('[System version] ' + SystemVersionValue.GetObjectDescription())


def getGitCommitHash() -> str:
    file_path = os.path.realpath(__file__)  # Absolute path
    dir_name = os.path.dirname(file_path)
    gitCommit = os.popen(f"git -C {dir_name} log --pretty=format:'%H'").readline()
    return gitCommit.replace('\n', '')


def getOptimizedStr() -> str:
    optimizedFalseCount = 0
    optimizedTrueCount = 0
    symbolContextList = lldb.debugger.GetSelectedTarget().FindFunctions("viewDidLoad")
    for i in range(symbolContextList.GetSize()):
        if i == 800:
            break
        ctx = symbolContextList.GetContextAtIndex(i)
        if ctx.GetFunction().IsValid():
            if ctx.GetFunction().GetIsOptimized():
                optimizedTrueCount += 1
            else:
                optimizedFalseCount += 1

    return f'False: {optimizedFalseCount}  True: {optimizedTrueCount}'


def getModelIdentifier() -> str:
    command_script = '''
        struct utsname systemInfo;
        (int)uname(&systemInfo);
        NSString *modelIdentifier = [NSString stringWithCString:systemInfo.machine encoding:(NSStringEncoding)4];
        modelIdentifier;
    '''
    modelIDValue = HM.evaluate_expression_value(command_script)
    return modelIDValue.GetObjectDescription()
