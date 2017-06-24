#!/usr/bin/python
# coding:utf-8


# for lldb in python
# color output information by priority
# Copyright (c) 2017, chengliang
# All rights reserved.


color_style = {
    'fore': {
        'black': 30,
        'red': 31,
        'green': 32,
        'yellow': 33,
        'blue': 34,
        'purple': 35,
        'cyan': 36,
        'white': 37},
    'back': {
        'black': 40,
        'red': 41,
        'green': 42,
        'yellow': 43,
        'blue': 44,
        'purple': 45,
        'cyan': 46,
        'white': 47},
    'mode': {
        'normal': 0,
        'bold': 1,
        'underline': 4,
        'blink': 5,
        'invert': 7,
        'hide': 8},
    'default': {
        'end': 0}}

important_level = {
    'high1': {'mode': 'bold', 'fore': 'red'},
    'high2': {'mode': 'bold', 'fore': 'yellow'},
    'high3': {'mode': 'bold', 'fore': 'green'},
    'medium1': {'mode': 'normal', 'fore': 'white'},
    'medium2': {'mode': 'normal', 'fore': 'blue'},
    'low1': {'mode': 'normal', 'fore': 'purple'},
    'low2': {'mode': 'normal', 'fore': 'cyan'},
    'low3': {'mode': 'normal', 'fore': 'black'},
    'block_red': {'mode': 'normal', 'back': 'red'},
    'block_yellow': {'mode': 'normal', 'back': 'yellow'},
    'block_green': {'mode': 'normal', 'back': 'green'},
    'block_blue': {'mode': 'normal', 'back': 'blue'},
    'block_purple': {'mode': 'normal', 'back': 'purple'},
    'block_cyan': {'mode': 'normal', 'back': 'cyan'}
}


def use_style_level(diclevel, string):
    mode = '%s' % diclevel['mode'] if 'mode' in diclevel else ''
    fore = '%s' % diclevel['fore'] if 'fore' in diclevel else ''
    back = '%s' % diclevel['back'] if 'back' in diclevel else ''
    return use_style(string, mode, fore, back)


def use_style(string, mode='', fore='', back=''):
    mode = '%d' % color_style['mode'][mode] if mode in color_style['mode'] else ''
    fore = '%d' % color_style['fore'][fore] if fore in color_style['fore'] else ''
    back = '%d' % color_style['back'][back] if back in color_style['back'] else ''
    style = ';'.join([s for s in [mode, fore, back] if s])
    style = '\033[%sm' % style if style else ''
    end = '\033[%sm' % color_style['default']['end'] if style else ''
    return '%s%s%s' % (style, string, end)
