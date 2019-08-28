from log_analyzer import LogAnalyzer
from analysis_utils import round_names
from collections import Counter
import math

discard_tags = ["D", "E", "F", "G"]

class EarliestCall(LogAnalyzer):
    def __init__(self):
        self.counter = dict()
        for name in round_names:
            self.counter[name] = Counter()

    def ParseLog(self, log, log_id):
        start = log.find("INIT")
        discards = 0
        round_name = round_names[int(start.attrib["seed"].split(",")[0])]
        has_counted_call = False
        element = start.getnext()

        while element is not None:
            if element.tag == "INIT":
                if has_counted_call == False:
                    self.counter[round_name]["Never"] += 1
                round_name = round_names[int(start.attrib["seed"].split(",")[0])]
                has_counted_call = False
                discards = 0
                element = element.getnext()
                continue

            if has_counted_call == True:
                element = element.getnext()
                continue
            
            if element.tag[0] in discard_tags and element.tag != "DORA":
                discards += 1
                element = element.getnext()
                continue

            if element.tag == "N":
                self.counter[round_name][math.ceil(discards / 4)] += 1
                has_counted_call = True
            
            element = element.getnext()

    def PrintResults(self):
        with open("./results/EarliestCall.csv", "w") as f:
            for name in round_names:
                print(name)
                f.write(name)
                print("First Call Turn,Count")
                f.write("First Call Turn,Count")
                for i in self.counter[name]:
                    print("{},{}".format(i, self.counter[name][i]))
                    f.write("{},{}".format(i, self.counter[name][i]))


