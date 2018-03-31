# chords given as list of strings representing chords
# notes given as list of ints representing literal pitches
# lastInterval given as int reptresents last observed interval
# startingPitchClass given as int representing pitch class of first note
# possibleIntervals given as list of ints representing all possible intervals
# noteChordPairs given as dictionary see learn.py for structure
# intervals given as dictionary see learn.py for structure


def pitchDistance(pitchStr1, pitchStr2):
    pitch1 = int(pitchStr1)
    pitch2 = int(pitchStr2)
    dist = min([abs(pitch1 - pitch2), abs(pitch1 - pitch2 + 12), abs(pitch1 - pitch2 - 12)])
    prob = 1 - dist / 6.0
    return prob


def viterbi(obs, states, start_p, trans_p, emit_p, prevPitch, melodyPitches, startW=0, transW=1, emW=1, distW=1):
    V = [{}]
    for st in states:
        if prevPitch is None:
            start = (start_p[st] * startW) + (1 - startW)
        else:
            start = (trans_p[prevPitch][st] * transW) + (1 - transW)
        em = (emit_p[st][obs[0]] * emW) + (1 - emW)
        dist = (pitchDistance(melodyPitches[0], st) * distW) + (1 - distW)
        V[0][st] = {"prob": start * em * dist, "prev": None}
    # Run Viterbi when t > 0
    for t in range(1, len(obs)):
        V.append({})
        for st in states:
            max_tr_prob = max(
                V[t - 1][prev_st]["prob"] * ((trans_p[prev_st][st] * transW) + (1 - transW)) for prev_st in states)
            for prev_st in states:
                if V[t - 1][prev_st]["prob"] * ((trans_p[prev_st][st] * transW) + (1 - transW)) == max_tr_prob:
                    em = (emit_p[st][obs[t]] * emW) + (1 - emW)
                    dist = (pitchDistance(melodyPitches[t], st) * distW) + (1 - distW)
                    max_prob = max_tr_prob * em * dist
                    V[t][st] = {"prob": max_prob, "prev": prev_st}
                    break
    opt = []
    # The highest probability
    max_prob = max(value["prob"] for value in V[-1].values())
    previous = None
    # Get most probable state and its backtrack
    for st, data in V[-1].items():
        if data["prob"] == max_prob:
            opt.append(st)
            previous = st
            break
    # Follow the backtrack till the first observation
    for t in range(len(V) - 2, -1, -1):
        opt.insert(0, V[t + 1][previous]["prev"])
        previous = V[t + 1][previous]["prev"]

    return opt
