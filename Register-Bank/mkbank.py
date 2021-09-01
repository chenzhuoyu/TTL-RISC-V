#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import collections

with open('Layer0/Layer0.sch') as fp:
    lines = fp.read().splitlines()

ret = []
ctr = collections.Counter()

for line in lines:
    if line.startswith('WR_{'):
        name = line[4:]
        rpos = name.index('}')
        tail = name[rpos + 1:]
        name = name[:rpos]
        ctr[name] += 1
        line = line[:3] + str(ctr[name])
    ret.append(line)

with open('Layer0/Layer0.sch', 'w') as fp:
    for line in ret:
        print(line, file = fp)
