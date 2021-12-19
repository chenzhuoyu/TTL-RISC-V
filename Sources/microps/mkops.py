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

REG_WE      = 1 << 5
PCREL       = 1 << 6
OPIMM       = 1 << 7
BRANCH      = 1 << 8
LINK        = 1 << 9
LDSX        = 1 << 10
LD0         = 1 << 11
LD1         = 1 << 12
ST0         = 1 << 13
ST1         = 1 << 14
CSR_EN      = 1 << 15
CSR_IMM     = 1 << 16
CSR_BIT     = 1 << 17
CSR_CLR     = 1 << 18
SHIFT       = 1 << 19
FUNCT       = 1 << 20
SYSTEM      = 1 << 21
HOLD        = 1 << 22
SIGILL      = 1 << 23

X        = -1
XXXXX    = -1

OUT_BITS = 24
ROM_SIZE = 1 << 11

bits = 0
microps = [
    SIGILL
    for _ in range(ROM_SIZE)
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
                            cc = (i << 10) | (j << 9) | (k << 8) | (v << 5) | op
                            if mop != SIGILL and not (microps[cc] & SIGILL):
                                raise ValueError('%s: instruction was already assigned: %08x == %05x' % (name, cc, microps[cc]))
                            else:
                                microps[cc] = mop

#  name       s  c  f  f3     op       mop
OP('LUI'    , 0, X, X, XXXXX, 0b01101, ALU_ADD | REG_WE | OPIMM)
OP('AUIPC'  , 0, X, X, XXXXX, 0b00101, ALU_ADD | REG_WE | PCREL | OPIMM)
OP('JAL'    , 0, X, X, XXXXX, 0b11011, ALU_ADD | REG_WE | PCREL | OPIMM | BRANCH | LINK | HOLD)
OP('JAL'    , 1, X, X, XXXXX, 0b11011, 0)
OP('JALR'   , 0, X, X, 0b000, 0b11001, ALU_ADD | REG_WE | OPIMM | BRANCH | LINK | HOLD)
OP('JALR'   , 1, X, X, 0b000, 0b11001, 0)
OP('Bcc'    , 0, 0, X, XXXXX, 0b11000, 0)
OP('Bcc'    , 0, 1, X, XXXXX, 0b11000, PCREL | OPIMM | BRANCH | HOLD)
OP('Bcc'    , 1, X, X, XXXXX, 0b11000, 0)
OP('Bcc'    , X, X, X, 0b010, 0b11000, SIGILL)
OP('Bcc'    , X, X, X, 0b011, 0b11000, SIGILL)
OP('LB'     , 0, X, X, 0b000, 0b00000, ALU_ADD | REG_WE | OPIMM | LDSX | LD0 | HOLD)
OP('LB'     , 1, X, X, 0b000, 0b00000, 0)
OP('LH'     , 0, X, X, 0b001, 0b00000, ALU_ADD | REG_WE | OPIMM | LDSX | LD1 | HOLD)
OP('LH'     , 1, X, X, 0b001, 0b00000, 0)
OP('LW'     , 0, X, X, 0b010, 0b00000, ALU_ADD | REG_WE | OPIMM | LD0 | LD1 | HOLD)
OP('LW'     , 1, X, X, 0b010, 0b00000, 0)
OP('LBU'    , 0, X, X, 0b100, 0b00000, ALU_ADD | REG_WE | OPIMM | LD0 | HOLD)
OP('LBU'    , 1, X, X, 0b100, 0b00000, 0)
OP('LHU'    , 0, X, X, 0b101, 0b00000, ALU_ADD | REG_WE | OPIMM | LD1 | HOLD)
OP('LHU'    , 1, X, X, 0b101, 0b00000, 0)
OP('SB'     , 0, X, X, 0b000, 0b01000, ALU_ADD | OPIMM | ST0 | HOLD)
OP('SB'     , 1, X, X, 0b000, 0b01000, 0)
OP('SH'     , 0, X, X, 0b001, 0b01000, ALU_ADD | OPIMM | ST1 | HOLD)
OP('SH'     , 1, X, X, 0b001, 0b01000, 0)
OP('SW'     , 0, X, X, 0b010, 0b01000, ALU_ADD | OPIMM | ST0 | ST1 | HOLD)
OP('SW'     , 1, X, X, 0b010, 0b01000, 0)
OP('ADDI'   , 0, X, X, 0b000, 0b00100, ALU_ADD  | REG_WE | OPIMM)
OP('SLTI'   , 0, X, X, 0b010, 0b00100, ALU_SLT  | REG_WE | OPIMM)
OP('SLTIU'  , 0, X, X, 0b011, 0b00100, ALU_SLTU | REG_WE | OPIMM)
OP('XORI'   , 0, X, X, 0b100, 0b00100, ALU_XOR  | REG_WE | OPIMM)
OP('ORI'    , 0, X, X, 0b110, 0b00100, ALU_OR   | REG_WE | OPIMM)
OP('ANDI'   , 0, X, X, 0b111, 0b00100, ALU_AND  | REG_WE | OPIMM)
OP('SLLI'   , 0, 0, 0, 0b001, 0b00100, ALU_SHL  | REG_WE | OPIMM | SHIFT | FUNCT)
OP('SRLI'   , 0, 0, 0, 0b101, 0b00100, ALU_SHR  | REG_WE | OPIMM | SHIFT | FUNCT)
OP('SRAI'   , 0, 1, 0, 0b101, 0b00100, ALU_SAR  | REG_WE | OPIMM | SHIFT | FUNCT)
OP('ADD'    , 0, 0, 0, 0b000, 0b01100, ALU_ADD  | REG_WE | FUNCT)
OP('SUB'    , 0, 1, 0, 0b000, 0b01100, ALU_SUB  | REG_WE | FUNCT)
OP('SLL'    , 0, 0, 0, 0b001, 0b01100, ALU_SHL  | REG_WE | SHIFT | FUNCT)
OP('SLT'    , 0, 0, 0, 0b010, 0b01100, ALU_SLT  | REG_WE | FUNCT)
OP('SLTU'   , 0, 0, 0, 0b011, 0b01100, ALU_SLTU | REG_WE | FUNCT)
OP('XOR'    , 0, 0, 0, 0b100, 0b01100, ALU_XOR  | REG_WE | FUNCT)
OP('SRL'    , 0, 0, 0, 0b101, 0b01100, ALU_SHR  | REG_WE | SHIFT | FUNCT)
OP('SRA'    , 0, 1, 0, 0b101, 0b01100, ALU_SAR  | REG_WE | SHIFT | FUNCT)
OP('OR'     , 0, 0, 0, 0b110, 0b01100, ALU_OR   | REG_WE | FUNCT)
OP('AND'    , 0, 0, 0, 0b111, 0b01100, ALU_AND  | REG_WE | FUNCT)
OP('FENCE'  , 0, X, X, 0b000, 0b00011, 0)
OP('FENCE.I', 0, X, X, 0b001, 0b00011, 0)
OP('SYSTEM' , 0, 0, X, 0b000, 0b11100, FUNCT | SYSTEM)

OP('MUL'    , 0, 0, 1, 0b000, 0b01100, ALU_MUL    | REG_WE | FUNCT)
OP('MULH'   , 0, 0, 1, 0b001, 0b01100, ALU_MULH   | REG_WE | FUNCT)
OP('MULHU'  , 0, 0, 1, 0b011, 0b01100, ALU_MULHU  | REG_WE | FUNCT)
OP('MULHSU' , 0, 0, 1, 0b010, 0b01100, ALU_MULHSU | REG_WE | FUNCT)
OP('DIV'    , 0, 0, 1, 0b100, 0b01100, ALU_DIV    | REG_WE | FUNCT)
OP('DIVU'   , 0, 0, 1, 0b101, 0b01100, ALU_DIVU   | REG_WE | FUNCT)
OP('REM'    , 0, 0, 1, 0b110, 0b01100, ALU_REM    | REG_WE | FUNCT)
OP('REMU'   , 0, 0, 1, 0b111, 0b01100, ALU_REMU   | REG_WE | FUNCT)

OP('CSRRW'  , 0, X, X, 0b001, 0b11100, 0)
OP('CSRRS'  , 0, X, X, 0b010, 0b11100, 0)
OP('CSRRC'  , 0, X, X, 0b011, 0b11100, 0)
OP('CSRRWI' , 0, X, X, 0b101, 0b11100, 0)
OP('CSRRSI' , 0, X, X, 0b110, 0b11100, 0)
OP('CSRRCI' , 0, X, X, 0b111, 0b11100, 0)

for v in microps:
    bits <<= OUT_BITS
    bits |= 0 if v == SIGILL else v ^ SHIFT

with open('microps-logisim.bin', 'wb') as fp:
    fp.write(bits.to_bytes(ROM_SIZE * OUT_BITS // 8, 'big'))
