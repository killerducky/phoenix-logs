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

unimportant_ids = [0, 1, 2, 3, 4, 5, 6, 52, 53, 54]

class PowerCouples(LogCounter):
    def ParseLog(self, log, log_id):
        wins = log.findall("AGARI")

        for win in wins:
            if "yaku" not in win.attrib:
                continue

            yaku = win.attrib['yaku'].split(',')
            ids = [int(x) for x in yaku[0::2]]
            actual_ids = ids.copy()

            for id_ in ids:
                if id_ in unimportant_ids:
                    actual_ids.remove(id_)
            
            if len(actual_ids) < 2:
                continue

            pairs = combinations(actual_ids, 2)

            for pair in pairs:
                self.Count("%s + %s" % (yaku_names[pair[0]], yaku_names[pair[1]]))

    def GetName(self):
        return "Power Couples"