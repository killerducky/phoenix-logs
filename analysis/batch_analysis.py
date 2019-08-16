# -*- coding: utf-8 -*-

import bz2
import sqlite3
from lxml import etree
from tqdm import tqdm
from third_dragon import ThirdDragon

analyzers = [ThirdDragon()]

with sqlite3.connect('../logs/2019.db') as conn:
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM logs WHERE is_tonpusen=0 AND is_hirosima=0')
    rowcount=cursor.fetchone()[0]
    cursor.execute('SELECT log_content, log_id FROM logs WHERE is_tonpusen=0 AND is_hirosima=0')

    for i in tqdm(range(rowcount), ncols=80, ascii=True):
        log = cursor.fetchone()
        if log is None:
            break

        content = bz2.decompress(log[0])
        xml = etree.XML(content, etree.XMLParser(recover=True)).getroottree().getroot()
        for analyzer in analyzers:
            analyzer.ParseLog(xml, log[1])

for analyzer in analyzers:
    print("==========")
    analyzer.PrintResults()