from log_counter import LogCounter
from analysis_utils import convertHai

class Iipeikou(LogCounter):
    def ParseLog(self, log, log_id):
        wins = log.findall("AGARI")

        for win in wins:
            if "yaku" not in win.attrib:
                continue
            
            yaku = win.attrib["yaku"].split(",")
            ids = [int(x) for x in yaku[0::2]]

            if 9 not in ids:
                continue
            
            hand = convertHai(win.attrib["hai"])

            for suit in range(3):
                for i in range(1,8):
                    base = suit * 10 + i
                    if hand[base] >= 2 and hand[base + 1] >= 2 and hand[base + 2] >= 2:
                        self.Count("%d%d%d" % (i, i+1, i+2))
                        break
            
    def GetName(self):
        return "Iipeikou"
