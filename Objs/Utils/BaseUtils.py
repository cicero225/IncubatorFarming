import bisect
import random



def WeightedDictRandom(inDict, num_sel=1):
    """Given an input dictionary with weights as values, picks num_sel uniformly weighted random selection from the keys"""
    # Selection is without replacement (important for use when picking participants etc.)
    if not inDict:
        return ()
    if num_sel > len(inDict):
        raise IndexError
    if not num_sel:
        return ()
    if num_sel == len(inDict):
        return list(inDict.keys())
    keys = []
    allkeys = list(inDict.keys())
    allvalues = list(inDict.values())
    cumsum = [0]
    for weight in allvalues:
        if weight < 0:
            raise TypeError(
                "Weights of a dictionary for random weight selection cannot be less than 0")
        cumsum.append(cumsum[-1] + weight)
    for dummy in range(num_sel):
        # The 1e-100 is important for numerical reasons
        thisrand = random.uniform(1e-100, cumsum[-1] - 1e-100)
        selected = bisect.bisect_left(cumsum, thisrand) - 1
        keys.append(allkeys.pop(selected))
        if dummy != num_sel - 1:
            remWeight = allvalues.pop(selected)
            for x in range(selected + 1, len(cumsum)):
                cumsum[x] -= remWeight
            cumsum.pop(selected + 1)
    return keys