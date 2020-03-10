from log_analyzer import LogAnalyzer
from collections import Counter, defaultdict
from analysis_utils import CheckDoubleRon, convertTile, convertHai
from shanten import calculateKokushiShanten

orphans = [
    0, 1, 2, 3, 32, 33, 34, 35,
    36, 37, 38, 39, 68, 69, 70, 71,
    72, 73, 74, 75, 104, 105, 106, 107,
    108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123,
    124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135
]

draws = ['T','U','V','W']

class KokushiResults(LogAnalyzer):
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
                        next_element = next_element.getnext()
                        continue
                    if name[0] == draws[i]:
                        hand[convertTile(name[1:])] += 1
                        break
                    if name == "AGARI" or name == "RYUUKYOKU" or name == "INIT":
                        no_turn = True
                        break
                    if name == "N":
                        if next_element.attrib["who"] == i:
                            no_turn = True
                            break
                        else:
                            next_element = next_element.getnext()
                            call = True
                            continue
                    next_element = next_element.getnext()
                
                if no_turn:
                    # Round ended before this player took a turn
                    break

                kokushi_shanten = calculateKokushiShanten(hand)
                self.results[kokushi_shanten]["Count"] += 1

                if call:
                    self.results[kokushi_shanten]["Call Before First Turn"] += 1

                next_element = round_.getnext()
                while next_element is not None:
                    if next_element.tag == "AGARI" or next_element.tag == "RYUUKYOKU":
                        break
                    next_element = next_element.getnext()

                if next_element.tag == "AGARI":
                    if int(next_element.attrib["who"]) == i:
                        if "yakuman" not in next_element.attrib:
                            self.results[kokushi_shanten]["Won Normal Hand"] += 1
                        else:
                            yakuman = next_element.attrib["yakuman"].split(",")
                            if "47" in yakuman or "48" in yakuman:
                                self.results[kokushi_shanten]["Won Kokushi"] += 1
                            else:
                                self.results[kokushi_shanten]["Won Other Yakuman"] += 1
                
                if next_element.tag == "RYUUKYOKU":
                    if "type" in next_element.attrib:
                        if next_element.attrib["type"] == "yao9":
                            if "hai%d" % i in next_element.attrib:
                                self.results[kokushi_shanten]["Kyuushuu Called"] += 1
    
    def PrintResults(self):
        with open("./results/%s.csv" % self.GetName(), "w") as f:
            print("Shanten,Count,Normal Hand Won,Kokushi Won,Other Yakuman Won,Kyuushuu Called,Call Before First Turn")
            f.write("Shanten,Count,Normal Hand Won,Kokushi Won,Other Yakuman Won,Kyuushuu Called,Call Before First Turn")
            for i in range(14):
                print("%d,%d,%d,%d,%d,%d,%d" % (
                    i,
                    self.results[i]["Count"],
                    self.results[i]["Won Normal Hand"],
                    self.results[i]["Won Kokushi"],
                    self.results[i]["Won Other Yakuman"],
                    self.results[i]["Kyuushuu Called"],
                    self.results[i]["Call Before First Turn"]
                ))

    def GetName(self):
        return "Kokushi Results"