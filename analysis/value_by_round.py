from log_by_round import LogByRound

class ValueByRound(LogByRound):    
    def ParseRound(self, start, end):
        if end.tag == "AGARI":
            if start.attrib["oya"] == end.attrib["who"]:
                self.CountRound(start, "Dealer Total Value", int(end.attrib["ten"].split(",")[1]))
                self.CountRound(start, "Dealer Count")
            else:
                self.CountRound(start, "Non-Dealer Total Value", int(end.attrib["ten"].split(",")[1]))
                self.CountRound(start, "Non-Dealer Count")
    
    def GetName(self):
        return "Value By Round"