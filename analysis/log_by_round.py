from log_analyzer import LogAnalyzer
from collections import Counter
from analysis_utils import GetRoundNameWithoutRepeats, CheckDoubleRon
from abc import abstractmethod

class LogByRound(LogAnalyzer):
    def __init__(self):
        self.rounds = dict()

    def ParseLog(self, log, log_id):
        starts = log.findall("INIT")
        ends = [ x for x in log.xpath("//*[self::AGARI or self::RYUUKYOKU]") if not CheckDoubleRon(x) ]

        for i in range(len(starts)):
            self.ParseRound(starts[i], ends[i])
    
    @abstractmethod
    def ParseRound(self, start, end):
        pass

    @abstractmethod
    def GetName(self):
        pass

    def CountRound(self, start, key, amount = 1):
        round_name = GetRoundNameWithoutRepeats(start)

        if round_name not in self.rounds:
            self.rounds[round_name] = Counter()

        self.rounds[round_name][key] += amount

    def PrintResults(self):
        print(self.GetName())
        with open("./results/%s.csv" % self.GetName(), "w") as f:
            print("Round,", end="")
            f.write("Round,")

            keys = []
            for key in self.rounds["East 1"]:
                keys.append(key)
                print(key, end=",")
                f.write("%s," % key)

            print()
            f.write("\n")

            for round_ in self.rounds:
                print(round_, end=",")
                f.write("%s," % round_)
                for key in keys:
                    f.write("%s," % self.rounds[round_][key])
                    print(self.rounds[round_][key], end=",")
                print()
                f.write("\n")