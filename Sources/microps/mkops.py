#!/usr/bin/env python3
# -*- coding: utf-8 -8-

ALU_ADD    = 0
ALU_SUB    = 1
ALU_MUL    = 2
ALU_MULH   = 3
ALU_MULHU  = 4
ALU_MULHSU = 5
ALU_DIV    = 6
ALU_DIVU   = 7
ALU_REM    = 8
ALU_REMU   = 9
ALU_OR     = 10
ALU_AND    = 11
ALU_XOR    = 12
ALU_SHL    = 13
ALU_SHR    = 14
ALU_SAR    = 15
ALU_SLT    = 16
ALU_SLTU   = 17

SHIFT       = 1 << 5
REG_WE      = 1 << 6
PCREL       = 1 << 7
OPIMM       = 1 << 8
BRANCH      = 1 << 9
LINK        = 1 << 10
LDSX        = 1 << 11
LD0         = 1 << 12
LD1         = 1 << 13
ST0         = 1 << 14
ST1         = 1 << 15
CSR_EN      = 1 << 16
CSR_IMM     = 1 << 17
CSR_BIT     = 1 << 18
CSR_CLR     = 1 << 19
STE         = 1 << 20
SIGILL      = 1 << 21

X        = -1
XXXXX    = -1

OUT_BITS = 22
ROM_SIZE = 1 << 11

bits = 0
microps = [
    SIGILL
    for _ in range(ROM_SIZE)
]

def OP(name: str, s: int, c: int, f: int, f3: int, op: int, mop: int):
    if s & ~0b1:
        raise ValueError(name + ': s must be a 1-bit value')
    elif op & ~0b11111:
        raise ValueError(name + ': op must be a 5-bit value')
    elif c != X and (c & ~0b1):
        raise ValueError(name + ': c must be a 1-bit value or X')
    elif f != X and (f & ~0b1):
        raise ValueError(name + ': f must be a 1-bit value or X')
    elif f3 != XXXXX and (f3 & ~0b111):
        raise ValueError(name + ': f3 must be a 3-bit value or XXXXX')
    else:
        for i in range(2):
            for j in range(2):
                for k in range(8):
                    if c in (i, X) and f in (j, X) and f3 in (k, XXXXX):
                        cc = (s << 10) | (i << 9) | (j << 8) | (k << 5) | op
                        if not (microps[cc] & SIGILL):
                            raise ValueError('%s: instruction was already assigned: %08x == %05x' % (name, cc, microps[cc]))
                        else:
                            microps[cc] = mop

