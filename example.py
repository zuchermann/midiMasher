from learn import start_learning, test_file

"""

    this file shows how to use an HMM-based system to fit a melody to a new
    chord progression. Uncomment the lines of code below 'EXAMPLE USE:' to
    use each part of the system.


    * Written in python version = 3.6.
    * External dependencies include: music21, matplotlib, numpy, & scipy.

    Author: Zach Kondak (2018)
"""

######################################################################
# TRAIN FROM A CORPUS OF MELODY AND CHORDS ACCEPTS MUSIC_XML OR MIDI #
# INPUT : (out_file, corpus, transpose_all)                          #
# outfile = out path of file to store learned info from the corpus   #
# corpus = path to folder with melody/chord files (musicXML or MIDI) #
# transpose_all = flag that indicates whether or not each song in... #
#   the corpus is transposed to every possible key. If true, the...  #
#   learning process will take much longer                           #

# EXAMPLE USE:
# start_learning("output.json", "./corpus", False)



######################################################################
# TEST IF A MUSIC_XML OR MIDI FILE IS IN THE CORRECT FORM            #
# INPUT: (input_file, melody_file, chord_file)                       #
# input_file = path to file to be tested                             #
# melody_file = path to output the extracted melody                  #
# chord_file = path to output the extracted chords                   #

# EXAMPLE USE:
# test_file("./corpus/isntshelovely.xml", "./testMelody.mid", "./testChords.mid")