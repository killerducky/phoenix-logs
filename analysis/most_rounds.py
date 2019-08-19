# -*- coding: utf-8 -*-

from log_count_and_max import LogCountAndMax

class MostRounds(LogCountAndMax):
    def ParseLog(self, log, log_id):
        rounds = log.findall('INIT')
        self.Count(len(rounds), log_id)

    def GetName(self):
        return "Round"
