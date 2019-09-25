from log_find_max import LogFindMax
from analysis_utils import GetNextRealTag

class LargestDoubleRon(LogFindMax):
    def ParseLog(self, log, log_id):
        wins = log.findall("AGARI")

        for win in wins:
            next_element = GetNextRealTag(win)

            if next_element is not None and next_element.tag == "AGARI":
                first_ron = int(win.attrib["ten"].split(",")[1])
                second_ron = int(next_element.attrib["ten"].split(",")[1])
                total = first_ron + second_ron

                self.CompareValue(total, log_id)