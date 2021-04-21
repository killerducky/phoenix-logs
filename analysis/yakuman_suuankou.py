from log_analyzer import LogAnalyzer
from collections import Counter, defaultdict
from analysis_utils import CheckDoubleRon, convertTile, convertHai, discards, draws, GetNextRealTag, getTilesFromCall

class YkmnSuuankou(LogAnalyzer):
    def __init__(self):
        self.results = defaultdict(Counter)

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
                
                ankou = 0
                pairs = 0
                for i in hand:
                    if i > 2:
                        ankou += 1
                    elif i == 2:
                        pairs += 1
                message = "%d ankou %d pairs" % (ankou, pairs)

                self.results[message]["Count"] += 1
                if call:
                    self.results[message]["Opened"] += 1

                if next_element.tag == "AGARI" and int(next_element.attrib["who"]) == i:
                    self.results[message]["Wins"] += 1
                    if "yaku" in next_element.attrib:
                        yaku = next_element.attrib['yaku'].split(',')
                        ids = [int(x) for x in yaku[0::2]]

                        if 28 in ids:
                            self.results[message]["Toitoi"] += 1
                        if 29 in ids:
                            self.results[message]["Sanankou"] += 1
                        if 22 in ids:
                            self.results[message]["Chiitoi"] += 1
                        if 32 in ids:
                            self.results[message]["Ryanpeikou"] += 1
                    else:
                        yakuman = next_element.attrib['yakuman'].split(',')
                        if "40" in yakuman or "41" in yakuman:
                            self.results[message]["Suuankou"] += 1

    
    def PrintResults(self):
        keys = ["Count","Wins","Opened","Suuankou","Sanankou","Toitoi","Chiitoi","Ryanpeikou"]

        with open("./results/YkmnSuuankou.csv", "w") as c:
            c.write("Pattern,Count,Wins,Opened,Suuankou,Sanankou,Toitoi,Chiitoi,Ryanpeikou\n")
            for pattern in self.results:
                c.write("%s," % pattern)
                for key in keys:
                    c.write("%d," % self.results[pattern][key])
                c.write("\n")

    def GetName(self):
        return "Suuankou Results"