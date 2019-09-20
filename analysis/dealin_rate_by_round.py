from log_by_round import LogByRound

class DealInRateByRound(LogByRound):    
    def ParseRound(self, start, end):
        if end.tag == "AGARI" and end.attrib["fromWho"] != end.attrib["who"]:
            self.CountRound(start, "Rons")
        self.CountRound(start, "Count")
    
    def GetName(self):
        return "Deal-in Rate By Round"