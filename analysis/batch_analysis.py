# -*- coding: utf-8 -*-
# This script is for running multiple analyses at once,
# to avoid reading the db and decompressing each log multiple times.

import bz2
import sqlite3
from lxml import etree
from tqdm import tqdm
from call_rate_by_round import CallRateByRound
from dealin_rate_by_round import DealInRateByRound
from value_by_round import ValueByRound
from yaku_by_round import YakuByRound
from riichi_by_round import RiichiByRound
from end_results import EndResults

analyzers = [CallRateByRound(), DealInRateByRound(), ValueByRound(), YakuByRound(), RiichiByRound(), EndResults()]
allowed_types = ["169", "225", "185"]

with sqlite3.connect('../logs/es4p.db') as conn:
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM logs')
    rowcount=cursor.fetchone()[0]
    cursor.execute('SELECT log_content, log_id FROM logs')

    for i in tqdm(range(rowcount), ncols=80, ascii=True):
        log = cursor.fetchone()
        if log is None:
            break

        content = bz2.decompress(log[0])
        xml = etree.XML(content, etree.XMLParser(recover=True)).getroottree().getroot()

        game_type = xml.find("GO").attrib["type"]

        if game_type in allowed_types:
            for analyzer in analyzers:
                analyzer.ParseLog(xml, log[1])

for analyzer in analyzers:
    print("==========")
    analyzer.PrintResults()