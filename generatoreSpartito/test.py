from music21 import *
from music21.note import Note
import os
    
s = stream.Score()
p = stream.Part()
m = stream.Measure()

ts0 = meter.TimeSignature('4/4')
s.append(ts0)

# cassa = note.Unpitched(displayName='C2', storedInstrument=instrument.BassDrum())
# snare = note.Unpitched(displayName='D2', storedInstrument=instrument.SnareDrum())
# hihat = note.Unpitched(displayName='F#2', storedInstrument=instrument.HiHatCymbal())

n = Note("C2", type='quarter')
n1 = Note("G2", type='quarter')
n2 = Note("F2", type='quarter')

p.insert(0, instrument.BassDrum())
p.insert(0, instrument.SnareDrum())
p.insert(0, instrument.HiHatCymbal())

m.append(n)
m.append(n1)
m.append(n2)
p.append(m)


# pChord = percussion.PercussionChord([cassa, snare, hihat])

# m.append(pChord)
# p.append(m)
s.append(p)

script_dir = os.path.dirname(os.path.abspath(__file__))  # Gets the script's directory
output_file = os.path.join(script_dir, 'spartito.xml') # Creates the path, same folder
s.write('musicxml', output_file)
output_file = os.path.join(script_dir, 'spartito.xml')
print("Spartito creato e salvato in spartito.xml")
s = converter.parse(output_file)
midi_file = s.write('midi', fp='output.mid')
s.show()


# This line actually generate the midi on my mac but there is no relevant software to read it and the opening fail
# drumPart.show()
# drumPart.show('midi')