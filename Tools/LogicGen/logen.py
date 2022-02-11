#!/usr/bin/env pypy3
# -*- coding: utf-8 -*-

""" Generates PLD functions from Truth-table for GAL devices """

import io
import os
import sys
import json
import pickle
import multiprocessing

from typing import Dict
from typing import List
from typing import Tuple
from typing import Union
from typing import TextIO

from sympy import Xor, logic
from sympy.core.symbol import Symbol

from sympy.logic.boolalg import Or
from sympy.logic.boolalg import And
from sympy.logic.boolalg import Not
from sympy.logic.boolalg import Boolean

class Device:
    name: str
    kind: str
    pins: str

    def __init__(self, name: str, kind: str, pins: str) -> None:
        self.name = name
        self.kind = kind
        self.pins = pins

    @staticmethod
    def load_devices() -> dict:
        with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'devices.json')) as fp:
            return json.load(fp)

DEVICES = {
    name: Device(dev['name'], dev['type'], dev['pins'])
    for name, dev in Device.load_devices().items()
}

PRECEDENCE = [
    '|',
    '^',
    '&',
]

def readline(ifp: TextIO) -> str:
    while True:
        buf = ifp.readline()
        if not buf:
            raise EOFError()
        src = buf.strip()
        if src and src[0] != '#':
            return src

def dump_dnf(dnf: Boolean) -> str:
    if isinstance(dnf, Not):
        return '/' + dump_dnf(dnf.args[0])
    elif isinstance(dnf, And):
        return ' * '.join(sorted(dump_dnf(v) for v in dnf.args))
    elif isinstance(dnf, Or):
        return ' +\n       '.join(sorted(dump_dnf(v) for v in dnf.args))
    else:
        return str(dnf)

def skip_space(expr: str, i: int) -> int:
    while i < len(expr) and expr[i].isspace():
        i += 1
    else:
        return i

def parse_name(expr: str, i: int) -> Tuple[str, int]:
    p = i
    while i < len(expr) and expr[p:i + 1].isidentifier():
        i += 1
    return expr[p:i], i

def parse_term(expr: str, row: int, i: int) -> Tuple[list, int]:
    i = skip_space(expr, i)
    if i >= len(expr):
        raise SyntaxError('unexpected EOF at line %d' % (row + 1))
    elif expr[i] == '~':
        lhs, i = parse_term(expr, row, i + 1)
        return ['~', lhs], i
    elif expr[i].isidentifier():
        name, i = parse_name(expr, i)
        return ['', name], i
    elif expr[i] == '(':
        i = skip_space(expr, i + 1)
        ret, i = parse_expr(expr, row, i, 0)
        i = skip_space(expr, i)
        if i >= len(expr):
            raise SyntaxError('unexpected EOF at line %d' % (row + 1))
        elif expr[i] != ')':
            raise SyntaxError('missing ")" at line %d, column %d' % (row + 1, i + 1))
        else:
            return ret, i + 1
    else:
        raise SyntaxError('invalid character at line %d, column %d' % (row + 1, i + 1))

def parse_expr(expr: str, row: int, i: int, p: int) -> Tuple[list, int]:
    if p >= len(PRECEDENCE):
        return parse_term(expr, row, i)
    op = PRECEDENCE[p]
    lhs, i = parse_expr(expr, row, i, p + 1)
    i = skip_space(expr, i)
    ret = [op, lhs]
    while i < len(expr) and expr[i] == op:
        rhs, i = parse_expr(expr, row, i + 1, p + 1)
        i = skip_space(expr, i)
        ret.append(rhs)
    return ret, i

