#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import subprocess

LDSX        = 1 << 0
LD0         = 1 << 1
LD1         = 1 << 2
ST0         = 1 << 3
ST1         = 1 << 4
SIGILL      = 1 << 5

X           = -1
OUT_BITS    = 6
ROM_BITS    = 11

microps = [
    SIGILL
    for _ in range(1 << ROM_BITS)
]

def OP(name: str, s: int, f3: int, op: int, mop: int):
    if op & ~0b11111:
        raise ValueError(name + ': op must be a 5-bit value')
    elif f3 & ~0b111:
        raise ValueError(name + ': f3 must be a 3-bit value')
    elif s != X and (s & ~0b1):
        raise ValueError(name + ': s must be a 1-bit value or X')
    else:
        for i in range(2):
            if s in (i, X):
                cc = (i << 10) | (f3 << 7) | (op << 2) | 0b11
                if mop != SIGILL and not (microps[cc] & SIGILL):
                    raise ValueError('%s: instruction was already assigned: %04x == %06x' % (name, cc, microps[cc]))
                else:
                    microps[cc] = mop

#  name   s  f3     op       mop
OP('LB' , 0, 0b000, 0b00000, LDSX | LD0)
OP('LH' , 0, 0b001, 0b00000, LDSX | LD1)
OP('LW' , 0, 0b010, 0b00000, LD0 | LD1)
OP('LBU', 0, 0b100, 0b00000, LD0)
OP('LHU', 0, 0b101, 0b00000, LD1)
OP('SB' , 0, 0b000, 0b01000, ST0)
OP('SH' , 0, 0b001, 0b01000, ST1)
OP('SW' , 0, 0b010, 0b01000, ST0 | ST1)

OP('LB' , 1, 0b000, 0b00000, 0)
OP('LH' , 1, 0b001, 0b00000, 0)
OP('LW' , 1, 0b010, 0b00000, 0)
OP('LBU', 1, 0b100, 0b00000, 0)
OP('LHU', 1, 0b101, 0b00000, 0)
OP('SB' , 1, 0b000, 0b01000, 0)
OP('SH' , 1, 0b001, 0b01000, 0)
OP('SW' , 1, 0b010, 0b01000, 0)

for i in range(len(microps)):
    microps[i] ^= SIGILL

with open('loadstore.logic', 'w') as fp:
    print('Instruction Decoder -- Load & Store.', file = fp)
    print(file = fp)
    print('device:', file = fp)
    print('    GAL22V10', file = fp)
    print(file = fp)
    print('pins:', file = fp)
    print('    GND CTR P14 P13 P12 P6  P5  P4  P3  P2  P1  P0', file = fp)
    print('    _   VLD ST1 ST0 LD1 LD0 SX  _   _   _   _   VCC', file = fp)
    print(file = fp)
    print('table:', file = fp)
    print('    CTR P14 P13 P12 P6  P5  P4  P3  P2  P1  P0  |  VLD ST1 ST0 LD1 LD0 SX', file = fp)
    for i in range(len(microps)):
        key = '   '.join(('{0:0%db}' % ROM_BITS).format(i))
        val = '   '.join('1' if microps[i] & (1 << v) else '0' for v in range(OUT_BITS - 1, -1, -1))
        print('    %s   |  %s' % (key, val), file = fp)

fpath = os.path.abspath(__file__)
fname = os.path.join(os.path.dirname(fpath), '../../Tools/LogicGen/logen.py')

subprocess.call([
    fname,
    os.path.join(os.path.dirname(fpath), 'loadstore.logic')
])
