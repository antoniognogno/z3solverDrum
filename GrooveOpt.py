import random
from z3 import *
from z3 import Optimize

class ParametriStile:
    def __init__(self):
        #Rock
        self.forzaDoppiaCassa = 95
        self.forzaDoppiaCassaFinale = 98
        self.densitaSincopi = 25
        self.preferenzaSilenzio = 20
        self.forzaCrash = 1  # Forza del crash iniziale o finale
        #Pop
        self.forzaOpenHiHat = 75 
        
        self.densitaComping = 15
        self.forzaSwing = 90

# =======================================================
# 1. Procedure/Funzioni ausiliarie
# =======================================================
def aggiungiPreferenza(optimizer, espressioneBooleana, peso):
    if peso > 0:
        optimizer.add_soft(espressioneBooleana, weight=peso)

def valoreInput(messaggio, default):
    val = input(f"- {messaggio} (default: {default}): ")
    if not val.strip():
        return default
    try:
        val = int(val)
        if 0 <= val <= 100:
            return val
        else:
            print(f"Valore '{val}' fuori range (0-100). Verrà usato il default: {default}")
            return default
    except ValueError:
        print(f"Input '{val}' non è un numero valido. Verrà usato il default: {default}")
        return default

def valoreInputBooleano(messaggio, defaultChar):
    #Chiede un booleana all'utente (es. 's'/'o')."""
    scelta = input(f"- {messaggio} (default: {defaultChar}): ").lower().strip()
    if not scelta:
        return defaultChar
    return scelta[0] # Prende solo il primo carattere


# =======================================================
# 2. Parametri per stile
# =======================================================
def parametriRock():
    print("\nPersonalizza i Pesi per lo Stile ROCK")
    params = ParametriStile()
    params.forzaDoppiaCassa = valoreInput("Forza Doppia Cassa su '3 e' (t=10)", params.forzaDoppiaCassa)
    params.forzaDoppiaCassaFinale = valoreInput("Forza Cassa su '4 e' (t=15)", params.forzaDoppiaCassaFinale)
    params.densitaSincopi = valoreInput("Presenza di altre sincopi di cassa", params.densitaSincopi)
    params.forzaCrash = valoreInput("Forza Crash sul primo quarto o sull'ultimo (t=0 o t=14) (>90 se vuoi inserirlo)", params.forzaCrash)
    params.preferenzaSilenzio = valoreInput("Tendenza al silenzio", params.preferenzaSilenzio)
    return params

def parametriPop():
    print("\nPersonalizza i Pesi per lo Stile POP")
    params = ParametriStile()
    params.forzaDoppiaCassa = valoreInput("Forza Cassa sui quarti", params.forzaDoppiaCassa)
    params.densitaSincopi = valoreInput("Presenza di sincopi", params.densitaSincopi)
    params.forzaOpenHiHat = valoreInput("Forza Open Hi-Hat di anticipo (su '4a')", params.forzaOpenHiHat)
    params.patternHiHat = valoreInputBooleano("Pattern Hi-Hat: (o)ttavi o (s)edicesimi?", 'o')
    return params

def parametriJazz():
    print("\nPersonalizza i Pesi per lo Stile JAZZ")
    params = ParametriStile()
    params.forzaSwing = valoreInput("Definizione del Ride Swing", params.forzaSwing)
    params.densitaComping = valoreInput("Densità note extra (Comping)", params.densitaComping)
    params.preferenzaSilenzio = valoreInput("Tendenza al silenzio", 5)
    return params


def parametriBlues():
    print("\nPersonalizza i Pesi per lo Stile BLUES")
    params = ParametriStile()
    params.forzaSwing = valoreInput("Definizione dello Shuffle", params.forzaSwing)
    params.forzaDoppiaCassaFinale = valoreInput("Forza Rullante su 2 & 4", params.forzaDoppiaCassaFinale)
    params.densitaSincopi = valoreInput("Presenza di sincopi (pickup)", params.densitaSincopi)
    return params

# =======================================================
# 3. Applicazione vincoli per stile
# =======================================================

