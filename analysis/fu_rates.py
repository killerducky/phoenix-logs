from log_counter import LogCounter
from analysis_utils import CheckIfWinWasDealer

class FuRates(LogCounter):
    def ParseLog(self, log, log_id):
        wins = log.findall("AGARI")
        
        for win in wins:
            points = win.attrib["ten"].split(",")
            dealer = CheckIfWinWasDealer(win)

            if points[2] == "0":
                han = [int(x) for x in win.attrib["yaku"].split(",")[1::2]]
                
                if dealer:
                    self.Count("Dealer %s han %s fu" % (sum(han), points[0]))
                else:
                    self.Count("Nondealer %s han %s fu" % (sum(han), points[0]))
    
    def GetName(self):
        return "Fu Rates"