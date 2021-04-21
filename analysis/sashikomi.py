from log_analyzer import LogAnalyzer
from collections import Counter, defaultdict
from analysis_utils import GetWhoTileWasCalledFrom
from urllib.parse import unquote

NUM_PLAYERS = 4

class Sashikomi(LogAnalyzer):
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

            if gap < 0:
                print("doing something wrong")

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

            next_element = end.getnext()
            has_called = False

            while next_element is not None:
                if next_element.tag == "AGARI":
                    if int(next_element.attrib["who"]) == first_place:
                        break
                    elif int(next_element.attrib["fromWho"]) == first_place:
                        self.data[gap_key]["Count"] += 1
                        self.data[gap_key][next_element.attrib["ten"].split(",")[1]] += 1
                    break

                next_element = next_element.getnext()

    def PrintResults(self):
        with open("./results/Sashikomi.csv", "w", encoding="utf8") as f:
            f.write("Lead,")
            for score in self.data["<4000"]:
                f.write("%s," % score)
            f.write("\n")

            for lead in self.data:
                f.write("%s," % lead)

                for score in self.data["<4000"]:
                    f.write("%d," % self.data[lead][score])
                
                f.write("\n")