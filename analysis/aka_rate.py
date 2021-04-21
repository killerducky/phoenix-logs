from log_counter import LogCounter
from analysis_utils import convertTile

class AkaRate(LogCounter):
    def ParseLog(self, log, log_id):
        ends = log.findall("AGARI")
        for end in ends:
            wait = int(end.attrib["machi"])
            tile = convertTile(wait)
            if tile < 30 and tile % 10 == 5:
                self.Count("Five")
                if wait % 4 == 0:
                    self.Count("Aka")

    def GetName(self):
        return "Aka Rate"
        