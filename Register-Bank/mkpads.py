#!/usr/bin/env python3
# -*- coding: utf-8 -*-

with open('Layer0/Layer0.sch') as fp:
    lines = fp.read().splitlines()

ret = []
part = None
comp = False

for line in lines:
    if line == '$Comp':
        comp = True
    elif line == '$EndComp':
        comp = False
    elif comp:
        mods = False
        args = line.split(' ')
        if args[0] == 'L':
            part = args[1]
        elif args[0] == 'F' and args[1] == '2' and args[2] == '""':
            if part == '74xx:74LS273':
                mods = True
                args[2] = '"Package_DIP:DIP-20_W7.62mm_Socket"'
            elif part == 'Device:C_Small':
                mods = True
                args[2] = '"Capacitor_THT:C_Disc_D4.7mm_W2.5mm_P5.00mm"'
            elif part == 'Connector:Conn_01x08_Male':
                mods = True
                args[2] = '"Connector_PinHeader_2.54mm:PinHeader_1x08_P2.54mm_Vertical"'
        if mods:
            line = ' '.join(args)
    ret.append(line)

with open('Layer0/Layer0.sch') as fp:
    with open('Layer0/Layer0.sch-bak', 'w') as wfp:
        wfp.write(fp.read())

with open('Layer0/Layer0.sch', 'w') as fp:
    for line in ret:
        print(line, file = fp)
