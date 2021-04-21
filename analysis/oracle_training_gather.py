from log_analyzer import LogAnalyzer
from analysis_utils import convertHai, CheckDoubleRon, CheckSeat
import pickle

class OracleTrainingGather(LogAnalyzer):
    def __init__(self):
        self.hands = []

    def ParseLog(self, log, log_id):
        starts = log.findall("INIT")
        ends = [ x for x in log.xpath("//*[self::AGARI or self::RYUUKYOKU]") if not CheckDoubleRon(x) ]

        for i in range(len(starts)):
            if ends[i].tag == "RYUUKYOKU": continue
            winner = ends[i].attrib["who"]
            starting_hand = convertHai(starts[i].attrib["hai%s" % winner])

            if "yaku" in ends[i].attrib:
                self.hands.append((
                    starting_hand,
                    starts[i].attrib["seed"],
                    ends[i].attrib["hai"],
                    "" if "m" not in ends[i].attrib else ends[i].attrib["m"],
                    ends[i].attrib["ten"],
                    CheckSeat(winner, starts[i].attrib["oya"]),
                    starts[i].attrib["ten"],
                    ends[i].attrib["yaku"])
                )
            else:
                self.hands.append((
                    starting_hand,
                    starts[i].attrib["seed"],
                    ends[i].attrib["hai"],
                    "" if "m" not in ends[i].attrib else ends[i].attrib["m"],
                    ends[i].attrib["ten"],
                    CheckSeat(winner, starts[i].attrib["oya"]),
                    starts[i].attrib["ten"],
                    ends[i].attrib["yakuman"])
                )
    
    def PrintResults(self):
        print("Storing %d hands..." % len(self.hands))
        with open("oracle.txt", "wb") as fp:
            pickle.dump(self.hands, fp)