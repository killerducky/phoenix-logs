# -*- coding: utf-8 -*-

from log_counter import LogCounter
from ukeire import calculateUkeire
from shanten import calculateMinimumShanten
from analysis_utils import convertHai, convertTile, GetNextRealTag, GetPreviousRealTag

discard_tags = ["D", "E", "F", "G"]
tile_names = [
    "0m", "1m", "2m", "3m", "4m", "5m", "6m", "7m", "8m", "9m",
    "0p", "1p", "2p", "3p", "4p", "5p", "6p", "7p", "8p", "9p",
    "0s", "1s", "2s", "3s", "4s", "5s", "6s", "7s", "8s", "9s",
    "0z", "1z", "2z", "3z", "4z", "5z", "6z", "7z"
]

class DaburiWaits(LogCounter):
    def ParseLog(self, log, log_id):
        rounds = [[]]

        for child in log.getchildren():
            if child.tag == "INIT":
                rounds.append([child])
            else:
                rounds[-1].append(child)
        
        for round_ in rounds[1:]:
            init = round_[0]

            next_element = init.getnext()
            discards = 0

            while next_element is not None:
                if next_element.tag == "N" or next_element.tag == "RYUUKYOKU" or next_element.tag == "AGARI":
                    break
                
                first_character = next_element.tag[0]

                if next_element.tag != "GO" and next_element.tag != "DORA" and first_character in discard_tags:
                    discards += 1
                
                if discards > 3:
                    break

                if next_element.tag == "REACH":
                    # Double riichi!
                    self.Count("Double Riichis")
                    who = int(next_element.attrib["who"])
                    hand = convertHai(init.attrib["hai%d" % who])

                    draw_element = GetPreviousRealTag(next_element)
                    draw = convertTile(draw_element.tag[1:])
                    hand[draw] += 1

                    remaining_tiles = [4]*38
                    for i in range(38):
                        remaining_tiles[i] -= hand[i]

                    discard_element = GetNextRealTag(next_element)
                    discard = convertTile(discard_element.tag[1:])
                    hand[discard] -= 1

                    ukeire = calculateUkeire(hand, remaining_tiles, calculateMinimumShanten, 0)
                    
                    self.Count("Waiting on %d tiles" % ukeire[0])
                    break
                
                next_element = next_element.getnext()

    def GetName(self):
        return "Double Riichi Wait"
                