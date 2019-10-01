from log_counter import LogCounter

class FuRates(LogCounter):
    def ParseLog(self, log, log_id):
        wins = log.findall("AGARI")
        
        for win in wins:
            points = win.attrib["ten"].split(",")

            if points[2] == "0":
                self.Count(points[0])
    
    def GetName(self):
        return "Fu Rates"