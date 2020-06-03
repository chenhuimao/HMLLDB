# Some commands are based on https://github.com/DerekSelander/LLDB/blob/master/lldb_commands/cmds.txt

command alias -h "Reload ~/.lldbinit" -- reload_lldbinit command source ~/.lldbinit

command alias -h "Alias for 'expression -l objc -O --'" -- cpo expression -l objc -O --

command alias -h "Alias for 'expression -l objc --'" -- cp expression -l objc --

command alias -h "Alias for 'expression -l swift -O --'" -- spo expression -l swift -O --

command alias -h "Alias for 'expression -l swift --'" -- sp expression -l swift --

command alias -h "Execute [CATransaction flush]" -- caflush expression -l objc -- (void)[CATransaction flush]

command regex ivars -h "Execute [%1 _ivarDescription]" -s "ivars <Instance>, 'ivars [UIView new]'" -- 's/(.+)/expression -l objc -O -- [%1 _ivarDescription]/'

command regex properties -h "Execute [%1 _propertyDescription]" -s "properties <Instance/Class>, 'properties UIView'" -- 's/(.+)/expression -l objc -O -- [%1 _propertyDescription]/'

command regex methods -h "Execute [%1 _methodDescription]" -s "methods <Instance/Class>, 'methods UIView'" -- 's/(.+)/expression -l objc -O -- [%1 _methodDescription]/'

command regex smethods -h "Execute [%1 _shortMethodDescription]" -s "smethods <Instance/Class>, 'smethods UIView'" -- 's/(.+)/expression -l objc -O -- [%1 _shortMethodDescription]/'
