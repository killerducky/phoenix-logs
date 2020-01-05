from log_counter import LogCounter
from log_seat_and_placement import LogSeatAndPlacement
from analysis_utils import convertTile, GetPlacements, CheckSeat, convertHai, getTilesFromCall, GetNextRealTag, GetRoundNameWithoutRepeats
from shanten import calculateMinimumShanten
import math

dragons = [35, 36, 37]
dora_indication = [
     6, 2, 3, 4, 5, 6, 7, 8, 9, 1,
    16,12,13,14,15,16,17,18,19,11,
    26,22,23,24,25,26,27,28,29,21,
    30,32,33,34,31,36,37,35
]
discard_tags = ["D", "E", "F", "G"]
draw_tags = ["T", "U", "V", "W"]

class DoraDragon(LogCounter, LogSeatAndPlacement):
    def __init__(self):
        LogCounter.__init__(self)
        LogSeatAndPlacement.__init__(self)

    def ParseLog(self, log, log_id):
        starts = log.findall("INIT")
        ends = [ x for x in log.xpath("//*[self::AGARI or self::RYUUKYOKU]") if not CheckDoubleRon(x) ]

        for i in range(len(starts)):
            dora_ind = convertTile(starts[i].attrib["seed"].split(",")[5])

            if dora_ind not in dragons:
                continue
            
            self.Count("Rounds With Dragon Dora")
            self.Count("Dora Dragon In %s" % GetRoundNameWithoutRepeats(starts[i]))
            dora = dora_indication[dora_ind]

            element = starts[i].getnext()
            is_in_riichi = [False, False, False, False]
            discarded = False
            discards = 0
            discards_since_first = 0

            while element is not None:
                if element.tag == "INIT":
                    break

                first_character = element.tag[0]

                if first_character in discard_tags:
                    tile = element.tag[1:]
                    try:
                        discard = convertTile(tile)
                    except ValueError:
                        element = element.getnext()
                        continue
                    
                    discards += 1
                    discards_since_first += 1
                    who = discard_tags.index(first_character)

                    if discard == dora:
                        if not discarded:
                            discarded = True
                            discards_since_first = 0
                            element = element.getnext()
                            continue

                        turn = math.ceil(discards / 4)
                        turns_since_first = math.ceil(discards_since_first / 4)

                        if is_in_riichi[who] == True:
                            self.Count("Discarded While In Riichi")
                        else:
                            self.Count("Discarded Willingly")

                        self.Count("Discarded Second On Turn %d" % turn)
                        self.Count("Discarded Second %d Turns After First" % turns_since_first)

                        next_element = GetNextRealTag(element)
                        if next_element.tag == "N":
                            self.Count("Called On Turn %d" % turn)
                            self.Count("Called After %d Turns" % turns_since_first)
                            caller = next_element.attrib["who"]
                            if ends[i].tag == "AGARI" and ends[i].attrib["who"] == caller:
                                self.Count("Ended Up Winning After Turn %d Call" % turn)
                                self.Count("Ended Up Winning After Calling Second %d Turns After First" % turns_since_first)
                        if next_element.tag == "AGARI":
                            self.Count("Dealt in After %d Turns" % turn)
                            self.Count("Dealt in %d Turns After First" % turns_since_first)
                        
                        break
                elif element.tag == "REACH" and element.attrib["step"] == "2":
                    who = int(element.attrib["who"])
                    is_in_riichi[who] = True
                
                element = element.getnext()

    def GetName(self):
        return "Dora Dragon Event"

    def PrintResults(self):
        LogCounter.PrintResults(self)
        LogSeatAndPlacement.PrintResults(self)

def CheckDoubleRon(element):
    next_element = element.getnext()

    if next_element is not None and next_element.tag == "AGARI":
        return True
    
    return False