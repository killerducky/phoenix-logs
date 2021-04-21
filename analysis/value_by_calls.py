from log_analyzer import LogAnalyzer
from collections import defaultdict, Counter
from analysis_utils import CheckIfWinWasDealer

class ValueByCalls(LogAnalyzer):
    def __init__(self):
        self.data = defaultdict(Counter)

    def ParseLog(self, log, log_id):
        wins = log.findall("AGARI")

        for win in wins:
            if "m" in win.attrib:
                num_calls = len(win.attrib["m"].split(","))
                if num_calls > 4: 
                    print(log_id)
                
                score = int(win.attrib["ten"].split(",")[1])

                is_dealer = CheckIfWinWasDealer(win)

                key = "Non-Dealer %d" % num_calls

                if is_dealer:
                    key = "Dealer %d" % num_calls

                self.data[key]["Count"] += 1
                self.data[key]["Value"] += score

    def PrintResults(self):
        with open("./results/ValueByCalls.csv", "w") as f:
            f.write("Type,Count,Value\n")
            for i in self.data:
                f.write("%s,%d,%d,\n" % (
                    i,
                    self.data[i]["Count"],
                    self.data[i]["Value"]
                ))