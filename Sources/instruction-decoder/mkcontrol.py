#!/usr/bin/env python3
# -*- coding: utf-8 -8-

import os
import subprocess

RD          = 1 << 0
RS1         = 1 << 1
RS2         = 1 << 2
OPIMM       = 1 << 3
HOLD        = 1 << 4

X           = -1
XXXXX       = -1

OUT_BITS    = 5
ROM_BITS    = 13

microps = [
    0
    for _ in range(1 << ROM_BITS)
]

def OP(name: str, s: int, c: int, f: int, f3: int, op: int, mop: int):
    if op & ~0b11111:
        raise ValueError(name + ': op must be a 5-bit value')
    elif s != X and (s & ~0b1):
        raise ValueError(name + ': s must be a 1-bit value or X')
    elif c != X and (c & ~0b1):
        raise ValueError(name + ': c must be a 1-bit value or X')
    elif f != X and (f & ~0b1):
        raise ValueError(name + ': f must be a 1-bit value or X')
    elif f3 != XXXXX and (f3 & ~0b111):
        raise ValueError(name + ': f3 must be a 3-bit value or XXXXX')
    else:
        for i in range(2):
            for j in range(2):
                for k in range(2):
                    for v in range(8):
                        if s in (i, X) and c in (j, X) and f in (k, X) and f3 in (v, XXXXX):
                            cc = (i << 12) | (j << 11) | (k << 10) | (v << 7) | (op << 2) | 0b11
                            if mop != 0 and microps[cc]:
                                raise ValueError('%s: instruction was already assigned: %04x == %06x' % (name, cc, microps[cc]))
                            else:
                                microps[cc] = mop

#  name       s  c  f  f3     op       mop
OP('LUI'    , 0, X, X, XXXXX, 0b01101, RD | OPIMM)
OP('AUIPC'  , 0, X, X, XXXXX, 0b00101, RD | OPIMM)
OP('JAL'    , 0, X, X, XXXXX, 0b11011, RD | OPIMM | HOLD)
OP('JAL'    , 1, X, X, XXXXX, 0b11011, 0)
OP('JALR'   , 0, X, X, 0b000, 0b11001, RD | RS1 | OPIMM | HOLD)
OP('JALR'   , 1, X, X, 0b000, 0b11001, 0)
OP('Bcc'    , 0, X, X, XXXXX, 0b11000, RS1 | RS2 | OPIMM | HOLD)
OP('Bcc'    , 1, X, X, XXXXX, 0b11000, 0)
OP('Bcc'    , X, X, X, 0b010, 0b11000, 0)
OP('Bcc'    , X, X, X, 0b011, 0b11000, 0)

OP('LB'     , 0, X, X, 0b000, 0b00000, RD | RS1 | OPIMM | HOLD)
OP('LH'     , 0, X, X, 0b001, 0b00000, RD | RS1 | OPIMM | HOLD)
OP('LW'     , 0, X, X, 0b010, 0b00000, RD | RS1 | OPIMM | HOLD)
OP('LBU'    , 0, X, X, 0b100, 0b00000, RD | RS1 | OPIMM | HOLD)
OP('LHU'    , 0, X, X, 0b101, 0b00000, RD | RS1 | OPIMM | HOLD)
OP('SB'     , 0, X, X, 0b000, 0b01000, RS1 | RS2 | OPIMM | HOLD)
OP('SH'     , 0, X, X, 0b001, 0b01000, RS1 | RS2 | OPIMM | HOLD)
OP('SW'     , 0, X, X, 0b010, 0b01000, RS1 | RS2 | OPIMM | HOLD)
OP('LB'     , 1, X, X, 0b000, 0b00000, 0)
OP('LH'     , 1, X, X, 0b001, 0b00000, 0)
OP('LW'     , 1, X, X, 0b010, 0b00000, 0)
OP('LBU'    , 1, X, X, 0b100, 0b00000, 0)
OP('LHU'    , 1, X, X, 0b101, 0b00000, 0)
OP('SB'     , 1, X, X, 0b000, 0b01000, 0)
OP('SH'     , 1, X, X, 0b001, 0b01000, 0)
OP('SW'     , 1, X, X, 0b010, 0b01000, 0)

