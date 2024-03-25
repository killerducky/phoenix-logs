from log_hand_analyzer import LogHandAnalyzer
from analysis_utils import GetDora, convertTile, yaku_names, convertHandToTenhouString, convertHand
from collections import defaultdict, Counter
from ukeire import calculateUkeire
from shanten import calculateMinimumShanten
import math, os, sys, random, pickle

# Just changing seed: 0.25336503460159937
#                     0.2533903941784605
#                           ^--- noise

# games riichi
#  5000  29082

# Best entropy and settings so far:
GS_C_ccw_bestEntropy = 0.25286634704921196
# penchan is the anchor at 1
GS_C_ccw_ryanmen = 3.7
GS_C_ccw_honorTankiShanpon = 1.9
GS_C_ccw_nonHonorTankiShanpon = 1.1
GS_C_ccw_kanchan = 0.275
GS_C_ccw_riichiSujiTrap = 11        # Applies after GS_C_ccw_kanchan
GS_C_ccw_uraSuji = 1.2

# Search for better settings
GS_C_ccw_ryanmen = 3.7               # worse: 3.6, 3.8
GS_C_ccw_honorTankiShanpon = 1.9     # worse: 1.8, 2.0
GS_C_ccw_nonHonorTankiShanpon = 1.1  # worse: 1.0, 1.2
GS_C_ccw_kanchan = 0.275             # worse: 0.27, 0.28
GS_C_ccw_riichiSujiTrap = 11         # worse: 10, 12
GS_C_ccw_uraSuji = 1.2               # worse: 1.1, 1.3

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


def combo2str(key, combos):
    if not key in combos:
        return f"{key} genbutsu"
    keyCombo = combos[key]
    k = convertHandToTenhouString(Counter({key:1}))
    if combos['all'] == 0:
        return f"{k} 0.0 all waits impossible!"
    return f"{k} {keyCombo['all']/combos['all']*100:.1f}"

def entropy_test(actual_prob, predicted_prob):
    N = 1000
    sum_entropy = 0
    sum_happened = 0
    for i in range(N):
        #if random.random() < actual_prob:
        if i/N < actual_prob:
            # It happened
            q_x = predicted_prob
            sum_happened += 1
        else:
            # It didn't happen
            q_x = 1-predicted_prob
        entropy = -math.log2(q_x)
        sum_entropy += entropy
    print(f'{actual_prob} {predicted_prob:.2f} {sum_entropy/N:.3f} {sum_happened}')

def entropy_tests():
    print(f'act pred ent sum_happened')
    entropy_test(.5, .1)
    entropy_test(.5, .5)
    entropy_test(.5, .9)
    entropy_test(.9, .1)
    entropy_test(.9, .5)
    entropy_test(.9, .85)
    entropy_test(.9, .9)
    entropy_test(.9, .95)
    sys.exit()
# entropy_tests()

