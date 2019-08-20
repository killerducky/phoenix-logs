from log_counter import LogCounter
from log_seat_and_placement import LogSeatAndPlacement
from analysis_utils import convertTile, GetPlacements, CheckSeat, convertHai, getTilesFromCall
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
            if ends[i].tag == "RYUUKYOKU":
                continue

            dora_ind = convertTile(ends[i].attrib["doraHai"].split(",")[0])

            if dora_ind not in dragons:
                continue
            
            self.Count("Rounds With Dragon Dora")
            dora = dora_indication[dora_ind]
            hands = []
            for h in range(4):
                hands.append(convertHai(starts[i].attrib["hai%d" % h]))

            element = starts[i].getnext()
            discards = 0
            last_shanten_logged = [-1, -1, -1, -1]

            while element is not None:
                if element.tag == "INIT":
                    self.Count("Dora Dragon Never Discarded")
                    break

                first_character = element.tag[0]

                if first_character in draw_tags:
                    tile = element.tag[1:]
                    try:
                        draw = convertTile(tile)
                        who = draw_tags.index(first_character)
                        hands[who][draw] += 1
                    except ValueError:
                        element = element.getnext()
                        continue
                elif first_character in discard_tags:
                    tile = element.tag[1:]
                    try:
                        discard = convertTile(tile)
                    except ValueError:
                        element = element.getnext()
                        continue
                    
                    discards += 1
                    who = discard_tags.index(first_character)

                    if discard == dora:
                        dealer = int(starts[i].attrib["oya"])
                        placements = GetPlacements(starts[i].attrib["ten"], dealer)

                        turn = math.ceil(discards / 4)
                        self.Count("Discarded On Turn %d" % turn)
                        self.CountBySeatAndPlacement("First To Discard Dora Dragon", CheckSeat(who, dealer), placements[who])
                        shanten = calculateMinimumShanten(hands[who])
                        self.Count("Discarded At %d-Shanten" % shanten)

                        if shanten < 0:
                            print(log_id)

                        if element.getnext().tag == "N":
                            self.Count("Called On Turn %d" % turn)
                            caller = element.getnext().attrib["who"]
                            if ends[i].attrib["who"] == caller:
                                self.Count("Ended Up Winning After Turn %d Call" % turn)
                        if element.getnext().tag == "AGARI":
                            self.Count("Dealt in on Turn %d" % turn)
                        
                        break
                    else:
                        hands[who][discard] -= 1

                        if hands[who][dora] == 1:
                            shanten = calculateMinimumShanten(hands[who], last_shanten_logged[who] - 1)
                            if last_shanten_logged[who] == -1 or shanten < last_shanten_logged[who]:
                                self.Count("Lone Dora Dragon Kept At %d-Shanten" % shanten)
                                last_shanten_logged[who] = shanten
                elif first_character == "N":
                    tiles = getTilesFromCall(element.attrib["m"])
                    tiles_count = len(tiles)
                    who = int(element.attrib["who"])
                    if tiles_count == 1:
                        hands[who][tiles[0]] -= 1
                    elif tiles_count == 3:
                        hands[who][tiles[1]] -= 1
                        hands[who][tiles[2]] -= 1
                        # hack to make shanten accurate
                        hands[who][31] += 3
                    else:
                        hands[who][tiles[0]] = 0
                        # hack to make shanten accurate
                        hands[who][31] += 3
                
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