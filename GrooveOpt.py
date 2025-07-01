import random
from z3 import *
from z3 import Optimize

from colorama import init, Fore, Style

# Inizializza colorama per funzionare anche su Windows
init(autoreset=True)

class ParametriStile:
    def __init__(self):
        #Rock
        self.forzaDoppiaCassa = 95
        self.forzaDoppiaCassaFinale = 98
        self.densitaSincopi = 25
        self.preferenzaSilenzio = 20
        self.forzaCrash = 1  # Forza del crash iniziale o finale
        #Pop
        self.densitaSincopiCassa = 20
        self.densitaSincopiRullante = 20
        self.forzaOpenHiHat = 98
        #Jazz
        self.densitaComping = 50
        self.forzaSwing = 90
        self.densitaToms = 20

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
    params.patternHiHat = valoreInputBooleano("Pattern Hi-Hat: (o)ttavi o (s)edicesimi?", 'o')
    params.densitaSincopiCassa = valoreInput("Presenza di sincopi della cassa", params.densitaSincopiCassa)
    params.densitaSincopiRullante = valoreInput("Presenza di sincopi sul rullante", params.densitaSincopiRullante)
    params.forzaOpenHiHat = valoreInput("Forza Open Hi-Hat di anticipo (su '4a')", params.forzaOpenHiHat)
    params.forzaCrash = valoreInput("Forza Crash sul primo quarto (t=0) (>90 se vuoi inserirlo)", params.forzaCrash)
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


#Bugs: il crash e l'OpenHIhat non sono gestiti correttamente e suonano sempre
def vincoliPop(optimizer, strumenti, params):

    cassa = strumenti['cassa']
    rullante = strumenti['rullante']
    hihat = strumenti['hihat']
    openhihat = strumenti['openhihat']
    crash = strumenti['crash']


    # 1. Cassa in quarti.
    for t in [0, 4, 8, 12]:
        optimizer.add(cassa[t] == True)
        
    # 2. Rullante su 2 e 4.
    for t in [4, 12]:
        optimizer.add(rullante[t] == True)

    # 3. Definiamo la posizione dell'open hi-hat per chiarezza
    posOpenHiHat = 14
    posCrash = 0

    if params.patternHiHat == 's':
        print("Pattern Hi-Hat impostato a 16esimi.")
        for t in range(16):
            if t != posOpenHiHat and t != posCrash and t != (posOpenHiHat+1): # Escludo il 14 e 15 (posizione dell'open hi-hat)
                optimizer.add(hihat[t] == True)
    else: # Default a ottavi
        print("Pattern Hi-Hat impostato a Ottavi.")
        for t in [2, 4, 6, 8, 10, 12]: # Escludo il 14!
            optimizer.add(hihat[t] == True)


    #Preferenze e vincoli per l'Open Hi-Hat
    aggiungiPreferenza(optimizer, openhihat[posOpenHiHat] == True, peso=params.forzaOpenHiHat)
    
    optimizer.add(Implies(openhihat[posOpenHiHat] == True, And(Not(hihat[posOpenHiHat]), Not(hihat[posOpenHiHat + 1])))) # Se suono l'open hi-hat, non suono l'hihat chiuso (neanche sul successivo)
    optimizer.add(Implies(Not(openhihat[posOpenHiHat]), hihat[posOpenHiHat] == True)) # Se non suono l'open hi-hat, suono l'hihat chiuso

    # 7. Preferenza per il Crash 
    aggiungiPreferenza(optimizer, crash[posCrash] == True, peso=params.forzaCrash)
    optimizer.add(Implies(crash[posCrash], Not(hihat[posCrash])))
    optimizer.add(Implies(Not(crash[posCrash]), hihat[posCrash] == True))
    
    # 8. Sincopi di cassa per rendere il ritmo più movimentato
    for t in [7, 15]: # '2a' e '4a'
        aggiungiPreferenza(optimizer, cassa[t] == True, peso=params.densitaSincopiCassa)
        aggiungiPreferenza(optimizer, rullante[t] == True, peso=params.densitaSincopiRullante)
        optimizer.add(Or(Not(cassa[t]), Not(rullante[t])))

    for t in range(16):
        if t in [posOpenHiHat, posCrash]:
            optimizer.add(Or((Implies(Not(openhihat[t]), hihat[t] == True), Implies(Not(crash[t]), hihat[t] == True)))) # Se non suono l'open hi-hat o il crash, suono l'hihat chiuso

