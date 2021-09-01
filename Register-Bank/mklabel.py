#!/usr/bin/env python3
# -*- coding: utf-8 -*-

with open('Layer0/Layer0.sch') as fp:
    lines = fp.read().splitlines()

ret = []
cur = None
ctr = {'C': 1, 'U': 1, 'J': 1}
comp = False

for line in lines:
    if line == '$Comp':
        cur = None
        comp = True
    elif line == '$EndComp':
        if cur is not None:
            ctr[cur] += 1
        comp = False
        update = False
    elif comp and '?' in line and '#PWR' not in line:
        args = line.split(' ')
        if args[0] == 'L':
            cur = args[2][:-1]
            args[2] = cur + str(ctr[cur])
        elif args[0] == 'F' and args[1] == '0':
            args[2] = '"%c%d"' % (cur, ctr[cur])
        line = ' '.join(args)
    ret.append(line)

with open('Layer0/Layer0.sch') as fp:
    with open('Layer0/Layer0.sch-bak', 'w') as wfp:
        wfp.write(fp.read())

with open('Layer0/Layer0.sch', 'w') as fp:
    for line in ret:
        print(line, file = fp)
