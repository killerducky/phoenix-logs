from log_counter import LogCounter

class SampleSize(LogCounter):
    def __init__(self):
        super().__init__()
        self.first_log_id = ""
        self.last_log_id = ""

    def ParseLog(self, log, log_id):
        self.Count("Games")
        self.counts["Rounds"] += len(log.findall("INIT"))

        if self.first_log_id == "":
            self.first_log_id = log_id

        self.last_log_id = log_id
    
    def GetName(self):
        return "Sample"

    def PrintResults(self):
        super().PrintResults()
        print("First Log: %s" % self.first_log_id)    
        print("Last Log: %s" % self.last_log_id)