from music21 import *
import os

def crea_battuta_con_note_e_pause(note_durate):
    """Crea una battuta con note e pause divise in sedicesimi.

    Args:
        note_durate: Una lista di tuple. Ogni tupla contiene una nota (es. 'C4')
                     e una durata (es. 'q' per quarto, 'e' per sedicesimo).
    Returns:
        stream.Measure: La battuta creata.
    """
    m = stream.Measure()
    note_mapping = {  # Mapping da testo a note/pause
        'C': note.Note('C4'),
        'D': note.Note('D4'),
        'E': note.Note('E4'),
        'F': note.Note('F4'),
        'G': note.Note('G4'),
        'A': note.Note('A4'),
        'B': note.Note('B4'),
        '_': note.Rest() # "_" è una pausa
    }
    tempi = { # Mapping dei tempi
        'q': duration.Duration(quarterLength=1.0), # Quarto
        'h': duration.Duration(quarterLength=2.0), # Mezzo
        'w': duration.Duration(quarterLength=4.0),  # Intera
        'e': duration.Duration(quarterLength=0.25)  # Sedicesimo
    }

    for nota_testo, durata_testo in note_durate:
        if nota_testo in note_mapping:
            nota = note_mapping[nota_testo]
            if durata_testo in tempi:
                nota.duration = tempi[durata_testo]
            m.append(nota)
        else:
            print(f"Warning: Invalid note symbol: {nota_testo}. Skipping.")

    return m

def crea_spartito_da_testo(testo_musicale):
    s = stream.Stream()
    
    #Battuta 1, in 4/4
    ts0 = meter.TimeSignature('4/4')
    s.append(ts0)
    n1 = note.Note('G5')
    n1.quarterLength = .5 #Ottavo
    n2 = note.Note('C4')
    n2.quarterLength = 0.75 #Ottavo
    var = 1 
    n3 = note.Note('C4', quarterLenght = var) # Quarto
    s.append(n1)
    s.append(n2)
    s.append(n3)
    s.makeMeasures(inPlace=True)
    

    # p = stream.Part()
    # s.insert(0, p)
    # note_mapping = {  # Mapping da testo a note/pause
    #     'H': note.Note('G5'), #Sol alto Hihat chiuso
    #     'K': note.Note('C4'), #Fa
    #     'S': note.Note('C5'), #Do alto
    #     '_': note.Rest() # "_" è una pausa
    # }
    # tempi = { # Mapping dei tempi
    #     'q': duration.Duration(quarterLength=1.0), # Quarto
    #     'h': duration.Duration(quarterLength=2.0), # Mezzo
    #     'w': duration.Duration(quarterLength=4.0),  # Intera
    #     'e': duration.Duration(quarterLength=0.25)  # Sedicesimo
    # }
    # # Parse del testo (esempio: "Cq Dq Eq Fq")
    # elementi = testo_musicale.split()  # Separa elementi (nota/durata)
    # note_durate = []
    # for elemento in elementi:  # Now, iterate each element
    #     if len(elemento) >= 2:  # Check if the element has at least note + duration (e.g., "Cq")
    #         nota_testo = elemento[0]
    #         durata_testo = elemento[1]

    #         if nota_testo in note_mapping and durata_testo in tempi:
    #             note_durate.append((nota_testo, durata_testo))
    #         elif nota_testo in note_mapping:
    #             note_durate.append((nota_testo, "q"))
    # # Creazione battuta
    # battuta = crea_battuta_con_note_e_pause(note_durate)
    # p.append(battuta)
    return s

# Input testuale (esempio)
testo_musicale = "K q _ K q S q" # Input
spartito = crea_spartito_da_testo(testo_musicale)

# Esportazione in MusicXML (per visualizzazione in software come MuseScore)
script_dir = os.path.dirname(os.path.abspath(__file__))  # Gets the script's directory
output_file = os.path.join(script_dir, 'spartito.xml') # Creates the path, same folder
spartito.write('musicxml', output_file)
output_file = os.path.join(script_dir, 'spartito.xml')
print("Spartito creato e salvato in spartito.xml")
s = converter.parse(output_file)
s.show()
