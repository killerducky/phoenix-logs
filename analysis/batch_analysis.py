# -*- coding: utf-8 -*-
# This script is for running multiple analyses at once,
# to avoid reading the db and decompressing each log multiple times.

import bz2
import sqlite3
from lxml import etree
from tqdm import tqdm
import cProfile
import argparse

#from pond_traits import PondTraits
from wait_estimator import WaitEstimator

parser = argparse.ArgumentParser()
parser.add_argument('-l', '--limit', default=10000)
parser.add_argument('-p', '--no_progress_bar', action=argparse.BooleanOptionalAction)
args = parser.parse_args()

def nop(it, *a, **k): 
    return it
if args.no_progress_bar:
    tqdm = nop

analyzers = [WaitEstimator()]
allowed_types = ["169", "225", "185"]

def RunAnalysis():
    decompress = bz2.decompress
    XML = etree.XML

    with sqlite3.connect('../logs/es4p.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM logs')
        rowcount = cursor.fetchone()[0]
        cursor.execute(f'SELECT * FROM logs LIMIT {args.limit}')
        last_print = 0

        for i in tqdm(range(rowcount), ncols=80, ascii=True):
            log = cursor.fetchone()
            if log is None:
                break

            content = decompress(log[2])
            xml = XML(content, etree.XMLParser(recover=True))

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
    
    return True

#cProfile.run("RunAnalysis()")
RunAnalysis()