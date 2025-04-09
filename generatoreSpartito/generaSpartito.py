#Parto da una lista di questo tipo:
# ['H', '_', 'S', 'H', 'K', 'S', '_', 'K', '_', 'H', '_', 'S']
# Che rappresenta una battuta di batteira dove H = HiHat, K = Cassa, S = Snare, _ = pausa
# NB: _ non rappresenta una pausa effettiva, rappresenta una pausa per quello strumento (asseganzione falsa variabile i al tempo j)
# Per essere una pausa completa tutte le variabili devono essere _, quindi del tipo '_', '_', '_'
#

from music21 import *
import os

# def crea_battuta_con_note_e_pause(note_durate):
#     """Crea una battuta con note e pause divise in sedicesimi.

#     Args:
#         note_durate: Una lista di tuple. Ogni tupla contiene una nota (es. 'C4')
#                      e una durata (es. 'q' per quarto, 'e' per sedicesimo).
#     Returns:
#         stream.Measure: La battuta creata.
#     """
#     m = stream.Measure()
#     note_mapping = {  # Mapping da testo a note/pause
#         'C': note.Note('C4'),
#         'D': note.Note('D4'),
#         'E': note.Note('E4'),
#         'F': note.Note('F4'),
#         'G': note.Note('G4'),
#         'A': note.Note('A4'),
#         'B': note.Note('B4'),
#         '_': note.Rest() # "_" è una pausa
#     }
#     tempi = { # Mapping dei tempi
#         'q': duration.Duration(quarterLength=1.0), # Quarto
#         'h': duration.Duration(quarterLength=2.0), # Mezzo
#         'w': duration.Duration(quarterLength=4.0),  # Intera
#         'e': duration.Duration(quarterLength=0.25)  # Sedicesimo
#     }

#     for nota_testo, durata_testo in note_durate:
#         if nota_testo in note_mapping:
#             nota = note_mapping[nota_testo]
#             if durata_testo in tempi:
#                 nota.duration = tempi[durata_testo]
#             m.append(nota)
#         else:
#             print(f"Warning: Invalid note symbol: {nota_testo}. Skipping.")

#     return m



#Funzione per generare la lista di note da questo formato:
# ['H', '_', 'S', 'H', 'K', 'S', '_', 'K', '_']
# 
#In questo formato:
# [<music21.note.Note G>, <music21.note.Rest quarter>, <music21.note.Note E>, 
# <music21.note.Note G>, <music21.note.Note C>, <music21.note.Note E>, 
# <music21.note.Rest quarter>, <music21.note.Note C>, <music21.note.Rest quarter>]

def creaListaNote(groove):    
    # Il tuo mapping da caratteri a oggetti music21
    note_mapping = {
        'H': note.Note('G5'), # Sol alto (Hihat chiuso)
        'K': note.Note('C4'), # Do centrale (Kick/Cassa) - Ho usato C4 come standard per la cassa
        'S': note.Note('E4'), # Mi (Snare/Rullante) - Spesso si usa D4 o E4 per il rullante
        '_': note.Rest()      # Pausa
    }
    
    # Lista per contenere la sequenza di oggetti music21 risultante
    music_sequence = []

    # Itera su ogni simbolo nel groove
    for symbol in groove:
        # Cerca il simbolo nel mapping
        
        music_object = note_mapping.get(symbol)

        if music_object is not None:
            music_sequence.append(music_object)
        else:
            # Gestisci il caso in cui un simbolo nel groove non sia presente nel mapping
            print(f"Attenzione: Simbolo '{symbol}' non trovato in note_mapping. Ignorato.")

    print(music_sequence)
    objToString(music_sequence)
    return music_sequence


#Funzione per cambiare da questo formato:
# 
# [<music21.note.Note G>, <music21.note.Rest quarter>, <music21.note.Note E>, 
# <music21.note.Note G>, <music21.note.Note C>, <music21.note.Note E>, 
# <music21.note.Rest quarter>, <music21.note.Note C>, <music21.note.Rest quarter>]
#
#A questo formato:
# ['G5', '_', 'E4', 'G5', 'C4', 'E4', '_', 'C4', '_']