class WaitEstimator(LogHandAnalyzer):
    def __init__(self):
        super().__init__()
        self.counts = defaultdict(Counter)
        self.entropy_sum = 0
        self.entropy_cnt = 0
        self.uniq_rounds = set()
        random.seed(1)
        self.calculateUkeireCache = {}
        if os.path.exists("ukeire_cache.pickle"):
            with open("ukeire_cache.pickle", "rb") as fp: self.calculateUkeireCache = pickle.load(fp)
        self.calculateUkeireCacheDirty = False
        print('params: ', GS_C_ccw_ryanmen, GS_C_ccw_honorTankiShanpon, 
              GS_C_ccw_nonHonorTankiShanpon, GS_C_ccw_kanchan, GS_C_ccw_riichiSujiTrap, GS_C_ccw_uraSuji)

    def calcCombos(self, riichiPidx, genbutsu, seen, discardsIncludingRiichiTile):
        riichiTile = discardsIncludingRiichiTile[-1]
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
            honorTankiShanpon = wait['type'] in ['shanpon','tanki'] and wait['tiles'][0] > 30
            nonHonorTankiShanpon = wait['type'] in ['shanpon','tanki'] and wait['tiles'][0] < 30
            if wait['type'] in ['ryanmen']:
                wait['combos'] *= GS_C_ccw_ryanmen
                uraSuji2 = False
                for discard in discardsIncludingRiichiTile:
                    if discard in wait['tiles']: continue
                    for waitTile in wait['tiles']:
                        if discard%10 >=4 and discard%10 <=6 and abs(discard - waitTile) == 2:
                            uraSuji2 = True
                if uraSuji2: wait['combos'] *= GS_C_ccw_uraSuji
            elif honorTankiShanpon:
                wait['combos'] *= GS_C_ccw_honorTankiShanpon
            elif nonHonorTankiShanpon:
                wait['combos'] *= GS_C_ccw_nonHonorTankiShanpon
            elif wait['type'] == 'kanchan':
                wait['combos'] *= GS_C_ccw_kanchan
                if (riichiTile%10)>=4 and (riichiTile%10) <=6 and abs(wait['waitsOn'][0] - riichiTile) == 3:
                    wait['combos'] *= GS_C_ccw_riichiSujiTrap
                    #if wait['waitsOn'][0] in self.riichi_ukeire[riichiPidx]:
                    #    print(f'rst {riichiTile} {self.riichi_ukeire[riichiPidx]} {convertHandToTenhouString(self.hands[riichiPidx])} https://tenhou.net/0/?log={self.round_key}')
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
        self.round_entropy_sums = []

    def RoundEnded(self, init):
        super().RoundEnded(init)
        if len(self.round_entropy_sums):
            picked_entropy_idx = random.randint(0, len(self.round_entropy_sums)-1)
            picked_entropy_sum = self.round_entropy_sums[picked_entropy_idx]
            self.entropy_cnt += 34 # 34 tiles
            self.entropy_sum += picked_entropy_sum

    def DoraRevealed(self, hai, element):
        super().DoraRevealed(hai, element)
        self.dora_indicator.append(convertTile(hai))
        self.dora.append(GetDora(convertTile(hai)))

    def TileDiscarded(self, who, tile, tsumogiri, element):
        super().TileDiscarded(who, tile, tsumogiri, element)

        for riichiPidx in range(4):
            # Note: Skipping furiten cases
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
            # print(f'{self.discards[riichiPidx]} {len(self.discards_at_riichi[riichiPidx])} https://tenhou.net/0/?log={self.round_key}' )
            combos = self.calcCombos(riichiPidx, self.genbutsu[riichiPidx], seen, self.discards_at_riichi[riichiPidx])
            debug = True
            debug = False
            if debug: print('tenpai hand:', convertHandToTenhouString(self.hands[riichiPidx]), self.riichi_ukeire[riichiPidx], self.genbutsu[riichiPidx])
            this_entropy_sum = 0
            for tmpTile in range(38):
                if tmpTile%10 == 0: continue
                # if tmpTile<30: continue  # for testing entropy on only honor tiles
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
                this_entropy_sum += entropy
            self.round_entropy_sums.append(this_entropy_sum)
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

    def calculateUkeire(self, who):
        # Riichi could have closed kans. For each add a fake ankou of East
        handPlusKans = Counter(self.hands[who])
        key = convertHandToTenhouString(handPlusKans)
        if not key in self.calculateUkeireCache:
            self.calculateUkeireCacheDirty = True
            remaining_tiles = [4] * 38
            remaining_tiles[0] = 0
            remaining_tiles[10] = 0
            remaining_tiles[20] = 0
            remaining_tiles[30] = 0
            for i in range(38):
                remaining_tiles[i] -= handPlusKans[i]
            for i in range(len(self.calls[who])):
                handPlusKans += Counter({31:3})
            [value, tiles] = calculateUkeire(handPlusKans, remaining_tiles, calculateMinimumShanten, 0)
            self.calculateUkeireCache[key] = [value, tiles]
        return self.calculateUkeireCache[key]

    def RiichiCalled(self, who, step, element):
        super().RiichiCalled(who, step, element)
        if step == 1:
            return
        self.discards_at_riichi[who] = self.discards[who].copy()
        # print('r dis', who, self.discards_at_riichi, self.discards)
        # print('r hand', who, convertHandToTenhouString(self.hands[who]))
        [value, tiles] = self.calculateUkeire(who)
        # print(tiles)
        self.riichi_ukeire[who] = tiles
        for t in tiles:
            if t in self.genbutsu[who]:
                self.furiten_riichi[who] = 1
                # print('furiten riichi', step, who, tiles, convertHandToTenhouString(self.hands[who]), self.init.attrib['seed'], self.current_log_id)
                break
        # print()

    def TileCalled(self, who, tiles, element):
        # TODO: Kakan can be Roned. If it isn't, add to genbutsu
        # print('call', who, tiles, element.attrib)
        super().TileCalled(who, tiles, element)

    def Win(self, element):
        super().Win(element)

    def PrintResults(self):
        diff = self.entropy_sum/self.entropy_cnt-GS_C_ccw_bestEntropy
        result = "better" if diff < 0 else "worse"
        print (f'entropy_cnt, entropy_cnt/34 average {self.entropy_cnt} {self.entropy_cnt/34:.0f} {self.entropy_sum/self.entropy_cnt} {diff} {result}')
        if self.calculateUkeireCacheDirty:
            with open("ukeire_cache.pickle", "wb") as fp: pickle.dump(self.calculateUkeireCache, fp)
