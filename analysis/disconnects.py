from analysis_utils import convertTile, discards, GetPreviousRealTag, GetNextRealTag, GetRoundNameWithoutRepeats
from log_analyzer import LogAnalyzer
from collections import defaultdict, Counter
from math import ceil

class Disconnects(LogAnalyzer):
    def __init__(self):
        self.turns = defaultdict(Counter)
        self.rounds = defaultdict(Counter)

    def ParseLog(self, log, log_id):
        disconnects = log.findall("BYE")

        listTree = list(log)
        lastElement = listTree[-1]
        if 'owari' not in lastElement.attrib:
            print(log_id)
            return

        init = log.find("INIT")
        discards_while_disconnected = [False, False, False, False]
        first_disconnect = ["Never", "Never", "Never", "Never"]

        for disconnect in disconnects:
            player = int(disconnect.attrib["who"])
            discards_while_disconnected[player] = True
            discarded_tiles = 0
            
            next_element = disconnect.getnext()

            while next_element is not None:
                if next_element.tag == "DORA":
                    next_element = next_element.getnext()
                    continue
                elif next_element.tag[0] in discards:
                    discarded_tiles += 1
                elif next_element.tag == "UN":
                    if "n%d" % player in next_element.attrib:
                        break
                next_element = next_element.getnext()
            
            discards_while_disconnected[player] += discarded_tiles

            if discarded_tiles > 0 and first_disconnect[player] == "Never":
                previous = disconnect.getprevious()

                while previous is not None:
                    if previous.tag == "INIT":
                        break
                    previous = previous.getprevious()
                
                round_number = ""

                if previous is None:
                    round_number = "East 1"    
                else:
                    round_number = GetRoundNameWithoutRepeats(previous)
                    
                first_disconnect[player] = round_number
            
        scores = list(map(int, lastElement.attrib["owari"].split(",")[0::2]))
        sorted_scores = scores.copy()
        sorted_scores.sort(reverse=True)

        for i in range(4):
            placement = sorted_scores.index(scores[i]) + 1
            self.turns[ceil(discards_while_disconnected[i] / 4)][placement] += 1
            self.rounds[first_disconnect[i]][placement] += 1

    def PrintResults(self):
        with open("./results/DisconnectedTurns.csv", "w") as f:
            f.write("Turns Disconnected,First,Second,Third,Fourth\n")
            for i in self.turns:
                f.write("%d," % i)
                for j in range(1,5):
                    f.write("%d," % self.turns[i][j])
                f.write("\n")

        with open("./results/DisconnectedRound.csv", "w") as f:
            f.write("Round Disconnected,First,Second,Third,Fourth\n")
            for i in self.rounds:
                f.write("%s," % i)
                for j in range(1,5):
                    f.write("%d," % self.rounds[i][j])
                f.write("\n")