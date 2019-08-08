# -*- coding: utf-8 -*-

import bz2
import math
import sqlite3
import re
from collections import Counter
from analysis_utils import convertTile, convertHand
from ukeire import calculateUkeire
from shanten import calculateMinimumShanten
from lxml import etree

wait_includes_tile = Counter()
ippatsu_win_on_tile_with_X_remaining = []
for i in range(38):
    ippatsu_win_on_tile_with_X_remaining.append(Counter())

discard_pattern = re.compile("[D-G](\\d+)")
def getRemainingTiles(agari):
    remaining_tiles = [4] * 37
    remaining_tiles[0] = 0
    remaining_tiles[10] = 0
    remaining_tiles[20] = 0
    remaining_tiles[30] = 0

    current = agari.getprevious()
    while current.tag != "TAIKYOKU":
        match = discard_pattern.match(current.tag)
        if match:
            remaining_tiles[convertTile(match.group(1))] -= 1
    
    return remaining_tiles

with sqlite3.connect('logs/2018.db') as conn:
    cursor = conn.cursor()
    cursor.execute('SELECT log_content FROM logs WHERE is_tonpusen=0 AND is_hirosima=0')

    while True:
        log = cursor.fetchone()
        if log is None:
            break

        content = bz2.decompress(log[0])
        xml = etree.XML(content, etree.XMLParser(recover=True)).getroottree().getroot()
        wins = xml.findall('AGARI')

        for win in wins:
            if 'yaku' not in win.attrib:
                continue
            
            # Only check hands for which there is only one indicator
            dora = win.attrib['doraHai'].split(',')
            if len(dora) > 1:
                continue

            yaku = win.attrib['yaku'].split(',')
            ids = [int(x) for x in yaku[0::2]]
            han = [int(x) for x in yaku[1::2]]

            # Look for ippatsu tsumo
            if ids.count(2) > 0 and ids.count(0) > 0:
                hand = map(convertTile, win.attrib['hai'].split(','))
                converted_hand = convertHand(hand)
                winning_tile = convertTile(win.attrib['machi'])
                converted_hand[winning_tile] -= 1
                remaining_tiles = getRemainingTiles(win)

                for i in range(38):
                    remaining_tiles[i] -= converted_hand[i]

                ukeire = calculateUkeire(hand, remaining_tiles, calculateMinimumShanten)

                for tile in ukeire[1]:
                    wait_includes_tile[tile] += 1
                
                ippatsu_win_on_tile_with_X_remaining[winning_tile][remaining_tiles[winning_tile]] += 1

