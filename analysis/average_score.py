from log_analyzer import LogAnalyzer

class AverageScore(LogAnalyzer):
    def __init__(self):
        self.total_score = 0
        self.wins = 0

    def ParseLog(self, log, log_id):
        wins = log.findall("AGARI")

        for win in wins:
            score = int(win.attrib["ten"].split(",")[1])
            self.total_score += score
            self.wins += 1

    def PrintResults(self):
        print("Total score: %d" % self.total_score)
        print("Num wins: %d" % self.wins)
        print("Average: %.1f" % (self.total_score / self.wins))