#  name       s  c  f  f3     op       mop
OP('LUI'    , 0, X, X, XXXXX, 0b01101, ALU_ADD | REG_WE | OPIMM)
OP('AUIPC'  , 0, X, X, XXXXX, 0b00101, ALU_ADD | REG_WE | PCREL | OPIMM)
OP('JAL'    , 0, X, X, XXXXX, 0b11011, 0)
OP('JALR'   , 0, X, X, 0b000, 0b11001, 0)
OP('BEQ'    , 0, X, X, 0b000, 0b11000, 0)
OP('BNE'    , 0, X, X, 0b001, 0b11000, 0)
OP('BLT'    , 0, X, X, 0b100, 0b11000, 0)
OP('BGE'    , 0, X, X, 0b101, 0b11000, 0)
OP('BLTU'   , 0, X, X, 0b110, 0b11000, 0)
OP('BGEU'   , 0, X, X, 0b111, 0b11000, 0)
OP('LB'     , 0, X, X, 0b000, 0b00000, 0)
OP('LH'     , 0, X, X, 0b001, 0b00000, 0)
OP('LW'     , 0, X, X, 0b010, 0b00000, 0)
OP('LBU'    , 0, X, X, 0b100, 0b00000, 0)
OP('LHU'    , 0, X, X, 0b101, 0b00000, 0)
OP('SB'     , 0, X, X, 0b000, 0b01000, 0)
OP('SH'     , 0, X, X, 0b001, 0b01000, 0)
OP('SW'     , 0, X, X, 0b010, 0b01000, 0)
OP('ADDI'   , 0, X, X, 0b000, 0b00100, ALU_ADD  | REG_WE | OPIMM)
OP('SLTI'   , 0, X, X, 0b010, 0b00100, ALU_SLT  | REG_WE | OPIMM)
OP('SLTIU'  , 0, X, X, 0b011, 0b00100, ALU_SLTU | REG_WE | OPIMM)
OP('XORI'   , 0, X, X, 0b100, 0b00100, ALU_XOR  | REG_WE | OPIMM)
OP('ORI'    , 0, X, X, 0b110, 0b00100, ALU_OR   | REG_WE | OPIMM)
OP('ANDI'   , 0, X, X, 0b111, 0b00100, ALU_AND  | REG_WE | OPIMM)
OP('SLLI'   , 0, 0, 0, 0b001, 0b00100, ALU_SHL  | REG_WE | OPIMM | SHIFT)
OP('SRLI'   , 0, 0, 0, 0b101, 0b00100, ALU_SHR  | REG_WE | OPIMM | SHIFT)
OP('SRAI'   , 0, 1, 0, 0b101, 0b00100, ALU_SAR  | REG_WE | OPIMM | SHIFT)
OP('ADD'    , 0, 0, 0, 0b000, 0b01100, ALU_ADD  | REG_WE)
OP('SUB'    , 0, 1, 0, 0b000, 0b01100, ALU_SUB  | REG_WE)
OP('SLL'    , 0, 0, 0, 0b001, 0b01100, ALU_SHL  | REG_WE | SHIFT)
OP('SLT'    , 0, 0, 0, 0b010, 0b01100, ALU_SLT  | REG_WE)
OP('SLTU'   , 0, 0, 0, 0b011, 0b01100, ALU_SLTU | REG_WE)
OP('XOR'    , 0, 0, 0, 0b100, 0b01100, ALU_XOR  | REG_WE)
OP('SRL'    , 0, 0, 0, 0b101, 0b01100, ALU_SHR  | REG_WE | SHIFT)
OP('SRA'    , 0, 1, 0, 0b101, 0b01100, ALU_SAR  | REG_WE | SHIFT)
OP('OR'     , 0, 0, 0, 0b110, 0b01100, ALU_OR   | REG_WE)
OP('AND'    , 0, 0, 0, 0b111, 0b01100, ALU_AND  | REG_WE)
OP('FENCE'  , 0, X, X, 0b000, 0b00011, 0)
OP('FENCE.I', 0, X, X, 0b001, 0b00011, 0)
OP('SYSTEM' , 0, X, X, 0b000, 0b11100, 0)

OP('MUL'    , 0, 0, 1, 0b000, 0b01100, ALU_MUL    | REG_WE)
OP('MULH'   , 0, 0, 1, 0b001, 0b01100, ALU_MULH   | REG_WE)
OP('MULHU'  , 0, 0, 1, 0b011, 0b01100, ALU_MULHU  | REG_WE)
OP('MULHSU' , 0, 0, 1, 0b010, 0b01100, ALU_MULHSU | REG_WE)
OP('DIV'    , 0, 0, 1, 0b100, 0b01100, ALU_DIV    | REG_WE)
OP('DIVU'   , 0, 0, 1, 0b101, 0b01100, ALU_DIVU   | REG_WE)
OP('REM'    , 0, 0, 1, 0b110, 0b01100, ALU_REM    | REG_WE)
OP('REMU'   , 0, 0, 1, 0b111, 0b01100, ALU_REMU   | REG_WE)

OP('CSRRW'  , 0, X, X, 0b001, 0b11100, 0)
OP('CSRRS'  , 0, X, X, 0b010, 0b11100, 0)
OP('CSRRC'  , 0, X, X, 0b011, 0b11100, 0)
OP('CSRRWI' , 0, X, X, 0b101, 0b11100, 0)
OP('CSRRSI' , 0, X, X, 0b110, 0b11100, 0)
OP('CSRRCI' , 0, X, X, 0b111, 0b11100, 0)

for v in microps:
    bits <<= OUT_BITS
    bits |= v ^ SHIFT

with open('microps-logisim.bin', 'wb') as fp:
    fp.write(bits.to_bytes(ROM_SIZE * OUT_BITS // 8, 'big'))
