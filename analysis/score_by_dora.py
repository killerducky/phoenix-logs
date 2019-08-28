from log_analyzer import LogAnalyzer
from analysis_utils import convertTile, CheckIfWinIsClosed
from collections import Counter

class ScoreByDora(LogAnalyzer):
    def __init__(self):
        self.dora = dict()
        for i in range(38):
            self.dora[i] = Counter()
    
    def ParseLog(self, log, log_id):
        starts = log.findall("INIT")
        ends = [ x for x in log.xpath("//*[self::AGARI or self::RYUUKYOKU]") if not CheckDoubleRon(x) ]

        for i in range(len(ends)):
            if ends[i].tag == "RYUUKYOKU":
                continue
            
            score = int(ends[i].attrib["ten"].split(",")[1])
            dealer = starts[i].attrib["oya"] == ends[i].attrib["who"]
            closed = CheckIfWinIsClosed(ends[i])
            dora = convertTile(ends[i].attrib["doraHai"].split(",")[0])

            if dealer:
                if closed:
                    self.dora[dora]["Dealer Closed Value"] += score
                    self.dora[dora]["Dealer Closed Wins"] += 1
                else:
                    self.dora[dora]["Dealer Open Value"] += score
                    self.dora[dora]["Dealer Open Wins"] += 1
            else:
                if closed:
                    self.dora[dora]["Non-Dealer Closed Value"] += score
                    self.dora[dora]["Non-Dealer Closed Wins"] += 1
                else:
                    self.dora[dora]["Non-Dealer Open Value"] += score
                    self.dora[dora]["Non-Dealer Open Wins"] += 1
    
    def PrintResults(self):
        print("Tile,Dealer Value,Dealer Wins,Dealer Average,Non-Dealer Value,Non-Dealer Wins,Non-Dealer Average")
        for key in self.dora:
            print("{},{},{},{},{},,{},{},{},{}".format(
                key,
                self.dora[key]["Dealer Closed Value"],
                self.dora[key]["Dealer Closed Wins"],
                self.dora[key]["Dealer Open Value"],
                self.dora[key]["Dealer Open Wins"],
                self.dora[key]["Non-Dealer Closed Value"],
                self.dora[key]["Non-Dealer Closed Wins"],
                self.dora[key]["Non-Dealer Open Value"],
                self.dora[key]["Non-Dealer Open Wins"],
            ))


def CheckDoubleRon(element):
    next_element = element.getnext()

    if next_element is not None and next_element.tag == "AGARI":
        return True
    
    return False