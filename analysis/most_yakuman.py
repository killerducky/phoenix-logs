# -*- coding: utf-8 -*-
from log_counter import LogCounter

class MostYakuman(LogCounter):
    def ParseLog(self, log, log_id):
        wins = log.findall('AGARI')
        count = 0
        for win in wins:
            if int(win.attrib['ten'].split(',')[2]) >= 5:
                count += 1

        self.Count(count, log_id)
        
    def GetName(self):
        return "Most Yakuman"