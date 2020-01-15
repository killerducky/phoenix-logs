import math

def calculateBasicPoints(han, fu, yakuman):
    if han <= 0: return 0

    basicPoints = 0

    if yakuman > 0:
        basicPoints = 8000 * yakuman
    elif han < 5:
        basicPoints = min(fu * math.pow(2, han + 2), 2000)
    elif han == 5:
        basicPoints = 2000
    elif han < 8:
        basicPoints = 3000
    elif han < 11:
        basicPoints = 4000
    elif han < 13:
        basicPoints = 6000
    else:
        basicPoints = 8000

    return basicPoints