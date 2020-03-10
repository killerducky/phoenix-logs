from log_counter import LogCounter
import math

class PlacementByPoints(LogCounter):
    def ParseLog(self, log, log_id):
        wins = log.findall("AGARI")
        wins.extend(log.findall("RYUUKYOKU"))
        riichis = log.findall("REACH")

        points_won = [0, 0, 0, 0]
        points_lost = [0, 0, 0, 0]
        owari = ""

        for win in wins:
            # sc="250,-52,250,0,250,52,250,0"
            scores = win.attrib["sc"].split(",")
            for i in range(4):
                score = int(scores[1 + i * 2])
                if score < 0:
                    points_lost[i] += abs(score)
                else:
                    points_won[i] += score
            
            if "owari" in win.attrib:
                owari = win.attrib["owari"]
        
        for riichi in riichis:
            if riichi.attrib["step"] == "2":
                points_lost[int(riichi.attrib["who"])] += 10

        # round to nearest 1000
        for i in range(4):
            points_won[i] = round(points_won[i] / 10) * 1000
            points_lost[i] = round(points_lost[i] / 10) * 1000

        # check placements
        final_scores = [float(x) for x in owari.split(",")[1::2]]
        sorted_scores = sorted(final_scores, reverse=True)

        for i in range(4):
            self.Count("Won %d points, came in %d" % (points_won[i], sorted_scores.index(final_scores[i])))
            self.Count("Lost %d points, came in %d" % (points_lost[i], sorted_scores.index(final_scores[i])))
            self.Count("Delta %d points, came in %d" % (points_won[i] - points_lost[i], sorted_scores.index(final_scores[i])))
    
    def GetName(self):
        return "Placement By Points"