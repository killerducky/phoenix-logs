from log_counter import LogCounter

class DealinBySeat(LogCounter):
    def ParseLog(self, log, log_id):
        starts = log.findall("INIT")
        ends = [ x for x in log.xpath("//*[self::AGARI or self::RYUUKYOKU]") if not CheckDoubleRon(x) ]

        for i in range(len(starts)):
            if ends[i].tag == "RYUUKYOKU":
                continue
            
            if ends[i].attrib["who"] == ends[i].attrib["fromWho"]:
                continue
            self.Count("Total Rons")
            self.Count(CheckSeat(ends[i].attrib["fromWho"], starts[i].attrib["oya"]))

    def GetName(self):
        return "Seat Deal-in"

def CheckDoubleRon(element):
    next_element = element.getnext()

    if next_element is not None and next_element.tag == "AGARI":
        return True
    
    return False

seats_by_oya = [
    [ "East", "South", "West", "North" ],
    [ "North", "East", "South", "West" ],
    [ "West", "North", "East", "South" ],
    [ "South", "West", "North", "East" ]
]

def CheckSeat(who, oya):
    return seats_by_oya[int(oya)][int(who)]