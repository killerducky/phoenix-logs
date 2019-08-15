from log_counter import LogCounter
from log_find_max import LogFindMax

class LogCountAndMax(LogCounter, LogFindMax):
    def __init__(self):
        LogCounter.__init__(self)
        LogFindMax.__init__(self)

    def Count(self, count, log_id):
        LogCounter.Count(self, count)
        LogFindMax.CompareValue(self, count, log_id)
    
    def PrintResults(self):
        LogCounter.PrintResults(self)
        LogFindMax.PrintResults(self)