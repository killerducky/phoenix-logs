from log_analyzer import LogAnalyzer
from collections import Counter, defaultdict
from analysis_utils import CheckDoubleRon, convertTile, convertHai, discards, draws, GetNextRealTag, getTilesFromCall

class YkmnDaisangen(LogAnalyzer):
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
                            break
                        else:
                            next_element = GetNextRealTag(next_element)
                            call = True
                            continue
                    next_element = GetNextRealTag(next_element)
                
                if no_turn:
                    # Round ended before this player took a turn
                    continue

                while next_element is not None:
                    if next_element.tag == "AGARI" or next_element.tag == "RYUUKYOKU":
                        break
                    next_element = GetNextRealTag(next_element)
                
                dragons = [min(3, hand[35]), min(3, hand[36]), min(3, hand[37])]
                dragons.sort()
                dragons.reverse()
                message = "%d-%d-%d" % (dragons[0], dragons[1], dragons[2])

                self.results[message]["Count"] += 1

                if next_element.tag == "AGARI" and int(next_element.attrib["who"]) == i:
                    self.results[message]["Wins"] += 1
                    if "yaku" in next_element.attrib:
                        yaku = next_element.attrib['yaku'].split(',')
                        ids = [int(x) for x in yaku[0::2]]
                        yakuhai_count = 0
                        if 18 in ids:
                            yakuhai_count += 1
                        if 19 in ids:
                            yakuhai_count += 1
                        if 20 in ids:
                            yakuhai_count += 1
                        if yakuhai_count > 0:
                            self.results[message]["%dx Yakuhai" % yakuhai_count] += 1
                        if 28 in ids:
                            self.results[message]["Toitoi"] += 1
                        if 30 in ids:
                            self.results[message]["Shousangen"] += 1
                        if 34 in ids:
                            self.results[message]["Honitsu"] += 1
                    else:
                        yakuman = next_element.attrib['yakuman'].split(',')
                        if "39" in yakuman:
                            self.results[message]["Daisangen"] += 1
                            if message == "0-0-0":
                                print(log_id)
                        if "42" in yakuman:
                            self.results[message]["Tsuuiisou"] += 1

    
    def PrintResults(self):
        keys = ["Count","Wins","Daisangen","Shousangen","1x Yakuhai","2x Yakuhai", "Toitoi", "Honitsu", "Tsuuiisou"]

        with open("./results/YkmnDaisangen.csv", "w") as c:
            c.write("Pattern,Count,Wins,Daisangen,Shousangen,Dragon,2x Dragon,Toitoi,Honitsu,Tsuuiisou\n")
            for pattern in self.results:
                c.write("%s," % pattern)
                for key in keys:
                    c.write("%d," % self.results[pattern][key])
                c.write("\n")

    def GetName(self):
        return "Daisangen Results"