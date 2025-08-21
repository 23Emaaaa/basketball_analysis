# Analisi Tattica di Partite di Basket Tramite Computer Vision

## Panoramica

Questo progetto utilizza la computer vision e il deep learning per analizzare video di partite di basket, estraendo automaticamente dati e insight tattici. Il sistema è in grado di rilevare e tracciare giocatori e palla, assegnare i giocatori alle rispettive squadre, mappare i loro movimenti su una vista tattica 2D e identificare eventi di gioco chiave come passaggi, intercettazioni e tiri.

L'obiettivo è fornire uno strumento potente per allenatori, analisti e appassionati per studiare le performance dei giocatori e le strategie di squadra in modo oggettivo e data-driven.

---

## Funzionalità Principali

- **Rilevamento e Tracciamento Giocatori**: Identifica ogni giocatore sul campo, gli assegna un ID univoco e ne traccia i movimenti per tutta la durata del video.
- **Rilevamento e Tracciamento Palla**: Localizza e segue la palla, gestendo anche situazioni di alta velocità e occlusioni.
- **Assegnazione Automatica delle Squadre**: Analizza il colore delle maglie per dividere i giocatori nelle due squadre avversarie.
- **Mappatura del Campo e Vista Tattica**: Riconosce i punti chiave del campo da basket per calcolare una matrice di omografia. Questa permette di proiettare le posizioni dei giocatori da una vista 2D del video a una mappa tattica 2D standard.
- **Analisi del Possesso Palla**: Determina quale giocatore ha il controllo della palla in ogni istante.
- **Rilevamento di Passaggi e Intercettazioni**: Identifica con successo i passaggi tra compagni di squadra e le palle rubate dagli avversari.
- **Calcolo di Velocità e Distanze**: Misura la distanza percorsa e la velocità istantanea di ogni giocatore.
- **Rilevamento e Classificazione Tiri**: Isola i momenti in cui un giocatore effettua un tiro e classifica il tentativo.
- **Visualizzazione Dati**: Sovrappone tutte le informazioni estratte direttamente sul video di output, includendo bounding box, tracce, ID giocatore, statistiche e una mini-mappa tattica.

---

## Come Funziona

Il sistema processa il video frame per frame attraverso una pipeline di analisi modulare:

1.  **Caricamento**: Il video di input viene letto da `main.py`.
2.  **Rilevamento**: Per ogni frame, i modelli di deep learning (YOLO) vengono usati per rilevare le posizioni di giocatori e palla.
3.  **Tracciamento**: I `Tracker` (basati su filtri di Kalman) associano le rilevazioni correnti a quelle dei frame precedenti per mantenere un tracciamento coerente.
4.  **Mappatura Campo**: Il `CourtKeypointDetector` identifica i punti di riferimento del campo per calcolare la trasformazione omografica.
5.  **Assegnazione Squadre**: Il `TeamAssigner` analizza i colori delle maglie e assegna ogni giocatore a una squadra.
6.  **Analisi di Gioco**: Moduli di logica superiore analizzano i dati di tracciamento per determinare il possesso palla, rilevare passaggi, intercettazioni e tiri.
7.  **Calcolo Metriche**: Vengono calcolate velocità e distanze per ogni giocatore.
8.  **Visualizzazione**: I moduli `Drawers` disegnano sul frame tutte le informazioni elaborate (box, tracce, vista tattica, etc.).
9.  **Output**: Il frame finale arricchito di dati viene salvato nella cartella `output_videos/`.

---

## Dettagli Tecnici e Strategie Implementative

Questa sezione approfondisce le tecniche utilizzate nei moduli chiave del progetto.

### Rilevamento Oggetti (Giocatori e Palla)
- **Tecnologia**: Il rilevamento si basa su modelli **YOLO (You Only Look Once)**, forniti dalla libreria `ultralytics`.
- **Modelli**: Vengono utilizzati modelli pre-addestrati su dataset specifici per il basket (contenuti in `roboflow_dataset/` e `basketball-player-detection.../`) per garantire un'alta accuratezza nell'identificare giocatori e la palla in contesti di gioco affollati.

