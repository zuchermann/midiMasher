import os, json, sys, music21, glob
from music21 import *


'''
*******************
STRUCTURE OF OUTPUT
*******************

{
	'intervals' :											bigrams of intervals in melodies
		{
			'0' : [											represents conditional interval; 0 is unison, 1 is half step, etc...
					{'value' : 0, 'prob' : 0.5},			means there is a 50% chance of a 0 interval following a 0 interval
					...
				  ],
			...
		}
	'noteChordPairs' :										probability of note being played over given chord
		{
			'[0, 5, 9]' : [									represent chord as list of pitch classes
							{'value' : 0, 'prob' : 0.5},	means note c (pitch class) has a 50% probability of being played over chord [0, 5, 9]
							...
						  ],
			...
		}
}
'''


def makeNoteList(melody):
    result = []
    for note in melody.recurse().notes:
        pitchClass = note.pitch.pitchClass
        octave = int(note.octave)
        val = pitchClass + (octave * 12)
        result.append(val)
    return result


def finalize(values):
    result = dict()
    for key in values:
        result[key] = dict()
        count = 0.0
        for innerKey in values[key]:
            count += values[key][innerKey]
        for innerKey in values[key]:
            result[key][innerKey] = values[key][innerKey] / float(count)
    return result


def learnIntervals(notelist, data):
    for i in range(len(notelist) - 1):
        if (i > 0):
            lastNote = notelist[i - 1]
            thisNote = notelist[i]
            nextNote = notelist[i + 1]
            lastInterval = str(thisNote - lastNote)
            nextInterval = nextNote - thisNote
            if (lastInterval in data['intervals']):
                data['intervals'][lastInterval].append(nextInterval)
            else:
                data['intervals'][lastInterval] = []
                data['intervals'][lastInterval].append(nextInterval)


def makeOffsetList(chords):
    result = []
    result.append(0)
    for chord in chords.recurse().getElementsByClass('Chord'):
        offset = chord.offset
        if (offset > 0):
            result.append(offset)
    return result


def chordString(chord):
    notelist = []
    for ch in chord.recurse().getElementsByClass('Chord'):
        for pitch in ch.pitches:
            notelist.append(pitch.pitchClass)
    notelist.sort()
    result = str(list(set(notelist)))  # conver list -> set -> list to remove duplicates
    return result


def chordList(chord):
    notelist = []
    for ch in chord.recurse().getElementsByClass('Chord'):
        for pitch in ch.pitches:
            notelist.append(pitch.pitchClass)
    notelist.sort()
    return notelist


def findClosestChord(chords, offsetList, offset):
    if offset in offsetList:
        return chordString(chords.getElementsByOffset(offset))
    lastOffset = 0
    for num in offsetList:
        if num < offset:
            lastOffset = num
        else:
            break
    return str(chordList(chords.getElementsByOffset(lastOffset)))


def findClosestChordList(chords, offsetList, offset):
    if offset in offsetList:
        return chordList(chords.getElementsByOffset(offset))
    lastOffset = 0
    for num in offsetList:
        if num < offset:
            lastOffset = num
        else:
            break
    return chordList(chords.getElementsByOffset(lastOffset))


def findLastChord(offset, chords):
    chordified = chords.chordify()
    chordOffsetList = makeOffsetList(chordified)
    chord = findClosestChord(chordified, chordOffsetList, offset)
    return chord


def learnNoteChordPairs(melody, chords, data):
    chordified = chords.chordify()
    chordOffsetList = makeOffsetList(chordified)
    for note in melody.recurse().notes:
        nearestChord = findClosestChord(chordified, chordOffsetList, note.offset)
        if (nearestChord in data['noteChordPairs']):
            data['noteChordPairs'][nearestChord].append(note.pitch.pitchClass)
        else:
            data['noteChordPairs'][nearestChord] = []
            data['noteChordPairs'][nearestChord].append(note.pitch.pitchClass)


def learn_intervals(song, data, transposeAll):
    keys = 1
    if transposeAll:
        keys = 12
    for transposition in range(keys):
        melody = song.parts[0].flat
        melody.transpose(transposition, inPlace=True)
        chords = song.parts[1].flat
        chords.transpose(transposition, inPlace=True)
        notelist = makeNoteList(melody)
        intervals = learnIntervals(notelist, data)
        noteChordPairs = learnNoteChordPairs(melody, chords, data)


def start_intervals(transposeAll, directory, outPath):
    data = dict()
    numberOfFiles = len(glob.glob1(directory, "*.xml"))
    numberOfFiles = numberOfFiles + len(glob.glob1(directory, "*.mid"))
    count = 0
    for filename in os.listdir(directory):
        if filename.endswith(".xml") or filename.endswith(".mid"):
            if (count == 0):
                data['intervals'] = {}
                data['noteChordPairs'] = {}
            parsed = music21.converter.parse(os.path.join(directory, filename))
            learn_intervals(parsed, data, transposeAll)
            count = count + 1
            print('learned ' + filename + ': ' + str(count) + ' out of ' + str(numberOfFiles))
            continue
        else:
            continue
    data['intervals'] = finalize(data['intervals'])
    data['noteChordPairs'] = finalize(data['noteChordPairs'])
    output(data, outPath)


