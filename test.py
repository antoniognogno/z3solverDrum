#Per torvare i pith giusti per la batteria
from music21 import stream, note, instrument, pitch, duration, chord, tempo

def crea_test_mappa_percussioni(nome_file="test_mappa.mid"):
    partitura = stream.Score()
    parte_batteria = stream.Part(instrument.Percussion())
    parte_batteria.insert(0, tempo.MetronomeMark(number=100))

    #Corretti
    mappa_da_testare = {
        'cassa': 'B1',      
        'rullante': 'D2',   
        'hihat': 'F#2',     
        'openhat': 'A#2',   
        'tom2 (Low Floor)': 'F2', 
        'tom1 (Hi-Mid)': 'B2', 
        'ride': 'D#3',      
        'crash': 'A3',     
    }

    offset = 0.0
    for nome_strumento, nota_pitch in mappa_da_testare.items():
        print(f"Aggiungendo '{nome_strumento}' sulla nota {nota_pitch}...")
        
        # Aggiungiamo 4 colpi per ogni suono per riconoscerlo bene
        for i in range(4):
            p = pitch.Pitch(nota_pitch)
            p.midiChannel = 10
            n = note.Note(p)
            n.duration.quarterLength = 0.25 # un sedicesimo di durata
            parte_batteria.insert(offset, n)
            offset += 0.5 # lascia un po' di spazio tra i suoni
        
        offset += 1.0 # Pausa più lunga tra i diversi strumenti

    partitura.insert(0, parte_batteria)
    partitura.write('midi', fp=nome_file)
    print(f"\nFile di test '{nome_file}' creato. Aprilo per ascoltare i suoni.")
    
    # Prova ad aprirlo direttamente
    try:
        partitura.show()
    except Exception as e:
        print(f"Impossibile aprire la partitura automaticamente: {e}")

# Esegui la funzione
crea_test_mappa_percussioni()


