from log_counter import LogCounter
from analysis_utils import convertTile
import math

dragons = [35, 36, 37]
dora_indication = [
     6, 2, 3, 4, 5, 6, 7, 8, 9, 1,
    16,12,13,14,15,16,17,18,19,11,
    26,22,23,24,25,26,27,28,29,21,
    30,32,33,34,31,36,37,35
]
discard_tags = ["D", "E", "F", "G"]

class DoraDragon(LogCounter):
    def ParseLog(self, log, log_id):
        starts = log.findall("INIT")
        ends = [ x for x in log.xpath("//*[self::AGARI or self::RYUUKYOKU]") if not CheckDoubleRon(x) ]

        for i in range(len(starts)):
            if ends[i].tag == "RYUUKYOKU":
                continue

            dora_ind = convertTile(ends[i].attrib["doraHai"].split(",")[0])

            if dora_ind not in dragons:
                continue
            
            self.Count("Rounds")
            dora = dora_indication[dora_ind]

            element = starts[i].getnext()
            discards = 0

            while element is not None:
                if element.tag == "INIT":
                    break

                first_character = element.tag[0]

                if first_character in discard_tags:
                    tile = element.tag[1:]
                    try:
                        discard = convertTile(tile)
                        discards += 1
                        if discard == dora:
                            self.Count("Discarded On Turn %d" % math.floor(discards / 4))

                            if element.getnext().tag == "N" or element.getnext().tag == "AGARI":
                                self.Count("Called On Turn %d" % math.floor(discards / 4))
                            
                            break
                    except ValueError:
                        element = element.getnext()
                        continue
                
                element = element.getnext()

    def GetName(self):
        return "Dora Dragon Event"

def CheckDoubleRon(element):
    next_element = element.getnext()

    if next_element is not None and next_element.tag == "AGARI":
        return True
    
    return False