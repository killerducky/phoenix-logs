from log_analyzer import LogAnalyzer
from collections import Counter, defaultdict
from urllib.parse import unquote

class DanRanks(LogAnalyzer):
    def __init__(self):
        self.player_data = defaultdict(Counter)

    def ParseLog(self, log, log_id):
        data = log.find("UN")
        ranks = data.attrib["dan"].split(",")

        for i in range(4):
            if int(ranks[i]) > 16:
                self.player_data[unquote(data.attrib["n%d" % i])][ranks[i]] += 1
            
    def PrintResults(self):
        print("Name,8d,9d,10d,Tenhoui")
        
        with open("./results/DanRanks.csv", "w", encoding="utf8") as f:
            f.write("Name,8d,9d,10d,Tenhoui\n")

            for player in self.player_data:
                print("%s,%d,%d,%d,%d" % (
                    player,
                    self.player_data[player]["17"],
                    self.player_data[player]["18"],
                    self.player_data[player]["19"],
                    self.player_data[player]["20"],
                    )
                )
                f.write("%s,%d,%d,%d,%d\n" % (
                    player,
                    self.player_data[player]["17"],
                    self.player_data[player]["18"],
                    self.player_data[player]["19"],
                    self.player_data[player]["20"],
                    )
                )