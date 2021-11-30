#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# import os
# import subprocess

PCREL     = 1 << 0
OPIMM     = 1 << 1
SHIFT     = 1 << 7
CSR       = 1 << 8
CSRI      = 1 << 9
CSRBIT    = 1 << 10
CSRCLR    = 1 << 11
SIGILL    = 1 << 12

ALU_ADD    = 0 << 2
ALU_SUB    = 1 << 2
ALU_MUL    = 2 << 2
ALU_MULH   = 3 << 2
ALU_MULHU  = 4 << 2
ALU_MULHSU = 5 << 2
ALU_DIV    = 6 << 2
ALU_DIVU   = 7 << 2
ALU_REM    = 8 << 2
ALU_REMU   = 9 << 2
ALU_OR     = 10 << 2
ALU_AND    = 11 << 2
ALU_XOR    = 12 << 2
ALU_SHL    = 13 << 2
ALU_SHR    = 14 << 2
ALU_SAR    = 15 << 2
ALU_SLT    = 16 << 2
ALU_SLTU   = 17 << 2

X        = -1
XXXXX    = -1
CTL_BITS = 13
ROM_SIZE = 1 << 10

bits = 0
microps = [SIGILL for _ in range(ROM_SIZE)]

def OP(name: str, f: int, g: int, f3: int, op: int, ctl: int):
    for i in range(2):
        for j in range(2):
            for k in range(8):
                if f in (i, X) and g in (j, X) and f3 in (k, XXXXX):
                    cc = (i << 9) | (j << 8) | (k << 5) | op
                    if microps[cc] != SIGILL:
                        raise ValueError('{0}: instruction was already assigned: {1:010b} == {2:014b}'.format(name, cc, microps[cc]))
                    else:
                        microps[cc] = ctl

#  name       f  g  f3     op       ctl
OP('LUI'    , X, X, XXXXX, 0b01101, OPIMM | ALU_ADD)
OP('AUIPC'  , X, X, XXXXX, 0b00101, PCREL | OPIMM | ALU_ADD)
OP('JAL'    , X, X, XXXXX, 0b11011, PCREL | OPIMM | ALU_ADD)
OP('JALR'   , X, X, 0b000, 0b11001, OPIMM | ALU_ADD)
OP('BEQ'    , X, X, 0b000, 0b11000, PCREL | OPIMM | ALU_ADD)
OP('BNE'    , X, X, 0b001, 0b11000, PCREL | OPIMM | ALU_ADD)
OP('BLT'    , X, X, 0b100, 0b11000, PCREL | OPIMM | ALU_ADD)
OP('BGE'    , X, X, 0b101, 0b11000, PCREL | OPIMM | ALU_ADD)
OP('BLTU'   , X, X, 0b110, 0b11000, PCREL | OPIMM | ALU_ADD)
OP('BGEU'   , X, X, 0b111, 0b11000, PCREL | OPIMM | ALU_ADD)
OP('LB'     , X, X, 0b000, 0b00000, OPIMM | ALU_ADD)
OP('LH'     , X, X, 0b001, 0b00000, OPIMM | ALU_ADD)
OP('LW'     , X, X, 0b010, 0b00000, OPIMM | ALU_ADD)
OP('LBU'    , X, X, 0b100, 0b00000, OPIMM | ALU_ADD)
OP('LHU'    , X, X, 0b101, 0b00000, OPIMM | ALU_ADD)
OP('SB'     , X, X, 0b000, 0b01000, OPIMM | ALU_ADD)
OP('SH'     , X, X, 0b001, 0b01000, OPIMM | ALU_ADD)
OP('SW'     , X, X, 0b010, 0b01000, OPIMM | ALU_ADD)
OP('ADDI'   , X, X, 0b000, 0b00100, OPIMM | ALU_ADD)
OP('SLTI'   , X, X, 0b010, 0b00100, OPIMM | ALU_SLT)
OP('SLTIU'  , X, X, 0b011, 0b00100, OPIMM | ALU_SLTU)
OP('XORI'   , X, X, 0b100, 0b00100, OPIMM | ALU_XOR)
OP('ORI'    , X, X, 0b110, 0b00100, OPIMM | ALU_OR)
OP('ANDI'   , X, X, 0b111, 0b00100, OPIMM | ALU_AND)
OP('SLLI'   , 0, 0, 0b001, 0b00100, OPIMM | ALU_SHL | SHIFT)
OP('SRLI'   , 0, 0, 0b101, 0b00100, OPIMM | ALU_SHR | SHIFT)
OP('SRAI'   , 1, 0, 0b101, 0b00100, OPIMM | ALU_SAR | SHIFT)
OP('ADD'    , 0, 0, 0b000, 0b01100, ALU_ADD)
OP('SUB'    , 1, 0, 0b000, 0b01100, ALU_SUB)
OP('SLL'    , 0, 0, 0b001, 0b01100, ALU_SHL)
OP('SLT'    , 0, 0, 0b010, 0b01100, ALU_SLT)
OP('SLTU'   , 0, 0, 0b011, 0b01100, ALU_SLTU)
OP('XOR'    , 0, 0, 0b100, 0b01100, ALU_XOR)
OP('SRL'    , 0, 0, 0b101, 0b01100, ALU_SHR)
OP('SRA'    , 1, 0, 0b101, 0b01100, ALU_SAR)
OP('OR'     , 0, 0, 0b110, 0b01100, ALU_OR)
OP('AND'    , 0, 0, 0b111, 0b01100, ALU_AND)
OP('FENCE'  , X, X, 0b000, 0b00011, 0)
OP('FENCE.I', X, X, 0b001, 0b00011, 0)
OP('SYSTEM' , X, X, 0b000, 0b11100, 0)