### Tracciamento (Tracking-by-Detection)
- **Strategia**: Il sistema adotta un approccio "Tracking-by-Detection". Invece di seguire i pixel, rileva oggetti in ogni frame e poi li collega nel tempo.
- **Filtro di Kalman**: Per ogni oggetto tracciato, viene istanziato un **Filtro di Kalman** (`utils/kalman_filter.py`). Questo filtro predice la posizione dell'oggetto nel frame successivo basandosi sulla sua cronologia di movimento.
- **Associazione**: Quando vengono rilevati nuovi oggetti, il sistema li associa alle tracce esistenti calcolando la metrica di **Intersection over Union (IoU)** tra le bounding box rilevate e quelle predette dal filtro di Kalman. Un'associazione riuscita aggiorna il filtro con la nuova posizione, mentre una mancata associazione può indicare un'occlusione o un oggetto che esce dalla scena.

### Assegnazione Squadre
- **Strategia**: L'assegnazione si basa sull'analisi del colore dominante delle maglie.
- **Processo**:
    1.  Per ogni giocatore, viene isolata una porzione centrale del suo bounding box (l'area del torso).
    2.  Viene applicato un algoritmo di clustering **K-Means** ai pixel di quest'area per trovare il colore dominante.
    3.  Una volta ottenuti i colori dominanti di tutti i giocatori, un secondo K-Means (con K=2) raggruppa questi colori nei due cluster principali, che rappresentano le due squadre.

### Omografia e Vista Tattica
- **Strategia**: La conversione delle coordinate dalla vista della telecamera a una vista 2D dall'alto (top-down) è realizzata tramite una **trasformazione omografica**.
- **Processo**:
    1.  Il `CourtKeypointDetector` rileva punti noti e fissi del campo (es. angoli dell'area dei tre secondi, centro campo).
    2.  Queste coordinate in pixel vengono messe in corrispondenza con le loro coordinate "reali" su un diagramma standard del campo da basket.
    3.  La funzione `cv2.findHomography` di OpenCV calcola la matrice di trasformazione (3x3) che mappa i punti tra i due piani.
    4.  Questa matrice viene poi usata per convertire la posizione di qualsiasi giocatore dal frame del video alla mappa tattica.

### Rilevamento Eventi (Passaggi e Tiri)
- **Logica a Stati**: Il rilevamento di eventi si basa sulla gestione dello stato del gioco.
- **Possesso Palla**: Il sistema determina il possesso assegnando la palla al giocatore più vicino, a condizione che la distanza sia inferiore a una certa soglia.
- **Passaggio**: Un evento "passaggio" viene registrato quando lo stato di possesso cambia da `Giocatore A` a `Giocatore B`, dove A e B appartengono alla stessa squadra. Se B è un avversario, l'evento è classificato come **intercettazione**.
- **Tiro**: Un "tiro" è identificato da una sequenza di segnali cinematici: un'improvvisa accelerazione verticale della palla, il superamento di un'altezza relativa alla testa del giocatore e la successiva perdita di possesso.

---

## Struttura del Progetto

Il codice è organizzato in moduli con responsabilità specifiche:

```
.
├── main.py                           # Entry point principale dell'applicazione
├── requirements.txt                  # Dipendenze Python
├── Dockerfile                        # Per la containerizzazione
├── configs/                          # File di configurazione centralizzati
├── input_videos/                     # Video da analizzare
├── output_videos/                    # Video analizzati
├── models/                           # Pesi dei modelli pre-addestrati (.pt)
├── training_notebooks/               # Notebooks per il training dei modelli
├── basketball-player-detection.../   # Dataset per il training
├── trackers/                         # Logica per il tracciamento di giocatori e palla
├── team_assigner/                    # Logica per l'assegnazione delle squadre
├── court_keypoint_detector/          # Rilevamento punti chiave del campo
├── tactical_view_converter/          # Calcolo omografia e vista tattica
├── pass_and_interception_detector/   # Rilevamento passaggi e intercettazioni
├── shot_detector/                    # Rilevamento tentativi di tiro
├── speed_and_distance_calculator/    # Calcolo velocità e distanze
├── drawers/                          # Moduli per la visualizzazione dei dati sul video
└── utils/                            # Funzioni di utilità (es. filtro di Kalman)
```

---

## Installazione

1.  **Clonare il repository:**
    ```bash
    git clone <URL_DEL_REPOSITORY>
    cd basketball_analysis
    ```

2.  **Creare un ambiente virtuale (consigliato):**
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # Su Windows: .venv\Scripts\activate
    ```

3.  **Installare le dipendenze:**
    ```bash
    pip install -r requirements.txt
    ```

---

## Utilizzo

1.  Assicurarsi che i percorsi dei video di input e dei modelli siano configurati correttamente nel file `configs/configs.py`.
2.  Eseguire lo script principale:
    ```bash
    python main.py
    ```
3.  Il video processato verrà salvato nella cartella `output_videos/`.

---

## Possibili Miglioramenti Futuri

Il progetto ha una solida base che può essere ulteriormente estesa. Le seguenti evoluzioni aumenterebbero notevolmente le capacità analitiche del sistema.

### 1. Rilevamento e Analisi del Tiro (Shot Detection & Analysis)

**Obiettivo**: Insegnare al sistema a riconoscere la "cinematica" di un tiro per identificarne automaticamente il tentativo, l'esito (canestro/errore) e la tipologia (da 2 o 3 punti).

- **Implementazione**:
    1.  **Definire la Zona del Canestro**: Mappare le coordinate 3D del canestro sull'immagine 2D tramite l'omografia.
    2.  **Identificare il "Trigger" del Tiro**: Riconoscere l'istante del tiro analizzando il movimento della palla (che supera la testa del giocatore) e la perdita di possesso.
    3.  **Tracciare la Traiettoria**: Seguire la traiettoria parabolica della palla dopo il trigger per determinare se interseca la zona del canestro (canestro) o la manca (errore).
    4.  **Classificare il Tipo di Tiro**: Usare la posizione del giocatore al momento del tiro per determinare se è stato effettuato da dentro o fuori l'arco da 3 punti.

### 2. Rilevamento di Tattiche di Squadra (Es: Pick-and-Roll)

**Obiettivo**: Identificare sequenze di movimenti complesse tra due o più compagni di squadra, come il pick-and-roll.

- **Implementazione**:
    1.  **Identificare il Blocco (Pick)**: Rilevare quando un giocatore (bloccante) si avvicina a un compagno in possesso palla (palleggiatore) e diventa quasi stazionario.
    2.  **Rilevare l'Uso del Blocco**: Verificare che il palleggiatore cambi direzione muovendosi attorno alla posizione del bloccante.
    3.  **Tracciare il Movimento del Bloccante (Roll)**: Verificare che il bloccante, dopo il blocco, si muova decisamente verso il canestro.
    4.  **Confermare l'Evento**: Se i tre passi avvengono in sequenza, registrare un evento "Pick-and-Roll".

### 3. Analisi Avanzata del Palleggio e del Possesso

**Obiettivo**: Estrarre dati più profondi sulla gestione della palla per capire lo stile di gioco e il processo decisionale dei giocatori.

- **Implementazione**:
    1.  **Contare i Palleggi**: Rilevare ogni ciclo di movimento verticale della palla vicino a un giocatore in possesso come un singolo palleggio.
    2.  **Calcolare il Tempo di Possesso Effettivo**: Cronometrare la durata di ogni possesso per ogni giocatore.
    3.  **Creare Metriche Avanzate**: Calcolare statistiche come "palleggi per possesso" o "tempo decisionale medio" per distinguere tra playmaker e finalizzatori.
