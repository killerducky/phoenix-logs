# -*- coding: utf-8 -*-
# This script is for running multiple analyses at once,
# to avoid reading the db and decompressing each log multiple times.

import bz2
import sqlite3
from lxml import etree
from tqdm import tqdm
import cProfile
import argparse
import numpy as np
from skopt import gp_minimize
from skopt.space import Real
from skopt.utils import use_named_args
from skopt import forest_minimize

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
    # TODO: fix tuning vs non-tuning to both work
    # analyzers[0].GS_C_ccw['ryanmen'] = ryanmen[0]
    # analyzers[0].GS_C_ccw['honorTankiShanpon'] = ryanmen[1]
    # analyzers[0].GS_C_ccw['nonHonorTankiShanpon'] = ryanmen[2]
    # analyzers[0].GS_C_ccw['kanchan'] = ryanmen[3]
    # analyzers[0].GS_C_ccw['kanchanRiichiSujiTrap'] = ryanmen[4]
    # analyzers[0].GS_C_ccw['uraSuji'] = ryanmen[5]
    # analyzers[0].GS_C_ccw['matagiSujiEarly'] = ryanmen[6]
    # analyzers[0].GS_C_ccw['matagiSujiRiichi'] = ryanmen[7]
    # analyzers[0].GS_C_ccw['doraGreed'] = ryanmen[8]

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

tuneMode = False
if tuneMode:
    dim1 = Real(name='ryanmen', low=0.1, high=10)
    dim2 = Real(name='honorTankiShanpon', low=0.1, high=10)
    dim3 = Real(name='nonHonorTankiShanpon', low=0.1, high=10)
    dim4 = Real(name='kanchan', low=0.1, high=10)
    dim5 = Real(name='kanchanRiichiSujiTrap', low=0.1, high=10)
    dim6 = Real(name='uraSuji', low=0.1, high=10)
    dim7 = Real(name='matagiSujiEarly', low=0.1, high=10)
    dim8 = Real(name='matagiSujiRiichi', low=0.1, high=10)
    dim9 = Real(name='doraGreed', low=0.1, high=10)

    dims = [dim1, dim2, dim3, dim4, dim5, dim6, dim7, dim8, dim9]
    res = forest_minimize(func=RunAnalysis, dimensions = dims, n_calls=100)

    print(res)
else:
    #cProfile.run("RunAnalysis()")
    RunAnalysis()
