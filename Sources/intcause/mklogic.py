#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import subprocess

TRG = 0
EAL = 1
ESL = 2
BRK = 3
SYS = 4
EPL = 5
ILL = 6

bits = [
    0
    for _ in range(1 << 7)
]

def OP(name: str, b: int, h: int, l: int):
    if h &~ 0b1:
        raise ValueError(name + ': h must be a 1-bit value')
    elif l &~ 0b1111:
        raise ValueError(name + ': l must be a 4-bit value')
    elif not (0 <= b <= 6):
        raise ValueError(name + ': b must >= 0 and <= 6')
    else:
        for i in range(1 << b, 1 << (b + 1)):
            bits[i] = (h << 4) | l

OP('TRG', TRG, 1, 0x0b)     # 0x8000000b: External Interrupt
OP('EAL', EAL, 0, 0x04)     # 0x00000004: Load Address Misaligned
OP('ESL', ESL, 0, 0x06)     # 0x00000006: Store Address Misaligned
OP('BRK', BRK, 0, 0x03)     # 0x00000003: Environment Break
OP('SYS', SYS, 0, 0x0b)     # 0x0000000b: Environment Call
OP('EPL', EPL, 0, 0x00)     # 0x00000000: Instruction Address Misaligned
OP('ILL', ILL, 0, 0x02)     # 0x00000002: Illegal Instruction

with open('intcause.logic', 'w') as fp:
    print('Prioritized interrupt cause decoder.', file = fp)
    print(file = fp)
    print('device:', file = fp)
    print('    GAL22V10', file = fp)
    print(file = fp)
    print('pins:', file = fp)
    print('    GND ILL EPL EAM LDR TRG BRK SYS _   _   _   _', file = fp)
    print('    _   IRQ C31 C3  C2  C1  C0  _   _   _   _   VCC', file = fp)
    print(file = fp)
    print('define:', file = fp)
    print('    ESL = EAM & LDR', file = fp)
    print('    EAL = EAM & ~LDR', file = fp)
    print('    IRQ = ILL | EPL | EAM', file = fp)
    print(file = fp)
    print('table:', file = fp)
    print('    ILL EPL SYS BRK ESL EAL TRG |  C31 C3  C2  C1  C0', file = fp)
    for i in range(len(bits)):
        key = '   '.join('{0:07b}'.format(i))
        val = '   '.join('1' if bits[i] & (1 << v) else '0' for v in range(4, -1, -1))
        print('    %s   |  %s' % (key, val), file = fp)

fpath = os.path.abspath(__file__)
fname = os.path.join(os.path.dirname(fpath), '../../Tools/LogicGen/logen.py')

subprocess.call([
    fname,
    os.path.join(os.path.dirname(fpath), 'intcause.logic')
])