# -*- coding: utf-8 -*-
from collections import Counter
from log_count_and_max import LogCountAndMax

class MostDealins(LogCountAndMax):
    def __init__(self):
        super().__init__()
        self.who_counter = Counter()

    def ParseLog(self, log, log_id):
        self.who_counter.clear()
        wins = log.findall('AGARI')

        for win in wins:
            if win.attrib['who'] == win.attrib['fromWho']:
                continue
            else:
                self.who_counter[win.attrib['fromWho']] += 1
        
        self.Count(self.who_counter["0"], log_id)
        self.Count(self.who_counter["1"], log_id)
        self.Count(self.who_counter["2"], log_id)
        self.Count(self.who_counter["3"], log_id)
        
    def GetName(self):
        return "Deal-in"