# -*- coding: utf-8 -*-

import bz2
import math
import sqlite3
from collections import Counter
from analysis_utils import convertTile
from lxml import etree

yakulist=[]

dora_indication = [
     6, 2, 3, 4, 5, 6, 7, 8, 9, 1,
    16,12,13,14,15,16,17,18,19,11,
    26,22,23,24,25,26,27,28,29,21,
    30,32,33,34,31,36,37,35
]

def convertDora(tile):
    return dora_indication[convertTile(tile)]

counters = []

for i in range(34):
    counters.append(Counter())

nondora_tsumo_count = 0
dora_tsumo_count = 0
nondora_ron_count = 0
dora_ron_count = 0
nondora_win_count = 0
dora_win_count = 0
games_count = 0

with sqlite3.connect('../logs/2014.db') as conn:
    cursor = conn.cursor()
    cursor.execute('SELECT log_content FROM logs WHERE is_tonpusen=0 AND is_hirosima=0')

    while True:
        log = cursor.fetchone()
        if log is None:
            break

        games_count += 1
        content = bz2.decompress(log[0])
        xml = etree.XML(content, etree.XMLParser(recover=True)).getroottree().getroot()
        wins = xml.findall('AGARI')

        for win in wins:
            if 'yaku' not in win.attrib:
                continue
            #hand = win.attrib['hai'].split(',')
            #converted_hand = list(map(convertTile, hand))
            dora = win.attrib['doraHai'].split(',')
            dora_tiles = list(map(convertDora, dora))

            winning_tile = convertTile(win.attrib['machi'])
            tsumo = win.attrib['who'] == win.attrib['fromWho']

            if dora_tiles.count(winning_tile) > 0:
                counters[winning_tile]['dora_win_count'] += 1
                if tsumo:
                    counters[winning_tile]['dora_tsumo_count'] += 1
                else:
                    counters[winning_tile]['dora_ron_count'] += 1
            else:
                counters[winning_tile]['nondora_win_count'] += 1
                if tsumo:
                    counters[winning_tile]['nondora_tsumo_count'] += 1
                else:
                    counters[winning_tile]['nondora_ron_count'] += 1

print('Analyzed %d games' % games_count)
print('tile,nondora wins,tsumos,rons,ron percent,dora wins,tsumos,rons,ron percent')
for i in range(34):
    print('%d,%d,%d,%d,%.1f,%d,%d,%d,%.1f' % (
        i,
        counters[i]['nondora_win_count'],
        counters[i]['nondora_tsumo_count'],
        counters[i]['nondora_ron_count'],
        counters[i]['nondora_ron_count'] / counters[i]['nondora_win_count'] * 100,
        counters[i]['dora_win_count'],
        counters[i]['dora_tsumo_count'],
        counters[i]['dora_ron_count'],
        counters[i]['dora_ron_count'] / counters[i]['dora_win_count'] * 100
    ))