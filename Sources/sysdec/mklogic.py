#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import subprocess

SYS = 1 << 0
BRK = 1 << 1
RET = 1 << 2
WFI = 1 << 3
ILL = 1 << 4

bits = [
    ILL
    for _ in range(1 << 5)
]

bits[0b00000] = SYS
bits[0b00001] = BRK
bits[0b01101] = WFI
bits[0b11010] = RET

with open('sysdec.logic', 'w') as fp:
    print('SYSTEM sub-opcode decoder.', file = fp)
    print(file = fp)
    print('device:', file = fp)
    print('    GAL22V10', file = fp)
    print(file = fp)
    print('pins:', file = fp)
    print('    GND P29 P28 P22 P21 P20 _   _   _   _   _   _', file = fp)
    print('    _   SYS BRK RET WFI ILL _   _   _   _   _   VCC', file = fp)
    print(file = fp)
    print('table:', file = fp)
    print('    P29 P28 P22 P21 P20 |  SYS BRK RET WFI ILL', file = fp)
    for i in range(len(bits)):
        key = '   '.join('{0:05b}'.format(i))
        val = '   '.join('1' if bits[i] & (1 << v) else '0' for v in range(5))
        print('    %s   |  %s' % (key, val), file = fp)

fpath = os.path.abspath(__file__)
fname = os.path.join(os.path.dirname(fpath), '../../Tools/LogicGen/logen.py')

subprocess.call([
    fname,
    os.path.join(os.path.dirname(fpath), 'sysdec.logic')
])