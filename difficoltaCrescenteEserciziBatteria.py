from z3 import *

def definisci_vincoli_rock(solver, cassa, rullante, hihat):
    #Definisce vincoli per uno stile Rock di base.
    # Vincoli Rock (esempio semplificato)
    solver.add(And(And(cassa[0], cassa[8]), And(rullante[4], rullante[12])))
    for t in range(0, 16, 2):
        solver.add(hihat[t] == True)
    for t in range(1, 16, 2):
        solver.add(hihat[t] == False)
    

def definisci_vincoli_jazz(solver, cassa, rullante, hihat):
    #Definisce vincoli per uno stile Jazz di base (molto semplificato).
    solver.add(cassa[3]) # Esempio di cassa jazz
    for t in range(0, 16, 2):
        solver.add(hihat[t] == True)
    for t in range(1, 16, 2):
        solver.add(hihat[t] == False)

style_constraints = {
    "rock": definisci_vincoli_rock,
    "jazz": definisci_vincoli_jazz,
}

# Ottimizzatore
optimizer = Optimize()

# Variabili per gli strumenti in ogni sedicesimo (0-15)
cassa = [Bool(f'cassa_{t}') for t in range(16)]
rullante = [Bool(f'rullante_{t}') for t in range(16)]
hihat = [Bool(f'hihat_{t}') for t in range(16)]

# Input stile dall'utente
stili_disponibili = list(style_constraints.keys())
print("Stili disponibili:", ", ".join(stili_disponibili))
stile_scelto = input("Inserisci lo stile desiderato: ").lower()

if stile_scelto not in stili_disponibili:
    print(f"Stile '{stile_scelto}' non valido. Utilizzo stile rock predefinito.")
    stile_scelto = "rock"

# Applica i vincoli in base allo stile scelto
funzione_vincoli = style_constraints.get(stile_scelto)
if funzione_vincoli:
    print(f"Applicando vincoli per lo stile: {stile_scelto}")
    funzione_vincoli(optimizer, cassa, rullante, hihat)
else:
    print("Errore: Funzione di vincoli non trovata per lo stile scelto.")


# Funzione obiettivo (esempio - massimizzare le preferenze rock, potrebbe essere diverso per altri stili)
# ... (la funzione obiettivo potrebbe anche essere dinamica e dipendere dallo stile) ...
preferenza_cassa_1 = If(cassa[0], IntVal(1), IntVal(0))
preferenza_cassa_3 = If(cassa[8], IntVal(1), IntVal(0))
preferenza_rullante_2 = If(rullante[4], IntVal(1), IntVal(0))
preferenza_rullante_4 = If(rullante[12], IntVal(1), IntVal(0))
obiettivo = preferenza_cassa_1 + preferenza_cassa_3 + preferenza_rullante_2 + preferenza_rullante_4
optimizer.maximize(obiettivo)


# Risolvi e visualizza (come prima)
if optimizer.check() == sat:
    model = optimizer.model()
    print(f"\nRitmo generato per stile: {stile_scelto}")
    for t in range(16):
        k = 'K' if model.evaluate(cassa[t]) == BoolVal(True) else '_'
        s = 'S' if model.evaluate(rullante[t]) == BoolVal(True) else '_'
        h = 'H' if model.evaluate(hihat[t]) == BoolVal(True) else '_'
        print(f"{h}{k}{s}", end=" ")
        if (t + 1) % 4 == 0:
            print("| ", end="")
    print()
    print("Preferenze soddisfatte:", model.evaluate(obiettivo))
else:
    print("Nessuna soluzione trovata.")