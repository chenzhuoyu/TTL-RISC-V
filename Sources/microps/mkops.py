#!/usr/bin/env python3
# -*- coding: utf-8 -8-

STEP        = 1 << 0
JMP         = 1 << 1
PCREL       = 1 << 2
OPIMM       = 1 << 3
REG_WE      = 1 << 4
LINK        = 1 << 5
SLT         = 1 << 6
SLTU        = 1 << 7
LDSX        = 1 << 8

LOADB       = 1 << 9
LOADH       = 2 << 9
LOADW       = 3 << 9

STOREB      = 1 << 11
STOREH      = 2 << 11
STOREW      = 3 << 11

ALU_ADD     = 0 << 13
ALU_SUB     = 1 << 13
ALU_SMULL   = 2 << 13
ALU_SMULH   = 3 << 13
ALU_UMULL   = 4 << 13
ALU_UMULH   = 5 << 13
ALU_SDIV    = 6 << 13
ALU_SREM    = 7 << 13
ALU_UDIV    = 8 << 13
ALU_UREM    = 9 << 13
ALU_OR      = 10 << 13
ALU_AND     = 11 << 13
ALU_XOR     = 12 << 13
ALU_SHL     = 13 << 13
ALU_SHR     = 14 << 13
ALU_SAR     = 15 << 13

FUNCT       = 1 << 17
SHIFT       = 1 << 18
SYSTEM      = 1 << 19
SIGILL      = 1 << 20

X        = -1
CTL_BITS = 21
ROM_SIZE = 1 << 12

bits = 0
microps = [
    STEP | SIGILL
    for _ in range(ROM_SIZE)
]

def OP(name: str, s: int, c: int, f: int, f3: int, op: int, mop: int):
    if s & ~0b11:
        raise ValueError(name + ': s must be a 2-bit value')
    elif f3 & ~0b111:
        raise ValueError(name + ': f3 must be a 3-bit value')
    elif op & ~0b11111:
        raise ValueError(name + ': op must be a 5-bit value')
    elif c != X and (c & ~0b1):
        raise ValueError(name + ': c must be a 1-bit value or X')
    elif f != X and (f & ~0b1):
        raise ValueError(name + ': f must be a 1-bit value or X')
    else:
        for i in range(2):
            for j in range(2):
                if c in (i, X) and f in (j, X):
                    cc = (s << 10) | (i << 9) | (j << 8) | (f3 << 5) | op
                    if not (microps[cc] & SIGILL):
                        raise ValueError('%s: instruction was already assigned: %08x == %05x' % (name, cc, microps[cc]))
                    else:
                        microps[cc] = mop

