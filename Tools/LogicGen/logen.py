#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Generates PLD functions from Truth-table for GAL devices """

import io
import os
import sys
import json

from sympy import core
from sympy import logic

from typing import List
from typing import Tuple
from typing import TextIO

from sympy.logic.boolalg import Or
from sympy.logic.boolalg import And
from sympy.logic.boolalg import Not

from sympy.core.symbol import Symbol
from sympy.logic.boolalg import BooleanFunction

class Device:
    kind: str
    pins: str

    def __init__(self, kind: str, pins: str) -> None:
        self.kind = kind
        self.pins = pins

    @staticmethod
    def load_devices() -> dict:
        with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'devices.json')) as fp:
            return json.load(fp)

DEVICES = {
    name: Device(dev['type'], dev['pins'])
    for name, dev in Device.load_devices().items()
}

def readline(ifp: TextIO) -> str:
    while True:
        buf = ifp.readline()
        if not buf:
            raise EOFError()
        src = buf.strip()
        if src and src[0] != '#':
            return src

def dump_dnf(dnf: BooleanFunction) -> str:
    if isinstance(dnf, Not):
        return '/' + dump_dnf(dnf.args[0])
    elif isinstance(dnf, Or):
        return ' + '.join(dump_dnf(v) for v in dnf.args)
    elif isinstance(dnf, And):
        return ' * '.join(dump_dnf(v) for v in dnf.args)
    else:
        return str(dnf)

def split_logic(line: str) -> Tuple[List[str], List[str]]:
    try:
        i = line.index('|')
    except ValueError:
        raise SyntaxError('no output variables in truth table') from None
    else:
        return line[:i], line[i + 1:]

def format_table(data: List[List[str]]) -> Tuple[List[int], List[str]]:
    wl = list(map(max, zip(*([len(v) for v in x] for x in data))))
    return wl, list('  '.join(v.ljust(n, ' ') for v, n in zip(x, wl)).strip() for x in data)

