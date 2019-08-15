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
        print("%s Count,Occurrences" % self.GetName())
        for count in self.counts.most_common():
            print("%s,%d" % count)