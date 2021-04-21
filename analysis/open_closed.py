from log_analyzer import LogAnalyzer

class OpenClosed(LogAnalyzer):
    def __init__(self):
        self.open = 0
        self.closed = 0

    def ParseLog(self, log, log_id):
        wins = log.findall("AGARI")

        for win in wins:
            if "m" in win.attrib:
                self.open += 1
            else:
                self.closed += 1
    
    def PrintResults(self):
        print("Open: %d" % self.open)
        print("Closed: %d" % self.closed)