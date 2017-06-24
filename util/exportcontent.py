#!/usr/bin/python
# coding:utf-8

# for lldb in python
# output to file and teminal
# Copyright (c) 2017, chengliang
# All rights reserved.

import os


def export_content(content, path='', writefile=True, newline=True):
    # print to teminal aways
    if newline:
        print content
    else:
        print content,
    if writefile:
        if path == '':
            logfile = os.path.join(os.curdir, 'ynlldb.log')
        else:
            logfile = path
        write_type = 'w'
        if os.path.exists(logfile):
            write_type = 'a'
        else:
            pass
        f = open(logfile, write_type)
        if newline:
            f.write(content + '\n')
        else:
            f.write(content)
