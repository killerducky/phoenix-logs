from log_counter import LogCounter

class TypeCounter(LogCounter):
    def ParseLog(self, log, log_id):
        go = log.find("GO")
        self.Count(go.attrib["type"])

    def GetName(self):
        return "Game Types"