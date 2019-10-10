from log_count_and_max import LogCountAndMax

class YakuMagnitude(LogCountAndMax):
    def ParseLog(self, log, log_id):
        wins = log.findall("AGARI")

        for win in wins:
            if 'yaku' not in win.attrib:
                continue

            yaku = [int(x) for x in win.attrib["yaku"].split(",")[1::2]]

            self.Count(sum(yaku), log_id)

    def GetName(self):
        return "Yaku Magnitude"