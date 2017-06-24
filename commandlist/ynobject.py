#!/usr/bin/python
# coding:utf-8


# for lldb in python
# here all function about managed object and managed heap
# Copyright (c) 2017, chengliang
# All rights reserved.

import lldb
import commandlist.ynbase as yn
from util.colorstyle import *
from util.exportcontent import *


def register_lldb_commands():
    return [
        YNObjectDump(),
        YNHeap()
    ]


class YNHeap(yn.YNCommand):
    """ display managed heap info """

    def __init__(self):
        self.reset_heap()
        pass

    __heap__ = {}
    __heap_hit__ = {}
    __block_count__ = 100

    def reset_heap(self):
        """ reset heap info and hit info """
        if len(self.__heap__) > 0:
            self.__heap__.clear()
        self.__heap__ = YNHeap.get_managed_heap()
        if len(self.__heap_hit__) > 0:
            self.__heap_hit__.clear()

    def output_heap_hit(self):
        """ output heap hit count """
        if len(self.__heap_hit__) > 0:
            for key, value in self.__heap_hit__.iteritems():
                export_content(
                    '    %s count:%s   ' %
                    (key, value), newline=False)
        export_content('    over.')

    def output_obj_heap(self, address):
        """ get managed object in which heap gen0,1,2 or LOH """
        long_value = int(address, 16)
        if len(self.__heap__) > 0 and long_value > 0:
            for key, value in self.__heap__.iteritems():
                if value.check_in_heap(long_value):
                    if key in self.__heap_hit__:
                        self.__heap_hit__[key] += 1
                    else:
                        self.__heap_hit__[key] = 1
                    export_content(
                        '    object heap: %s' %
                        use_style_level(
                            important_level['high1'], key))
                    return
        export_content(
            '    object heap: %s' %
            use_style_level(
                important_level['high1'],
                ' what address??? '))

    def name(self):
        # register function name
        return 'yn_heap_dump'

    def options(self):
        return [
            yn.YNArgument(
                short='-s',
                long='--stat',
                dest='stat',
                type=yn.str_to_bool,
                default=True,
                help='Display managed heap statistics info .')]

    def description(self):
        return 'Display managed heap info.'

    def run(self, options, arguments):
        target = lldb.debugger.GetSelectedTarget()
        if target:
            self.reset_heap()
            if options.stat:
                self.handle_command_heap_stat()

    def handle_command_heap_stat(self):
        """ display heap statistics info. """
        if len(self.__heap__) > 0:
            # heap_block = [[0] * 4] * len(self.__heap__)
            heap_block = [[0 for _ in range(4)]
                          for _ in range(len(self.__heap__))]
            for key, value in self.__heap__.iteritems():
                loop = 0
                if len(value.__heapRange__) > 0:
                    for min, max in value.__heapRange__:
                        if value.__heapName__ == "Gen 2":
                            heap_block[loop][0] = max - min
                        elif value.__heapName__ == "Gen 1":
                            heap_block[loop][1] = max - min
                        elif value.__heapName__ == "Gen 0":
                            heap_block[loop][2] = max - min
                        elif value.__heapName__ == "LOH":
                            heap_block[loop][3] = max - min
                        else:
                            pass
                        loop += 1
                else:
                    pass

            if len(heap_block) > 0:
                for i in range(len(heap_block)):
                    if len(heap_block[i]) == 4:
                        sum_byte = sum(heap_block[i])
                        if sum_byte > 0:
                            gen2_per = heap_block[i][0] * 1.0 / sum_byte
                            gen1_per = heap_block[i][1] * 1.0 / sum_byte
                            gen0_per = heap_block[i][2] * 1.0 / sum_byte
                            # loh_per = heap_block[i][3] * 1.0 / sum_byte
                            total = yn.get_max_byte_string(sum_byte)
                            block_gen2 = round(
                                gen2_per * self.__block_count__)
                            block_gen1 = round(
                                gen1_per * self.__block_count__)
                            block_gen0 = round(
                                gen0_per * self.__block_count__)
                            block_loh = self.__block_count__ \
                                        - gen2_per * self.__block_count__ \
                                        - gen1_per * self.__block_count__ \
                                        - gen0_per * self.__block_count__

                            export_content(
                                '    %sGen2:%f%%  %sGen1:%f%%  %sGen0:%f%%  %sLOH:%f%%      Total:%s' %
                                (use_style_level(
                                    important_level['block_red'],
                                    ' '),
                                 gen2_per *
                                 self.__block_count__,
                                 use_style_level(
                                     important_level['block_yellow'],
                                     ' '),
                                 gen1_per *
                                 self.__block_count__,
                                 use_style_level(
                                     important_level['block_green'],
                                     ' '),
                                 gen0_per *
                                 self.__block_count__,
                                 use_style_level(
                                     important_level['block_purple'],
                                     ' '),
                                 block_loh,
                                 total))

                            export_content(
                                '    %s%s%s%s' %
                                (use_style_level(
                                    important_level['block_red'],
                                    ' ' *
                                    int(block_gen2)),
                                 use_style_level(
                                     important_level['block_yellow'],
                                     ' ' *
                                     int(block_gen1)),
                                 use_style_level(
                                     important_level['block_green'],
                                     ' ' *
                                     int(block_gen0)),
                                 use_style_level(
                                     important_level['block_purple'],
                                     ' ' *
                                     (100 - int(block_gen2) - int(block_gen1) - int(block_gen0)))))

    @staticmethod
    def get_managed_heap():
        """ current managed heap range. """
        dic_heap = {}
        gen0 = yn.YNManageHeap(0, "Gen 0")
        gen1 = yn.YNManageHeap(0, "Gen 1")
        gen2 = yn.YNManageHeap(0, "Gen 2")
        loh = yn.YNManageHeap(0, "LOH")

        (ci_gen, result_gen) = yn.run_log_command("eeheap -gc")
        success_gen = result_gen.Succeeded()
        if success_gen:
            output_gen = result_gen.GetOutput()
            contents_gen = output_gen.strip()
            lines_gen = contents_gen.splitlines(False)

            start_loh = False

            gen2_start = 0  # segment start here, low address for heap
            gen1_start = 0
            gen0_start = 0
            gen0_end = 0  # segment end here, high address for heap
            loh_start = 0
            loh_end = 0

            for i in range(len(lines_gen)):
                if lines_gen[i].find('-') >= 0:
                    """ end heap """
                    if gen0_end > gen0_start > gen1_start > gen2_start > 0 \
                            and loh_end > loh_start > 0:
                        gen2.add_range(gen2_start, gen1_start)
                        gen1.add_range(gen1_start, gen0_start)
                        gen0.add_range(gen0_start, gen0_end)
                        loh.add_range(loh_start, loh_end)

                    start_loh = False
                    continue

                if lines_gen[i].find('Large object heap starts at') >= 0:
                    """ start large object heap """
                    start_loh = True
                    continue

                dic_gen = yn.get_value_by_re(
                    'generation\s+(0|1|2)\s+starts\s+at\s+([a-zA-Z0-9]+)', lines_gen[i], 1, 2)
                if dic_gen and len(dic_gen) > 1:
                    """ small obj heap """
                    if dic_gen[1] == '0':
                        gen0_start = int(dic_gen[2], 16)
                    elif dic_gen[1] == '1':
                        gen1_start = int(dic_gen[2], 16)
                    elif dic_gen[1] == '2':
                        gen2_start = int(dic_gen[2], 16)
                    else:
                        pass
                    continue

                dic_segment = yn.get_value_by_re(
                    '([a-zA-Z0-9]+)\s+([a-zA-Z0-9]+)\s+([a-zA-Z0-9]+)\s+([a-zA-Z0-9]+)\([0-9]+\)',
                    lines_gen[i], 1, 2, 3)
                if dic_segment and len(dic_segment) > 2:
                    """ segment for small and large heap """
                    if not start_loh:
                        if int(dic_segment[2], 16) == gen2_start:
                            gen0_end = int(dic_segment[3], 16)
                    else:
                        loh_start = int(dic_segment[2], 16)
                        loh_end = int(dic_segment[3], 16)
                    continue

        dic_heap["Gen 0"] = gen0
        dic_heap["Gen 1"] = gen1
        dic_heap["Gen 2"] = gen2
        dic_heap["LOH"] = loh
        return dic_heap


