import bz2
import sqlite3
from analysis_utils import convertHai, convertTile, getTilesFromCall, GetNextRealTag, draws, discards
from log_analyzer import LogAnalyzer
from shanten import calculateStandardShanten
from collections import Counter, defaultdict
from lxml import etree

class RatesByShanten(LogAnalyzer):
    def __init__(self):
        super().__init__()
        self.shantens = defaultdict(Counter)

    def ParseLog(self, log, log_id):
        rounds = log.findall('INIT')

        for round_ in rounds:
            for i in range(4):
                round_ended = False
                hand = convertHai(round_.attrib['hai%d' % i])
                draw = draws[i]
                discard_count = 0
                is_open = False

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
                        is_open = True
                        break
                    if tag == "AGARI" or tag == "RYUUKYOKU" or tag == "INIT" or tag == "RIICHI":
                        round_ended = True
                        break

                    next_element = GetNextRealTag(next_element)
                
                if round_ended:
                    break
                
                standard_shanten = calculateStandardShanten(hand)
                self.shantens[standard_shanten]["Count"] += 1

                won = False
                riichi = False
                dealt_in = False
                riichi_turn = 0

                next_element = next_element.getnext()

                while next_element is not None:
                    tag = next_element.tag

                    if tag == "N" and int(next_element.attrib["who"]) == i:
                        is_open = True
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
                        riichi_turn = discard_count
                    if tag == "DORA":
                        pass
                    elif tag[0] == discards[i]:
                        discard_count += 1

                    next_element = next_element.getnext()
                
                if is_open:
                    self.shantens[standard_shanten]["Opened"] += 1
                    if won:
                        self.shantens[standard_shanten]["Open Wins"] += 1
                        self.shantens[standard_shanten]["Open Value"] += int(next_element.attrib["ten"].split(",")[1])
                if riichi:
                    self.shantens[standard_shanten]["Riichi"] += 1
                    self.shantens[standard_shanten]["Riichi Turn Totals"] += riichi_turn
                    if won:
                        self.shantens[standard_shanten]["Riichi Wins"] += 1
                        self.shantens[standard_shanten]["Riichi Value"] += int(next_element.attrib["ten"].split(",")[1])
                if dealt_in:
                    self.shantens[standard_shanten]["Deal-ins"] += 1
                if won:
                    self.shantens[standard_shanten]["Wins"] += 1
                    self.shantens[standard_shanten]["Total Value"] += int(next_element.attrib["ten"].split(",")[1])
                    if not riichi and not is_open:
                        self.shantens[standard_shanten]["Dama Wins"] += 1
                        self.shantens[standard_shanten]["Dama Value"] += int(next_element.attrib["ten"].split(",")[1])

    def PrintResults(self):
        with open("./results/StartingShantenRates.csv", "w") as f:
            f.write("Shanten,Count,Open,Riichi,Riichi Turn Totals,Deal-ins,Wins,Total Value,Riichi Wins,Riichi Value,Open Wins,Open Value,Dama Wins,Dama Value\n")
            for i in self.shantens:
                f.write("%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d\n" % (
                    i,
                    self.shantens[i]["Count"],
                    self.shantens[i]["Opened"],
                    self.shantens[i]["Riichi"],
                    self.shantens[i]["Riichi Turn Totals"],
                    self.shantens[i]["Deal-ins"],
                    self.shantens[i]["Wins"],
                    self.shantens[i]["Total Value"],
                    self.shantens[i]["Riichi Wins"],
                    self.shantens[i]["Riichi Value"],
                    self.shantens[i]["Open Wins"],
                    self.shantens[i]["Open Value"],
                    self.shantens[i]["Dama Wins"],
                    self.shantens[i]["Dama Value"],
                    )
                )