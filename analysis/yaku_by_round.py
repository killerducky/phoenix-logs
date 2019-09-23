from log_by_round import LogByRound

yaku_names = [
    "Tsumo", "Riichi", "Ippatsu", "Chankan", "Rinshan", "Haitei", "Houtei", "Pinfu", "Tanyao", "Iipeikou",
    "Yakuhai Wind", "Yakuhai Wind", "Yakuhai Wind", "Yakuhai Wind", "Yakuhai Wind", "Yakuhai Wind", "Yakuhai Wind", "Yakuhai Wind",
    "Yakuhai Dragon", "Yakuhai Dragon", "Yakuhai Dragon", "Double Riichi", "Chiitoitsu", "Chanta", "Itsu", "Doujun", "Doukou",
    "Sankantsu", "Toitoi", "Sanankou", "Shousangen", "Honroutou", "Ryanpeikou", "Junchan", "Honitsu", "Chinitsu",
    "Renhou", "Tenhou", "Chihou", "Daisangen", "Suuankou", "Suuankou", "Tsuuiisou", "Ryuuiisou", "Chinroutou", "Chuuren", "Chuuren",
    "Kokushi", "Kokushi", "Daisuushi", "Shousuushi", "Suukantsu", "Dora", "Uradora", "Akadora"
]

class YakuByRound(LogByRound):
    def ParseRound(self, start, end):
        if 'yaku' not in end.attrib:
            if 'yakuman' not in end.attrib:
                return
            else:
                yakuman = end.attrib['yakuman'].split(',')[0::2]
                for ykmn in yakuman:
                    self.CountRound(start, yaku_names[int(ykmn)])
                return

        yaku = end.attrib['yaku'].split(',')

        ids = [int(x) for x in yaku[0::2]]
        cnt = [int(x) for x in yaku[1::2]]
        try:
            ura_position = ids.index(53)
            if not cnt[ura_position]:
                del ids[ura_position]
        except:
            pass
        
        for id_ in ids:
            self.CountRound(start, yaku_names[id_])

    def GetName(self):
        return "Yaku By Round"