def generate_from(ifp: TextIO, ofp: TextIO):
    desc = []
    line = readline(ifp)
    while line != 'device:':
        desc.append(line)
        line = readline(ifp)
    if line != 'device:':
        raise SyntaxError('missing device declaration')
    dev = readline(ifp).upper()
    if dev not in DEVICES:
        raise SyntaxError('invalid device: ' + repr(dev))
    pdev = DEVICES[dev]
    print(dev, file = ofp)
    print(pdev.kind, file = ofp)
    print(file = ofp)
    line = readline(ifp)
    if line != 'pins:':
        raise SyntaxError('missing pin declaration')
    pin1 = readline(ifp).split()
    pin2 = readline(ifp).split()
    pind = pdev.pins
    if not (len(pin1) == len(pin2) == len(pind) // 2):
        raise SyntaxError('invalid pin declaration')
    print(''.join('NC  ' if p == '_' else p.ljust(4, ' ') for p in pin1[::-1]), file = ofp)
    print(''.join('NC  ' if p == '_' else p.ljust(4, ' ') for p in pin2), file = ofp)
    print(file = ofp)
    pins = pin1 + pin2
    pini = list(range(1, len(pind) + 1))
    pini = pini[:len(pind) // 2][::-1] + pini[len(pind) // 2:]
    args, defs, outs = [], {}, []
    for i, name, decl in zip(pini, pins, pind):
        if decl not in 'VGio_':
            raise SystemError('invalid pin type ' + repr(decl))
        elif decl == '_' and name != '_':
            raise SyntaxError('pin %d is a NC pin so it must have the name "_"' % i)
        elif decl == 'V' and name != 'VCC':
            raise SyntaxError('pin %d is a power pin so it must have the name "VCC"' % i)
        elif decl == 'G' and name != 'GND':
            raise SyntaxError('pin %d is a ground pin so it must have the name "GND"' % i)
        elif decl == 'i' and name != '_':
            sym = core.symbols(name)
            if sym in args:
                raise SyntaxError('duplicated input pin ' + repr(name))
            else:
                args.append(sym)
        elif decl == 'o' and name != '_':
            if name in defs:
                raise SyntaxError('duplicated output pin ' + repr(name))
            else:
                outs.append(name)
                defs[name] = None
    if not outs:
        raise SyntaxError('no output pins declared')
    for v in args:
        defs[str(v)] = v
    line = readline(ifp)
    if line == 'define:':
        while True:
            try:
                line = readline(ifp)
            except EOFError:
                break
            if '=' not in line:
                break
            exec(line, {}, defs)
    if line == 'table:':
        hdr = readline(ifp).split()
        var, ret = split_logic(hdr)
        col, val = [[] for _ in range(len(var))], [[] for _ in range(len(ret))]
        while True:
            try:
                line = readline(ifp).split()
            except EOFError:
                break
            vals, rets = split_logic(line)
            if len(vals) != len(var) or len(rets) != len(ret):
                raise SyntaxError('inconsistent input and output values')
            for i, (k, v) in enumerate(zip(var, vals)):
                if v == '1':
                    col[i].append(defs[k])
                elif v == '0':
                    col[i].append(~defs[k])
                else:
                    raise SyntaxError('invalid logic bit ' + repr(v))
            for i, (k, v) in enumerate(zip(ret, rets)):
                if v == '1':
                    val[i].append(True)
                elif v == '0':
                    val[i].append(False)
                else:
                    raise SyntaxError('invalid logic bit ' + repr(v))
        rows = [And(*v) for v in zip(*col)]
        for i, row in enumerate(val):
            expr = logic.false
            for j, exp in enumerate(row):
                if exp:
                    expr = expr | rows[j]
            if defs[ret[i]] is not None:
                raise SyntaxError('logic function of output %s defined twice' % repr(ret[i]))
            else:
                defs[ret[i]] = expr
    try:
        readline(ifp)
    except EOFError:
        pass
    else:
        raise SyntaxError('junk after truth table')
    exprs = {}
    for p in outs:
        if defs[p] is None:
            raise SyntaxError('undefined logic function of output ' + repr(p))
        else:
            exprs[p] = logic.to_dnf(defs[p], simplify = True, force = True)
    for p in outs:
        print('%s = %s' % (p, dump_dnf(exprs[p])), file = ofp)
    ands = 0
    terms = []
    for expr in exprs.values():
        if isinstance(expr, (And, Not, Symbol)):
            ands += 1
            if expr not in terms:
                terms.append(expr)
        elif isinstance(expr, Or):
            ands += len(expr.args)
            for arg in expr.args:
                if arg not in terms:
                    terms.append(arg)
        else:
            raise SystemError('unknown kind of term ' + repr(expr))
    desc.append('')
    desc.append('STATISTICS')
    desc.append('    Terms        = %d' % ands)
    desc.append('    Unique Terms = %d' % len(terms))
    desc.append('')
    desc.append('LOGISIM-PLA-FUSE')
    if len(terms) > 32:
        desc.append('    (not possible due to excess number of unique terms)')
    else:
        outr = []
        andr = []
        head = [list(map(str, args)) + ['|'] + outs]
        for term in terms:
            ors = {}
            ands = {}
            line = []
            for arg in args:
                ands[arg] = None
            if isinstance(term, Symbol):
                ands[term] = True
            elif isinstance(term, Not):
                ands[term.args[0]] = False
            elif isinstance(term, And):
                for fac in term.args:
                    if isinstance(fac, Symbol):
                        ands[fac] = True
                    elif isinstance(fac, Not):
                        ands[fac.args[0]] = False
                    else:
                        raise SystemError('invalid factor type')
            else:
                raise SystemError('invalid term type')
            for out in outs:
                row = exprs[out]
                if isinstance(row, (And, Not, Symbol)):
                    ors[out] = term == row
                elif isinstance(row, Or):
                    ors[out] = term in row.args
                else:
                    raise SystemError('invalid row type')
            for cond in ands.values():
                if cond is None:
                    andr.append(0)
                    line.append('· ·')
                elif cond:
                    andr.append(2)
                    line.append('· X')
                else:
                    andr.append(1)
                    line.append('X ·')
            line.append('|')
            for cond in ors.values():
                if cond:
                    outr.append(1)
                    line.append('X')
                else:
                    outr.append(0)
                    line.append('·')
            head.append(line)
        wtab, data = format_table(head)
        desc.append('    ' + data[0])
        desc.append('    ' + '-' * (sum(wtab) + (len(wtab) - 1) * 2))
        desc.extend('    ' + v for v in data[1:])
        bits = [[andr[0], 1]]
        for bv in andr[1:]:
            if bv == bits[-1][0]:
                bits[-1][1] += 1
            else:
                bits.append([bv, 1])
        bits.append([outr[0], 1])
        for bv in outr[1:]:
            if bv == bits[-1][0]:
                bits[-1][1] += 1
            else:
                bits.append([bv, 1])
        prom = []
        for bv, cnt in bits:
            if cnt == 1:
                prom.append(str(bv))
            elif cnt == 2:
                prom.extend((str(bv), str(bv)))
            else:
                prom.append('%d*%d' % (bv, cnt))
        desc.append('')
        desc.append('LOGISIM-PLA-ROM-CONTENT')
        desc.append('    ' + ' '.join(prom))
    print(file = ofp)
    print('DESCRIPTION', file = ofp)
    print('\n'.join(desc), file = ofp)

def main():
    if len(sys.argv) != 2:
        print('usage: %s <input-file>', file = sys.stderr)
        return 1
    ifn = os.path.abspath(sys.argv[1])
    ofn = os.path.splitext(ifn)[0] + '.pld'
    with open(ifn) as ifp:
        with open(ofn, 'w') as ofp:
            try:
                generate_from(ifp, ofp)
            except SyntaxError as e:
                print('* error: ' + str(e))
                return 1

if __name__ == '__main__':
    sys.exit(main())
