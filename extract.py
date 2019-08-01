# -*- coding: utf-8 -*-

import bz2
import pickle
import sqlite3

from lxml import etree

yakulist=[]

with sqlite3.connect('logs/2018.db') as conn:
    cursor = conn.cursor()

    cursor.execute('SELECT log_content FROM logs') #  LIMIT 1000

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
            yaku = win.attrib['yaku'].split(',')
            # id, count, id, count: id 53 is uradora; 37-51 are yakuman
            # riichi 1, pinfu 7, tanyao 8
            # yaku hai 10-20
            ids = [int(x) for x in yaku[0::2]]
            cnt = [int(x) for x in yaku[1::2]]
            try:
                ura_position = ids.index(53)
                if not cnt[ura_position]:
                    del yaku[ura_position]
                    del cnt[ura_position]
            except:
                pass
            yakulist.append(ids)

with open('d:/azps/tenhou/logs/2018ayaku.pickle', 'wb') as f:
    pickle.dump(yakulist, f, protocol=4)

"""
    YAKU = {
        # one-han yaku
        0:'門前清自摸和',     # menzen tsumo
        1:'立直',           # riichi
        2:'一発',           # ippatsu
        3:'槍槓',           # chankan
        4:'嶺上開花',        # rinshan kaihou
        5:'海底摸月',        # haitei raoyue
        6:'河底撈魚',        # houtei raoyui
        7:'平和',           # pinfu
        8:'断幺九',         # tanyao
        9:'一盃口',         # iipeiko
        # seat winds
        10:'自風 東',       # ton
        11:'自風 南',       # nan
        12:'自風 西',       # xia
        13:'自風 北',       # pei
        # round winds
        14:'場風 東',       # ton
        15:'場風 南',       # nan
        16:'場風 西',       # xia
        17:'場風 北',       # pei
        18:'役牌 白',       # haku
        19:'役牌 發',       # hatsu
        20:'役牌 中',       # chun
        # two-han yaku
        21:'両立直',        # daburu riichi
        22:'七対子',        # chiitoitsu
        23:'混全帯幺九',     # chanta
        24:'一気通貫',       # ittsu
        25:'三色同順',       # sanshoku doujun
        26:'三色同刻',       # sanshoku doukou
        27:'三槓子',        # sankantsu
        28:'対々和',        # toitoi
        29:'三暗刻',        # sanankou
        30:'小三元',        # shousangen
        31:'混老頭',        # honroutou
        # three-han yaku
        32:'二盃口',        # ryanpeikou
        33:'純全帯幺九',     # junchan
        34:'混一色',        # honitsu
        # six-han yaku
        35:'清一色',        # chinitsu
        # unused
        36:'人和',          # renhou
        # yakuman
        37:'天和',          # tenhou
        38:'地和',          # chihou
        39:'大三元',        # daisangen
        40:'四暗刻',        # suuankou
        41:'四暗刻単騎',     # suuankou tanki
        42:'字一色',        # tsuuiisou
        43:'緑一色',        # ryuuiisou
        44:'清老頭',        # chinroutou
        45:'九蓮宝燈',       # chuuren pouto
        46:'純正九蓮宝燈',    # chuuren pouto 9-wait
        47:'国士無双',       # kokushi musou
        48:'国士無双１３面',   # kokushi musou 13-wait
        49:'大四喜',        # daisuushi
        50:'小四喜',        # shousuushi
        51:'四槓子',        # suukantsu
        # dora
        52:'ドラ',          # dora
        53:'裏ドラ',         # uradora
        54:'赤ドラ',         # akadora
        }


"""