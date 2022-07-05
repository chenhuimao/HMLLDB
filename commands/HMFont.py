# The MIT License (MIT)
#
# Copyright (c) 2021 Huimao Chen
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
import HMLLDBHelpers as HM


def __lldb_init_module(debugger, internal_dict):
    debugger.HandleCommand('command script add -f HMFont.printFont pfont -h "Print all font names supported by the device."')


def printFont(debugger, command, exe_ctx, result, internal_dict):
    """
    Syntax:
        pfont

    Examples:
        (lldb) pfont

    This command is implemented in HMFont.py
    """

    command_script = '''
        NSMutableString *result = [[NSMutableString alloc] init];
        unsigned int fontNamesCount = 0;
    
        NSArray *familyNames = [UIFont familyNames];
        for (NSString *familyName in familyNames) {
            [result appendFormat:@"familyNames: %@\\n", familyName];
            
            NSArray *fontNames = [UIFont fontNamesForFamilyName:familyName];
            for (NSString *fontName in fontNames) {
                [result appendFormat:@"\\tfontName: %@\\n", fontName];
                fontNamesCount += 1;
            }
        }
        [result insertString:[[NSString alloc] initWithFormat:@"Family names count: %ld, font names count: %u\\n", [familyNames count], fontNamesCount] atIndex:0];
        (NSMutableString *)result;
    '''

    fontNames = HM.evaluateExpressionValue(command_script).GetObjectDescription()
    HM.DPrint(fontNames)