OP('MUL'    , 0, 1, 0b000, 0b01100, ALU_MUL)
OP('MULH'   , 0, 1, 0b001, 0b01100, ALU_MULH)
OP('MULHU'  , 0, 1, 0b011, 0b01100, ALU_MULHU)
OP('MULHSU' , 0, 1, 0b010, 0b01100, ALU_MULHSU)
OP('DIV'    , 0, 1, 0b100, 0b01100, ALU_DIV)
OP('DIVU'   , 0, 1, 0b101, 0b01100, ALU_DIVU)
OP('REM'    , 0, 1, 0b110, 0b01100, ALU_REM)
OP('REMU'   , 0, 1, 0b111, 0b01100, ALU_REMU)

OP('CSRRW'  , X, X, 0b001, 0b11100, CSR)
OP('CSRRS'  , X, X, 0b010, 0b11100, CSR | CSRBIT)
OP('CSRRC'  , X, X, 0b011, 0b11100, CSR | CSRBIT | CSRCLR)
OP('CSRRWI' , X, X, 0b101, 0b11100, CSR | CSRI | OPIMM)
OP('CSRRSI' , X, X, 0b110, 0b11100, CSR | CSRI | OPIMM | CSRBIT)
OP('CSRRCI' , X, X, 0b111, 0b11100, CSR | CSRI | OPIMM | CSRBIT | CSRCLR)

for v in microps:
    bits <<= CTL_BITS
    bits |= v ^ SHIFT

with open('insdec-logisim.bin', 'wb') as fp:
    fp.write(bits.to_bytes(ROM_SIZE * CTL_BITS // 8, 'big'))

# with open('insdec.logic', 'w') as fp:
#     print('Instruction decoder.', file = fp)
#     print(file = fp)
#     print('device:', file = fp)
#     print('    GAL22V10', file = fp)
#     print(file = fp)
#     print('pins:', file = fp)
#     print('    GND P30 P25 P14 P13 P12 P6  P5  P4  P3  P2  _', file = fp)
#     print('    _   PCR OPI SLT SLU OP0 OP1 OP2 OP3 SHX _   VCC', file = fp)
#     print(file = fp)
#     print('table:', file = fp)
#     print('    P30 P25 P14 P13 P12 P6  P5  P4  P3  P2  |  PCR OPI SLT SLU OP0 OP1 OP2 OP3 SHX', file = fp)
#     for i in range(ROM_SIZE):
#         key = '   '.join('{0:010b}'.format(i))
#         val = '   '.join('1' if microps[i] & (1 << v) else '0' for v in range(9))
#         print('    %s   |  %s' % (key, val), file = fp)

# fname = os.path.abspath(__file__)
# fname = os.path.join(os.path.dirname(fname), '../../Tools/LogicGen/logen.py')

# subprocess.call([
#     fname,
#     './insdec.logic'
# ])
