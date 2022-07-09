#!/usr/bin/env python3
# -*- coding: utf-8 -*-

for i in range(32):
    print('<comp lib="0" loc="(1370,%d)" name="Constant">' % (1090 + i * 40))
    print('  <a name="value" val="0x0"/>')
    print('  <a name="width" val="%d"/>' % (i + 1))
    print('</comp>')
    print('<comp lib="0" loc="(1330,%d)" name="Splitter">' % (1110 + i * 40))
    print('  <a name="appear" val="center"/>')
    for p in range(32):
        print('  <a name="bit%d" val="%s"/>' % (31 - p, '0' if p > i else 'none'))
    print('  <a name="fanout" val="1"/>')
    print('  <a name="incoming" val="32"/>')
    print('  <a name="spacing" val="2"/>')
    print('</comp>')
    print('<comp lib="0" loc="(1390,%d)" name="Splitter">' % (1110 + i * 40))
    print('  <a name="appear" val="center"/>')
    for p in range(32):
        print('  <a name="bit%d" val="%d"/>' % (p, int(p > i)))
    print('  <a name="facing" val="west"/>')
    print('  <a name="incoming" val="32"/>')
    print('  <a name="spacing" val="2"/>')
    print('</comp>')
    print('<wire from="(1350,%d)" to="(1370,%d)"/>' % (1110 + i * 40, 1110 + i * 40))