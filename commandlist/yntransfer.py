#!/usr/bin/python
# coding:utf-8


# for lldb in python
# transfer lldb command for log
# Copyright (c) 2017, chengliang
# All rights reserved.


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
        # register function name
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
