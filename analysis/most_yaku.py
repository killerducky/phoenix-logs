from log_find_max import LogFindMax

class MostYaku(LogFindMax):
    def __init__(self):
        self.highest = 0
        self.highest_id = ""

    def ParseLog(self, log, log_id):
        wins = log.findall("AGARI")

        for win in wins:
            if "yaku" not in win.attrib:
                continue
            
            yaku = win.attrib["yaku"].split(",")
            ids = [x for x in yaku[0::2]]

            self.CompareValue(len(ids), log_id)