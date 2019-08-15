# -*- coding: utf-8 -*-
from collections import Counter
from abc import abstractmethod
from log_analyzer import LogAnalyzer

class LogCounter(LogAnalyzer):
    def __init__(self):
        self.counts = Counter()

    @abstractmethod
    def GetName(self):
        pass

    def Count(self, count):
        self.counts[count] += 1
        
    def PrintResults(self):
        with open("./results/%s.csv" % self.GetName(), "w") as f:
            print("%s Count,Occurrences" % self.GetName())
            f.write("%s Count,Occurrences\n" % self.GetName())
            for count in self.counts.most_common():
                print("%s,%d" % count)
                f.write("%s,%d\n" % count)
