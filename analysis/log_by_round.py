from log_analyzer import LogAnalyzer
from collections import Counter
from analysis_utils import GetRoundName

class LogByRound(LogAnalyzer):
    def __init__(self):
        self.rounds = Counter()

    def CountRound(self, init):
        self.rounds[GetRoundName(init).split("-")[0]] += 1
    
    def PrintResults(self):
        print("Round,Count")
        for key in self.rounds:
            print("%s,%d" % (key, self.rounds[key]))