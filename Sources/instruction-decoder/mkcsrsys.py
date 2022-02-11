#!/usr/bin/env python3
# -*- coding: utf-8 -8-

import os
import subprocess

CSR_EN      = 1 << 0
CSR_IMM     = 1 << 1
CSR_BIT     = 1 << 2
CSR_CLR     = 1 << 3
SYSTEM      = 1 << 4
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

#  name       s  f3     op       mop
OP('FENCE'  , 0, 0b000, 0b00011, 0)
OP('FENCE.I', 0, 0b001, 0b00011, 0)
OP('SYSTEM' , X, 0b000, 0b11100, SYSTEM)

OP('CSRRW'  , 0, 0b001, 0b11100, CSR_EN)
OP('CSRRS'  , 0, 0b010, 0b11100, CSR_EN | CSR_BIT)
OP('CSRRC'  , 0, 0b011, 0b11100, CSR_EN | CSR_BIT | CSR_CLR)
OP('CSRRWI' , 0, 0b101, 0b11100, CSR_EN | CSR_IMM)
OP('CSRRSI' , 0, 0b110, 0b11100, CSR_EN | CSR_IMM | CSR_BIT)
OP('CSRRCI' , 0, 0b111, 0b11100, CSR_EN | CSR_IMM | CSR_BIT | CSR_CLR)

for i in range(len(microps)):
    microps[i] ^= SIGILL

with open('csrsys.logic', 'w') as fp:
    print('Instruction Decoder -- CSR & SYSTEM instructions.', file = fp)
    print(file = fp)
    print('device:', file = fp)
    print('    GAL22V10', file = fp)
    print(file = fp)
    print('pins:', file = fp)
    print('    GND CTR P14 P13 P12 P6  P5  P4  P3  P2  P1  P0', file = fp)
    print('    _   VLD SYS CLR BIT CSI CSE _   _   _   _   VCC', file = fp)
    print(file = fp)
    print('table:', file = fp)
    print('    CTR P14 P13 P12 P6  P5  P4  P3  P2  P1  P0  |  VLD SYS CLR BIT CSI CSE', file = fp)
    for i in range(len(microps)):
        key = '   '.join(('{0:0%db}' % ROM_BITS).format(i))
        val = '   '.join('1' if microps[i] & (1 << v) else '0' for v in range(OUT_BITS - 1, -1, -1))
        print('    %s   |  %s' % (key, val), file = fp)

fpath = os.path.abspath(__file__)
fname = os.path.join(os.path.dirname(fpath), '../../Tools/LogicGen/logen.py')

subprocess.call([
    fname,
    os.path.join(os.path.dirname(fpath), 'csrsys.logic')
])