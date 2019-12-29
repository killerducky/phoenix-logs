from log_counter import LogCounter
from itertools import combinations

yaku_names = [
    "Tsumo", "Riichi", "Ippatsu", "Chankan", "Rinshan", "Haitei", "Houtei", "Pinfu", "Tanyao", "Iipeikou",
    "Yakuhai Wind", "Yakuhai Wind", "Yakuhai Wind", "Yakuhai Wind", "Yakuhai Wind", "Yakuhai Wind", "Yakuhai Wind", "Yakuhai Wind",
    "Yakuhai Dragon", "Yakuhai Dragon", "Yakuhai Dragon", "Double Riichi", "Chiitoitsu", "Chanta", "Itsu", "Doujun", "Doukou",
    "Sankantsu", "Toitoi", "Sanankou", "Shousangen", "Honroutou", "Ryanpeikou", "Junchan", "Honitsu", "Chinitsu",
    "Renhou", "Tenhou", "Chihou", "Daisangen", "Suuankou", "Suuankou", "Tsuuiisou", "Ryuuiisou", "Chinroutou", "Chuuren", "Chuuren",
    "Kokushi", "Kokushi", "Daisuushi", "Shousuushi", "Suukantsu", "Dora", "Uradora", "Akadora"
]

class PowerCouples(LogCounter):
    def ParseLog(self, log, log_id):
        wins = log.findall("AGARI")

        for win in wins:
            if "yaku" not in win.attrib:
                continue

            yaku = win.attrib['yaku'].split(',')
            ids = [int(x) for x in yaku[0::2]]
            cnt = [int(x) for x in yaku[1::2]]

            # Ura is always present on a riichi win, so remove it if it's 0 ura
            try:
                ura_position = ids.index(53)
                if not cnt[ura_position]:
                    del ids[ura_position]
            except:
                pass
            
            for id_ in ids:
                self.Count(yaku_names[id_])

            if len(ids) < 2:
                continue
            
            pairs = combinations(ids, 2)

            for pair in pairs:
                self.Count("%s + %s" % (yaku_names[pair[0]], yaku_names[pair[1]]))

    def GetName(self):
        return "Power Couples"