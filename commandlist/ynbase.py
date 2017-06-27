#!/usr/bin/python
# coding:utf-8

# for lldb in python
# base class for the command
# Copyright (c) 2017, chengliang
# All rights reserved.

import re
import lldb
from util.colorstyle import *
from util.exportcontent import *


class YNCommand:
    """ command """

    def name(self):
        return None

    def options(self):
        return []

    def args(self):
        return []

    def description(self):
        return ''

    def run(self, option, arguments):
        pass


class YNArgument:
    """ command argument  """

    def __init__(
            self,
            short='',
            long='',
            dest='',
            nargs='?',
            type=str,
            help='',
            default='',
            required=False,
            mutually=0):
        self.short = short
        self.long = long
        self.dest = dest
        self.nargs = nargs
        self.type = type
        self.help = help
        self.default = default
        self.required = required
        self.mutually = mutually


class YNManageHeap:
    """ managed heap """
    __heapNum__ = 0
    __heapName__ = ""
    __heapRange__ = []

    def __init__(self, num, name):
        self.__heapNum__ = num
        self.__heapName__ = name
        self.__heapRange__ = []

    def add_range(self, min_add, max_add):
        """ add heap range """
        self.__heapRange__.append((min_add, max_add))

    def check_in_heap(self, address):
        """ check managed object address is in current heap range """
        if len(self.__heapRange__) > 0:
            for i in range(0, len(self.__heapRange__)):
                if self.__heapRange__[
                        i][0] < address < self.__heapRange__[i][1]:
                    return True
        else:
            pass
        return False


def str_to_bool(v):
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


def run_log_command(command, need_log=False):
    if need_log:
        export_content(
            '    command: %s' %
            use_style_level(
                important_level['low1'],
                command))
    ci = lldb.debugger.GetCommandInterpreter()
    result = lldb.SBCommandReturnObject()
    ci.HandleCommand(command, result)
    return ci, result


def get_value_by_re(regular, content, *index):
    """ get values by regular expression, and return which index from match group """
    dict = {}
    if content and re and len(index) > 0:
        match_obj = re.match(regular, content, re.I)
        if match_obj:
            for i in index:
                if match_obj.group(i):
                    dict[i] = match_obj.group(i)
        else:
            pass
    return dict


def get_max_byte_string(bytes):
    """ return human readable by bytes """
    if bytes >= 1024:
        k_byte = bytes * 1.0 / 1024
        if k_byte >= 1024:
            m_byte = k_byte / 1024
            if m_byte >= 1024:
                g_byte = m_byte / 1024
                return '%s GB' % round(g_byte, 2)
            return '%s MB' % round(m_byte, 2)
        return '%s KB' % round(k_byte, 2)
    else:
        return '%d bytes' % bytes
    pass
