# -*- coding: utf-8 -*-

import bz2
import sqlite3
from analysis_utils import convertHai, convertTile
from shanten import calculateKokushiShanten, calculateChiitoitsuShanten, calculateStandardShanten
from collections import Counter
from lxml import etree

minimum = Counter()
chiitoi = Counter()
kokushi = Counter()
standard = Counter()
hands = 0
draws = ['T','U','V','W']

with sqlite3.connect('../logs/2019.db') as conn:
    cursor = conn.cursor()
    cursor.execute('SELECT log_content FROM logs WHERE is_tonpusen=0 AND is_hirosima=0')

    while True:
        log = cursor.fetchone()
        if log is None:
            break

        content = bz2.decompress(log[0])
        xml = etree.XML(content, etree.XMLParser(recover=True)).getroottree().getroot()
        rounds = xml.findall('INIT')

        for round_ in rounds:
            hands += 4
            round_ended = False
            for i in range(4):
                hand = convertHai(round_.attrib['hai%d' % i])

                # Add the first drawn tile to the hand
                next_element = round_.getnext()
                while next_element is not None:
                    name = next_element.tag
                    if name == "UN":
                        continue
                    if name[0] == draws[i]:
                        hand[convertTile(name[1:])] += 1
                        break
                    if name == "AGARI" or name == "RYUUKYOKU" or name == "INIT" or name == "N":
                        round_ended = True
                        break
                    next_element = next_element.getnext()
                
                if round_ended:
                    break
                
                standard_shanten = calculateStandardShanten(hand)
                chiitoi_shanten = calculateChiitoitsuShanten(hand)
                kokushi_shanten = calculateKokushiShanten(hand)
                min_shanten = min((standard_shanten, chiitoi_shanten, kokushi_shanten))
                minimum[min_shanten] += 1
                kokushi[kokushi_shanten] += 1
                chiitoi[chiitoi_shanten] += 1
                standard[standard_shanten] += 1

print("Total hands: %d" % hands)
print("Shanten Type,Shanten,Count")
for i in range(-1, 7):
    print("Minimum,%d,%d" % (i, minimum[i]))
for i in range(-1, 9):
    print("Standard,%d,%d" % (i, standard[i]))
for i in range(-1, 7):
    print("Chiitoitsu,%d,%d" % (i, chiitoi[i]))
for i in range(-1, 14):
    print("Kokushi,%d,%d" % (i, kokushi[i]))