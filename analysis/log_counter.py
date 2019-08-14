# -*- coding: utf-8 -*-
from collections import Counter
from abc import abstractmethod
from log_analyzer import LogAnalyzer

class LogCounter(LogAnalyzer):
    def __init__(self):
        self.counts = Counter()
        self.highest = 0
        self.highest_id = ""

    @abstractmethod
    def GetName(self):
        pass

    def Count(self, count, log_id):
        self.counts[count] += 1

        if count > self.highest:
            self.highest = count
            self.highest_id = log_id
        
    def PrintResults(self):
        print("%s Count,Occurrences" % self.GetName())
        for count in self.counts.most_common():
            print("%s,%d" % count)
        print("Most: %d, replay id: %s" % (self.highest, self.highest_id))