# -*- coding: utf-8 -*-

import bz2
import math
import sqlite3
from collections import Counter
from analysis_utils import convertTile
from lxml import etree

ura_by_unique_tiles = dict()

# Can't have less than 5 unique tiles (toitoi)
for i in range(5, 14):
    ura_by_unique_tiles[i] = Counter()

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

            try:
                ura_position = ids.index(53)
                if han[ura_position] > 0:
                    hand = map(convertTile, win.attrib['hai'].split(','))
                    hand_no_duplicates = list(dict.fromkeys(hand))
                    uniques = len(hand_no_duplicates)
                    ura_by_unique_tiles[uniques]["wins"] += 1
                    ura_by_unique_tiles[uniques][han[ura_position]] += 1
            except:
                # No uradora in list; wasn't riichi, or was yakuman
                pass