#!/usr/bin/env python3
# -*- coding: utf-8 -*-

MVENDORID = 1
MARCHID   = 2
MIMPID    = 3
MHARTID   = 4
MISA      = 5
MIE       = 6
MTVEC     = 7
MSCRATCH  = 8
MEPC      = 9
MCAUSE    = 10
SIGILL    = 1 << 4

R         = 1
W         = 2
CSR_BITS  = 5
CSR_SIZE  = 1 << 13

bits = 0
csrid = [
    SIGILL
    for _ in range(CSR_SIZE)
]

def OP(name: str, addr: int, reg: int, rw: int):
    for i in (0, 1):
        if rw & (1 << i):
            p = (i << 12) | addr
            if csrid[p] != SIGILL:
                raise ValueError('{0}: CSR was already assigned: {1:013b} == {2:05b}'.format(name, p, csrid[p]))
            else:
                csrid[p] = reg

OP('mvendorid' , 0xf11, MVENDORID , R)     # hw: 0x43685a59 (ChZY)
OP('marchid'   , 0xf12, MARCHID   , R)     # hw: 0x00001000
OP('mimpid'    , 0xf13, MIMPID    , R)     # hw: 0x00000001
OP('mhartid'   , 0xf14, MHARTID   , R)     # hw: 0x00000000
OP('misa'      , 0x301, MISA      , R | W) # ro: 0x40001100 (RV32IM)
OP('mie'       , 0x304, MIE       , R | W) # rw: 0x00000000 (bit 3, 11)
OP('mtvec'     , 0x305, MTVEC     , R | W) # ro: 0xfffffff0
OP('mscratch'  , 0x340, MSCRATCH  , R | W) # rw: 0x00000000
OP('mepc'      , 0x341, MEPC      , R | W) # rw: 0x00000000
OP('mcause'    , 0x342, MCAUSE    , R | W) # ro: 0x00000000

for v in csrid:
    bits <<= CSR_BITS
    bits |= v

with open('csrid-logisim.bin', 'wb') as fp:
    fp.write(bits.to_bytes(CSR_SIZE * CSR_BITS // 8, 'big'))
