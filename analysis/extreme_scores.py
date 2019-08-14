# -*- coding: utf-8 -*-
from log_analyzer import LogAnalyzer

class ExtremeScores(LogAnalyzer):
    def __init__(self):
        self.highest_score = 0
        self.highest_id = ""
        self.lowest_score = 0
        self.lowest_id = ""

    def ParseLog(self, log, log_id):
        round_ends = log.findall('AGARI')

        if 'owari' not in round_ends[-1].attrib:
            round_ends = log.findall('RYUUKYOKU')

        scores = list(map(int, round_ends[-1].attrib["owari"].split(",")[0::2]))
        highest = max(scores)
        lowest = min(scores)

        if highest > self.highest_score:
            self.highest_score = highest
            self.highest_id = log_id

        if lowest < self.lowest_score:
            self.lowest_score = lowest
            self.lowest_id = log_id
        
    def PrintResults(self):
        print("Highest Score: %d, replay id: %s" % (self.highest_score * 100, self.highest_id))
        print("Lowest Score: %d, replay id: %s" % (self.lowest_score * 100, self.lowest_id))