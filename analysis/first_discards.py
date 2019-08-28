from log_counter import LogCounter 
from analysis_utils import convertTile

discard_tags = ["D", "E", "F", "G"]

class FirstDiscards(LogCounter):
    def ParseLog(self, log, log_id):
        starts = log.findall("INIT")

        for start in starts:
            discards = []
            discards_left = 24

            ele = start.getnext()

            while ele is not None and discards_left > 0:
                if ele.tag == "AGARI" or ele.tag == "REACH" or ele.tag == "RYUUKYOKU":
                    break

                first_character = ele.tag[0]

                if first_character in discard_tags:
                    tile = ele.tag[1:]
                    try:
                        tile = int(tile)
                    except ValueError:
                        ele = ele.getnext()
                        continue
                    
                    discards.append(tile)
                    discards_left -= 1
                
                ele = ele.getnext()

            if discards_left <= 0:
                for discard in discards:
                    tile = convertTile(discard)
                    if tile % 10 == 5 and tile != 35 and discard % 4 == 0:
                        self.Count("Red %d" % tile)
                    else:
                        self.Count(convertTile(discard))
    
    def GetName(self):
        return "Tile Discarded Early"
            
