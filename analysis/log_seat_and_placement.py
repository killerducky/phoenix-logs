from log_analyzer import LogAnalyzer
from collections import Counter

class LogSeatAndPlacement(LogAnalyzer):
    def __init__(self):
        self.events = dict()

    def CountBySeatAndPlacement(self, key, seat, placement):
        if key not in self.events:
            self.events[key] = dict()
            self.events[key]["East"] = Counter()
            self.events[key]["South"] = Counter()
            self.events[key]["West"] = Counter()
            self.events[key]["North"] = Counter()

        self.events[key][seat][placement] += 1
    
    def PrintResults(self):
        for key in self.events:
            print(key)
            print("Seat,First,Second,Third,Fourth")
            for seat in self.events[key]:
                print("%s,%d,%d,%d,%d" % (
                    seat,
                    self.events[key][seat][0],
                    self.events[key][seat][1],
                    self.events[key][seat][2],
                    self.events[key][seat][3]
                ))