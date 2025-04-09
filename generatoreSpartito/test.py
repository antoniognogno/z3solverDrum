from music21 import *
import os
    
s = stream.Score()
p = stream.Part()
m = stream.Measure()

ts0 = meter.TimeSignature('4/4')
s.append(ts0)

cassa = note.Unpitched(displayName='G4', storedInstrument=instrument.BassDrum())
snare = note.Unpitched(displayName='C4', storedInstrument=instrument.SnareDrum())
pChord = percussion.PercussionChord([cassa, snare])

m.append(pChord)
p.append(m)
s.append(p)

script_dir = os.path.dirname(os.path.abspath(__file__))  # Gets the script's directory
output_file = os.path.join(script_dir, 'spartito.xml') # Creates the path, same folder
s.write('musicxml', output_file)
output_file = os.path.join(script_dir, 'spartito.xml')
print("Spartito creato e salvato in spartito.xml")
s = converter.parse(output_file)
midi_file = s.write('midi', fp='output.mid')
s.show()