def vincoliRock(optimizer, strumenti, params):
    hihat = strumenti['hihat']
    rullante = strumenti['rullante']
    cassa = strumenti['cassa']
    crash = strumenti['crash']


    for t in [2, 4, 6, 8, 10, 12]:
        optimizer.add(hihat[t] == True)

    #Scelgo se mettere un crash o hi-hat sul primo quarto o sull'ultimo
    if random.random() < 0.4:
        print("Preferenza crash impostata su t=0")
        aggiungiPreferenza(optimizer, And(crash[0] == True, crash[14] == False), peso=params.forzaCrash)
    else:
        print("Preferenza crash impostata su t=14")
        aggiungiPreferenza(optimizer, And(crash[0] == False, crash[14] == True), peso=params.forzaCrash)
    
    for t in [0, 14]:
        aggiungiPreferenza(optimizer, hihat[t] == True, peso=90)

    for t in [0, 8]:
        optimizer.add(cassa[t] == True) # Kick sul 1 e 3
    for t in [4, 12]:
        optimizer.add(rullante[t] == True) # Snare sul 2 e 4

    aggiungiPreferenza(optimizer, cassa[10] == True, peso=params.forzaDoppiaCassa)
    aggiungiPreferenza(optimizer, cassa[15] == True, peso=params.forzaDoppiaCassaFinale)
    for t in [3, 7, 11, 15]:
        aggiungiPreferenza(optimizer, Or(cassa[t] == True, rullante[t] == True), peso=params.densitaSincopi) # Sincopi


    for t in range(16):
        # Dove non ci aspettiamo la cassa, preferiamo il silenzio.
        if t not in [0, 6, 8, 10, 15]:
            aggiungiPreferenza(optimizer, cassa[t] == False, peso=params.preferenzaSilenzio)
        # Dove non ci aspettiamo il rullante, preferiamo il silenzio.
        if t not in [4, 12]:
            aggiungiPreferenza(optimizer, rullante[t] == False, peso=params.preferenzaSilenzio)



def vincoliPop(optimizer, strumenti, params):

    hihat, rullante, cassa, crash, openhihat = strumenti['hihat'], strumenti['rullante'], strumenti['cassa'], strumenti['crash'], strumenti['openhihat']
    for t in [0, 2, 4, 6, 8, 10, 12, 14]:
        optimizer.add(hihat[t] == True)
        #cassa dritta sui quarti
        if (t%4) == 0:
            optimizer.add(cassa[t] == True)
        #rullante su 2 e 4
        if t == 4 or t == 12:
            optimizer.add(rullante[t] == True)

    if params.patternHiHat == 's':
        print("Pattern Hi-Hat impostato in 16esimi.")
        # Se l'utente vuole i 16esimi, questa è una regola quasi rigida
        for t in range(16):
            aggiungiPreferenza(optimizer, hihat[t] == True, peso=varia(90))
    else: # Default a ottavi
        print("Pattern Hi-Hat impostato a Ottavi.")
        for t in [0, 2, 4, 6, 8, 10, 12, 14]:
            aggiungiPreferenza(optimizer, hihat[t] == True, peso=varia(95))
    

def vincoliJazz(optimizer, strumenti, params):
    hihat, rullante, cassa, crash = strumenti['hihat'], strumenti['rullante'], strumenti['cassa'], strumenti['crash']
    optimizer.add(hihat[4] == True)
    optimizer.add(hihat[12] == True)
    optimizer.add(Implies(hihat[4], Not(rullante[4])))
    optimizer.add(Implies(hihat[12], Not(rullante[12])))
    for t in [0, 4, 8, 12]:
        aggiungiPreferenza(optimizer, hihat[t] == True, peso=int(params.forzaSwing * 0.9))
        aggiungiPreferenza(optimizer, hihat[t + 2] == True, peso=params.forzaSwing)
        aggiungiPreferenza(optimizer, hihat[t + 1] == False, peso=int(params.forzaSwing * 0.8))
    for t in range(16):
        if t not in [4, 12]:
            aggiungiPreferenza(optimizer, cassa[t] == True, peso=params.densitaComping)
            aggiungiPreferenza(optimizer, rullante[t] == True, peso=int(params.densitaComping * 0.7))
    for t in range(16):
        aggiungiPreferenza(optimizer, cassa[t] == False, peso=params.preferenzaSilenzio)
        aggiungiPreferenza(optimizer, rullante[t] == False, peso=params.preferenzaSilenzio)


