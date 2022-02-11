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
    ILL if i & 0b0100000 else 0
    for i in range(1 << 7)
]

bits[0b0000000] = 0
bits[0b1000000] = 0
bits[0b0100000] = 0
bits[0b1100000] = SYS
bits[0b0000001] = 0
bits[0b1000001] = 0
bits[0b0100001] = 0
bits[0b1100001] = BRK
bits[0b0001101] = 0
bits[0b1001101] = 0
bits[0b0101101] = WFI
bits[0b1101101] = WFI
bits[0b0011010] = 0
bits[0b1011010] = 0
bits[0b0111010] = 0
bits[0b1111010] = RET

with open('sysdec.logic', 'w') as fp:
    print('SYSTEM sub-opcode decoder.', file = fp)
    print(file = fp)
    print('device:', file = fp)
    print('    GAL22V10_14_8', file = fp)
    print(file = fp)
    print('pins:', file = fp)
    print('    GND V3  V2  V1  V0  S0  SYS P29 P28 P22 P21 P20', file = fp)
    print('    FN  IM1 IM0 ILL WFI RET BRK EMC _   _   _   VCC', file = fp)
    print(file = fp)
    print('no-opt:', file = fp)
    print('    ILL', file = fp)
    print(file = fp)
    print('define:', file = fp)
    print('    VLD = V3 | V2 | V1 | V0', file = fp)
    print('    ILL = FN & IM1 | SYS & IM0 | ~VLD | ERR', file = fp)
    print(file = fp)
    print('table:', file = fp)
    print('    S0  SYS P29 P28 P22 P21 P20 |  ERR WFI RET BRK EMC', file = fp)
    for i in range(len(bits)):
        key = '   '.join('{0:07b}'.format(i))
        val = '   '.join('1' if bits[i] & (1 << v) else '0' for v in range(5))
        print('    %s   |  %s' % (key, val), file = fp)

fpath = os.path.abspath(__file__)
fname = os.path.join(os.path.dirname(fpath), '../../Tools/LogicGen/logen.py')

subprocess.call([
    fname,
    os.path.join(os.path.dirname(fpath), 'sysdec.logic')
])