def parse_logic(expr: str, row: int) -> Tuple[str, list]:
    i = skip_space(expr, 0)
    if i >= len(expr):
        raise SyntaxError('no logic expressions at line %d' % (row + 1))
    name, i = parse_name(expr, i)
    if not name:
        raise SyntaxError('variable name expected at line %d, column %s' % (row + 1, i + 1))
    i = skip_space(expr, i)
    if i >= len(expr):
        raise SyntaxError('unexpected EOF at line %d' % (row + 1))
    if expr[i] != '=':
        raise SyntaxError('operator "=" expected at line %d, column %d' % (row + 1, i + 1))
    i = skip_space(expr, i + 1)
    ret, i = parse_expr(expr, row, i, 0)
    i = skip_space(expr, i)
    if i < len(expr):
        raise SyntaxError('junk after expression at line %d, column %d' % (row + 1, i + 1))
    return name, ret

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

def resolve_expr(
    defs: Dict[str, Union[list, Boolean]],
    name: str,
    expr: list,
    memo: Dict[str, Boolean],
    prog: str,
    path: str,
) -> Boolean:
    State.update_progress(prog, path)
    def reduce_expr(ops):
        return ops(*(
            resolve_expr(defs, name, v, memo, prog, '%s[%d/%d]' % (path, i + 1, len(expr) - 1))
            for (i, v) in enumerate(expr[1:])
        ))
    if not expr[0]:
        name = expr[1]
        if name not in memo:
            memo[name] = None
            memo[name] = resolve_value(defs, name, memo, prog, path)
            return memo[name]
        elif memo[name] is None:
            raise SyntaxError('circular reference to variable "%s"' % name)
        else:
            State.update_progress(prog, '%s > %s' % (path, name))
            return memo[name]
    elif expr[0] == '~':
        return Not(resolve_expr(defs, name, expr[1], memo, prog, '%s > (invert)' % path))
    elif expr[0] == '|':
        return reduce_expr(Or)
    elif expr[0] == '&':
        return reduce_expr(And)
    elif expr[0] == '^':
        return reduce_expr(Xor)
    else:
        raise RuntimeError('fatal: invalid expression (operator "%s"): %s' % (expr[0], expr))

def resolve_value(
    defs: Dict[str, Union[list, Boolean]],
    name: str,
    memo: Dict[str, Boolean],
    prog: str,
    path: str,
) -> Boolean:
    val = defs.get(name)
    path = '%s > %s' % (path, name)
    if val is None:
        raise SyntaxError('unresolved reference to variable "%s"' % name)
    elif isinstance(val, Boolean):
        State.update_progress(prog, path)
        return val
    else:
        return resolve_expr(defs, name, val, memo, prog, path)

class State:
    prog = {}
    lock = multiprocessing.Lock()

    @staticmethod
    def init(keys: List[str]):
        for key in keys:
            if key in State.prog:
                raise RuntimeError('duplicated name: ' + key)
            State.prog[key] = len(State.prog)
            sys.stderr.write('* Output %-4s : Waiting for execution ...\n' % key)
        sys.stderr.write('\r\x1b[%dA' % len(keys))
        sys.stderr.flush()

    @staticmethod
    def finish():
        sys.stderr.write('\n' * len(State.prog))
        sys.stderr.flush()

    @staticmethod
    def update_progress(key: str, status: str):
        pos = State.prog[key]
        State.lock.acquire()
        sys.stderr.write('\r%s* Output %-4s : %s\x1b[K\r%s' % (
            '' if pos == 0 else '\x1b[%dB' % pos,
            key,
            status,
            '' if pos == 0 else '\x1b[%dA' % pos,
        ))
        State.lock.release()
        sys.stderr.flush()

def optimize_expr(args):
    sys.setrecursionlimit(65536)
    defs, State.prog, nopt, key = args
    State.update_progress(key, 'Loading ...')
    defs = pickle.loads(defs)
    State.update_progress(key, 'Resolving ...')
    expr = resolve_value(defs, key, {}, key, 'Resolving')
    if key in nopt:
        State.update_progress(key, 'Converting ...')
        ret = logic.to_dnf(expr)
    else:
        State.update_progress(key, 'Optimizing ...')
        ret = logic.to_dnf(expr, simplify = True, force = True)
    State.update_progress(key, 'Generating ...')
    dump = '%-4s = %s' % (key, dump_dnf(ret))
    State.update_progress(key, 'Done')
    return key, ret, dump