def objToString(notes):

    # Lista per contenere le stringhe risultanti
    notestr = []

    # Itera su ogni oggetto nella sequenza musicale
    for item in notes:
        if isinstance(item, note.Note):
            # Se è una Nota, prendi il nome della nota con l'ottava
            notestr.append(item.pitch.nameWithOctave)
        elif isinstance(item, note.Rest):
            # Se è una Pausa, aggiungi il simbolo desiderato
            notestr.append('_')
        #-------------------------------------------------------
        #Manca la gestione dell'errore se ci fosse qualcosa di "sconosciuto" (simboli)

    # Stampa la lista di stringhe risultante
    print(notestr)
    return notestr

def creaSpartitoDaNote(notes):
    
    s = stream.Score()
    p = stream.Part()
    m = stream.Measure()
    
    ts0 = meter.TimeSignature('4/4')
    s.append(ts0)

    #Devo raggiungere 2 liste del genere
    # notes = ['G5', 'C4', 'C4', 'C4', 'C4', 'C4']
    # durations = [1, 0.5, 0.5, 1, 1, 0.5, 1, 1, 0.5, 0.5, 1, 0.5]

    # if len(notes) != len(durations):
    #     print("Errore le liste devonno avere la stessa lunghezza")
    # else:
        # for n, dur_val in zip(notes, durations):
        #     nota = note.Note(n, quarterLength = dur_val) 
        #     m.append(nota)
    
    # for n in notes:
    #     print(n)
    #     if n == "_":
    #         nota = note.Rest()
    #     else:
    #         nota = note.Note(n) 
    #     m.append(nota)

    nStrumenti = 3

    # Crea la lista di chunk direttamente con una list comprehension
    notePerOgniBattito = [notes[i : i + nStrumenti] for i in range(0, len(notes), nStrumenti)]
    print(notePerOgniBattito)

    notePerOgniBattitoSenzaPause = [[item for item in sub_list if item != '_'] for sub_list in notePerOgniBattito]
    print(notePerOgniBattitoSenzaPause)



    # Accordi
    for strumenti in notePerOgniBattitoSenzaPause:
        accordo = chord.Chord(strumenti)
        m.append(accordo)
    


    p.append(m)
    s.append(p)
    s.insert(0, metadata.Metadata())
    s.metadata.title = 'CCL Drum'
    s.metadata.composer = 'Antonio'
    s.makeMeasures(inPlace=True)
    
    #Battuta 1, in 4/4
    # ts0 = meter.TimeSignature('4/4')
    # streams.append(ts0)
    # n1 = note.Note('G5')
    # n1.quarterLength = .5 #Ottavo
    # n2 = note.Note('C4')
    # n2.quarterLength = 0.75 #Ottavo
    # var = 1 
    # n3 = note.Note('C4', quarterLenght = var) # Quarto
    # streams.append(s)
    # streams.append(n1)
    # streams.append(n2)
    # streams.append(n3)
    # streams.makeMeasures(inPlace=True)
    

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



groove = ['H', '_', 'S', 'H', 'K', 'S', '_', 'K', '_', 'H', '_', 'S']
noteGroove = creaListaNote(groove)
noteFinali = objToString(noteGroove)
spartito = creaSpartitoDaNote(noteFinali)


# #FUNZIONA
# # Input testuale (esempio)
# testo_musicale = "K q _ K q S q" # Input
# spartito = creaSpartitoDaNote(noteGroove)

# Esportazione in MusicXML (per visualizzazione in software come MuseScore)
script_dir = os.path.dirname(os.path.abspath(__file__))  # Gets the script's directory
output_file = os.path.join(script_dir, 'file/spartito.xml') # Creates the path, same folder
spartito.write('musicxml', output_file)
output_file = os.path.join(script_dir, 'file/spartito.xml')
print("Spartito creato e salvato in spartito.xml")
s = converter.parse(output_file)
midi_file = s.write('midi', fp='output.mid')
s.show()
