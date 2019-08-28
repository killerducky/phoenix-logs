from log_counter import LogCounter
from analysis_utils import CheckIfWinIsClosed, CheckIfWinWasRiichi, convertTile

yakuman_names = [
    "Tenhou", "Chihou", "Daisangen", "Suuankou", "Suuankou Tanki", "Tsuiisou", "Ryuuiisou", "Chinroutou",
    "Chuuren", "Pure Chuuren", "Kokushi", "Pure Kokushi", "Daisuushii", "Shousuushii", "Suukantsu"
]

class RonRateByValue(LogCounter):
    def ParseLog(self, log, log_id):
        wins = log.findall("AGARI")

        for win in wins:
            tsumo = win.attrib["who"] == win.attrib["fromWho"]
            closed = CheckIfWinIsClosed(win)
            riichi = False
            if closed:
                riichi = CheckIfWinWasRiichi(win)
            
            if "yakuman" in win.attrib:
                yakuman = win.attrib["yakuman"].split(",")

                if len(yakuman) > 1:
                    self.LogResult(tsumo, closed, riichi, "Multiple Yakuman", "Yakuman ")
                else:
                    self.LogResult(tsumo, closed, riichi, yakuman_names[int(yakuman[0]) - 37], "Yakuman ")
            elif "yaku" in win.attrib:
                yaku = win.attrib["yaku"].split(",")
                ids = [int(x) for x in yaku[0::2]]
                cnt = [int(x) for x in yaku[1::2]]
                han = sum(cnt)
                adjusted_han = han

                try:
                    ura_position = ids.index(53)
                    adjusted_han -= cnt[ura_position]
                except:
                    pass
                try:
                    ippatsu_position = ids.index(2)
                    adjusted_han -= cnt[ippatsu_position]
                except:
                    pass
                try:
                    tsumo_position = ids.index(0)
                    adjusted_han -= cnt[tsumo_position]
                except:
                    pass

                winning_tile = int(win.attrib["machi"])
                converted_tile = convertTile(winning_tile)
                if converted_tile % 10 == 5:
                    if winning_tile % 4 == 0:
                        # Tsumo'd an aka dora
                        adjusted_han -= 1

                self.LogResult(tsumo, closed, riichi, "%d Han" % han)
                self.LogResult(tsumo, closed, riichi, "%d Han" % adjusted_han, "Luckless ")

    def GetName(self):
        return "Win Type By Value"

    def LogResult(self, tsumo, closed, riichi, point, prefix = ""):
        if tsumo:
            if closed:
                if riichi:
                    self.Count("%sTsumo Closed Riichi %s" % (prefix, point))
                else:
                    self.Count("%sTsumo Closed Dama %s" % (prefix, point))
            else:
                self.Count("%sTsumo Open %s" % (prefix, point))
        else:
            if closed:
                if riichi:
                    self.Count("%sRon Closed Riichi %s" % (prefix, point))
                else:
                    self.Count("%sRon Closed Dama %s" % (prefix, point))
            else:
                self.Count("%sRon Open %s" % (prefix, point))