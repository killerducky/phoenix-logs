from log_by_round import LogByRound

class RiichiByRound(LogByRound):    
    def ParseRound(self, start, end):
        current = start.getnext()
        flags = [False, False, False, False]

        while current.tag != "AGARI" and current.tag != "RYUUKYOKU":
            if current.tag == "REACH":
                flags[int(current.attrib["who"])] = True
            
            current = current.getnext()
        
        for flag in flags:
            if flag:
                self.CountRound(start, "Riichis")
        
        self.CountRound(start, "Count")
    
    def GetName(self):
        return "Riichi Rate By Round"