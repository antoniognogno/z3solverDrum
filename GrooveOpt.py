import random
from z3 import *
from z3 import Optimize

# =======================================================
#               0. CLASSE PER I PARAMETRI (CORRETTA)
# =======================================================
class ParametriStile:
    def __init__(self):
        # Valori predefiniti (da 0 a 100) - Nomi resi coerenti (camelCase)
        self.forzaDownbeat = 95
        self.forzaBackbeat = 98
        self.forzaSwing = 90
        self.densitaComping = 15 # Corretto da densita_comping
        self.densitaSincopi = 25
        self.preferenzaSilenzio = 20

# =======================================================
#               1. FUNZIONI DI SUPPORTO
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

# =======================================================
#               2. FUNZIONI PER CHIEDERE I PARAMETRI
# =======================================================
def parametriRock():
    print("\nPersonalizza i Pesi per lo Stile ROCK")
    params = ParametriStile()
    params.forzaDownbeat = valoreInput("Forza Cassa su 1 & 3", params.forzaDownbeat)
    params.forzaBackbeat = valoreInput("Forza Rullante su 2 & 4", params.forzaBackbeat)
    params.densitaSincopi = valoreInput("Presenza di sincopi di cassa", params.densitaSincopi)
    params.preferenzaSilenzio = valoreInput("Tendenza al silenzio", params.preferenzaSilenzio)
    return params

def parametriJazz():
    print("\nPersonalizza i Pesi per lo Stile JAZZ")
    params = ParametriStile()
    params.forzaSwing = valoreInput("Definizione del Ride Swing", params.forzaSwing)
    params.densitaComping = valoreInput("Densità note extra (Comping)", params.densitaComping)
    params.preferenzaSilenzio = valoreInput("Tendenza al silenzio", 5)
    return params

def parametriPop():
    print("\nPersonalizza i Pesi per lo Stile POP")
    params = ParametriStile()
    params.forzaDownbeat = valoreInput("Forza Cassa sui quarti", params.forzaDownbeat)
    params.densitaSincopi = valoreInput("Presenza di sincopi", params.densitaSincopi)
    return params

def parametriBlues():
    print("\nPersonalizza i Pesi per lo Stile BLUES")
    params = ParametriStile()
    params.forzaSwing = valoreInput("Definizione dello Shuffle", params.forzaSwing)
    params.forzaBackbeat = valoreInput("Forza Rullante su 2 & 4", params.forzaBackbeat)
    params.densitaSincopi = valoreInput("Presenza di sincopi (pickup)", params.densitaSincopi)
    return params

# =======================================================
#               3. DEFINIZIONI DEGLI STILI (CORRETTE)
# =======================================================

def vincoliRock(optimizer, cassa, rullante, hihat, params):
    # Vincoli Rigidi
    for t in [0, 2, 4, 6, 8, 10, 12, 14]:
        optimizer.add(hihat[t] == True)
    # Vincoli Morbidi
    for t in [0, 8]:
        aggiungiPreferenza(optimizer, cassa[t] == True, peso=params.forzaDownbeat)
    for t in [4, 12]:
        aggiungiPreferenza(optimizer, rullante[t] == True, peso=params.forzaBackbeat)
    # Sincopi per variazioni
    aggiungiPreferenza(optimizer, cassa[6] == True, peso=params.densitaSincopi)
    aggiungiPreferenza(optimizer, cassa[14] == True, peso=int(params.densitaSincopi * 0.8))
    # Preferenza per il silenzio
    for t in range(16):
        if t not in [0, 6, 8, 14]:
            aggiungiPreferenza(optimizer, cassa[t] == False, peso=params.preferenzaSilenzio)
        if t not in [4, 12]:
            aggiungiPreferenza(optimizer, rullante[t] == False, peso=params.preferenzaSilenzio)

def vincoliJazz(optimizer, cassa, rullante, hihat, params):
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

def vincoliPop(optimizer, cassa, rullante, hihat, params):
    for t in [0, 2, 4, 6, 8, 10, 12, 14]:
        optimizer.add(hihat[t] == True)
    optimizer.add(rullante[4] == True)
    optimizer.add(rullante[12] == True)
    for t in [0, 4, 8, 12]:
        aggiungiPreferenza(optimizer, cassa[t] == True, peso=params.forzaDownbeat)
    for t in [3, 7, 11, 15]:
        aggiungiPreferenza(optimizer, cassa[t] == True, peso=params.densitaSincopi)

def vincoliBlues(optimizer, cassa, rullante, hihat, params):
    for t in [0, 4, 8, 12]:
        aggiungiPreferenza(optimizer, hihat[t] == True, peso=params.forzaSwing)
        aggiungiPreferenza(optimizer, hihat[t + 2] == True, peso=params.forzaSwing)
        aggiungiPreferenza(optimizer, hihat[t + 1] == False, peso=int(params.forzaSwing * 0.8))
    aggiungiPreferenza(optimizer, cassa[0] == True, peso=params.forzaDownbeat)
    aggiungiPreferenza(optimizer, cassa[8] == True, peso=params.forzaDownbeat)
    aggiungiPreferenza(optimizer, rullante[4] == True, peso=params.forzaBackbeat)
    aggiungiPreferenza(optimizer, rullante[12] == True, peso=params.forzaBackbeat)
    aggiungiPreferenza(optimizer, cassa[15] == True, peso=params.densitaSincopi)

# =======================================================
#               4. BLOCCO PRINCIPALE (CORRETTO)
# =======================================================

vincoliStile = {"rock": vincoliRock, "jazz": vincoliJazz, "pop": vincoliPop, "blues": vincoliBlues}
parametriPerStile = {"rock": parametriRock, "jazz": parametriJazz, "pop": parametriPop, "blues": parametriBlues}

# 1. Inizializzazione
optimizer = Optimize()
cassa = [Bool(f'cassa_{t}') for t in range(16)]
rullante = [Bool(f'rullante_{t}') for t in range(16)]
hihat = [Bool(f'hihat_{t}') for t in range(16)]

# 2. Scelta Stile
stiliDisponibili = list(vincoliStile.keys())
print(f"Stili disponibili: {stiliDisponibili}")
stileScelto = input("Inserisci lo stile desiderato: ").lower()
if stileScelto not in stiliDisponibili:
    print(f"Stile '{stileScelto}' non valido. Utilizzo stile 'rock' predefinito.")
    stileScelto = "rock"

# 3. Richiesta Parametri
funzioneParametri = parametriPerStile.get(stileScelto)
parametriUtente = funzioneParametri() if funzioneParametri else ParametriStile()

# 4. Applicazione Vincoli
funzioneVincoli = vincoliStile.get(stileScelto)
if funzioneVincoli:
    print(f"\nApplicando vincoli e preferenze per lo stile: {stileScelto}")
    funzioneVincoli(optimizer, cassa, rullante, hihat, parametriUtente)
else:
    print(f"Errore: Funzione di vincoli non trovata per lo stile '{stileScelto}'.")
    exit()

# 4. Risoluzione e Visualizzazione
print("Cercando la soluzione ottimale")
if optimizer.check() == sat:
    model = optimizer.model()

    print(f"\nRitmo generato per stile: {stileScelto} (una soluzione valida):")
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
    print(f"Nessuna soluzione trovata per {stileScelto}.")