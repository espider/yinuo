#!/usr/bin/python
# coding:utf-8


# for lldb in python
# here all function about thread
# Copyright (c) 2017, chengliang
# All rights reserved.


import lldb
import commandlist.ynbase as yn
from util.colorstyle import *
from util.exportcontent import *


def register_lldb_commands():
    return [
        YNThreadsClrStack(),
        YNThreadsPE()
    ]


class YNThreadsPE(yn.YNCommand):
    """ display managed exception on this thread. """

    def __init__(self):
        pass

    def name(self):
        # register function name
        return 'yn_thread_pe'

    def options(self):
        return [
            yn.YNArgument(
                short='-t',
                long='--thread',
                dest='thread',
                help='Display managed exception for one (thread index num) or all threads(-t all).')]

    def description(self):
        return 'Display managed exception for one (thread index num) or all threads.'

    def run(self, options, arguments):
        target = lldb.debugger.GetSelectedTarget()
        if target:
            if options.thread:
                if options.thread == 'all':

                    if target:
                        process = target.GetProcess()
                        if process:
                            threads_list = process.get_threads_access_object()
                            for i in range(len(threads_list)):
                                export_content(
                                    '    thread #%s' % str(
                                        threads_list[i].GetIndexID()))
                                YNThreadsPE.display_one_thread_pe(
                                    threads_list[i].GetIndexID(), arguments)
                else:
                    try:
                        index = int(options.thread)
                        if index > 0:
                            YNThreadsPE.display_one_thread_pe(index, arguments)
                        else:
                            export_content(
                                '   invalid thread #%s' %
                                use_style_level(
                                    important_level['high2'],
                                    str(index)))
                    except Exception as e:
                        export_content(
                            ' %s' %
                            use_style_level(
                                important_level['high3'],
                                'invalid arguments -t=all or -t=thread index'))
                        export_content('    error:%s' % e)
            else:
                YNThreadsPE.handle_command_pe(arguments)
                # end
        else:
            export_content('    no target in current debugger.')

    @staticmethod
    def display_one_thread_pe(index, args):
        """ change thread by thread index """
        if index > 0:
            target = lldb.debugger.GetSelectedTarget()
            if target:
                process = target.GetProcess()
                if process:
                    if process.SetSelectedThreadByIndexID(index):
                        YNThreadsPE.handle_command_pe(args)
                    else:
                        export_content(
                            '   current process has no the index #%s thread' %
                            use_style_level(
                                important_level['high2'], str(index)))

    @staticmethod
    def handle_command_pe(args):
        """ display current thread clr stack trace """
        (ci, result) = yn.run_log_command(
            "pe " + (" ".join(args) if len(args) > 0 else ''))
        success = result.Succeeded()
        if success:
            output = result.GetOutput()
            contents = output.strip()
            lines = contents.splitlines(False)
            for i in range(len(lines)):
                if i <= 1 or len(lines) <= 5:
                    # title & head for output 1,2 line or line less then 6
                    # there are no color
                    export_content('    %s' % lines[i])
                else:
                    line_words = lines[i].split()
                    if len(line_words) > 2:
                        export_content('    %s' % line_words[0], newline=False)
                        export_content(
                            '    %s' %
                            use_style_level(
                                important_level['high2'],
                                line_words[1]),
                            newline=False)
                        export_content('   %s' % use_style_level(
                            important_level['high3'], ' '.join(line_words[2:])))
                    else:
                        export_content('    %s' % lines[i])
            pass
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


class YNThreadsClrStack(yn.YNCommand):
    """ display threads clr stack trace. """

    def __init__(self):
        pass

    def name(self):
        # register function name
        return 'yn_thread_clrstack'

    def options(self):
        return [
            yn.YNArgument(
                short='-t',
                long='--thread',
                dest='thread',
                help='Display call stack trace for one (thread index num) or all threads(-t all).')]

    def description(self):
        return 'Display call stack trace for one (thread index num) or all threads.'

    def run(self, options, arguments):
        target = lldb.debugger.GetSelectedTarget()
        if target:
            if options.thread:
                if options.thread == 'all':

                    if target:
                        process = target.GetProcess()
                        if process:
                            threads_list = process.get_threads_access_object()
                            for i in range(len(threads_list)):
                                YNThreadsClrStack.display_one_thread_clrstack(
                                    threads_list[i].GetIndexID(), arguments)
                else:
                    try:
                        index = int(options.thread)
                        if index > 0:
                            YNThreadsClrStack.display_one_thread_clrstack(
                                index, arguments)
                        else:
                            export_content(
                                '   invalid thread #%s' %
                                use_style_level(
                                    important_level['high2'],
                                    str(index)))
                    except Exception as e:
                        export_content(
                            ' %s' %
                            use_style_level(
                                important_level['high3'],
                                'invalid arguments -t=all or -t=thread index'))
                        export_content('    error:%s' % e)
            else:
                YNThreadsClrStack.handle_command_clrstack(arguments)
                # end
        else:
            export_content('    no target in current debugger.')

    @staticmethod
    def display_one_thread_clrstack(index, args):
        """ change thread by thread index """
        if index > 0:
            target = lldb.debugger.GetSelectedTarget()
            if target:
                process = target.GetProcess()
                if process:
                    if process.SetSelectedThreadByIndexID(index):
                        YNThreadsClrStack.handle_command_clrstack(args)
                    else:
                        export_content(
                            '   current process has no the index #%s thread' %
                            use_style_level(
                                important_level['high2'], str(index)))

    @staticmethod
    def handle_command_clrstack(args):
        """ display current thread clr stack trace """
        (ci, result) = yn.run_log_command(
            "clrstack " + (" ".join(args) if len(args) > 0 else ''))
        success = result.Succeeded()
        if success:
            output = result.GetOutput()
            contents = output.strip()
            lines = contents.splitlines(False)
            for i in range(len(lines)):
                if i <= 1 or len(lines) <= 5:
                    # title & head for output 1,2 line or line less then 6
                    # there are no color
                    export_content('    %s' % lines[i])
                else:
                    line_words = lines[i].split()
                    if len(line_words) > 2:
                        export_content('    %s' % line_words[0], newline=False)
                        export_content(
                            ' %s' %
                            use_style_level(
                                important_level['high2'],
                                line_words[1]),
                            newline=False)
                        export_content(' %s' % use_style_level(
                            important_level['high3'], ' '.join(line_words[2:])))
                    else:
                        export_content(' %s' % lines[i])
            pass
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