def vincoliBlues(optimizer, strumenti, params):
    hihat, rullante, cassa, crash = strumenti['hihat'], strumenti['rullante'], strumenti['cassa'], strumenti['crash']
    for t in [0, 4, 8, 12]:
        aggiungiPreferenza(optimizer, hihat[t] == True, peso=params.forzaSwing)
        aggiungiPreferenza(optimizer, hihat[t + 2] == True, peso=params.forzaSwing)
        aggiungiPreferenza(optimizer, hihat[t + 1] == False, peso=int(params.forzaSwing * 0.8))

    aggiungiPreferenza(optimizer, cassa[0] == True, peso=params.forzaDoppiaCassa)
    aggiungiPreferenza(optimizer, cassa[8] == True, peso=params.forzaDoppiaCassa)
    aggiungiPreferenza(optimizer, rullante[4] == True, peso=params.forzaDoppiaCassaFinale)
    aggiungiPreferenza(optimizer, rullante[12] == True, peso=params.forzaDoppiaCassaFinale)
    aggiungiPreferenza(optimizer, cassa[15] == True, peso=params.densitaSincopi)

# =======================================================
# 4. Main Program
# =======================================================

while True:
    print("\n--- Generatore di Ritmi per Batteria ---")
    vincoliStile = {"rock": vincoliRock, "jazz": vincoliJazz, "pop": vincoliPop, "blues": vincoliBlues}
    parametriPerStile = {"rock": parametriRock, "jazz": parametriJazz, "pop": parametriPop, "blues": parametriBlues}

    #inizializzazione
    optimizer = Optimize()
    strumenti = {
        'cassa':   [Bool(f'cassa_{t}') for t in range(16)],
        'rullante': [Bool(f'rullante_{t}') for t in range(16)],
        'hihat':    [Bool(f'hihat_{t}') for t in range(16)],
        'crash':    [Bool(f'crash_{t}') for t in range(16)],
        'openhihat':  [Bool(f'openhihat_{t}') for t in range(16)], # NUOVO: Hi-Hat Aperto
        'tom1':     [Bool(f'tom1_{t}') for t in range(16)],
        'tom2':     [Bool(f'tom2_{t}') for t in range(16)]
    }
    
    simboli = {
        'crash': 'C',
        'hihat': 'H',
        'rullante': 'S',
        'cassa': 'K',
        'openhihat': 'O',
        'tom1': 'T1',
        'tom2': 'T2'
    }
    
    hihat, rullante, cassa, crash = strumenti['hihat'], strumenti['rullante'], strumenti['cassa'], strumenti['crash']
    #Input utente stile
    stiliDisponibili = list(vincoliStile.keys())
    print(f"Stili disponibili: {stiliDisponibili}")
    stileScelto = input("Inserisci lo stile desiderato: ").lower()
    if stileScelto not in stiliDisponibili:
        print(f"Stile '{stileScelto}' non valido. Utilizzo stile 'rock' predefinito.")
        stileScelto = "rock"

    #Richiesta parametri
    funzioneParametri = parametriPerStile.get(stileScelto)
    parametriUtente = funzioneParametri() if funzioneParametri else ParametriStile()

    #Applicazione vincoli

    #Vincoli generici
    print(f"\nApplicando vincoli generici:")
    for t in range(16):
        optimizer.add(Implies(strumenti['crash'][t], Not(strumenti['hihat'][t]))) #Se suono il crash, non suono l'hihat
        

    funzioneVincoli = vincoliStile.get(stileScelto)
    if funzioneVincoli:
        print(f"\nApplicando vincoli e preferenze per lo stile: {stileScelto}")
        funzioneVincoli(optimizer, strumenti, parametriUtente)
    else:
        print(f"Errore: Funzione di vincoli non trovata per lo stile '{stileScelto}'.")
        exit()

    #sat e Visualizzazione
    print("Cercando la soluzione ottimale")
    if optimizer.check() == sat:
        model = optimizer.model()

        print(f"\nRitmo generato per stile: {stileScelto} (una soluzione valida):")
        print()
        for t in range(16):    
            k = 'K ' if is_true(model.evaluate(cassa[t])) else '_ '
            s = 'S ' if is_true(model.evaluate(rullante[t])) else '_ '
            if is_true(model.evaluate(crash[t])):
                h = 'C '
            elif is_true(model.evaluate(hihat[t])):
                h = 'H '
            else:
                h = '_ '

            print(f"{h}{k}{s}", end="  ")
            if (t + 1) % 4 == 0:
                print("| ", end="")
        print()
        print("1       i       e       a       | 2       i       e       a       | 3       i       e       a       | 4       i       e       a       |") 

    else:
        print(f"Nessuna soluzione trovata per {stileScelto}.")