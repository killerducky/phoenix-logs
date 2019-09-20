from log_analyzer import LogAnalyzer
from collections import Counter, defaultdict
from urllib.parse import unquote

class GenderCount(LogAnalyzer):
    def __init__(self):
        self.players = defaultdict(Counter)

    def ParseLog(self, log, log_id):
        data = log.find("UN")
        names = [data.attrib["n0"], data.attrib["n1"], data.attrib["n2"], data.attrib["n3"]]
        genders = data.attrib["sx"].split(",")

        for i in range(4):
            name = unquote(names[i])
            self.players[name][genders[i]] += 1
    
    def PrintResults(self):
        with open("./results/GenderCounts.csv", "w", encoding="utf8") as f:
            f.write("Name,Male,Female\n")

            for player in self.players:
                f.write("%s,%d,%d\n" % (player, self.players[player]["M"], self.players[player]["F"]))