#  name       s  c  f  f3     op       mop
OP('LUI'    , 0, X, X, 0b000, 0b01101, STEP | OPIMM | REG_WE)
OP('AUIPC'  , 0, X, X, 0b000, 0b00101, STEP | PCREL | REG_WE)
OP('JAL'    , 0, X, X, 0b000, 0b11011, JMP | PCREL | OPIMM | REG_WE | LINK)
OP('JAL'    , 1, X, X, 0b000, 0b11011, STEP)
OP('JALR'   , 0, X, X, 0b000, 0b11001, JMP | OPIMM | REG_WE | LINK)
OP('JALR'   , 1, X, X, 0b000, 0b11001, STEP)
OP('BEQ'    , 0, X, X, 0b000, 0b11000, 0)
OP('BEQ'    , 1, 0, X, 0b000, 0b11000, STEP)
OP('BEQ'    , 1, 1, X, 0b000, 0b11000, JMP | PCREL | OPIMM)
OP('BEQ'    , 2, X, X, 0b000, 0b11000, STEP)
OP('BNE'    , 0, X, X, 0b001, 0b11000, 0)
OP('BNE'    , 1, 0, X, 0b001, 0b11000, STEP)
OP('BNE'    , 1, 1, X, 0b001, 0b11000, JMP | PCREL | OPIMM)
OP('BNE'    , 2, X, X, 0b001, 0b11000, STEP)
OP('BLT'    , 0, X, X, 0b100, 0b11000, 0)
OP('BLT'    , 1, 0, X, 0b100, 0b11000, STEP)
OP('BLT'    , 1, 1, X, 0b100, 0b11000, JMP | PCREL | OPIMM)
OP('BLT'    , 2, X, X, 0b100, 0b11000, STEP)
OP('BGE'    , 0, X, X, 0b101, 0b11000, 0)
OP('BGE'    , 1, 0, X, 0b101, 0b11000, STEP)
OP('BGE'    , 1, 1, X, 0b101, 0b11000, JMP | PCREL | OPIMM)
OP('BGE'    , 2, X, X, 0b101, 0b11000, STEP)
OP('BLTU'   , 0, X, X, 0b110, 0b11000, 0)
OP('BLTU'   , 1, 0, X, 0b110, 0b11000, STEP)
OP('BLTU'   , 1, 1, X, 0b110, 0b11000, JMP | PCREL | OPIMM)
OP('BLTU'   , 2, X, X, 0b110, 0b11000, STEP)
OP('BGEU'   , 0, X, X, 0b111, 0b11000, 0)
OP('BGEU'   , 1, 0, X, 0b111, 0b11000, STEP)
OP('BGEU'   , 1, 1, X, 0b111, 0b11000, JMP | PCREL | OPIMM)
OP('BGEU'   , 2, X, X, 0b111, 0b11000, STEP)
OP('LB'     , 0, X, X, 0b000, 0b00000, STEP | REG_WE | LDSX | LOADB)
OP('LH'     , 0, X, X, 0b001, 0b00000, STEP | REG_WE | LDSX | LOADH)
OP('LW'     , 0, X, X, 0b010, 0b00000, STEP | REG_WE | LOADW)
OP('LBU'    , 0, X, X, 0b100, 0b00000, STEP | REG_WE | LOADB)
OP('LHU'    , 0, X, X, 0b101, 0b00000, STEP | REG_WE | LOADH)
OP('SB'     , 0, X, X, 0b000, 0b01000, STEP | OPIMM | STOREB)
OP('SH'     , 0, X, X, 0b001, 0b01000, STEP | OPIMM | STOREH)
OP('SW'     , 0, X, X, 0b010, 0b01000, STEP | OPIMM | STOREW)
OP('ADDI'   , 0, X, X, 0b000, 0b00100, STEP | OPIMM | REG_WE | ALU_ADD)
OP('SLTI'   , 0, X, X, 0b010, 0b00100, STEP | OPIMM | REG_WE | SLT)
OP('SLTIU'  , 0, X, X, 0b011, 0b00100, STEP | OPIMM | REG_WE | SLT | SLTU)
OP('XORI'   , 0, X, X, 0b100, 0b00100, STEP | OPIMM | REG_WE | ALU_XOR)
OP('ORI'    , 0, X, X, 0b110, 0b00100, STEP | OPIMM | REG_WE | ALU_OR)
OP('ANDI'   , 0, X, X, 0b111, 0b00100, STEP | OPIMM | REG_WE | ALU_AND)
OP('SLLI'   , 0, X, 0, 0b001, 0b00100, STEP | OPIMM | REG_WE | ALU_SHL | FUNCT | SHIFT)
OP('SRLI'   , 0, X, 0, 0b101, 0b00100, STEP | OPIMM | REG_WE | ALU_SHR | FUNCT | SHIFT)
OP('SRAI'   , 0, X, 1, 0b101, 0b00100, STEP | OPIMM | REG_WE | ALU_SAR | FUNCT | SHIFT)
OP('ADD'    , 0, X, 0, 0b000, 0b01100, STEP | REG_WE | ALU_ADD    | FUNCT)
OP('SUB'    , 0, X, 1, 0b000, 0b01100, STEP | REG_WE | ALU_SUB    | FUNCT)
OP('SLL'    , 0, X, 0, 0b001, 0b01100, STEP | REG_WE | ALU_SHL    | FUNCT)
OP('SLT'    , 0, X, 0, 0b010, 0b01100, STEP | REG_WE | SLT        | FUNCT)
OP('SLTU'   , 0, X, 0, 0b011, 0b01100, STEP | REG_WE | SLT | SLTU | FUNCT)
OP('XOR'    , 0, X, 0, 0b100, 0b01100, STEP | REG_WE | ALU_XOR    | FUNCT)
OP('SRL'    , 0, X, 0, 0b101, 0b01100, STEP | REG_WE | ALU_SHR    | FUNCT)
OP('SRA'    , 0, X, 1, 0b101, 0b01100, STEP | REG_WE | ALU_SAR    | FUNCT)
OP('OR'     , 0, X, 0, 0b110, 0b01100, STEP | REG_WE | ALU_OR     | FUNCT)
OP('AND'    , 0, X, 0, 0b111, 0b01100, STEP | REG_WE | ALU_AND    | FUNCT)
OP('FENCE'  , 0, X, X, 0b000, 0b00011, STEP)
OP('SYSTEM' , 0, X, 0, 0b000, 0b11100, STEP | FUNCT | SYSTEM)

for v in microps:
    bits <<= CTL_BITS
    bits |= v ^ SHIFT

with open('microps-logisim.bin', 'wb') as fp:
    fp.write(bits.to_bytes(ROM_SIZE * CTL_BITS // 8, 'big'))
