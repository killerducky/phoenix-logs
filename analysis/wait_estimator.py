from log_hand_analyzer import LogHandAnalyzer
from analysis_utils import GetDora, convertTile, yaku_names, convertHandToTenhouString
from collections import defaultdict, Counter
from ukeire import calculateUkeire
from shanten import calculateMinimumShanten
import math

terminal_tiles = [1,9,11,19,21,29]
two_eight_tiles = [2,8,12,18,22,28]

def generateWaits():
    waitsArray = []
    for ryanmen in [[2,3],[3,4],[4,5],[5,6],[6,7],[7,8]]:
        for suit in range(3):
            wait = {}
            wait['tiles'] = [suit*10+ryanmen[0], suit*10+ryanmen[1]]
            wait['waitsOn'] = [suit*10+ryanmen[0]-1, suit*10+ryanmen[1]+1]
            wait['type'] = 'ryanmen'
            waitsArray.append(wait)
    for kanchan in [[1,3],[2,4],[3,5],[4,6],[5,7],[6,8],[7,9]]:
        for suit in range(3):
            wait = {}
            wait['tiles'] = [suit*10+kanchan[0], suit*10+kanchan[1]]
            wait['waitsOn'] = [suit*10+kanchan[0]+1]
            wait['type'] = 'kanchan'
            waitsArray.append(wait)
    # Beware this is getting a little more ad-hoc...
    for penchan in [[1,2,3],[8,9,7]]:
        for suit in range(3):
            wait = {}
            wait['tiles'] = [suit*10+penchan[0], suit*10+penchan[1]]
            wait['waitsOn'] = [suit*10+penchan[2]]
            wait['type'] = 'penchan'
            waitsArray.append(wait)
    for tankiShanpon in ([1,2,3,4,5,6,7,8,9]):
        for type in ['tanki', 'shanpon']:
            for suit in range(4):
                if suit==3 and tankiShanpon>7:
                    continue # honors are 31-37 only
                wait = {}
                wait['type'] = type
                wait['tiles'] = [suit*10+tankiShanpon]*(1 if type=='tanki' else 2)
                wait['waitsOn'] = [suit*10+tankiShanpon]
                waitsArray.append(wait)
    # for wait in waitsArray:
    #     print('w', wait['tiles'], wait['type'])
    return waitsArray

GS_C_ccw_ryanmen = 3
GS_C_ccw_honorTankiShanpon = 2
GS_C_ccw_nonHonorTankiShanpon = 0.5
GS_C_ccw_ryanmen = 3
GS_C_ccw_honorTankiShanpon = 2
GS_C_ccw_nonHonorTankiShanpon = 0.5

def calcCombos(genbutsu, seen):
    waitsArray = generateWaits()
    heroUnseenTiles = Counter({i: 4 for i in range(1,38)})
    heroUnseenTiles -= seen
    # print('gen', genbutsu)
    # print('seen           ', seen)
    # print('heroUnseenTiles', heroUnseenTiles)
    # print('16,17', heroUnseenTiles[16], heroUnseenTiles[17], seen[16], seen[17])

    combos = {'all':0}
    comboTypes = {}
    for wait in waitsArray:
        wait['combos'] = 1
        wait['numUnseen'] = []
        for [i,t] in enumerate(wait['tiles']):
            if i>0 and wait['type']=='shanpon':
                wait['combos'] *= heroUnseenTiles[t]-1 # Shanpons pull the same tile, so after the first one there is 1 less remaining
                wait['numUnseen'].append(heroUnseenTiles[t]-1)
            else:
                wait['combos'] *= heroUnseenTiles[t]
                wait['numUnseen'].append(heroUnseenTiles[t])
        # Shanpons: Order doesn't matter
        if wait['type']=='shanpon':
            wait['combos'] /= len(wait['tiles']) # Technically Math.exp(length) but it's always 2 for this case
        thisGenbutsu = any(t in genbutsu for t in wait['waitsOn'])
        # thisGenbutsu = False
        if thisGenbutsu:
            continue
        wait['origCombos'] = wait['combos']
        # heuristic adjustment for waits that players tend to aim for
        honorTankiShanpon = wait['type'] in ['shanpon','tanki'] and wait['tiles'][0] > 40
        nonHonorTankiShanpon = wait['type'] in ['shanpon','tanki'] and wait['tiles'][0] < 40
        if wait['type'] in ['ryanmen']:
            wait['combos'] *= GS_C_ccw_ryanmen
        elif honorTankiShanpon:
            wait['combos'] *= GS_C_ccw_honorTankiShanpon
        elif nonHonorTankiShanpon:
            wait['combos'] *= GS_C_ccw_nonHonorTankiShanpon
        combos['all'] += wait['combos']
        if not wait['type'] in comboTypes:
            comboTypes[wait['type']] = 0
        comboTypes[wait['type']] += wait['combos']
        if wait['type']=='shanpon':
            wait['combos'] *= 2 # Shanpons always have a partner pair, so multiply by 2 *after* adding the the 'all' combos denominator
        for t in wait['waitsOn']:
            if not t in combos:
                combos[t]={'all':0, 'types':[]}
            combos[t]['all'] += wait['combos']
            combos[t]['types'].append(wait)
    return combos

