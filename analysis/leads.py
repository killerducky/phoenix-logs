from log_analyzer import LogAnalyzer
from collections import Counter, defaultdict
from analysis_utils import GetWhoTileWasCalledFrom, GetNextRealTag
from urllib.parse import unquote

NUM_PLAYERS = 4

class Leads(LogAnalyzer):
    def __init__(self):
        self.data = defaultdict(Counter)

    def ParseLog(self, log, log_id):
        round_ends = log.findall('AGARI') + log.findall('RYUUKYOKU')

        for end in round_ends:
            if "owari" in end.attrib:
                continue

            scores = list(map(int, end.attrib["sc"].split(",")[0::2]))
            sorted_scores = scores.copy()
            sorted_scores.sort(reverse=True)

            first_place = scores.index(sorted_scores[0])
            gap = sorted_scores[0] - sorted_scores[1]

            if gap == 0:
                continue

            gap_key = "<4000"

            if gap > 40:
                if gap < 80:
                    gap_key = "<8000"
                elif gap < 120:
                    gap_key = "<12000"
                elif gap < 160:
                    gap_key = "<16000"
                elif gap < 200:
                    gap_key = "<20000"
                else:
                    gap_key = ">20000"

            next_element = GetNextRealTag(end)

            if next_element.tag != "INIT":
                #double ron, avoid double counting
                continue
            
            dealer = int(next_element.attrib["oya"])

            if dealer == first_place:
                gap_key = "Dealer %s" % gap_key
            else:
                gap_key = "Nondealer %s" % gap_key

            self.data[gap_key]["Count"] += 1
            has_called = False

            while next_element is not None:
                if next_element.tag == "N":
                    if not has_called and GetWhoTileWasCalledFrom(next_element) != 0:
                        if int(next_element.attrib["who"]) == first_place:
                            has_called = True
                            self.data[gap_key]["Calls"] += 1
                
                elif next_element.tag == "REACH":
                    if next_element.attrib["step"] == "2":
                        pass
                    elif int(next_element.attrib["who"]) == first_place:
                        self.data[gap_key]["Riichi"] += 1
                
                elif next_element.tag == "AGARI":
                    if int(next_element.attrib["who"]) == first_place:
                        self.data[gap_key]["Win"] += 1
                        self.data[gap_key]["Win Value"] += int(next_element.attrib["ten"].split(",")[1])
                    elif int(next_element.attrib["fromWho"]) == first_place:
                        self.data[gap_key]["Deal-in"] += 1
                        self.data[gap_key]["Deal-in Value"] += int(next_element.attrib["ten"].split(",")[1])
                    break
                    
                elif next_element.tag == "RYUUKYOKU":
                    break

                next_element = next_element.getnext()

    def PrintResults(self):
        print("Lead,Count,Calls,Riichi,Dealin,Dealin Value,Win,Win Value")
        
        with open("./results/Leads.csv", "w", encoding="utf8") as f:
            f.write("Lead,Count,Calls,Riichi,Dealin,Dealin Value,Win,Win Value\n")

            for lead in self.data:
                print("%s,%d,%d,%d,%d,%d,%d,%d" % (
                    lead,
                    self.data[lead]["Count"],
                    self.data[lead]["Calls"],
                    self.data[lead]["Riichi"],
                    self.data[lead]["Deal-in"],
                    self.data[lead]["Deal-in Value"],
                    self.data[lead]["Win"],
                    self.data[lead]["Win Value"]
                    )
                )
                f.write("%s,%d,%d,%d,%d,%d,%d,%d\n" % (
                    lead,
                    self.data[lead]["Count"],
                    self.data[lead]["Calls"],
                    self.data[lead]["Riichi"],
                    self.data[lead]["Deal-in"],
                    self.data[lead]["Deal-in Value"],
                    self.data[lead]["Win"],
                    self.data[lead]["Win Value"]
                    )
                )