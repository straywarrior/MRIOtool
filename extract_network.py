#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2016 StrayWarrior <i@straywarrior.com>
#

import sys
import csv
import re



def main(argv):
    trans_lines = []
    with open(argv[1], encoding='utf-8') as network_csv:
        netreader = csv.reader(network_csv, delimiter=',')
        for line in netreader:
            for i in range(6, len(line), 3):
                cur = line[i]
                if (len(cur) == 0):
                    continue
                prog = re.compile('(.*)－(.*)')
                mres = prog.match(cur)
                if (not mres):
                    continue
                trans_lines.append((mres.group(1), mres.group(2), line[i - 1]))
    print("{} lines processed.".format(len(trans_lines)))
    with open(argv[2], 'w', newline='', encoding='utf-8') as network_csv:
        netwriter = csv.writer(network_csv, delimiter=',')
        #for i in trans_lines:
        netwriter.writerows(trans_lines)


if __name__ == '__main__':
    main(sys.argv)