def combo2str(key, combos):
    if not key in combos:
        return f"{key} genbutsu"
    keyCombo = combos[key]
    k = convertHandToTenhouString(Counter({key:1}))
    if combos['all'] == 0:
        return f"{k} 0.0 all waits impossible!"
    return f"{k} {keyCombo['all']/combos['all']*100:.1f}"

class WaitEstimator(LogHandAnalyzer):
    def __init__(self):
        super().__init__()
        self.counts = defaultdict(Counter)
        self.entropy_sum = 0
        self.entropy_cnt = 0
        self.uniq_rounds = set()

    def RoundStarted(self, init):
        super().RoundStarted(init)
        self.round_key = f'{self.current_log_id} {init.attrib["seed"]}'
        # print('current round: ', round_key)
        if self.round_key in self.uniq_rounds:
            print('error duplicate round: ', self.round_key) # I had a bug and thought there were dups...
            raise
        else:
            self.uniq_rounds.add(self.round_key)
        self.tsumogiri = [0,0,0,0]
        self.first_discards = [0,0,0,0]
        self.dora_discarded = [0,0,0,0]
        self.discards_at_riichi = [[],[],[],[]]
        self.riichi_ukeire= [[],[],[],[]]
        self.genbutsu=[set(), set(), set(), set()]
        self.furiten_riichi = [0,0,0,0]
        self.init = init
        self.dora_indicator = [convertTile(init.attrib["seed"].split(",")[5])]
        self.dora = [GetDora(self.dora_indicator[0])]

    def DoraRevealed(self, hai, element):
        super().DoraRevealed(hai, element)
        self.dora_indicator.append(convertTile(hai))
        self.dora.append(GetDora(convertTile(hai)))

    def TileDiscarded(self, who, tile, tsumogiri, element):
        super().TileDiscarded(who, tile, tsumogiri, element)

        for riichiPidx in range(4):
            if not self.riichi_ukeire[riichiPidx] or riichiPidx == who or self.furiten_riichi[riichiPidx]:
                continue
            seen = Counter(self.hands[who])
            for t in self.dora_indicator:
                seen[t] += 1
            for thisPidx in range(4):
                for t in self.discards[thisPidx]:
                    seen[t] += 1
                for call in self.calls[thisPidx]:
                    # print(call)
                    # TODO: Not true for closed kan!
                    for t in call[1:]:
                        seen[t] += 1
            combos = calcCombos(self.genbutsu[riichiPidx], seen)
            debug = True
            debug = False
            if debug: print('tenpai hand:', convertHandToTenhouString(self.hands[riichiPidx]), self.riichi_ukeire[riichiPidx], self.genbutsu[riichiPidx])
            for tmpTile in range(38):
                if tmpTile == 'all': continue
                # print(combo2str(tmpTile, combos), 1 if tmpTile in self.riichi_ukeire[riichiPidx] else 0)
                q_x = 0 if tmpTile not in combos else combos[tmpTile]['all']/combos['all']
                if not tmpTile in self.riichi_ukeire[riichiPidx]:
                    q_x = 1 - q_x
                if q_x == 0:
                    print(f'error in https://tenhou.net/0/?log={self.round_key}')
                    print('tenpai hand:', riichiPidx, convertHandToTenhouString(self.hands[riichiPidx]), self.riichi_ukeire[riichiPidx], self.genbutsu[riichiPidx])
                    print(combo2str(tmpTile, combos), 1 if tmpTile in self.riichi_ukeire[riichiPidx] else 0)
                entropy = -math.log2(q_x)
                if debug:
                    if not tmpTile in self.riichi_ukeire[riichiPidx]:
                        print(f'  tmpTile, q, entropy {tmpTile} {q_x:.3f} {entropy:.1f}')
                    else:
                        print(f'o tmpTile, q, entropy {tmpTile} {q_x:.3f} {entropy:.1f}')
                self.entropy_cnt += 1
                self.entropy_sum += entropy
        for thisPidx in range(4):
            if thisPidx == who:
                self.genbutsu[thisPidx].add(tile) # Always add to our own genbutsu set
                if tile in self.riichi_ukeire[thisPidx]:
                    # print('furiten after riichi', tile)
                    # TODO: Most of these are actually Rons
                    # Add detection for actual furiten after riichi case
                    self.furiten_riichi[thisPidx] = 1
            elif self.riichi_ukeire[thisPidx]:
                self.genbutsu[thisPidx].add(tile) # Riichi player didn't Ron, so add
                if tile in self.riichi_ukeire[thisPidx]:
                    # print('furiten after riichi', tile)
                    self.furiten_riichi[thisPidx] = 1

    def RiichiCalled(self, who, step, element):
        super().RiichiCalled(who, step, element)
        if step == 1:
            self.discards_at_riichi[who] = self.discards[who].copy()
            return
        converted_hand = Counter(self.hands[who])
        remaining_tiles = [4] * 38
        remaining_tiles[0] = 0
        remaining_tiles[10] = 0
        remaining_tiles[20] = 0
        remaining_tiles[30] = 0
        for i in range(38):
            remaining_tiles[i] -= converted_hand[i]
        # Riichi could have closed kans. For each add a fake ankou of East
        handPlusKans = Counter(self.hands[who])
        for i in range(len(self.calls[who])):
            handPlusKans += Counter({31:3})
        [value, tiles] = calculateUkeire(handPlusKans, remaining_tiles, calculateMinimumShanten)
        # print(tiles)
        self.riichi_ukeire[who] = tiles
        for t in tiles:
            if t in self.genbutsu[who]:
                self.furiten_riichi[who] = 1
                print('furiten riichi', step, who, tiles, convertHandToTenhouString(self.hands[who]), self.init.attrib['seed'], self.current_log_id)
                break
        # print()

    def TileCalled(self, who, tiles, element):
        # TODO: Kakan can be Roned. If it isn't, add to genbutsu
        # print('call', who, tiles, element.attrib)
        super().TileCalled(who, tiles, element)

    def Win(self, element):
        super().Win(element)
        who = int(element.attrib["who"])
        if len(self.discards_at_riichi[who]) < 8: return

        yaku = []

        if "yaku" in element.attrib:
            yaku = [int(x) for x in element.attrib["yaku"].split(",")[0::2]]
        else:
            yaku = [int(x) for x in element.attrib["yakuman"].split(",")[0::2]]

        tile_counts = Counter(self.discards_at_riichi[who])

        terminals = 0
        two_eights = 0
        middles = 0
        honors = 0
        pairs = 0
        suits = [0, 0, 0]

        for tile in tile_counts:
            if tile > 30:
                honors += tile_counts[tile]
            else:
                suits[int(tile / 10)] += tile_counts[tile]

                if tile in terminal_tiles:
                    terminals += tile_counts[tile]
                elif tile in two_eight_tiles:
                    two_eights += tile_counts[tile]
                else:
                    middles += tile_counts[tile]
            
            if tile_counts[tile] > 1:
                pairs += 1

        suits.sort()
        
        for i in yaku:
            name = yaku_names[i]
            self.counts[name]["Discards"] += len(self.discards_at_riichi[who])
            self.counts[name]["Dora"] += self.dora_discarded[who]
            self.counts[name]["First"] += self.first_discards[who]
            self.counts[name]["Tsumogiri"] += self.tsumogiri[who]
            self.counts[name]["1/9"] += terminals
            self.counts[name]["2/8"] += two_eights
            self.counts[name]["Middle"] += middles
            self.counts[name]["Honors"] += honors
            self.counts[name]["Pairs"] += pairs
            self.counts[name]["Suit 1"] += suits[0]
            self.counts[name]["Suit 2"] += suits[1]
            self.counts[name]["Suit 3"] += suits[2]

    def PrintResults(self):
        print (f'entropy_cnt, average {self.entropy_cnt} {self.entropy_sum/self.entropy_cnt:.4f}')
        with open("./results/PondTraits.csv", "w", encoding="utf8") as f:
            f.write("Yaku,Discards,1/9,2/8,Middle,Honors,Suit 1,Suit 2,Suit 3,Pairs,Dora,Live,Tsumogiri\n")

            for yaku in self.counts:
                f.write("%s," % yaku)
                f.write("%d," % self.counts[yaku]["Discards"])
                f.write("%d," % self.counts[yaku]["1/9"])
                f.write("%d," % self.counts[yaku]["2/8"])
                f.write("%d," % self.counts[yaku]["Middle"])
                f.write("%d," % self.counts[yaku]["Honors"])
                f.write("%d," % self.counts[yaku]["Suit 1"])
                f.write("%d," % self.counts[yaku]["Suit 2"])
                f.write("%d," % self.counts[yaku]["Suit 3"])
                f.write("%d," % self.counts[yaku]["Pairs"])
                f.write("%d," % self.counts[yaku]["Dora"])
                f.write("%d," % self.counts[yaku]["First"])
                f.write("%d," % self.counts[yaku]["Tsumogiri"])
                f.write("\n")