from log_counter import LogCounter
from analysis_utils import GetRoundName

class GameLength(LogCounter):
    def ParseLog(self, log, log_id):
        rounds = log.findall("INIT")
        last_round = rounds[-1]
        self.Count(GetRoundName(last_round))
        self.Count("Games")
        self.counts["Total Rounds"] += len(rounds)
    
    def GetName(self):
        return "Final Round"