import random
from z3 import *
from z3 import Optimize


class ParametriStile:
    """
    Una classe contenitore per i pesi.
    Non tutti gli stili useranno tutti i parametri.
    """
    def __init__(self):
        # Valori predefiniti (da 0 a 100)
        self.forza_downbeat = 95
        self.forza_backbeat = 98
        self.forza_swing = 90
        self.densita_comping = 15
        self.densita_sincopi = 25
        self.preferenza_silenzio = 20

# =======================================================
#               1. FUNZIONI DI SUPPORTO
# =======================================================

def aggiungiPreferenza(optimizer, espressione_booleana, peso):
    """
    Aggiunge un vincolo morbido (una preferenza) all'ottimizzatore.
    L'ottimizzatore cercherà di rendere l'espressione vera.
    Più alto è il 'peso', più forte è la preferenza.
    """
    if peso > 0:
        optimizer.add_soft(espressione_booleana, weight=peso)

def valoreInput(messaggio, default):
    """Funzione di supporto per non ripetere il codice di input."""
    val = int(input(f"- {messaggio} (default: {default}): "))
    if val < 0 or val > 100:
        print(f"Valore fuori range. Usando il default: {default}")
    else:
        return val
    return default

# =======================================================
#               2. FUNZIONI PER CHIEDERE I PARAMETRI
# =======================================================

def parametriRock():
    print("\n--- Personalizza i Pesi per lo Stile ROCK ---")
    params = ParametriStile() # Inizia con i default
    params.forza_downbeat = valoreInput("Forza Cassa su 1 & 3", params.forza_downbeat)
    params.forza_backbeat = valoreInput("Forza Rullante su 2 & 4", params.forza_backbeat)
    params.preferenza_silenzio = valoreInput("Tendenza al silenzio", params.preferenza_silenzio)
    return params

def parametriJazz():
    print("\n--- Personalizza i Pesi per lo Stile JAZZ ---")
    params = ParametriStile()
    params.forza_swing = valoreInput("Definizione del Ride Swing", params.forza_swing)
    params.densita_comping = valoreInput("Densità note extra (Comping)", params.densita_comping)
    params.preferenza_silenzio = valoreInput("Tendenza al silenzio", 5) # Default basso per il jazz
    return params

def parametriPop():
    print("\n--- Personalizza i Pesi per lo Stile POP ---")
    params = ParametriStile()
    params.forza_downbeat = valoreInput("Forza Cassa sui quarti", params.forza_downbeat)
    params.densita_sincopi = valoreInput("Presenza di sincopi", params.densita_sincopi)
    return params

def parametriBlues():
    print("\n--- Personalizza i Pesi per lo Stile BLUES ---")
    params = ParametriStile()
    params.forza_swing = valoreInput("Definizione dello Shuffle", params.forza_swing)
    params.forza_backbeat = valoreInput("Forza Rullante su 2 & 4", params.forza_backbeat)
    params.densita_sincopi = valoreInput("Presenza di sincopi (pickup)", params.densita_sincopi)
    return params

# =======================================================
#               2. DEFINIZIONI DEGLI STILI
# =======================================================

def vincoliRock(optimizer, cassa, rullante, hihat):
    """Definisce vincoli e preferenze per uno stile Rock di base."""
    # --- Vincoli Rigidi (DEVONO essere veri) ---
    # Hi-hat sugli ottavi. Questo è il fondamento del ritmo.
    for t in [0, 2, 4, 6, 8, 10, 12, 14]:
        optimizer.add(hihat[t] == True)

    # --- Preferenze ---
    # Cassa: forte preferenza per i downbeat (1 e 3)
    for t in [0, 8]:
        aggiungiPreferenza(optimizer, cassa[t] == True, peso=95)

    # Rullante: forte preferenza per i backbeat (2 e 4)
    for t in [4, 12]:
        aggiungiPreferenza(optimizer, rullante[t] == True, peso=98)

    # Preferenza per il silenzio altrove, per evitare ritmi troppo pieni
    for t in range(16):
        if t not in [0, 8]:
            aggiungiPreferenza(optimizer, cassa[t] == False, peso=20)
        if t not in [4, 12]:
            aggiungiPreferenza(optimizer, rullante[t] == False, peso=20)


def vincoliJazz(optimizer, cassa, rullante, hihat):
    """Definisce vincoli e preferenze per uno stile Jazz di base."""
    # --- Vincoli Rigidi ---
    # Il piatto ride (hi-hat) suona sui beat 2 e 4 con il piede. È una convenzione fortissima.
    optimizer.add(hihat[4] == True)
    optimizer.add(hihat[12] == True)
    # Per chiarezza, il rullante non suona insieme al ride su 2 e 4
    optimizer.add(Implies(hihat[4], Not(rullante[4])))
    optimizer.add(Implies(hihat[12], Not(rullante[12])))

    # --- Preferenze per il pattern SWING sull'Hi-Hat/Ride ---
    # La formula dello swing è "1 & a 2 & a...", che in 16esimi è t, t+2
    for t in [0, 4, 8, 12]:
        # Preferenza per il colpo sul quarto ("ching")
        aggiungiPreferenza(optimizer, hihat[t] == True, peso=80)
        # Preferenza MOLTO FORTE per il colpo swingato ("ka-ching"), che è il cuore del feel
        aggiungiPreferenza(optimizer, hihat[t + 2] == True, peso=95)
        # Preferenza per il silenzio nella seconda suddivisione (il "e"), per creare il tipico "lilt"
        aggiungiPreferenza(optimizer, hihat[t + 1] == False, peso=70)

    # --- Preferenze per il "COMPING" (accompagnamento sparso) ---
    # Incoraggiamo colpi sparsi di cassa e rullante con un peso basso
    for t in range(16):
        if t not in [4, 12]:
            aggiungiPreferenza(optimizer, cassa[t] == True, peso=15)
            aggiungiPreferenza(optimizer, rullante[t] == True, peso=10)

    # Preferenza generale per il silenzio per bilanciare il comping
    for t in range(16):
        aggiungiPreferenza(optimizer, cassa[t] == False, peso=5)
        aggiungiPreferenza(optimizer, rullante[t] == False, peso=8)


