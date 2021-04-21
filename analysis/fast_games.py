from log_analyzer import LogAnalyzer
from analysis_utils import GetNextRealTag, discards

class FastGames(LogAnalyzer):
    def __init__(self):
        self.games = []

    def ParseLog(self, log, log_id):
        rounds = log.findall("INIT")
        discarded_tiles = 0
        if len(rounds) == 1:
            next_element = GetNextRealTag(rounds[0])

            while next_element is not None:
                if next_element.tag[0] in discards:
                    if next_element.tag != "DORA":
                        discarded_tiles += 1
                next_element = GetNextRealTag(next_element)

            self.games.append("%d discards - http://tenhou.net/3/?log=%s" % (discarded_tiles, log_id))

    def PrintResults(self):
        self.games.sort()
        with open("./results/FastGames.csv", "w") as f:
            for game in self.games:
                f.write("%s\n" % game)
