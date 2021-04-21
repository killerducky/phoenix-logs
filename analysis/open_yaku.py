yaku_names = [
    "Tsumo", "Riichi", "Ippatsu", "Chankan", "Rinshan", "Haitei", "Houtei", "Pinfu", "Tanyao", "Iipeikou",
    "Yakuhai", "Yakuhai", "Yakuhai", "Yakuhai", "Yakuhai", "Yakuhai", "Yakuhai", "Yakuhai",
    "Yakuhai", "Yakuhai", "Yakuhai", "Double Riichi", "Chiitoitsu", "Chanta", "Ittsu", "Doujun", "Doukou",
    "Sankantsu", "Toitoi", "Sanankou", "Shousangen", "Honroutou", "Ryanpeikou", "Junchan", "Honitsu", "Chinitsu",
    "Renhou", "Tenhou", "Chihou", "Daisangen", "Suuankou", "Suuankou", "Tsuuiisou", "Ryuuiisou", "Chinroutou", "Chuuren", "Chuuren",
    "Kokushi", "Kokushi", "Daisuushi", "Shousuushi", "Suukantsu", "Dora", "Uradora", "Akadora"
]

from log_counter import LogCounter
from analysis_utils import convertHai, CheckIfWinIsClosed, CheckIfWinWasRiichi

class OpenYakuRates(LogCounter): 
    def ParseLog(self, log, log_id):
        wins = log.findall("AGARI")

        for win in wins:
            if 'yaku' not in win.attrib:
                continue
            if not CheckIfWinWasRiichi(win):
                continue
            
            yaku = win.attrib['yaku'].split(',')
            ids = [int(x) for x in yaku[0::2]]

            self.Count("Hands")
            found_yaku = []
            for id_ in ids:
                found_yaku.append(yaku_names[id_])
            yaku_no_duplicates = list(dict.fromkeys(found_yaku))
            for name in yaku_no_duplicates:
                self.Count(name)
    
    def GetName(self):
        return "RiichiYakuRates"