from log_hand_analyzer import LogHandAnalyzer
from analysis_utils import GetDora, convertTile, yaku_names, convertHandToTenhouString
from collections import defaultdict, Counter
from ukeire import calculateUkeire
from shanten import calculateMinimumShanten

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

def calcCombos(genbutsu, seen):
    waitsArray = generateWaits()
    heroUnseenTiles = Counter({i: 4 for i in range(1,38)})
    heroUnseenTiles -= seen
    # print('gen', genbutsu)
    # print('seen', seen)
    # print('heroUnseenTiles', heroUnseenTiles)

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
    keyCombo = combos[key]
    k = convertHandToTenhouString(Counter({key:1}))
    if not key in combos:
        return f"{k} genbutsu"
    # print(key, keyCombo['all'], combos['all'])
    if combos['all'] == 0:
        return f"{k} 0.0 all waits impossible!"
    return f"{k} {keyCombo['all']/combos['all']*100:.1f}"

class WaitEstimator(LogHandAnalyzer):
    def __init__(self):
        super().__init__()
        self.tsumogiri = [0,0,0,0]
        self.first_discards = [0,0,0,0]
        self.dora = []
        self.dora_discarded = [0,0,0,0]
        self.discards_at_riichi = [[],[],[],[]]
        self.riichi_ukeire= [[],[],[],[]]
        self.genbutsu=[set(), set(), set(), set()]
        self.counts = defaultdict(Counter)

    def RoundStarted(self, init):
        super().RoundStarted(init)
        self.tsumogiri = [0,0,0,0]
        self.first_discards = [0,0,0,0]
        self.dora_discarded = [0,0,0,0]
        self.discards_at_riichi = [[],[],[],[]]
        self.riichi_ukeire= [[],[],[],[]]
        self.dora = [GetDora(convertTile(init.attrib["seed"].split(",")[5]))]

    def DoraRevealed(self, hai, element):
        super().DoraRevealed(hai, element)
        self.dora.append(GetDora(convertTile(hai)))

    def TileDiscarded(self, who, tile, tsumogiri, element):
        if self.discards_at_riichi[who]:
            return super().TileDiscarded(who, tile, tsumogiri, element)

        if tsumogiri:
            self.tsumogiri[who] += 1
        
        first = True

        for i in range(4):
            if tile in self.discards[i]:
                first = False
                break
            for call in self.calls[i]:
                if tile in call:
                    first = False
                    break

        if tile in self.dora:
            first = False

        if first:
            self.first_discards[who] += 1
        
        if tile in self.dora:
            self.dora_discarded[who] += 1
        # ----------------------
        self.genbutsu[who].add(tile) # Add to our own genbutsu set
        for riichiPidx in range(4):
            if not self.riichi_ukeire[riichiPidx] or riichiPidx == who:
                continue
            seen = self.hands[who]
            for t in self.dora:
                seen[t] += 1
            for thisPidx in range(4):
                for t in self.discards[thisPidx]:
                    seen[t] += 1
                for call in self.calls[thisPidx]:
                    for t in call:
                        seen[t] += 1
            # Note: calcCombos before adding this discard to genbutsu
            combos = calcCombos(self.genbutsu[riichiPidx], seen)
            print(convertHandToTenhouString(self.hands[riichiPidx]), self.riichi_ukeire[riichiPidx], self.genbutsu[riichiPidx])
            print('len', len(combos))
            for k in sorted(combos, key=lambda x: 0 if x=='all' else x):
                if k == 'all': continue
                print(combo2str(k, combos))
            print()
            self.genbutsu[riichiPidx].add(tile) # Assuming this passes, add to genbutsu set for riichiPidx player

        super().TileDiscarded(who, tile, tsumogiri, element)

    def RiichiCalled(self, who, step, element):
        super().RiichiCalled(who, step, element)
        if step == 1:
            self.discards_at_riichi[who] = self.discards[who].copy()
            return
        # TODO: [4] * 40? not quite right
        [value, tiles] = calculateUkeire(self.hands[who], [4] * 40, calculateMinimumShanten)
        print(tiles)
        self.riichi_ukeire[who] = tiles
        for t in tiles:
            if t in self.genbutsu[who]:
                print('furiten riichi')
        if self.calls[who] != []:
            print("TODO: ankan", self.calls[who])
        print()

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