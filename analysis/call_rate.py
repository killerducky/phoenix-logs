from log_analyzer import LogAnalyzer
from collections import Counter

rounds = ["East 1", "East 2", "East 3", "East 4", "South 1", "South 2", "South 3", "South 4", "West 1", "West 2", "West 3", "West 4"]

class CallRate(LogAnalyzer):
    def __init__(self):
        self.round_counters = dict()

        for round_ in rounds:
            seat_counters = dict()
            seat_counters["East"] = Counter()
            seat_counters["South"] = Counter()
            seat_counters["West"] = Counter()
            seat_counters["North"] = Counter()
            seat_counters["Total"] = 1
            self.round_counters[round_] = seat_counters

    def ParseLog(self, log, log_id):
        start = log.find("INIT")
        current_oya = int(start.attrib["oya"])
        starting_oya = current_oya
        current_round = int(start.attrib["seed"].split(",")[0])
        current = start.getnext()
        flags = [False, False, False, False]
        placements = GetPlacements(start.attrib["ten"], starting_oya)

        while current is not None:
            if current.tag == "INIT":
                for i in range(4):
                    if flags[i] == True:
                        self.round_counters[rounds[current_round]][CheckSeat(i, current_oya)][placements[i]] += 1

                flags = [False, False, False, False]
                current_oya = int(current.attrib["oya"])
                current_round = int(current.attrib["seed"].split(",")[0])
                placements = GetPlacements(current.attrib["ten"], starting_oya)
                self.round_counters[rounds[current_round]]["Total"] += 1
            
            if current.tag == "N":
                flags[int(current.attrib["who"])] = True
            
            current = current.getnext()

    def PrintResults(self):
        for round_ in self.round_counters:
            print("-- %s --" % round_)
            print("Seat,Calls as First,Calls as Second,Calls as Third,Calls as Fourth")
            for seat in seats_by_oya[0]:
                print("%s,%d,%d,%d,%d" % (
                    seat,
                    self.round_counters[round_][seat][0],
                    self.round_counters[round_][seat][1],
                    self.round_counters[round_][seat][2],
                    self.round_counters[round_][seat][3]
                ))
            print("Total: %d" % self.round_counters[round_]["Total"])

seats_by_oya = [
    [ "East", "South", "West", "North" ],
    [ "North", "East", "South", "West" ],
    [ "West", "North", "East", "South" ],
    [ "South", "West", "North", "East" ]
]

def CheckSeat(who, oya):
    return seats_by_oya[oya][who]

def GetPlacements(ten, starting_oya):
    points = list(map(int, ten.split(",")))
    # For tiebreaking
    points[0] -= (4 - starting_oya) % 4
    points[1] -= (5 - starting_oya) % 4
    points[2] -= (6 - starting_oya) % 4
    points[3] -= (7 - starting_oya) % 4
    ordered_points = points.copy()
    ordered_points.sort(reverse=True)

    return [
        ordered_points.index(points[0]),
        ordered_points.index(points[1]),
        ordered_points.index(points[2]),
        ordered_points.index(points[3])
    ]