import random
from z3 import *

def aggiungi_vincolo_probabilistico(solver, variabile, probabilita):
    if random.random() < probabilita:
        solver.add(variabile == True)
    else:
        solver.add(variabile == False)

def definisci_vincoli_rock(solver, cassa, rullante, hihat):
    # Hi-hat (sugli ottavi)
    for t in [0, 2, 4, 6, 8, 10, 12, 14]:
        solver.add(hihat[t] == True)

    # Cassa: sui downbeat (1 e 3) - con probabilità per una lieve variazione
    probabilita_cassa = 0.7
    for t in [0, 8]:
        aggiungi_vincolo_probabilistico(solver, cassa[t], probabilita_cassa)

    # Rullante: sui backbeat (2 e 4) - con probabilità
    probabilita_rullante = 0.8
    for t in [4, 12]:
        aggiungi_vincolo_probabilistico(solver, rullante[t], probabilita_rullante)

#Bisogna torvare la giusta xombinazione fra probabilità e vincoli in quanto una combinazione non conforme fra i due rende spesso la soluzione difficile da trovare 
def definisci_vincoli_jazz(solver, cassa, rullante, hihat):
    """Definisce vincoli per uno stile Jazz di base (16esimi)."""
    # Hi-hat - Swingato (primo ___) con probabilità
    probabilita_hihat_forte = 0.8  # Probabilità *più bassa* sui primi ottavi (terzine)
    probabilita_hihat_debole = 0.5 # Probabilità bassa sui secondi ottavi (terzine)
    probabilita_swing = 0.5 # probability that swing will happen
    # Hi-hat:  Swingato
    for t in [0, 4, 8, 12]:  # Primi ottavi (1° ___)
        probGenerata = random.random()
        print(f"La probabilità di suonare l'Hi-Hat forte è di {probGenerata * 100:.2f}% nel tempo t = {t}")
        aggiungi_vincolo_probabilistico(solver, hihat[t], probabilita_hihat_forte)

    for t in [2, 6, 10, 14]:  # Secondi ottavi (2° ___)
        probGenerata = random.random()
        print(f"La probabilità di suonare l'Hi-Hat debole è di {probGenerata * 100:.2f}% nel tempo t = {t}")
        aggiungi_vincolo_probabilistico(solver, hihat[t], probabilita_hihat_debole)
    
    # Swing probabilistico:
    probabilita_swing = 0.2 # Probabilità che ci sia anche il secondo hi-hat
    for t in [0, 4, 8, 12]: #Per ogni primo ottavo
        # Genera una probabilità per decidere se applicare la regola di swing
        probGenerata = random.random()
        print(f"La probabilità di suonare lo swing è di {probGenerata * 100:.2f}% nel tempo t = {t}")
        if random.random() < probabilita_swing:
            print(f"Regola di swing applicata per t={t}: Se hihat[{t}] suona, allora suonano anche hihat[{t+2}] e hihat[{t+3}]")
            solver.add(Implies(hihat[t], And(hihat[t + 2] == True, hihat[t + 3] == True)))
        else:
            print(f"Regola di swing NON applicata per t={t} (per scelta probabilistica di Python)")

    # Cassa - Probabilistico
    probabilita_cassa = 0.6 
    for t in range(16):
        probGenerata = random.random()
        aggiungi_vincolo_probabilistico(solver, cassa[t], probabilita_cassa)

    # Rullante - Probabilistico
    probabilita_rullante = 0.5
    for t in range(16):
        probGenerata = random.random()
        aggiungi_vincolo_probabilistico(solver, rullante[t], probabilita_rullante)

def definisci_vincoli_pop(solver, cassa, rullante, hihat):
    """Definisce vincoli per uno stile Pop di base (16esimi)."""
    # Hi-hat (come nel rock)
    for t in [0, 2, 4, 6, 8, 10, 12, 14]:
        solver.add(hihat[t] == True)

    # Cassa: Spesso su tutti e quattro i battiti (o sincopata)
    probabilita_cassa_forte = 0.7  # Alta probabilità per i downbeat
    for t in [0, 4, 8, 12]:  # Cassa sui 4 quarti (o quasi)
        aggiungi_vincolo_probabilistico(solver, cassa[t], probabilita_cassa_forte)

    # Rullante: Forte sul backbeat
    solver.add(rullante[4])
    solver.add(rullante[12])

def definisci_vincoli_blues(solver, cassa, rullante, hihat):
    """Definisce vincoli per uno stile Blues di base (16esimi)."""
    # Hi-hat (come in rock e pop, anche se nel blues può variare)
    for t in [0, 2, 4, 6, 8, 10, 12, 14]:
        solver.add(hihat[t] == True)

    # Cassa: Sul 1 e 3 - Potrebbe avere un shuffle (sincopato)
    solver.add(cassa[0])  # Cassa sul 1
    solver.add(cassa[8])  # Cassa sul 3
    # Rullante: sul 2 e 4 (backbeat)
    solver.add(rullante[4])
    solver.add(rullante[12])

vincoliStile = {
    "rock": definisci_vincoli_rock,
    "jazz": definisci_vincoli_jazz,
    "pop": definisci_vincoli_pop,
    "blues": definisci_vincoli_blues,
}

# Solver
solver = Solver()

# Variabili per gli strumenti in ogni sedicesimo (0-15)
cassa = [Bool(f'cassa_{t}') for t in range(16)]
rullante = [Bool(f'rullante_{t}') for t in range(16)]
hihat = [Bool(f'hihat_{t}') for t in range(16)]

# Input stile dall'utente
stili_disponibili = list(vincoliStile.keys())
print(f"Stili disponibili: {stili_disponibili}")
stile_scelto = input("Inserisci lo stile desiderato: ").lower()

if stile_scelto not in stili_disponibili:
    print(f"Stile '{stile_scelto}' non valido. Utilizzo stile rock predefinito.")
    stile_scelto = "rock"

# Applica i vincoli in base allo stile scelto
funzione_vincoli = vincoliStile.get(stile_scelto)
if funzione_vincoli:
    print(f"Applicando vincoli per lo stile: {stile_scelto}")
    funzione_vincoli(solver, cassa, rullante, hihat)
else:
    print("Errore: Funzione di vincoli non trovata per lo stile scelto.")


# Risolvi e visualizza
if solver.check() == sat:
    model = solver.model()
    print(f"\nRitmo generato per stile: {stile_scelto} (una soluzione valida):")
    print()
    for t in range(16):
        k = 'K' if model.evaluate(cassa[t]) == BoolVal(True) else '_'
        s = 'S' if model.evaluate(rullante[t]) == BoolVal(True) else '_'
        h = 'H' if model.evaluate(hihat[t]) == BoolVal(True) else '_'
        print(f"{h}{k}{s}", end=" ")
        if (t + 1) % 4 == 0: # 4 sedicesimi per quarto
            print("| ", end="")
    print()

    print("1   i   e   a   | 2   i   e   a   | 3   i   e   a   | 4   i   e   a   |") 
else:
    print(f"Nessuna soluzione trovata per {stile_scelto}.")