def vincoliJazz(optimizer, strumenti, params):
    cassa = strumenti['cassa']
    rullante = strumenti['rullante']
    hihat = strumenti['hihat']
    openhihat = strumenti['openhihat']
    crash = strumenti['crash']
    ride = strumenti['ride']
    tom1 = strumenti['tom1']
    tom2 = strumenti['tom2']    

    for t in range(16):
        # Il ride e l'hi-hat (suonato con la bacchetta) sono mutualmente esclusivi.
        optimizer.add(AtMost(ride[t], hihat[t], 1))
        # Un crash esclude gli altri piatti.
        optimizer.add(Implies(crash[t], And(Not(ride[t]), Not(hihat[t]), Not(openhihat[t]))))
        


    #hi hat per scandire il tempo
    for t in [4, 12]:
        optimizer.add(hihat[t] == True) # Chick secco sul 2 e 4
        
        # In questi punti, la cassa e il rullante e i toms non devono suonare.
        optimizer.add(cassa[t] == False)
        optimizer.add(rullante[t] == False)
        optimizer.add(strumenti['tom1'][t] == False)
        optimizer.add(strumenti['tom2'][t] == False)
    
    for t in range(15): # Fino al penultimo tempo
        # È fortemente preferibile che cassa[t] e cassa[t+1] non siano entrambi True
        aggiungiPreferenza(optimizer, Not(And(cassa[t], cassa[t+1])), peso=90)
    
        #Ghost notes per il rullante
        if t in [0, 8]:
            aggiungiPreferenza(optimizer, Implies(ride[t], rullante[t+1]), peso=30)

    for t in [0, 8]:
        aggiungiPreferenza(optimizer, ride[t] == True, peso=params.forzaSwing)
        aggiungiPreferenza(optimizer, ride[t + 2] == True, peso=params.forzaSwing)
        aggiungiPreferenza(optimizer, ride[t + 1] == False, peso=params.forzaSwing)

    # 1. Vincolo di cardinalità per i tamburi: al massimo 2 alla volta
    for t in range(16):
        optimizer.add(AtMost(rullante[t], tom1[t], tom2[t], 2))

    # 2. Logica del Comping Sparso
    probabilitaCompingCassa = params.densitaComping / 100.0
    probabilitaCompingRullante = (params.densitaComping * 0.7) / 100.0
    # La densità dei tom è derivata da quella generale
    probabilitaCompingTom1 = (params.densitaComping * 0.5) / 100.0
    probabilitaCompingTom2 = (params.densitaComping * 0.4) / 100.0

    for t in range(16):
        if t not in [4, 12]: # Evitiamo il comping dove c'è l'open-hat fisso
            # Cassa
            if random.random() < probabilitaCompingCassa:
                aggiungiPreferenza(optimizer, cassa[t] == True, peso=50)
            # Rullante
            if random.random() < probabilitaCompingRullante:
                aggiungiPreferenza(optimizer, rullante[t] == True, peso=45)
            # Tom 1
            if random.random() < probabilitaCompingTom1:
                aggiungiPreferenza(optimizer, tom1[t] == True, peso=40)
            # Tom 2
            if random.random() < probabilitaCompingTom2:
                aggiungiPreferenza(optimizer, tom2[t] == True, peso=40)

    # 4. Preferenza Generale per il Silenzio
    for t in range(16):
        aggiungiPreferenza(optimizer, cassa[t] == False, peso=params.preferenzaSilenzio)
        aggiungiPreferenza(optimizer, rullante[t] == False, peso=params.preferenzaSilenzio)
        aggiungiPreferenza(optimizer, tom1[t] == False, peso=params.preferenzaSilenzio)
        aggiungiPreferenza(optimizer, tom2[t] == False, peso=params.preferenzaSilenzio)

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
        'openhihat':  [Bool(f'openhihat_{t}') for t in range(16)],
        'tom1':     [Bool(f'tom1_{t}') for t in range(16)],
        'tom2':     [Bool(f'tom2_{t}') for t in range(16)],
        'ride':    [Bool(f'ride_{t}') for t in range(16)] 
    }
    
    simboli = {
        'crash': 'C',
        'hihat': 'H',
        'rullante': 'S',
        'cassa': 'K',
        'openhihat': 'O',
        'tom1': 'T1',
        'tom2': 'T2',
        'ride': 'R'
    }
    
    colori = {
        'cassa':   Fore.RED + Style.BRIGHT,    # Rosso brillante
        'rullante': Fore.YELLOW + Style.BRIGHT, # Giallo brillante
        'hihat':    Fore.CYAN,                  # Ciano
        'openhat':  Fore.CYAN + Style.BRIGHT,   # Ciano brillante
        'crash':    Fore.MAGENTA + Style.BRIGHT,# Magenta brillante
        'tom1':     Fore.GREEN,                 # Verde
        'tom2':     Fore.GREEN + Style.BRIGHT,   # Verde brillante
        'ride':     Fore.BLUE + Style.BRIGHT      # Blu brillante
    }

    hihat, rullante, cassa, crash = strumenti['hihat'], strumenti['rullante'], strumenti['cassa'], strumenti['crash']
    #Input utente stile
    stiliDisponibili = list(vincoliStile.keys())
    print(f"Stili disponibili: {stiliDisponibili}")
    stileScelto = input("Inserisci lo stile desiderato: ").lower()
    if stileScelto not in stiliDisponibili:
        print(f"Stile '{stileScelto}' non valido. Utilizzo stile 'pop' predefinito.")
        stileScelto = "jazz"

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
        print(f"\nRitmo generato per stile: {stileScelto} (soluzione ottimale):")
        print("-" * 55)
        
        # Dizionario dei simboli per ogni strumento
        simboli = {
            'crash': 'C', 'openhihat':  'O', 'hihat': 'H', 
            'rullante': 'S', 'tom1': '1', 'tom2': '2', 'cassa': 'K', 'ride': 'R'
        }
        
        # Lista degli strumenti nell'ordine in cui vuoi stamparli
        ordine_stampa = ['crash', 'ride', 'openhihat', 'hihat', 'rullante', 'cassa', 'tom1', 'tom2']
        
        # Itera su ogni strumento e stampa la sua riga
        for nome_strumento in ordine_stampa:
            # Fissa la lunghezza del nome per un allineamento perfetto
            etichetta = f"{nome_strumento.capitalize():<9}: "
            riga = etichetta
            
            colore_strumento = colori.get(nome_strumento, Fore.WHITE)

            for t in range(16):
                simbolo_da_stampare = simboli[nome_strumento]
                
                if is_true(model.evaluate(strumenti[nome_strumento][t])):
                # Applica il colore prima del simbolo
                    riga += f"{colore_strumento}{simbolo_da_stampare}   "
                else:

                    # Il punto rimane del colore di default grazie a autoreset=True
                    riga += f'{Fore.WHITE}_   '
                
                # Aggiungi il separatore di battuta
                if (t + 1) % 4 == 0 and t < 15:
                    riga += f"{Fore.WHITE}|   "
            print(riga)
            print(end="\n") 
            
        # Stampa la guida ritmica
        print("-" * 100)
        print("Tempo:     1   e   &   a   |   2   e   &   a   |   3   e   &   a   |   4   e   &   a")
        print("-" * 100)

    else:
        print(f"Nessuna soluzione trovata per {stileScelto}.")
        
    # if optimizer.check() == sat:
    #     model = optimizer.model()

    #     print(f"\nRitmo generato per stile: {stileScelto} (una soluzione valida):")
    #     print()
    #     for t in range(16):    
    #         k = 'K ' if is_true(model.evaluate(cassa[t])) else '_ '
    #         s = 'S ' if is_true(model.evaluate(rullante[t])) else '_ '
    #         if is_true(model.evaluate(crash[t])):
    #             h = 'C '
    #         elif is_true(model.evaluate(hihat[t])):
    #             h = 'H '
    #         else:
    #             h = '_ '

    #         print(f"{h}{k}{s}", end="  ")
    #         if (t + 1) % 4 == 0:
    #             print("| ", end="")
    #     print()
    #     print("1       i       e       a       | 2       i       e       a       | 3       i       e       a       | 4       i       e       a       |") 

    # else:
    #     print(f"Nessuna soluzione trovata per {stileScelto}.")