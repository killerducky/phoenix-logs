def calculateUkeire(hand, remainingTiles, shantenFunction, baseShanten = -2):
    if baseShanten == -2:
        baseShanten = shantenFunction(hand)

    value = 0
    tiles = []

    # Check adding every tile to see if it improves the shanten
    for i in range(len(hand)):
        if i % 10 == 0: continue

        hand[i] += 1

        if shantenFunction(hand, baseShanten - 1) < baseShanten:
            # Improves shanten. Add the number of remaining tiles to the ukeire count
            value += remainingTiles[i]
            tiles.append(i)

        hand[i] -= 1

    return [value, tiles]