def learnPitcheClassesAndChords(melody, chords, data, allChordsList):
    count = 0
    chordified = chords.chordify()
    chordOffsetList = makeOffsetList(chordified)
    for note in melody.recurse().notes:

        try:
            pitches = [note.pitch]
        except AttributeError:
            pitches = note.pitches

        # print(count)
        for pitch in pitches:
            if count > 0:
                key = lastPitch.pitchClass
                if key in data['transition_probability']:
                    nextKey = pitch.pitchClass
                    if nextKey in data['transition_probability'][key]:
                        data['transition_probability'][key][nextKey] += 1
                    else:
                        data['transition_probability'][key][nextKey] = 1
                else:
                    data['transition_probability'][key] = dict()
                    nextKey = pitch.pitchClass
                    data['transition_probability'][key][nextKey] = 1
            else:
                key = pitch.pitchClass
                if key in data['start_probability']:
                    data['start_probability'][key] += 1
                else:
                    data['start_probability'][key] = 1
            nearestChord = findClosestChord(chordified, chordOffsetList, note.offset)
            nearestChordList = findClosestChordList(chordified, chordOffsetList, note.offset)
            if (nearestChordList not in allChordsList):
                allChordsList.append(nearestChordList);
            key = pitch.pitchClass
            if key in data['emission_probability']:
                if nearestChord in data['emission_probability'][key]:
                    data['emission_probability'][key][nearestChord] += 1
                else:
                    data['emission_probability'][key][nearestChord] = 1
            else:
                data['emission_probability'][key] = dict()
                data['emission_probability'][key][nearestChord] = 1
            key = pitch.pitchClass
            if str(key) not in data['states']:
                data['states'].append(str(key))
            if nearestChord not in data['observations']:
                data['observations'].append(nearestChord)
            count = count + 1
            lastPitch = pitch


def learn_pitchClasses(song, data, transposeAll, allChordsList):
    keys = 1
    if transposeAll:
        keys = 12
    for transposition in range(keys):
        if transposition > 0:
            trans = 1
        else:
            trans = 0
        melody = song.parts[0].flat
        melody.transpose(trans, inPlace=True)
        chords = song.parts[1].flat
        chords.transpose(trans, inPlace=True)
        learnPitcheClassesAndChords(melody, chords, data, allChordsList)

        # notelist = makeNoteList(melody)
        # intervals = learnIntervals(notelist, data)
        # noteChordPairs = learnNoteChordPairs(melody, chords, data)


def getAllScales():
    scales = []
    for i in range(12):
        # major
        newscale = []
        for p in scale.MajorScale(pitch.Pitch(i)).pitches:
            newscale.append(p.pitchClass)
        scales.append(newscale)

        # minor
        newscale = []
        for p in scale.MinorScale(pitch.Pitch(i)).pitches:
            newscale.append(p.pitchClass)
        scales.append(newscale)
    return scales


def addScales(allChordsList, data, allScales):
    for chord in allChordsList:
        for scale in allScales:
            isin = 1
            for note in chord:
                if note not in scale:
                    isin = 0
                    break
            if isin == 1:
                emission = data['emission_probability']
                if note in emission:
                    if str(chord) in emission[note]:
                        emission[note][str(chord)] = emission[note][str(chord)] + 1
                    else:
                        emission[note][str(chord)] = 1
                else:
                    emission[note] = {}
                    emission[note][str(chord)] = 1


def start_pitchClasses(transposeAll, directory, outPath):
    data = dict()
    numberOfFiles = len(glob.glob1(directory, "*.xml"))
    numberOfFiles = numberOfFiles + len(glob.glob1(directory, "*.mid"))
    count = 0
    allChordsList = []
    for filename in os.listdir(directory):
        if filename.endswith(".xml") or filename.endswith(".mid"):
            if (count == 0):
                data['transition_probability'] = {}
                data['emission_probability'] = {}
                data['start_probability'] = {}
                data['states'] = []
                data['observations'] = []
            print('learning ' + filename + ': ' + str(count + 1) + ' out of ' + str(numberOfFiles))
            parsed = music21.converter.parse(os.path.join(directory, filename))
            learn_pitchClasses(parsed, data, transposeAll, allChordsList)
            count = count + 1
            continue
        else:
            continue
    # print(allChordsList)
    allScales = getAllScales()
    # print(allScales)
    addScales(allChordsList, data, allScales)
    data['transition_probability'] = finalize(data['transition_probability'])
    data['emission_probability'] = finalize(data['emission_probability'])
    startCount = 0.0
    for key in data['start_probability']:
        startCount += data['start_probability'][key]
    for key in data['start_probability']:
        data['start_probability'][key] = data['start_probability'][key] / float(startCount)
    output(data, outPath)


def start_pitches(transposeAll):
    print('not supported')


def output(data, outPath):
    with open(outPath, 'w') as outfile:
        json.dump(data, outfile, sort_keys=True, indent=4, separators=(',', ': '))


def start_learning(out_file, corpus, transpose_all):
    start_pitchClasses(transpose_all, corpus, out_file)


def test_file(input_file, melody_file, chord_file):
    song = music21.converter.parse(input_file)
    melody = song.parts[0].flat
    chords = song.parts[1].flat
    subConverter = music21.converter.subConverters.ConverterMidi()
    subConverter.write(melody, 'mid', melody_file)
    subConverter.write(chords, 'mid', chord_file)