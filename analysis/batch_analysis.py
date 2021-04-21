# -*- coding: utf-8 -*-
# This script is for running multiple analyses at once,
# to avoid reading the db and decompressing each log multiple times.

import bz2
import sqlite3
from lxml import etree
from tqdm import tqdm

from pond_traits import PondTraits

analyzers = [PondTraits()]
allowed_types = ["169", "225", "185"]

with sqlite3.connect('../logs/es4p.db') as conn:
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM logs')
    rowcount = cursor.fetchone()[0]
    cursor.execute('SELECT * FROM logs')
    last_print = 0

    for i in tqdm(range(rowcount), ncols=80, ascii=True):
        log = cursor.fetchone()
        if log is None:
            break

        content = bz2.decompress(log[2])
        xml = etree.XML(content, etree.XMLParser(recover=True)).getroottree().getroot()

        game_type = xml.find("GO").attrib["type"]

        if game_type in allowed_types:
            for analyzer in analyzers:
                analyzer.ParseLog(xml, log[0])
        
        if i - last_print > 100000:
            last_print = i
            for analyzer in analyzers:
                print("==========")
                analyzer.PrintResults()

for analyzer in analyzers:
    print("==========")
    analyzer.PrintResults()