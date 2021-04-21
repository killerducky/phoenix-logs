from log_find_max import LogFindMax

class Ryuukyoku(LogFindMax):
    def ParseLog(self, log, log_id):
        ryuukyoku = log.findall("RYUUKYOKU")
        wins = log.findall("AGARI")

        self.CompareValue(len(ryuukyoku) - len(wins), log_id)
    
    def GetName(self):
        return "Discards in Round"
                    