def vincoliPop(optimizer, cassa, rullante, hihat):
    """Definisce vincoli e preferenze per uno stile Pop di base."""
    # --- Vincoli Rigidi ---
    for t in [0, 2, 4, 6, 8, 10, 12, 14]:
        optimizer.add(hihat[t] == True)
    optimizer.add(rullante[4] == True)
    optimizer.add(rullante[12] == True)

    # --- Preferenze ---
    # Cassa "Four-on-the-floor" (sui quarti) è una forte preferenza.
    for t in [0, 4, 8, 12]:
        aggiungiPreferenza(optimizer, cassa[t] == True, peso=90)
    # Preferenza per qualche sincope di cassa per rendere il ritmo più interessante
    for t in [3, 7, 11, 15]:
        aggiungiPreferenza(optimizer, cassa[t] == True, peso=25)


def vincoliBlues(optimizer, cassa, rullante, hihat):
    """Definisce vincoli e preferenze per uno stile Blues shuffle."""
    # --- Preferenze per il pattern SHUFFLE sull'Hi-Hat ---
    # Simile allo swing del jazz, un pattern "ternario"
    for t in [0, 4, 8, 12]:
        aggiungiPreferenza(optimizer, hihat[t] == True, peso=90)
        aggiungiPreferenza(optimizer, hihat[t + 2] == True, peso=90)
        aggiungiPreferenza(optimizer, hihat[t + 1] == False, peso=70)

    # --- Preferenze per Cassa e Rullante ---
    aggiungiPreferenza(optimizer, cassa[0] == True, peso=95)
    aggiungiPreferenza(optimizer, cassa[8] == True, peso=95)
    aggiungiPreferenza(optimizer, rullante[4] == True, peso=98)
    aggiungiPreferenza(optimizer, rullante[12] == True, peso=98)
    aggiungiPreferenza(optimizer, cassa[15] == True, peso=40) # Pickup occasionale


# =======================================================
#               3. BLOCCO PRINCIPALE
# =======================================================

# Dizionario che associa i nomi degli stili alle loro funzioni
vincoliStile = {
    "rock": vincoliRock,
    "jazz": vincoliJazz,
    "pop": vincoliPop,
    "blues": vincoliBlues,
}

parametri_per_stile = {
    "rock": parametriRock,
    "jazz": parametriJazz,
    "pop": parametriPop,
    "blues": parametriBlues,
}

# 1. Inizializzazione
optimizer = Optimize()


cassa = [Bool(f'cassa_{t}') for t in range(16)]
rullante = [Bool(f'rullante_{t}') for t in range(16)]
hihat = [Bool(f'hihat_{t}') for t in range(16)]

# 2. Interazione con l'Utente
stili_disponibili = list(vincoliStile.keys())
print(f"Stili disponibili: {stili_disponibili}")
stile_scelto = input("Inserisci lo stile desiderato: ").lower()

if stile_scelto not in stili_disponibili:
    print(f"Stile '{stile_scelto}' non valido. Utilizzo stile 'rock' predefinito.")
    stile_scelto = "rock"

funzione_parametri = parametri_per_stile.get(stile_scelto)
if funzione_parametri:
    parametri_utente = funzione_parametri()
else:
    #Caso in cui uno stile non abbia una funzione di parametri
    parametri_utente = ParametriStile()

# 3. Applicazione dei Vincoli
funzione_vincoli = vincoliStile.get(stile_scelto)
if funzione_vincoli:
    print(f"\nApplicando vincoli e preferenze per lo stile: {stile_scelto}")
    funzione_vincoli(optimizer, cassa, rullante, hihat)
else:
    print(f"Errore: Funzione di vincoli non trovata per lo stile '{stile_scelto}'.")
    exit()

# 4. Risoluzione e Visualizzazione
print("Cercando la soluzione ottimale")
if optimizer.check() == sat:
    model = optimizer.model()

    print(f"\nRitmo generato per stile: {stile_scelto} (una soluzione valida):")
    print()
    for t in range(16):
        
        k = 'K ' if model.evaluate(cassa[t]) == BoolVal(True) else '_ '
        s = 'S ' if model.evaluate(rullante[t]) == BoolVal(True) else '_ '
        h = 'H ' if model.evaluate(hihat[t]) == BoolVal(True) else '_ '

        print(f"{h}{k}{s}", end="  ")
        if (t + 1) % 4 == 0: # 4 sedicesimi per quarto
            print("| ", end="")
    print()
    print("1       i       e       a       | 2       i       e       a       | 3       i       e       a       | 4       i       e       a       |") 

else:
    print(f"Nessuna soluzione trovata per {stile_scelto}.")