class YNObjectDump(yn.YNCommand):
    """ display managed objects by MethodTable address or Type name. """

    def __init__(self):
        pass

    __heap_info__ = None  # YNHeap()

    def name(self):
        # register function name
        return 'yn_object_dump'

    def options(self):
        return [
            yn.YNArgument(
                short='-a',
                long='--address',
                dest='address',
                help='Display one managed objects by address.'),
            yn.YNArgument(
                short='-m',
                long='--methodtable',
                dest='mt',
                help='Display managed objects by MethodTable address.',
                mutually=1),
            yn.YNArgument(
                short='-t',
                long='--type',
                dest='type_name',
                help='Display managed objects by Type name.',
                mutually=1),
            yn.YNArgument(
                short='-d',
                long='--dumpobj',
                dest='dumpobj',
                type=yn.str_to_bool,
                default=True,
                help='Dump every one object by type ,default=True.'),
            yn.YNArgument(
                short='-o',
                long='--offset',
                dest='offset',
                help='Display managed objects by offset (hex like 0xF0) on same type objects.'),
            yn.YNArgument(
                short='-g',
                long='--gen',
                dest='gen',
                type=yn.str_to_bool,
                default=True,
                help='Display managed objects in which heap gen 0,1,2 or LOH.')]

    def description(self):
        return 'Display managed objects by MethodTable address or Type name.'

    def run(self, options, arguments):
        target = lldb.debugger.GetSelectedTarget()
        if target:
            """ reset current heap info """
            # self.reset_heap()
            self.__heap_info__ = YNHeap()
            if options.address:
                self.handle_command_obj(options)
            elif options.mt or options.type_name:
                self.handle_command_type(options, arguments)
            else:
                export_content(
                    '    no object address or methodtable address or type name.')
                # end
        else:
            export_content('    no target in current debugger.')

    def handle_command_obj(self, options):
        """ dump one managed object """
        if options.gen:
            self.__heap_info__.output_obj_heap(options.address)
            pass
        else:
            pass
        YNObjectDump.display_object_address(options.address)
        pass

    def handle_command_type(self, options, args):
        """ dump managed object by type MT or type name."""
        # if show gen,first get managed heap now.

        # all_args = ''
        if options.dumpobj:
            if options.mt:
                all_args = "-mt " + options.mt + " -short " + \
                           (" ".join(args) if len(args) > 0 else '')
            elif options.type_name:
                all_args = "-type " + options.type_name + " -short " + \
                           (" ".join(args) if len(args) > 0 else '')
            else:
                export_content('    no methodtable address or type name.')
                return
        else:
            if options.mt:
                all_args = "-mt " + options.mt + " " + \
                           (" ".join(args) if len(args) > 0 else '')
            elif options.type_name:
                all_args = "-type " + options.type_name + " " + \
                           (" ".join(args) if len(args) > 0 else '')
            else:
                export_content('    no methodtable address or type name.')
                return

        (ci, result) = yn.run_log_command("dumpheap %s" % all_args)
        success = result.Succeeded()
        if success:
            output = result.GetOutput()
            contents = output.strip()
            lines = contents.splitlines(False)
            if options.dumpobj:
                export_content('    len(lines): %d' % len(lines))
            for i in range(len(lines)):
                if options.dumpobj:
                    """ dump every manage object """
                    export_content(
                        '    object address: %s' %
                        use_style_level(
                            important_level['high2'],
                            lines[i]))
                    if options.gen:
                        self.__heap_info__.output_obj_heap(lines[i])
                        pass

                    new_obj_address = lines[i]
                    if options.offset:
                        """ dump deep object with offset """
                        new_obj_address = int(
                            lines[i], 16) + int(options.offset, 16)

                        error = lldb.SBError()
                        target = lldb.debugger.GetSelectedTarget()
                        if target:
                            process = target.GetProcess()
                            if process:
                                ptr = process.ReadPointerFromMemory(
                                    new_obj_address, error)
                                if error.Success() and ptr > 0:
                                    new_obj_address = hex(ptr)
                                    export_content(
                                        '    deep offset object address: %s' %
                                        use_style_level(
                                            important_level['high2'],
                                            new_obj_address))
                                else:
                                    export_content(
                                        '    error="%s" and ptr="%s"' %
                                        (use_style_level(
                                            important_level['high2'], error), ptr))
                                    continue
                    else:
                        pass
                    YNObjectDump.display_object_address(new_obj_address)
                else:
                    """ display dumpheap output """
                    export_content('    %s' % lines[i])
            pass
            if options.dumpobj:
                export_content('    object count: %d   ' % len(lines))
                self.__heap_info__.output_heap_hit()

        else:
            export_content(
                '    error="%s"' %
                use_style_level(
                    important_level['high2'],
                    result.GetError()))

    @staticmethod
    def display_object_address(address):
        (ci, result_one) = yn.run_log_command("dumpobj " + address)
        success_one = result_one.Succeeded()
        if success_one:
            output_one = result_one.GetOutput()
            contents_one = output_one.strip()
            lines_obj = contents_one.splitlines(False)
            for index_one in range(len(lines_obj)):
                line_words = lines_obj[index_one].split()
                if len(line_words) == 8 and (
                            (len(
                                line_words[6]) == 16 or len(
                                line_words[6]) == 8) and line_words[6] != 'Value'):
                    export_content(
                        '    %s' %
                        lines_obj[index_one].replace(
                            line_words[6],
                            use_style_level(
                                important_level['high2'],
                                line_words[6])))
                else:
                    export_content('    %s' % lines_obj[index_one])

            export_content(
                '    %s   ' %
                use_style_level(
                    important_level['low2'],
                    '-------------'))
        pass
