from log_analyzer import LogAnalyzer
from analysis_utils import convertTile, CheckIfWinWasRiichi, CheckIfWinIsClosed, CheckIfWinWasDealer
from collections import defaultdict, Counter

class DealinByTile(LogAnalyzer):
    def __init__(self):
        super().__init__()
        self.data = defaultdict(Counter)

    def ParseLog(self, log, log_id):
        wins = log.findall("AGARI")

        for win in wins:
            if win.attrib["who"] == win.attrib["fromWho"]:
                continue

            winning_tile = convertTile(win.attrib["machi"])

            if winning_tile < 30 and winning_tile % 10 == 5 and int(win.attrib["machi"]) % 4 == 0:
                winning_tile -= 5

            if winning_tile < 30:
                winning_tile = winning_tile % 10
                
            score = int(win.attrib["ten"].split(",")[1])

            dealer = CheckIfWinWasDealer(win)

            if CheckIfWinWasRiichi(win):
                if (dealer):
                    self.data["Count %d" % winning_tile]["Dealer Riichi"] += 1
                    self.data["Score %d" % winning_tile]["Dealer Riichi"] += score
                else:
                    self.data["Count %d" % winning_tile]["Riichi"] += 1
                    self.data["Score %d" % winning_tile]["Riichi"] += score
            else:
                if CheckIfWinIsClosed(win):
                    if (dealer):
                        self.data["Count %d" % winning_tile]["Dealer Dama"] += 1
                        self.data["Score %d" % winning_tile]["Dealer Dama"] += score
                    else:
                        self.data["Count %d" % winning_tile]["Dama"] += 1
                        self.data["Score %d" % winning_tile]["Dama"] += score
                else:
                    if (dealer):
                        self.data["Count %d" % winning_tile]["Dealer Open"] += 1
                        self.data["Score %d" % winning_tile]["Dealer Open"] += score
                    else:
                        self.data["Count %d" % winning_tile]["Open"] += 1
                        self.data["Score %d" % winning_tile]["Open"] += score
            
    def PrintResults(self):
        with open("./results/DealinByTile.csv", "w", encoding="utf8") as f:
            f.write("Tile,Count,Riichi,Dama,Open,Dealer Riichi,Dealer Dama,Dealer Open\n")

            order = ["Riichi", "Dama", "Open", "Dealer Riichi", "Dealer Dama", "Dealer Open"]
            for tile in self.data:
                f.write("%s," % tile)
                for win in order:
                    f.write("%d," % self.data[tile][win])
                f.write("\n")