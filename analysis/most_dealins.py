# -*- coding: utf-8 -*-

import bz2
import sqlite3
from collections import Counter
from lxml import etree

results = Counter()
who_counter = Counter()

with sqlite3.connect('../logs/2018.db') as conn:
    cursor = conn.cursor()
    cursor.execute('SELECT log_content FROM logs WHERE is_tonpusen=0 AND is_hirosima=0')

    while True:
        log = cursor.fetchone()
        if log is None:
            break

        content = bz2.decompress(log[0])
        xml = etree.XML(content, etree.XMLParser(recover=True)).getroottree().getroot()
        who_counter.clear()
        wins = xml.findall('AGARI')

        for win in wins:
            if win.attrib['who'] == win.attrib['fromWho']:
                continue
            else:
                who_counter[win.attrib['fromWho']] += 1
        
        results[who_counter["0"]] += 1
        results[who_counter["1"]] += 1
        results[who_counter["2"]] += 1
        results[who_counter["3"]] += 1
        

print("Deal-in Count,Occurrences")
for result in results:
    print("%s,%d" % result, results[result])