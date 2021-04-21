from log_analyzer import LogAnalyzer
from collections import defaultdict, Counter
from analysis_utils import round_names, GetNextRealTag, discards, GetRoundNameWithoutRepeats

class ChasingRiichis(LogAnalyzer):    
    def __init__(self):
        super().__init__()
        self.riichis = defaultdict(Counter)
        self.chased_after = defaultdict(Counter)

        for name in round_names:
            self.riichis[name][0] = 0
            self.chased_after[name][0] = 0

    def ParseLog(self, log, log_id):
        rounds = log.findall("INIT")

        for _round in rounds:
            first_riichi_turn = -1
            discarded_tiles = 0

            next_element = GetNextRealTag(_round)

            while next_element is not None:
                if next_element.tag == "DORA":
                    pass
                elif next_element.tag[0] in discards:
                    discarded_tiles += 1
                elif next_element.tag == "REACH":
                    if first_riichi_turn < 0 and next_element.attrib["step"] == "2":
                        first_riichi_turn = int(discarded_tiles / 4)
                        self.riichis[GetRoundNameWithoutRepeats(_round)][first_riichi_turn] += 1
                    elif first_riichi_turn > -1:
                        self.chased_after[GetRoundNameWithoutRepeats(_round)][first_riichi_turn] += 1
                        break
                elif next_element.tag == "INIT":
                    break
                next_element = GetNextRealTag(next_element)
            
    def PrintResults(self):
        with open("./results/ChasingRiichisCount.csv", "w") as f:
            f.write("Round,0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18\n")
            for i in self.riichis:
                f.write("%s," % i)
                for j in range(19):
                    f.write("%d," % self.riichis[i][j])
                f.write("\n")
        
        with open("./results/ChasingRiichisChases.csv", "w") as f:
            f.write("Round,0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18\n")
            for i in self.chased_after:
                f.write("%s," % i)
                for j in range(19):
                    f.write("%d," % self.chased_after[i][j])
                f.write("\n")