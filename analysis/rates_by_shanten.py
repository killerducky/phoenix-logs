import bz2
import sqlite3
from analysis_utils import convertHai, convertTile, getTilesFromCall, GetNextRealTag
from log_counter import LogCounter
from shanten import calculateStandardShanten
from collections import Counter
from lxml import etree

draws = ['T','U','V','W']   
        
class RatesByShanten(LogCounter):
    def ParseLog(self, log, log_id):
        rounds = log.findall('INIT')

        for round_ in rounds:
            for i in range(4):
                round_ended = False
                hand = convertHai(round_.attrib['hai%d' % i])
                draw = draws[i]

                # Add the first drawn tile to the hand
                next_element = GetNextRealTag(round_)
                while next_element is not None:
                    tag = next_element.tag

                    if tag[0] == draw:
                        hand[convertTile(tag[1:])] += 1
                        break
                    if tag == "N" and int(next_element.attrib["who"]) == i:
                        tiles = getTilesFromCall(next_element.attrib["m"])
                        hand[tiles[0]] += 1
                        break
                    if tag == "AGARI" or tag == "RYUUKYOKU" or tag == "INIT":
                        round_ended = True
                        break

                    next_element = GetNextRealTag(next_element)
                
                if round_ended:
                    break
                
                standard_shanten = calculateStandardShanten(hand)
                self.Count("Started at %d-shanten" % standard_shanten)

                called = False
                won = False
                riichi = False
                dealt_in = False

                next_element = next_element.getnext()

                while next_element is not None:
                    tag = next_element.tag

                    if tag == "N" and int(next_element.attrib["who"]) == i:
                        called = True
                    
                    if tag == "AGARI":
                        if int(next_element.attrib["who"]) == i:
                            won = True
                        elif int(next_element.attrib["fromWho"]) == i:
                            dealt_in = True
                        break

                    if tag == "RYUUKYOKU" or tag == "INIT":
                        break

                    if tag == "REACH" and int(next_element.attrib["who"]) == i and int(next_element.attrib["step"]) == 2:
                        riichi = True

                    next_element = next_element.getnext()
                
                if called:
                    self.Count("Opened after a %d-shanten start" % standard_shanten)
                if riichi:
                    self.Count("Riichi'd after a %d-shanten start" % standard_shanten)
                if dealt_in:
                    self.Count("Dealt in after a %d-shanten start" % standard_shanten)
                if won:
                    self.Count("Won after a %d-shanten start" % standard_shanten)


    def GetName(self):
        return "Rates By Shanten Event"