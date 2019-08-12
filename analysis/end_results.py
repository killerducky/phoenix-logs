# -*- coding: utf-8 -*-

import bz2
import sqlite3
from collections import Counter
from lxml import etree

results = Counter()

with sqlite3.connect('../logs/2018.db') as conn:
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
            results["Total"] += 1
            if win.attrib['who'] == win.attrib['fromWho']:
                results["Tsumo"] += 1
            else:
                results["Ron"] += 1
        
        draws = xml.findall('RYUUKYOKU')

        for draw in draws:
            results["Total"] += 1
            if 'type' not in draw.attrib:
                results["Exhaustive Draw"] += 1
                continue
            
            results[draw.attrib['type']] += 1

print("Result,Count,Percent")
for result in results:
    print("%s,%d,%.2f" % result, results[result], results[result] / results["Total"])