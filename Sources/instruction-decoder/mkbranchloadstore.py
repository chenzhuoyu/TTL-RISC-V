#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import subprocess

PCREL       = 1 << 0
BRANCH      = 1 << 1
LINK        = 1 << 2
LDSX        = 1 << 3
LD0         = 1 << 4
LD1         = 1 << 5
ST0         = 1 << 6
ST1         = 1 << 7
SIGILL      = 1 << 8

X           = -1
XXXXX       = -1
OUT_BITS    = 9
ROM_BITS    = 11

microps = [
    SIGILL
    for _ in range(1 << ROM_BITS)
]

def OP(name: str, s: int, f3: int, op: int, mop: int):
    if op & ~0b11111:
        raise ValueError(name + ': op must be a 5-bit value')
    elif s != X and (s & ~0b1):
        raise ValueError(name + ': s must be a 1-bit value or X')
    elif f3 != XXXXX and (f3 & ~0b111):
        raise ValueError(name + ': f3 must be a 3-bit value or XXXXX')
    else:
        for i in range(2):
            for v in range(8):
                if s in (i, X) and f3 in (v, XXXXX):
                    cc = (i << 10) | (v << 7) | (op << 2) | 0b11
                    if mop != SIGILL and not (microps[cc] & SIGILL):
                        raise ValueError('%s: instruction was already assigned: %04x == %06x' % (name, cc, microps[cc]))
                    else:
                        microps[cc] = mop

#  name     s  f3     op       mop
OP('LUI'  , 0, XXXXX, 0b01101, 0)
OP('AUIPC', 0, XXXXX, 0b00101, PCREL)
OP('JAL'  , 0, XXXXX, 0b11011, PCREL | BRANCH | LINK)
OP('JAL'  , 1, XXXXX, 0b11011, 0)
OP('JALR' , 0, 0b000, 0b11001, BRANCH | LINK)
OP('JALR' , 1, 0b000, 0b11001, 0)
OP('Bcc'  , 0, XXXXX, 0b11000, PCREL | BRANCH)
OP('Bcc'  , 1, XXXXX, 0b11000, 0)
OP('Bcc'  , X, 0b010, 0b11000, SIGILL)
OP('Bcc'  , X, 0b011, 0b11000, SIGILL)

OP('LB'   , 0, 0b000, 0b00000, LDSX | LD0)
OP('LH'   , 0, 0b001, 0b00000, LDSX | LD1)
OP('LW'   , 0, 0b010, 0b00000, LD0 | LD1)
OP('LBU'  , 0, 0b100, 0b00000, LD0)
OP('LHU'  , 0, 0b101, 0b00000, LD1)
OP('SB'   , 0, 0b000, 0b01000, ST0)
OP('SH'   , 0, 0b001, 0b01000, ST1)
OP('SW'   , 0, 0b010, 0b01000, ST0 | ST1)

OP('LB'   , 1, 0b000, 0b00000, 0)
OP('LH'   , 1, 0b001, 0b00000, 0)
OP('LW'   , 1, 0b010, 0b00000, 0)
OP('LBU'  , 1, 0b100, 0b00000, 0)
OP('LHU'  , 1, 0b101, 0b00000, 0)
OP('SB'   , 1, 0b000, 0b01000, 0)
OP('SH'   , 1, 0b001, 0b01000, 0)
OP('SW'   , 1, 0b010, 0b01000, 0)

for i in range(len(microps)):
    microps[i] ^= SIGILL

with open('branchloadstore.logic', 'w') as fp:
    print('Instruction Decoder -- Load & Store.', file = fp)
    print(file = fp)
    print('device:', file = fp)
    print('    GAL22V10', file = fp)
    print(file = fp)
    print('pins:', file = fp)
    print('    GND CTR P14 P13 P12 P6  P5  P4  P3  P2  P1  P0', file = fp)
    print('    _   VLD ST1 ST0 LD1 LD0 SX  LNK BR  REL _   VCC', file = fp)
    print(file = fp)
    print('table:', file = fp)
    print('    CTR P14 P13 P12 P6  P5  P4  P3  P2  P1  P0  |  VLD ST1 ST0 LD1 LD0 SX  LNK BR  REL', file = fp)
    for i in range(len(microps)):
        key = '   '.join(('{0:0%db}' % ROM_BITS).format(i))
        val = '   '.join('1' if microps[i] & (1 << v) else '0' for v in range(OUT_BITS - 1, -1, -1))
        print('    %s   |  %s' % (key, val), file = fp)

fpath = os.path.abspath(__file__)
fname = os.path.join(os.path.dirname(fpath), '../../Tools/LogicGen/logen.py')

subprocess.call([
    fname,
    os.path.join(os.path.dirname(fpath), 'branchloadstore.logic')
])
