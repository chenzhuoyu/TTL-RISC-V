#!/usr/bin/env python3
# -*- coding: utf-8 -8-

import os
import subprocess

ALU_ADD     = 0b00000
ALU_SUB     = 0b10000
ALU_SHL     = 0b00001
ALU_SLT     = 0b00010
ALU_SLTU    = 0b00011
ALU_XOR     = 0b00100
ALU_SHR     = 0b00101
ALU_SAR     = 0b10101
ALU_OR      = 0b00110
ALU_AND     = 0b00111
ALU_MUL     = 0b01000
ALU_MULH    = 0b01001
ALU_MULHSU  = 0b01010
ALU_MULHU   = 0b01011
ALU_DIV     = 0b01100
ALU_DIVU    = 0b01101
ALU_REM     = 0b01110
ALU_REMU    = 0b01111

FUNCT       = 1 << 5
SIGILL      = 1 << 6

X           = -1
OUT_BITS    = 7
ROM_BITS    = 13

microps = [
    SIGILL
    for _ in range(1 << ROM_BITS)
]

def OP(name: str, s: int, c: int, f: int, f3: int, op: int, mop: int):
    if op & ~0b11111:
        raise ValueError(name + ': op must be a 5-bit value')
    elif f3 & ~0b111:
        raise ValueError(name + ': f3 must be a 3-bit value')
    elif s != X and (s & ~0b1):
        raise ValueError(name + ': s must be a 1-bit value or X')
    elif c != X and (c & ~0b1):
        raise ValueError(name + ': c must be a 1-bit value or X')
    elif f != X and (f & ~0b1):
        raise ValueError(name + ': f must be a 1-bit value or X')
    else:
        for i in range(2):
            for j in range(2):
                for k in range(2):
                    if s in (i, X) and c in (j, X) and f in (k, X):
                        cc = (i << 12) | (j << 11) | (k << 10) | (f3 << 7) | (op << 2) | 0b11
                        if mop != SIGILL and not (microps[cc] & SIGILL):
                            raise ValueError('%s: instruction was already assigned: %04x == %06x' % (name, cc, microps[cc]))
                        else:
                            microps[cc] = mop

#  name       s  c  f  f3     op       mop
OP('ADDI'   , 0, X, X, 0b000, 0b00100, ALU_ADD)
OP('SLTI'   , 0, X, X, 0b010, 0b00100, ALU_SLT)
OP('SLTIU'  , 0, X, X, 0b011, 0b00100, ALU_SLTU)
OP('XORI'   , 0, X, X, 0b100, 0b00100, ALU_XOR)
OP('ORI'    , 0, X, X, 0b110, 0b00100, ALU_OR)
OP('ANDI'   , 0, X, X, 0b111, 0b00100, ALU_AND)
OP('SLLI'   , 0, 0, 0, 0b001, 0b00100, ALU_SHL    | FUNCT)
OP('SRLI'   , 0, 0, 0, 0b101, 0b00100, ALU_SHR    | FUNCT)
OP('SRAI'   , 0, 1, 0, 0b101, 0b00100, ALU_SAR    | FUNCT)
OP('ADD'    , 0, 0, 0, 0b000, 0b01100, ALU_ADD    | FUNCT)
OP('SUB'    , 0, 1, 0, 0b000, 0b01100, ALU_SUB    | FUNCT)
OP('SLL'    , 0, 0, 0, 0b001, 0b01100, ALU_SHL    | FUNCT)
OP('SLT'    , 0, 0, 0, 0b010, 0b01100, ALU_SLT    | FUNCT)
OP('SLTU'   , 0, 0, 0, 0b011, 0b01100, ALU_SLTU   | FUNCT)
OP('XOR'    , 0, 0, 0, 0b100, 0b01100, ALU_XOR    | FUNCT)
OP('SRL'    , 0, 0, 0, 0b101, 0b01100, ALU_SHR    | FUNCT)
OP('SRA'    , 0, 1, 0, 0b101, 0b01100, ALU_SAR    | FUNCT)
OP('OR'     , 0, 0, 0, 0b110, 0b01100, ALU_OR     | FUNCT)
OP('AND'    , 0, 0, 0, 0b111, 0b01100, ALU_AND    | FUNCT)
OP('MUL'    , X, 0, 1, 0b000, 0b01100, ALU_MUL    | FUNCT)
OP('MULH'   , X, 0, 1, 0b001, 0b01100, ALU_MULH   | FUNCT)
OP('MULHSU' , X, 0, 1, 0b010, 0b01100, ALU_MULHSU | FUNCT)
OP('MULHU'  , X, 0, 1, 0b011, 0b01100, ALU_MULHU  | FUNCT)
OP('DIV'    , X, 0, 1, 0b100, 0b01100, ALU_DIV    | FUNCT)
OP('DIVU'   , X, 0, 1, 0b101, 0b01100, ALU_DIVU   | FUNCT)
OP('REM'    , X, 0, 1, 0b110, 0b01100, ALU_REM    | FUNCT)
OP('REMU'   , X, 0, 1, 0b111, 0b01100, ALU_REMU   | FUNCT)

for i in range(len(microps)):
    microps[i] ^= SIGILL

with open('arith.logic', 'w') as fp:
    print('Instruction Decoder -- Arithmetic & Logic.', file = fp)
    print(file = fp)
    print('device:', file = fp)
    print('    GAL22V10_13_9', file = fp)
    print(file = fp)
    print('pins:', file = fp)
    print('    GND P25 P14 P13 P12 P6  P5  P4  P3  P2  P1  P0', file = fp)
    print('    CTR P30 VLD FN  OP4 OP3 OP2 OP1 OP0 _   _   VCC', file = fp)
    print(file = fp)
    print('table:', file = fp)
    print('    CTR P30 P25 P14 P13 P12 P6  P5  P4  P3  P2  P1  P0  |  VLD FN  OP4 OP3 OP2 OP1 OP0', file = fp)
    for i in range(len(microps)):
        key = '   '.join(('{0:0%db}' % ROM_BITS).format(i))
        val = '   '.join('1' if microps[i] & (1 << v) else '0' for v in range(OUT_BITS - 1, -1, -1))
        print('    %s   |  %s' % (key, val), file = fp)

fpath = os.path.abspath(__file__)
fname = os.path.join(os.path.dirname(fpath), '../../Tools/LogicGen/logen.py')

subprocess.call([
    fname,
    os.path.join(os.path.dirname(fpath), 'arith.logic')
])
