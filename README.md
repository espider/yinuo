# Yinuo
`Yinuo` is a collection of LLDB commands for troubleshooting or debugging .Net Core applications on linux , objective is increase of debugging efficiency.

## Installation

```shell
git clone https://github.com/espider/yinuo
```

## Load & Used

* start ```lldb```
* attach Process in lldb like ``` (lldb) attach -p PID```
* load yinuo module where located at clone directory ```(lldb) command script import ~/yinuo/ynlldb.py```
* if sucessed u well see the welcome and base info ...

## Commands
|Command          |Description     |Options        |
|-----------------|----------------|---------------|
|**yn_heap_dump**| Display managed heap info.| **--stat/-s** &lt;stat&gt;; type: bool and default: true; Display the managed heap statistics info.|
|**yn_object_dump**|Display managed objects by MethodTable address or Type name.|**--address/-a** &lt;address&gt;; type: str; Display one managed objects by address.<br/><br/>**--methodtable/-m** &lt;mt&gt;; type: str; Display managed objects by MethodTable address,either this or type name.<br/><br/>**--type/-t** &lt;type_name&gt;; type: str; Display managed objects by Type name,either this or MT address.<br/><br/>**--dumpobj/-d** &lt;dumpobj&gt;; type: bool and default: true; Dump every one object by type ,default=True.<br/><br/>**--offset/-o** &lt;offset&gt;; type: str; Display managed objects by offset (hex like 0xF0) on same type objects.<br/><br/>**--gen/-g** &lt;gen&gt;; type: bool and default: true; Display managed objects in which heap gen 0,1,2 or LOH.|
|**yn_thread_clrstack**|Display call stack trace for one (thread index num) or all threads.|**--thread/-t** &lt;thread&gt;; type: str; Display call stack trace for one (thread index num) or all threads(-t all).|
|**yn_thread_pe**|Display managed exception for one (thread index num) or all threads.|**--thread/-t** &lt;thread&gt;; type: str; Display managed exception for one (thread index num) or all threads(-t all).|
|**yn_transfer**|Transfer lldb command with arguments and log.|e.g. arguments: dumpheap -stat|

## Custom Commands


* You can add custom commands in python and located at yinuo/commandlist directory, it's auto load by regist function when script import yinuo/ynlldb.py in the lldb.

* custom example:

```python
#!/usr/bin/python
# coding:utf-8

import lldb
import commandlist.ynbase as yn
from util.colorstyle import *
from util.exportcontent import *


def register_lldb_commands():
    return [
        YNTransfer()
    ]


class YNTransfer(yn.YNCommand):
    """ transfer lldb command and exe it for log """

    def __init__(self):
        pass

    def name(self):
        # register function name in lldb
        return 'yn_transfer'

    def options(self):
        return [
        ]

    def description(self):
        return 'Transfer lldb command for log,e.g. arguments: dumpheap -stat'

    def run(self, options, arguments):
        target = lldb.debugger.GetSelectedTarget()
        if target:
            if arguments:
                YNTransfer.handle_command(arguments)
            else:
                export_content('    no arguments in yn_transfer.')
        else:
            export_content('    no target in current debugger.')

    @staticmethod
    def handle_command(args):
        (ci, result) = yn.run_log_command(
            " " + (" ".join(args) if len(args) > 0 else ''))
        success = result.Succeeded()
        if success:
            output = result.GetOutput()
            contents = output.strip()
            lines = contents.splitlines(False)
            for i in range(len(lines)):
                export_content('    %s' % lines[i])
        else:
            export_content(
                '    error="%s"' %
                use_style_level(
                    important_level['high2'],
                    result.GetError()))
        export_content(
            '    %s   ' %
            use_style_level(
                important_level['low2'],
                '-------------'))

```

## Limitations 

* only lldb version 3.6.0 I was tested,other versions could not be determined. 

* debugging .net Core application dependent on SOS plugin `libsosplugin.so` and it's must be identical to the same version of the application runtime version.

## Refrence
*  https://github.com/dotnet/coreclr/blob/master/Documentation/building/debugging-instructions.md

## License
`Yinuo` is BSD-licensed. 

