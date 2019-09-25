from log_by_round import LogByRound
from analysis_utils import GetWhoTileWasCalledFrom, getTilesFromCall

class CallRateByRound(LogByRound):    
    def ParseRound(self, start, end):
        current = start.getnext()
        flags = [False, False, False, False]

        while current.tag != "AGARI" and current.tag != "RYUUKYOKU":
            if current.tag == "N":
                tiles = getTilesFromCall(current.attrib["m"])

                if len(tiles) == 1:
                    current = current.getnext()
                    continue

                if GetWhoTileWasCalledFrom(current) != 0:
                    flags[int(current.attrib["who"])] = True
            
            current = current.getnext()
        
        for flag in flags:
            if flag:
                self.CountRound(start, "Players Open")
        
        self.CountRound(start, "Count")
    
    def GetName(self):
        return "Call Rate By Round"