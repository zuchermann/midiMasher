import json, music21, sys
from music21 import *
from viterbi import viterbi

BIG_BOY = 99999


# Read data from stdin
def read_in():
    lines = sys.stdin.readlines()
    # Since our input would only be having one line, parse our JSON data from that
    return json.loads(lines[0])


def simpleMash(song1, song2):
    s = music21.stream.Score(id='mainScore')
    # s2Parts = song2.getElementsByClass('Part')
    # s.insert(0, song1.parts[0])
    # s.insert(0, song2.parts[1])
    mel = song1.parts[0]
    chords = song2.chordify()
    chord = chords.getElementsByOffset(0)
    for el in mel.recurse().notes:
        noteClass = el.pitch.pitchClass
        offset = el.offset
        newChord = chords.getElementsByOffset(offset)
        count = 0
        for n in newChord.recurse().notes:
            for note in n.pitches:
                count = count + 1
                break;
        if (count > 1):
            chord = newChord
        diff = 0;
        for n in chord.recurse().notes:
            for note in n.pitches:
                chordNote = note.pitchClass
                if (abs(chordNote - noteClass) < diff):
                    diff = chordNote - noteClass
                if (diff == 0):
                    diff = chordNote - noteClass
        el.transpose(diff, inPlace=True)
    s.insert(0, mel)
    count = 0
    for part in song2.parts:
        if (count > 0):
            s.insert(part)
        count = count + 1
    s.show()
    return s


def chordString(chord):
    notelist = []
    for ch in chord.recurse().getElementsByClass('Chord'):
        for pitch in ch.pitches:
            notelist.append(pitch.pitchClass)
    notelist.sort()
    result = str(list(set(notelist)))  # conver list -> set -> list to remove duplicates
    return result


def findClosestChord(chords, offsetList, offset):
    if offset in offsetList:
        return chordString(chords.getElementsByOffset(offset))
    lastOffset = 0
    for num in offsetList:
        if num < offset:
            lastOffset = num
        else:
            break
    return chordString(chords.getElementsByOffset(lastOffset))


def makeOffsetList(chords):
    result = []
    result.append(0)
    for chord in chords.recurse().getElementsByClass('Chord'):
        offset = chord.offset
        if (offset > 0):
            result.append(offset)
    return result


def generateWindows(windowSize, melody, chords):
    chordified = chords.chordify()
    chordOffsetList = makeOffsetList(chordified)
    output = []
    counter = 0
    prevPitch = None

    for note in melody.recurse().notes:
        try:
            pitches = [note.pitch]
        except AttributeError:
            pitches = note.pitches

        for pitch in pitches:
            if counter == 0:
                output.append({})
                output[-1]['notes'] = []
                output[-1]['prevNote'] = prevPitch
                output[-1]['pitchClasses'] = []
                output[-1]['chordStrings'] = []
            output[-1]['pitchClasses'].append(str(pitch.pitchClass))
            output[-1]['notes'].append(pitch)
            chord = findClosestChord(chordified, chordOffsetList, note.offset)
            output[-1]['chordStrings'].append(chord)
            counter = (counter + 1) % windowSize
            prevPitch = pitch
    return output


def litteralNote(note):
    pitchClass = note.pitch.pitchClass
    octave = int(note.octave)
    val = pitchClass + (octave * 12)
    return val


def getIntervals(melody):
    lastNote = BIG_BOY
    intervals = []
    for note in melody.recurse().notes:
        if lastNote != BIG_BOY:
            thisNote = litteralNote(note)
            interval = thisNote - lastNote
            intervals.append(interval)
        lastNote = litteralNote(note)
    return intervals


def intervalsDiff(intervalList, startingNote):
    result = []
    acc = 0
    for interval in intervalList:
        result.append(startingNote + acc)
        acc = acc + interval
    return result


def mash(song1, song2, startW, transW, emW, distW):
    emission_probability = {}
    transition_probability = {}
    observations = []
    start_probability = {}
    states = []

    with open('output.json') as data_file:
        data = json.load(data_file)
        emission_probability = data['emission_probability']
        transition_probability = data['transition_probability']
        observations = data['observations']
        start_probability = data['start_probability']
        states = data['states']

    s = music21.stream.Score(id='mainScore')
    melody = song1.parts[0]
    chords = song2.parts[1]
    windowSize = 4
    print('generating windows')
    windows = generateWindows(windowSize, melody.flat,
                              chords.flat)  # generates list or lists of size = windowSize {note, chord, offset}
    # print(windows)
    for window in windows:
        notes = window['notes']
        prevNote = window['prevNote']
        pitchClasses = window['pitchClasses']
        chordStrings = window['chordStrings']
        count = 0
        prev = None
        for prevState in states:
            for thisState in states:
                if thisState not in transition_probability[prevState]:
                    transition_probability[prevState][thisState] = 0.0
        for chordString in chordStrings:
            for state in states:
                if chordString not in emission_probability[state]:
                    emission_probability[state][chordString] = 0.0
        if prevNote is None:
            lastPitch = None
        else:
            lastPitch = str(prevNote.pitchClass)
        pitchList = viterbi(chordStrings, states, start_probability, transition_probability, emission_probability,
                            lastPitch, pitchClasses, startW, transW, emW, distW)
        for i in range(len(pitchList)):
            newPitch = int(pitchList[i])
            melodyPitch = int(pitchClasses[i])
            transposeUp = 0
            for trans in range(12):
                if ((((melodyPitch + trans) - newPitch) + 24) % 12) == 0:
                    transposeUp = trans
                    break
            transposeDown = 0
            for trans in range(12):
                if ((((melodyPitch - trans) - newPitch) + 24) % 12) == 0:
                    transposeDown = -1 * trans
                    break
            transpose = transposeDown
            if (abs(transposeUp) < abs(transposeDown)):
                transpose = transposeUp
            notes[i].transpose(transpose, inPlace=True)
            # print(pitch)
    s.insert(0, melody)
    s.insert(0, chords)
    s.show()
    # s.show()
    return s


def main():
    # get our data as an array from read_in()
    lines = read_in()
    song1_path = lines.get(u'song1')
    song2_path = lines.get(u'song2')
    destination = lines.get(u'destination')
    startW = float(lines.get(u'startingNoteWeight'))
    transW = float(lines.get(u'corpusWeight'))
    emW = float(lines.get(u'chordWeight'))
    distW = float(lines.get(u'melodyWeight'))
    song1_parsed = music21.converter.parse(song1_path)
    song2_parsed = music21.converter.parse(song2_path)
    mashed = mash(song1_parsed, song2_parsed, startW, transW, emW, distW)
    SubConverter = music21.converter.subConverters.ConverterMidi()
    midi = SubConverter.write(mashed, 'mid', destination)


# print midi

# start process
if __name__ == '__main__':
    main()

# to test run: cat pytest.txt | python mashup.py
