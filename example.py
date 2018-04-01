from learn import start_learning, test_file
from mashup import mash_songs

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


#########################################################################################
# PERFORMS A MASHUP!                                                                    #
# INPUT: (song1_path, song2_path, corpus_data, destination, startW, transW, emW, distW) #
# song1_path = path to song (musicXML or midi) from which melody will be used           #
# song2_path = path to song (musicXML or midi) from which chords will be used           #
# corpus_data = path to data that has been extracted via the "start_learning"...        #
#   function that was described above                                                   #
# destination = destination file that will store the mashup result, this is a midi...   #
#   file, so make sure the path ends in .mid                                            #
# startW = float from 0.0 to 1.0 indicating the importance of the first note in the...  #
#   song1 melody on the resultant melody                                                #
# transW = float from 0.0 to 1.0 indicating the importance of the state transitions...  #
#   transitions learned from the corpus on the resultant melody                         #
# emW = float from 0.0 to 1.0 indicating the importance of the chords in song2 on...    #
#   the resultant melody                                                                #
# distW = float from 0.0 to 1.0 indicating the importance of the melody in song1 on...  #
#   the resultant melody                                                                #


# EXAMPLE USE:
#mash_songs("./corpus/isntshelovely.xml", "./corpus/Gymnopedie.xml", "output.json", "mash.mid", 0.5, 0.4, 0.6, 0.5)

# NOTE: the result of the above line may be a bit skewed in our fafor since both #
# song1 and song2 are in the corpus, however, we would need a much larger corpus #
# to get these sorts of results on unseen data                                   #
