def calculateUkeire(hand, remainingTiles, shantenFunction, baseShanten = -2):
    hand = hand.copy()
    if baseShanten == -2:
        baseShanten = shantenFunction(hand)

    value = 0
    tiles = []

    has_manzu = False
    has_souzu = False
    has_pinzu = False

    for i in range(10):
        if hand[i] > 0:
            has_manzu = True
        if hand[i+10] > 0:
            has_pinzu = True
        if hand[i+20] > 0:
            has_souzu = True

    # Check adding every tile to see if it improves the shanten
    for i in range(len(hand)):
        if i % 10 == 0: continue
        if i < 10:
            if not has_manzu: continue
        elif i < 20:
            if not has_pinzu: continue
        elif i < 30:
            if not has_souzu: continue
        elif i > 30 and hand[i] == 0: continue

        hand[i] += 1

        if shantenFunction(hand, baseShanten - 1) < baseShanten:
            # Improves shanten. Add the number of remaining tiles to the ukeire count
            value += remainingTiles[i]
            tiles.append(i)

        hand[i] -= 1

    return [value, tiles]