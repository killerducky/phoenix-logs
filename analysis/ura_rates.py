from log_analyzer import LogAnalyzer
from analysis_utils import convertHai, CheckIfWinWasRiichi
from collections import Counter, defaultdict

class UraRates(LogAnalyzer):
    def __init__(self):
        self.ura = defaultdict(Counter)
    
    def ParseLog(self, log, log_id):
        wins = log.findall("AGARI")

        for win in wins:
            if "yakuman" in win.attrib:
                continue
            if not CheckIfWinWasRiichi(win):
                continue

            hand = convertHai(win.attrib["hai"])
            unique_tiles = 0
            for tile in hand:
                if tile > 0:
                    unique_tiles += 1
            
            if "m" in win.attrib:
                continue
                unique_tiles += len(win.attrib["m"].split(","))
            
            indicators = len(win.attrib["doraHai"].split(","))

            yaku = win.attrib['yaku'].split(',')
            ids = [int(x) for x in yaku[0::2]]
            han = [int(x) for x in yaku[1::2]]

            try:
                ura_position = ids.index(53)
                self.ura["%d ura %d ind" % (han[ura_position], indicators)][unique_tiles] += 1
            except:
                # No uradora in list...?
                print(log_id)
    
    def PrintResults(self):
        with open("./results/UraChance.csv", "w") as f:
            f.write("Type,Total,13,12,11,10,9,7,6,5,4\n")
            for i in self.ura:
                f.write("%s,," % i)
                for j in range(13, 3, -1):
                    f.write("%d," % self.ura[i][j])
                f.write("\n")