OP('ADDI'   , 0, X, X, 0b000, 0b00100, RD | RS1 | OPIMM)
OP('SLTI'   , 0, X, X, 0b010, 0b00100, RD | RS1 | OPIMM)
OP('SLTIU'  , 0, X, X, 0b011, 0b00100, RD | RS1 | OPIMM)
OP('XORI'   , 0, X, X, 0b100, 0b00100, RD | RS1 | OPIMM)
OP('ORI'    , 0, X, X, 0b110, 0b00100, RD | RS1 | OPIMM)
OP('ANDI'   , 0, X, X, 0b111, 0b00100, RD | RS1 | OPIMM)
OP('SLLI'   , 0, 0, 0, 0b001, 0b00100, RD | RS1 | OPIMM)
OP('SRLI'   , 0, 0, 0, 0b101, 0b00100, RD | RS1 | OPIMM)
OP('SRAI'   , 0, 1, 0, 0b101, 0b00100, RD | RS1 | OPIMM)
OP('ADD'    , 0, 0, 0, 0b000, 0b01100, RD | RS1 | RS2)
OP('SUB'    , 0, 1, 0, 0b000, 0b01100, RD | RS1 | RS2)
OP('SLL'    , 0, 0, 0, 0b001, 0b01100, RD | RS1 | RS2)
OP('SLT'    , 0, 0, 0, 0b010, 0b01100, RD | RS1 | RS2)
OP('SLTU'   , 0, 0, 0, 0b011, 0b01100, RD | RS1 | RS2)
OP('XOR'    , 0, 0, 0, 0b100, 0b01100, RD | RS1 | RS2)
OP('SRL'    , 0, 0, 0, 0b101, 0b01100, RD | RS1 | RS2)
OP('SRA'    , 0, 1, 0, 0b101, 0b01100, RD | RS1 | RS2)
OP('OR'     , 0, 0, 0, 0b110, 0b01100, RD | RS1 | RS2)
OP('AND'    , 0, 0, 0, 0b111, 0b01100, RD | RS1 | RS2)
OP('MUL'    , 0, 0, 1, 0b000, 0b01100, RD | RS1 | RS2)
OP('MULH'   , 0, 0, 1, 0b001, 0b01100, RD | RS1 | RS2)
OP('MULHU'  , 0, 0, 1, 0b011, 0b01100, RD | RS1 | RS2)
OP('MULHSU' , 0, 0, 1, 0b010, 0b01100, RD | RS1 | RS2)
OP('DIV'    , 0, 0, 1, 0b100, 0b01100, RD | RS1 | RS2)
OP('DIVU'   , 0, 0, 1, 0b101, 0b01100, RD | RS1 | RS2)
OP('REM'    , 0, 0, 1, 0b110, 0b01100, RD | RS1 | RS2)
OP('REMU'   , 0, 0, 1, 0b111, 0b01100, RD | RS1 | RS2)

OP('FENCE'  , 0, X, X, 0b000, 0b00011, RD | RS1)
OP('FENCE.I', 0, X, X, 0b001, 0b00011, RD | RS1)
OP('SYSTEM' , X, 0, X, 0b000, 0b11100, HOLD)

OP('CSRRW'  , 0, X, X, 0b001, 0b11100, RD | RS1)
OP('CSRRS'  , 0, X, X, 0b010, 0b11100, RD | RS1)
OP('CSRRC'  , 0, X, X, 0b011, 0b11100, RD | RS1)
OP('CSRRWI' , 0, X, X, 0b101, 0b11100, RD)
OP('CSRRSI' , 0, X, X, 0b110, 0b11100, RD)
OP('CSRRCI' , 0, X, X, 0b111, 0b11100, RD)

with open('control.logic', 'w') as fp:
    print('Instruction Decoder -- Common Control Signals.', file = fp)
    print(file = fp)
    print('device:', file = fp)
    print('    GAL22V10_13_9', file = fp)
    print(file = fp)
    print('pins:', file = fp)
    print('    GND P25 P14 P13 P12 P6  P5  P4  P3  P2  P1  P0', file = fp)
    print('    CTR P30 HLD OPI RS2 RS1 RD  _   _   _   _   VCC', file = fp)
    print(file = fp)
    print('table:', file = fp)
    print('    CTR P30 P25 P14 P13 P12 P6  P5  P4  P3  P2  P1  P0  |  HLD OPI RS2 RS1 RD', file = fp)
    for i in range(len(microps)):
        key = '   '.join(('{0:0%db}' % ROM_BITS).format(i))
        val = '   '.join('1' if microps[i] & (1 << v) else '0' for v in range(OUT_BITS - 1, -1, -1))
        print('    %s   |  %s' % (key, val), file = fp)

fpath = os.path.abspath(__file__)
fname = os.path.join(os.path.dirname(fpath), '../../Tools/LogicGen/logen.py')

subprocess.call([
    fname,
    os.path.join(os.path.dirname(fpath), 'control.logic')
])
