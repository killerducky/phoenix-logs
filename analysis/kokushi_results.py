from log_analyzer import LogAnalyzer
from collections import Counter, defaultdict
from analysis_utils import CheckDoubleRon, convertTile, convertHai

orphans = [
    0, 1, 2, 3, 32, 33, 34, 35,
    36, 37, 38, 39, 68, 69, 70, 71,
    72, 73, 74, 75, 104, 105, 106, 107,
    108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123,
    124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135
]

draws = ['T', 'U', 'V', 'W']
discards = ['D', 'E', 'F', 'G']
NUM_PLAYERS = 4

def calculateKokushiShanten(handToCheck):
    uniqueTiles = 0
    hasPair = 0

    for i in range(1, len(handToCheck)):
        if i % 10 == 1 or i % 10 == 9 or i > 30:
            if handToCheck[i] != 0:
                uniqueTiles += 1

                if handToCheck[i] >= 2:
                    hasPair = 1
               
    return (13 - uniqueTiles - hasPair, uniqueTiles)

class KokushiResults(LogAnalyzer):
    def __init__(self):
        self.results = defaultdict(Counter)

    def ParseLog(self, log, log_id):
        rounds = log.findall('INIT')

        for round_ in rounds:
            for i in range(NUM_PLAYERS):
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
                    continue

                kokushi_shanten = calculateKokushiShanten(hand)
                message = "%d tiles %d types" % (13 - kokushi_shanten[0], kokushi_shanten[1])
                self.results[message]["Count"] += 1

                if call:
                    self.results[message]["Call Before First Turn"] += 1

                next_element = round_.getnext()
                discard_count = 0
                abandoned = False
                riichi = False
                previous_uniques = kokushi_shanten[1]
                while next_element is not None:
                    name = next_element.tag
                    if name == "UN" or name == "DORA":
                        next_element = next_element.getnext()
                        continue
                    if previous_uniques > 6 and not riichi and not abandoned and discard_count < 6:
                        if name[0] == draws[i]:
                            hand[convertTile(name[1:])] += 1
                        if name[0] == discards[i]:
                            discard_count += 1
                            hand[convertTile(name[1:])] -= 1
                            new_uniques = calculateKokushiShanten(hand)[1]
                            if new_uniques < previous_uniques:
                                abandoned = True
                            previous_shanten = new_uniques
                    if name == "REACH":
                        riichi = True
                    if name == "AGARI" or name == "RYUUKYOKU":
                        break
                    next_element = next_element.getnext()

                if abandoned == True:
                    self.results[message]["Abandoned"] += 1
                    self.results[message]["Abandoned on turn %d" % discard_count] += 1

                if next_element.tag == "AGARI":
                    if int(next_element.attrib["who"]) == i:
                        if "yakuman" not in next_element.attrib:
                            self.results[message]["Won Normal Hand"] += 1
                        else:
                            yakuman = next_element.attrib["yakuman"].split(",")
                            if "47" in yakuman or "48" in yakuman:
                                self.results[message]["Won Kokushi"] += 1
                            else:
                                self.results[message]["Won Other Yakuman"] += 1
                
                if next_element.tag == "RYUUKYOKU":
                    if "type" in next_element.attrib:
                        if next_element.attrib["type"] == "yao9":
                            if "hai%d" % i in next_element.attrib:
                                self.results[message]["Kyuushuu Called"] += 1
    
    def PrintResults(self):
        with open("./results/%s.csv" % self.GetName(), "w") as f:
            print("Start,Count,Normal Hand Won,Kokushi Won,Other Yakuman Won,Kyuushuu Called,Call Before First Turn,Abandoned,D1,D2,D3,D4,D5,D6")
            f.write("Start,Count,Normal Hand Won,Kokushi Won,Other Yakuman Won,Kyuushuu Called,Call Before First Turn,Abandoned,D1,D2,D3,D4,D5,D6\n")
            for i in self.results:
                print("%s,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d" % (
                    i,
                    self.results[i]["Count"],
                    self.results[i]["Won Normal Hand"],
                    self.results[i]["Won Kokushi"],
                    self.results[i]["Won Other Yakuman"],
                    self.results[i]["Kyuushuu Called"],
                    self.results[i]["Call Before First Turn"],
                    self.results[i]["Abandoned"],
                    self.results[i]["Abandoned on turn 1"],
                    self.results[i]["Abandoned on turn 2"],
                    self.results[i]["Abandoned on turn 3"],
                    self.results[i]["Abandoned on turn 4"],
                    self.results[i]["Abandoned on turn 5"],
                    self.results[i]["Abandoned on turn 6"]
                ))
                f.write("%s,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d\n" % (
                    i,
                    self.results[i]["Count"],
                    self.results[i]["Won Normal Hand"],
                    self.results[i]["Won Kokushi"],
                    self.results[i]["Won Other Yakuman"],
                    self.results[i]["Kyuushuu Called"],
                    self.results[i]["Call Before First Turn"],
                    self.results[i]["Abandoned"],
                    self.results[i]["Abandoned on turn 1"],
                    self.results[i]["Abandoned on turn 2"],
                    self.results[i]["Abandoned on turn 3"],
                    self.results[i]["Abandoned on turn 4"],
                    self.results[i]["Abandoned on turn 5"],
                    self.results[i]["Abandoned on turn 6"]
                ))

    def GetName(self):
        return "Kokushi Results %d Player" % NUM_PLAYERS