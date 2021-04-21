from log_analyzer import LogAnalyzer
from collections import Counter, defaultdict
from analysis_utils import CheckDoubleRon, convertTile, convertHai, discards, draws, GetNextRealTag, getTilesFromCall

class YkmnChuuren(LogAnalyzer):
    def __init__(self):
        self.results = defaultdict(Counter)
        self.max_shanten = 0
        self.max_log = ""

    def ParseLog(self, log, log_id):
        rounds = log.findall('INIT')

        for round_ in rounds:
            for i in range(4):
                hand = convertHai(round_.attrib['hai%d' % i])

                # Add the first drawn tile to the hand
                next_element = round_.getnext()
                no_turn = False
                call = False
                while next_element is not None:
                    name = next_element.tag
                    if name == "UN":
                        next_element = GetNextRealTag(next_element)
                        continue
                    if name[0] == draws[i]:
                        hand[convertTile(name[1:])] += 1
                        break
                    if name == "AGARI" or name == "RYUUKYOKU" or name == "INIT":
                        no_turn = True
                        break
                    if name == "N":
                        if int(next_element.attrib["who"]) == i:
                            tiles = getTilesFromCall(next_element.attrib["m"])
                            hand[tiles[0]] += 1
                            call = True
                            break
                        else:
                            next_element = GetNextRealTag(next_element)
                            continue
                    next_element = GetNextRealTag(next_element)
                
                if no_turn:
                    # Round ended before this player took a turn
                    continue

                while next_element is not None:
                    if next_element.tag == "AGARI" or next_element.tag == "RYUUKYOKU":
                        break
                    if not call and next_element.tag == "N":
                        if int(next_element.attrib["who"]) == i:
                            tiles = getTilesFromCall(next_element.attrib["m"])
                            if len(tiles) < 4:
                                call = True
                    next_element = GetNextRealTag(next_element)
                
                chuuren_tiles = [0,0,0]
                extra = [0,0,0]
                for i in range(0,3):
                    suit = i * 10
                    chuuren_tiles[i] += min(3, hand[suit + 1]) + min(3, hand[suit + 9])
                    if hand[suit + 1] == 4 or hand[suit + 9] == 4:
                        extra[i] = 1
                    
                    for j in range(2,9):
                        if hand[suit + j] > 0:
                            chuuren_tiles[i] += 1
                        if hand[suit + j] > 1:
                            extra[i] = 1

                biggest = chuuren_tiles.index(max(chuuren_tiles))
                shanten = 13 - chuuren_tiles[biggest] - extra[biggest]
                message = "%d-shanten" % shanten

                self.results[message]["Count"] += 1
                if call:
                    self.results[message]["Opened"] += 1

                if next_element.tag == "AGARI" and int(next_element.attrib["who"]) == i:
                    self.results[message]["Wins"] += 1
                    if "yaku" in next_element.attrib:
                        yaku = next_element.attrib['yaku'].split(',')
                        ids = [int(x) for x in yaku[0::2]]
                        
                        if 34 in ids:
                            self.results[message]["Honitsu"] += 1
                        if 35 in ids:
                            self.results[message]["Chinitsu"] += 1
                        if 24 in ids:
                            self.results[message]["Ittsu"] += 1
                    else:
                        yakuman = next_element.attrib['yakuman'].split(',')
                        if "45" in yakuman or "46" in yakuman:
                            self.results[message]["Chuuren"] += 1
                            if shanten > self.max_shanten:
                                self.max_shanten = shanten
                                self.max_log = log_id

    
    def PrintResults(self):
        print(self.max_log)
        keys = ["Count","Wins","Opened","Chuuren","Honitsu","Chinitsu","Ittsu"]

        with open("./results/YkmnChuuren.csv", "w") as c:
            c.write("Shanten,Count,Wins,Opened,Chuuren,Honitsu,Chinitsu,Ittsu\n")
            for pattern in self.results:
                c.write("%s," % pattern)
                for key in keys:
                    c.write("%d," % self.results[pattern][key])
                c.write("\n")

    def GetName(self):
        return "Daisangen Results"