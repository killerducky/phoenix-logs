# -*- coding: utf-8 -*-

from collections import Counter
from analysis_utils import convertTile
from log_analyzer import LogAnalyzer

dora_indication = [
     6, 2, 3, 4, 5, 6, 7, 8, 9, 1,
    16,12,13,14,15,16,17,18,19,11,
    26,22,23,24,25,26,27,28,29,21,
    30,32,33,34,31,36,37,35
]

def convertDora(tile):
    return dora_indication[convertTile(tile)]

class DoraRonRates(LogAnalyzer):
    def __init__(self):
        self.counters = []

        for i in range(34):
            self.counters.append(Counter())

    def ParseLog(self, log, log_id):
        wins = log.findall('AGARI')

        for win in wins:
            if 'yaku' not in win.attrib:
                continue

            dora = win.attrib['doraHai'].split(',')
            dora_tile = convertDora(dora[0])

            winning_tile = convertTile(win.attrib['machi'])
            tsumo = win.attrib['who'] == win.attrib['fromWho']

            if dora_tile == winning_tile:
                self.counters[winning_tile]['dora_win_count'] += 1
                if tsumo:
                    self.counters[winning_tile]['dora_tsumo_count'] += 1
                else:
                    self.counters[winning_tile]['dora_ron_count'] += 1
            else:
                self.counters[winning_tile]['nondora_win_count'] += 1
                if tsumo:
                    self.counters[winning_tile]['nondora_tsumo_count'] += 1
                else:
                    self.counters[winning_tile]['nondora_ron_count'] += 1

    def PrintResults(self):
        print('tile,nondora wins,tsumos,rons,ron percent,dora wins,tsumos,rons,ron percent')
        for i in range(34):
            print('%d,%d,%d,%d,%d,%d,%d' % (
                i,
                self.counters[i]['nondora_win_count'],
                self.counters[i]['nondora_tsumo_count'],
                self.counters[i]['nondora_ron_count'],
                self.counters[i]['dora_win_count'],
                self.counters[i]['dora_tsumo_count'],
                self.counters[i]['dora_ron_count']
            ))