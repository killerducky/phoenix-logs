from log_counter import LogCounter
from score_calculation import calculateBasicPoints
from analysis_utils import CheckIfWinWasDealer, CheckIfWinWasRiichi, convertTile
import math

discard_tags = ["D", "E", "F", "G"]

dora_indication = [
     6, 2, 3, 4, 5, 6, 7, 8, 9, 1,
    16,12,13,14,15,16,17,18,19,11,
    26,22,23,24,25,26,27,28,29,21,
    30,32,33,34,31,36,37,35
]

terminals = [1, 9, 11, 19, 21, 29]
honors = [31, 32, 33, 34, 35, 36, 37]
two_eight = [2, 8, 12, 18, 22, 18]

class RiichiValue(LogCounter):
    def ParseLog(self, log, log_id):
        wins = log.findall("AGARI")
        
        for win in wins:
            if not "yaku" in win.attrib:
                continue
            if not CheckIfWinWasRiichi(win):
                continue

            # Check how long ago the riichi was
            discards_since_riichi = 0
            dora = dora_indication[convertTile(win.attrib["doraHai"].split(",")[0])]
            dora_discarded_after_riichi = 0
            winner = win.attrib["who"]
            previous = win.getprevious()

            while previous is not None:
                if previous.tag == "REACH" and previous.attrib["who"] == winner:
                    break

                if previous.tag == "DORA":
                    previous = previous.getprevious()
                    continue

                if previous.tag[0] in discard_tags:
                    discards_since_riichi += 1
                    discard = convertTile(previous.tag[1:])
                    if discard == dora:
                        dora_discarded_after_riichi += 1
                    # Check if red five
                    if discard % 10 == 5 and int(previous.tag[1:]) / 4 == 0:
                        dora_discarded_after_riichi += 1

                
                previous = previous.getprevious()
            
            # Find what turn the riichi happened, as well as the dora visible at riichi
            discards_before_riichi = 0
            dora_discarded_before_riichi = 0

            # Check if the dora indicator is a red five
            doras = win.attrib["doraHai"].split(",")

            for indicator in doras:
                if convertTile(indicator) % 10 == 5 and int(indicator) / 4 == 0:
                    dora_discarded_before_riichi += 1

            while previous is not None:
                if previous.tag == "INIT":
                    dora = dora_indication[convertTile(previous.attrib["seed"].split(",")[5])]
                    break

                if previous.tag == "DORA":
                    previous = previous.getprevious()
                    continue

                if previous.tag[0] in discard_tags:
                    discards_before_riichi += 1
                    discard = convertTile(previous.tag[1:])
                    if discard == dora:
                        dora_discarded_before_riichi += 1
                    # Check if red five
                    if discard % 10 == 5 and int(previous.tag[1:]) / 4 == 0:
                        dora_discarded_before_riichi += 1
                
                previous = previous.getprevious()

            points = int(win.attrib["ten"].split(",")[1])
            dealer = CheckIfWinWasDealer(win)

            riichi_turn = math.ceil(discards_before_riichi / 4)
            win_turn = math.ceil((discards_before_riichi + discards_since_riichi) / 4)

            yaku = win.attrib["yaku"].split(",")
            ids = [int(x) for x in yaku[0::2]]
            cnt = [int(x) for x in yaku[1::2]]

            ippatsu = False

            if 2 in ids:
                ippatsu = True

            tsumo = win.attrib["who"] == win.attrib["fromWho"]
            ron_value = points

            if tsumo:
                fu = int(win.attrib["ten"].split(",")[0])
                han = sum(cnt) - 1 # Remove the han from tsumo
                basic_points = calculateBasicPoints(han, fu, 0)
                if dealer:
                    ron_value = basic_points * 6
                else:
                    ron_value = basic_points * 4

            total_visible_dora = dora_discarded_after_riichi + dora_discarded_before_riichi

            dora_text = "Middle"
            if dora in terminals:
                dora_text = "Terminal"
            elif dora in honors:
                dora_text = "Honor"
            elif dora in two_eight:
                dora_text = "Two/Eight"
            
            self.Count("%d,%d,%d,%d,%d,%d,%s,%d,%d" %
                (int(dealer), riichi_turn, win_turn, dora_discarded_before_riichi, total_visible_dora, int(ippatsu), dora_text, points, ron_value)
            )
    
    def GetName(self):
        return "Dealer,Riichi Turn,Win Turn,Dora At Riichi,Dora At Win,Ippatsu,Dora Type,Value,Ron Value,"