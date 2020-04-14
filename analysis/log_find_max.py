from log_analyzer import LogAnalyzer

class LogFindMax(LogAnalyzer):
    def __init__(self):
        self.highest = 0
        self.highest_id = ""

    def CompareValue(self, new, log_id):
        if self.highest < new:
            self.highest = new
            self.highest_id = log_id
            print("Found %d in %s" % (new, log_id))

    def PrintResults(self):
        print("Max: %d in replay id %s" % (self.highest, self.highest_id))