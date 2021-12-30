#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import struct

INIT = [
    0xc01ff06f,     # jal     x0, -1024
]

INSTR = [
    0x000012b7,     # lui     x5, 0x1
    0x80028293,     # addi    x5, x5, -2048
    0x3042a073,     # csrrs   x0, mie, x5
    0x0800c137,     # lui     x2, 0x800c
    0xfffc0337,     # lui     x6, 0xfffc0
    0x34131073,     # csrrw   x0, mepc, x6
    0x08800393,     # addi    x7, x0, 136
    0x3003a073,     # csrrs   x0, mstatus, x7
    0x30200073,     # mret
]

with open(sys.argv[1], 'rb') as fp:
    buf = bytearray(fp.read())

buf.extend(0 for _ in range(65536 * 4 - len(buf)))
struct.pack_into('=' + 'I' * len(INIT), buf, 0xfffc * 4, *INIT)
struct.pack_into('=' + 'I' * len(INSTR), buf, 0xfefc * 4, *INSTR)

with open(sys.argv[1], 'wb') as fp:
    fp.write(buf)
