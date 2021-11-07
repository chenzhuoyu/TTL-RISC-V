#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import subprocess

FUNCT       = 1 << 0
SYSTEM      = 1 << 1
SIGILL      = 1 << 2

X        = -1
XXXXX    = -1
ROM_SIZE = 1 << 10

microps = [
    SIGILL
    for _ in range(ROM_SIZE)
]

def OP(name: str, f: int, g: int, f3: int, op: int, ctl: int):
    for i in range(2):
        for j in range(2):
            for k in range(8):
                if f in (i, X) and g in (j, X) and f3 in (k, XXXXX):
                    cc = (i << 9) | (j << 8) | (k << 5) | op
                    if not (microps[cc] & SIGILL):
                        raise ValueError('{0}: instruction was already assigned: {1:09b} == {2:03b}'.format(name, cc, microps[cc]))
                    else:
                        microps[cc] = ctl

#  name       f  g  f3     op       ctl
OP('LUI'    , X, X, XXXXX, 0b01101, 0)
OP('AUIPC'  , X, X, XXXXX, 0b00101, 0)
OP('JAL'    , X, X, XXXXX, 0b11011, 0)
OP('JALR'   , X, X, 0b000, 0b11001, 0)
OP('BEQ'    , X, X, 0b000, 0b11000, 0)
OP('BNE'    , X, X, 0b001, 0b11000, 0)
OP('BLT'    , X, X, 0b100, 0b11000, 0)
OP('BGE'    , X, X, 0b101, 0b11000, 0)
OP('BLTU'   , X, X, 0b110, 0b11000, 0)
OP('BGEU'   , X, X, 0b111, 0b11000, 0)
OP('LB'     , X, X, 0b000, 0b00000, 0)
OP('LH'     , X, X, 0b001, 0b00000, 0)
OP('LW'     , X, X, 0b010, 0b00000, 0)
OP('LBU'    , X, X, 0b100, 0b00000, 0)
OP('LHU'    , X, X, 0b101, 0b00000, 0)
OP('SB'     , X, X, 0b000, 0b01000, 0)
OP('SH'     , X, X, 0b001, 0b01000, 0)
OP('SW'     , X, X, 0b010, 0b01000, 0)
OP('ADDI'   , X, X, 0b000, 0b00100, 0)
OP('SLTI'   , X, X, 0b010, 0b00100, 0)
OP('SLTIU'  , X, X, 0b011, 0b00100, 0)
OP('XORI'   , X, X, 0b100, 0b00100, 0)
OP('ORI'    , X, X, 0b110, 0b00100, 0)
OP('ANDI'   , X, X, 0b111, 0b00100, 0)
OP('SLLI'   , 0, 0, 0b001, 0b00100, FUNCT)
OP('SRLI'   , 0, 0, 0b101, 0b00100, FUNCT)
OP('SRAI'   , 1, 0, 0b101, 0b00100, FUNCT)
OP('ADD'    , 0, 0, 0b000, 0b01100, FUNCT)
OP('SUB'    , 1, 0, 0b000, 0b01100, FUNCT)
OP('SLL'    , 0, 0, 0b001, 0b01100, FUNCT)
OP('SLT'    , 0, 0, 0b010, 0b01100, FUNCT)
OP('SLTU'   , 0, 0, 0b011, 0b01100, FUNCT)
OP('XOR'    , 0, 0, 0b100, 0b01100, FUNCT)
OP('SRL'    , 0, 0, 0b101, 0b01100, FUNCT)
OP('SRA'    , 1, 0, 0b101, 0b01100, FUNCT)
OP('OR'     , 0, 0, 0b110, 0b01100, FUNCT)
OP('AND'    , 0, 0, 0b111, 0b01100, FUNCT)
OP('FENCE'  , X, X, 0b000, 0b00011, 0)
OP('SYSTEM' , 0, 0, 0b000, 0b11100, FUNCT | SYSTEM)
OP('MUL'    , 0, 1, 0b000, 0b01100, FUNCT)
OP('MULH'   , 0, 1, 0b001, 0b01100, FUNCT)
OP('MULHU'  , 0, 1, 0b011, 0b01100, FUNCT)
OP('MULHSU' , 0, 1, 0b010, 0b01100, FUNCT)
OP('DIV'    , 0, 1, 0b100, 0b01100, FUNCT)
OP('DIVU'   , 0, 1, 0b101, 0b01100, FUNCT)
OP('REM'    , 0, 1, 0b110, 0b01100, FUNCT)
OP('REMU'   , 0, 1, 0b111, 0b01100, FUNCT)

with open('inscheck.logic', 'w') as fp:
    print('Check for illegal instructions.', file = fp)
    print(file = fp)
    print('device:', file = fp)
    print('    GAL22V10', file = fp)
    print(file = fp)
    print('pins:', file = fp)
    print('    GND P30 P25 P14 P13 P12 P6  P5  P4  P3  P2  _', file = fp)
    print('    _   FN  SYS ILL _   _   _   _   _   _   _   VCC', file = fp)
    print(file = fp)
    print('table:', file = fp)
    print('    P30 P25 P14 P13 P12 P6  P5  P4  P3  P2  |  FN  SYS ILL', file = fp)
    for i in range(ROM_SIZE):
        key = '   '.join('{0:010b}'.format(i))
        val = '   '.join('1' if microps[i] & (1 << v) else '0' for v in range(3))
        print('    %s   |  %s' % (key, val), file = fp)

fname = os.path.abspath(__file__)
fname = os.path.join(os.path.dirname(fname), '../../Tools/LogicGen/logen.py')

subprocess.call([
    fname,
    './inscheck.logic'
])