def generate_from(ifp: TextIO, ofp: TextIO):
    row = 0
    desc = []
    line = readline(ifp)
    while line != 'device:':
        desc.append(line)
        row += 1
        line = readline(ifp)
    if line != 'device:':
        raise SyntaxError('missing device declaration')
    dev = readline(ifp)
    row += 1
    if dev not in DEVICES:
        raise SyntaxError('invalid device: ' + repr(dev))
    pdev = DEVICES[dev]
    print(pdev.name, file = ofp)
    print(pdev.kind, file = ofp)
    print(file = ofp)
    row += 1
    line = readline(ifp)
    if line != 'pins:':
        raise SyntaxError('missing pin declaration')
    row += 2
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
            sym = Symbol(name)
            if sym in args:
                raise SyntaxError('duplicated input pin ' + repr(name))
            else:
                args.append(sym)
                defs[name] = sym
        elif decl == 'o' and name != '_':
            if name in defs:
                raise SyntaxError('duplicated output pin ' + repr(name))
            else:
                outs.append(name)
                defs[name] = None
    if not outs:
        raise SyntaxError('no output pins declared')
    row += 1
    nopt = frozenset()
    line = readline(ifp)
    if line == 'no-opt:':
        line = readline(ifp)
        nopt = frozenset(v.strip() for v in line.split(','))
        line = readline(ifp)
    if line == 'define:':
        while True:
            try:
                row += 1
                line = readline(ifp)
            except EOFError:
                break
            if '=' not in line:
                break
            name, expr = parse_logic(line, row)
            defs[name] = expr
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
                    col[i].append(['', k])
                elif v == '0':
                    col[i].append(['~', ['', k]])
                else:
                    raise SyntaxError('invalid logic bit ' + repr(v))
            for i, (k, v) in enumerate(zip(ret, rets)):
                if v == '1':
                    val[i].append(True)
                elif v == '0':
                    val[i].append(False)
                else:
                    raise SyntaxError('invalid logic bit ' + repr(v))
        rows = [
            ['&'] + list(v)
            for v in zip(*col)
        ]
        for i, row in enumerate(val):
            if ret[i] in defs and defs[ret[i]] is not None:
                raise SyntaxError('logic function of output %s defined twice' % repr(ret[i]))
            expr = ['|']
            for j, bitval in enumerate(row):
                if bitval:
                    expr.append(rows[j])
            if len(expr) == 1:
                raise SyntaxError('%s is always false' % ret[i])
            else:
                defs[ret[i]] = expr
    try:
        readline(ifp)
    except EOFError:
        pass
    else:
        raise SyntaxError('junk after truth table')
    for p in outs:
        if defs[p] is None:
            raise SyntaxError('undefined logic function of output ' + repr(p))
    exprs = {}
    defsv = pickle.dumps(defs)
    State.init(outs)
    with multiprocessing.Pool() as mp:
        req = zip([defsv] * len(outs), [State.prog] * len(outs), [nopt] * len(outs), outs)
        for key, ret, expr in mp.map(optimize_expr, req):
            exprs[key] = ret
            print(expr, file = ofp)
    ands = 0
    terms = []
    State.finish()
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
        print('usage: %s <input-file>' % sys.argv[0], file = sys.stderr)
        return 1
    ifn = os.path.abspath(sys.argv[1])
    ofn = os.path.splitext(ifn)[0] + '.pld'
    print('LogicGen v1.0', file = sys.stderr)
    print('* Logic file  :', ifn, file = sys.stderr)
    print('* PLD file    :', ofn, file = sys.stderr)
    with open(ifn) as ifp:
        try:
            ret = io.StringIO()
            generate_from(ifp, ret)
        except SyntaxError as e:
            print('* error: ' + str(e))
            return 1
        else:
            with open(ofn, 'w') as ofp:
                ofp.write(ret.getvalue())

if __name__ == '__main__':
    sys.setrecursionlimit(65536)
    sys.exit(main())
