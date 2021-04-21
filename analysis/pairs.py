# -*- coding: utf-8 -*-

from analysis_utils import convertHai, convertTile
from shanten import calculateChiitoitsuShanten
from log_counter import LogCounter

draws = ['T','U','V','W']

class Pairs(LogCounter):
    def ParseLog(self, log, log_id):
        rounds = log.findall('INIT')
        round_number = -1
        for round_ in rounds:
            round_number += 1
            next_element = round_.getnext()
            while next_element is not None:
                next_element = next_element.getnext()
                
                if next_element.tag == "AGARI" or next_element.tag == "RYUUKYOKU":
                    break
            end = next_element

            for i in range(4):
                round_ended = False
                hand = convertHai(round_.attrib['hai%d' % i])

                # Add the first drawn tile to the hand
                next_element = round_.getnext()
                while next_element is not None:
                    name = next_element.tag
                    if name == "UN":
                        next_element = next_element.getnext()
                        continue
                    if name == "N" and int(next_element.attrib["who"]) == i:
                        #ignore hands that are called before the first draw
                        round_ended = True
                        break
                    if name[0] == draws[i]:
                        hand[convertTile(name[1:])] += 1
                        break
                    if name == "AGARI" or name == "RYUUKYOKU" or name == "INIT":
                        round_ended = True
                        break
                    next_element = next_element.getnext()
                
                if round_ended:
                    break
                
                chiitoi_shanten = calculateChiitoitsuShanten(hand)
                self.Count("Starts at %d" % chiitoi_shanten)
                
                if end.tag == "AGARI" and int(end.attrib["who"]) == i:
                    self.Count("Won from %d start" % chiitoi_shanten)

                    if not "yaku" in end.attrib:
                        continue

                    yaku = end.attrib["yaku"].split(",")
                    ids = [x for x in yaku[0::2]]
                    if "22" in ids:
                        self.Count("Won chiitoi from %d start" % chiitoi_shanten)
                    elif "28" in ids:
                        self.Count("Won toitoi from %d start" % chiitoi_shanten)
                        if chiitoi_shanten == 0:
                            print("https://tenhou.net/3/?log=%s&tw=%d&ts=%d" % (log_id, i, round_number))
                    elif "32" in ids:
                        self.Count("Won ryanpeikou from %d start" % chiitoi_shanten)
                    elif "9" in ids:
                        self.Count("Won iipeikou from %d start" % chiitoi_shanten)
                    elif "29" in ids:
                        self.Count("Won san'ankou from %d start" % chiitoi_shanten)

    def GetName(self):
        return "Pairs"