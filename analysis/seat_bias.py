from log_counter import LogCounter
import math

seats = ["East", "South", "West", "North"]

class SeatBias(LogCounter):
    def ParseLog(self, log, log_id):
        ends = [ x for x in log.xpath("//*[self::AGARI or self::RYUUKYOKU]")]
        final_scores = [float(x) for x in ends[-1].attrib["owari"].split(",")[1::2]]
        sorted_scores = final_scores.copy()
        sorted_scores.sort(reverse=True)

        self.Count("East %d" % sorted_scores.index(final_scores[0]))
        self.Count("South %d" % sorted_scores.index(final_scores[1]))
        self.Count("West %d" % sorted_scores.index(final_scores[2]))
        self.Count("North %d" % sorted_scores.index(final_scores[3]))

    def GetName(self):
        return "Seat Bias"
        