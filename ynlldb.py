#!/usr/bin/python
# coding:utf-8


# help for debug .net core with lldb
# this work with lldb.like:command script import ~/ynlldb.py
# ref: https://lldb.llvm.org/python-reference.html
# ref: https://lldb.llvm.org/python_reference/index.html
# Copyright (c) 2017, chengliang
# All rights reserved.


import os
import imp
import lldb
import shlex
import datetime
import commands
import argparse

from util.colorstyle import *
from util.exportcontent import *


def __lldb_init_module(debugger, internal_dict):
    """ start with lldb import py """
    export_content(
        '    %s' %
        use_style_level(
            important_level['high3'],
            'welcome to use ynlldb module.'))
    show_base_info()
    register_lldb_commands()


def show_base_info():
    """ show the target base info like process,threads,execute path etc. """
    export_content('    ')
    export_content(
        '    time: %s' %
        use_style_level(
            important_level['high3'],
            datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    export_content(
        '    system: %s' %
        use_style_level(
            important_level['high3'],
            commands.getoutput('cat /etc/redhat-release')))
    export_content(
        '    lldb.debugger: %s' %
        use_style_level(
            important_level['high3'],
            lldb.debugger))
    target = lldb.debugger.GetSelectedTarget()
    if target:
        export_content(
            '    target: %s' %
            use_style_level(
                important_level['high3'],
                target))
        ptr_size = target.GetAddressByteSize()
        if ptr_size == 8:
            export_content(
                '    target.GetAddressByteSize: %s' %
                use_style_level(
                    important_level['high3'],
                    '64-bit'))
        elif ptr_size == 4:
            export_content(
                '    target.GetAddressByteSize: %s' %
                use_style_level(
                    important_level['high3'],
                    '32-bit'))
        else:
            export_content(
                '    target.GetAddressByteSize: %s' %
                use_style_level(
                    important_level['high3'], '???'))

        export_content(
            '    target.executable: %s' %
            use_style_level(
                important_level['high3'],
                target.executable))
        export_content(
            '    target.executable.basename: %s' %
            use_style_level(
                important_level['high3'],
                target.executable.basename))
        export_content(
            '    target.executable.fullpath: %s' %
            use_style_level(
                important_level['high3'],
                target.executable.fullpath))
        for module in target.modules:
            if module.file.basename == 'libcoreclr.so':
                netcorelib_dir = os.path.dirname(module.file.fullpath)
                export_content(
                    '    .net core lib dir: %s' %
                    use_style_level(
                        important_level['high3'],
                        netcorelib_dir))
                libsosplugin_file = os.path.join(
                    netcorelib_dir, 'libsosplugin.so')
                if os.path.exists(libsosplugin_file):
                    lldb.debugger.HandleCommand(
                        'plugin load %s' %
                        libsosplugin_file)
                    export_content(
                        '    libsosplugin file: %s load over' %
                        use_style_level(
                            important_level['high3'],
                            libsosplugin_file))
                else:
                    export_content(
                        '    libsospluginfile no file in %s' %
                        use_style_level(
                            important_level['high3'],
                            libsosplugin_file))

        process = target.GetProcess()
        if process:
            pid = process.id
            export_content(
                '    pid: %s' %
                use_style_level(
                    important_level['high3'],
                    pid))
            export_content(
                '    process: %s' %
                use_style_level(
                    important_level['high3'],
                    process))

    else:
        export_content(
            '    %s' %
            use_style_level(
                important_level['high3'],
                'no target in current debugger, attach -p PID and reload ynlldb.py use command script import'))


def register_lldb_commands():
    """ register all commands to lldb """
    target = lldb.debugger.GetSelectedTarget()
    if target:
        current_file = os.path.realpath(__file__)
        current_dir = os.path.dirname(current_file)
        commands_directory = os.path.join(current_dir, 'commandlist')
        export_content(
            '    register commands directory: %s' %
            use_style_level(
                important_level['high3'],
                commands_directory))
        for file in os.listdir(commands_directory):
            file_name, file_extension = os.path.splitext(file)
            if file_extension == '.py':
                module = imp.load_source(
                    file_name, os.path.join(
                        commands_directory, file))
                module._loadedFunctions = {}
                if hasattr(module, 'register_lldb_commands'):
                    for command in module.register_lldb_commands():
                        # os.path.join(commands_directory, file_name + file_extension)
                        func = make_run_command(command)
                        name = command.name()
                        help_text = command.description().splitlines()[0]
                        key = file_name + '_' + name
                        module._loadedFunctions[key] = func
                        function_name = '__' + key
                        # export_content('    register command name : %s' %
                        # use_style_level(important_level['high3'], key))
                        # alias function name
                        lldb.debugger.HandleCommand(
                            'script ' +
                            function_name +
                            ' = sys.modules[\'' +
                            module.__name__ +
                            '\']._loadedFunctions[\'' +
                            key +
                            '\']')
                        # register name to lldb command
                        lldb.debugger.HandleCommand(
                            'command script add --help "{help}" --function {function} {name}'.format(
                                help=help_text.replace(
                                    '"', '\\"'), function=function_name, name=name))
                else:
                    pass
            else:
                export_content('no .py file')


def make_run_command(command):
    def run_command(debugger, input, result, dict):
        split_input = shlex.split(input)
        parser = argparse.ArgumentParser('')
        options = command.options()

        if len(options) > 0:
            last_group = 0
            group = None
            for i in range(len(options)):
                if options[i].mutually > 0:
                    # mutually group
                    if last_group != options[i].mutually:
                        # new group
                        group = parser.add_mutually_exclusive_group()
                        group.add_argument(
                            options[i].short,
                            options[i].long,
                            dest=options[i].dest,
                            nargs=options[i].nargs,
                            type=options[i].type,
                            help=options[i].help,
                            default=options[i].default,
                            required=options[i].required)
                        last_group = options[i].mutually
                    else:
                        # same group
                        group.add_argument(
                            options[i].short,
                            options[i].long,
                            dest=options[i].dest,
                            nargs=options[i].nargs,
                            type=options[i].type,
                            help=options[i].help,
                            default=options[i].default,
                            required=options[i].required)
                else:
                    # no mutually group
                    parser.add_argument(
                        options[i].short,
                        options[i].long,
                        dest=options[i].dest,
                        nargs=options[i].nargs,
                        type=options[i].type,
                        help=options[i].help,
                        default=options[i].default,
                        required=options[i].required)
                    last_group = 0

        args = parser.parse_known_args(split_input)
        export_content('    %s   ' % use_style_level(important_level['low2'], '-------------'))
        command.run(args[0], args[1])

    run_command.__doc__ = help_for_command(command)
    return run_command


def help_for_command(command):
    """ generate help doc for command """
    help = command.description()
    if command.options():
        help += '\n\nOptions:'
        for option in command.options():
            if option.long and option.short:
                option_flag = option.long + '/' + option.short
            elif option.longName:
                option_flag = option.long
            else:
                option_flag = option.short

            help += '\n  ' + option_flag + ' '
            if option.type.__name__ == 'str_to_bool':
                help += '<' + str(option.dest) + '>; Type: bool'
            else:
                help += '<' + str(option.dest) + '>; Type: ' + option.type.__name__
            help += '; ' + option.help

    return help
