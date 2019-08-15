# -*- coding: utf-8 -*-

import bz2
import sqlite3
from urllib import parse
from collections import Counter
from lxml import etree

counts = Counter()

with sqlite3.connect('../logs/es4p.db') as conn:
    cursor = conn.cursor()
    cursor.execute('SELECT log_content, log_id FROM logs')

    while True:
        log = cursor.fetchone()
        if log is None:
            break

        content = bz2.decompress(log[0])
        xml = etree.XML(content, etree.XMLParser(recover=True)).getroottree().getroot()
        rounds = xml.findall('INIT')

        count = len(rounds)
        
        if counts[count] == 0:
            print("%d rounds: %s" % (count, log[1]))

        counts[count] += 1

print("Rounds,Games")
for i in range(1,28):
    print("%d,%d" % (i, counts[i]))
