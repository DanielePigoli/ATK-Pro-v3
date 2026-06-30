# Piano consolidamento post-RC ATK-Pro v3.0.0

Data snapshot: 2026-06-24

Questo documento raccoglie l'ordine progressivo degli interventi emersi
dall'analisi delle nuove funzioni v3 e dal primo ciclo di riscontri RC.
Non contiene date: serve come guida operativa per procedere a piccoli passi,
con PR separati e verificabili.

## Principi guida

- Correggere prima i comportamenti potenzialmente errati, poi la struttura.
- Evitare interventi ampi quando una correzione piccola riduce gia' il rischio.
- Conservare la prudenza legale sui portali e renderla coerente con il runtime.
- Alleggerire build e uso risorse senza togliere funzionalita' gia' validate.
- Mantenere RC e feedback esterni come strumenti di verifica, non come vincoli
  a rilasciare in fretta.

## Fase 1 - Stabilita' e correttezza

Interventi da completare prima di considerare una release pubblica finale.

Stato operativo 2026-06-30:

- punto 1: chiuso;
- punto 2: chiuso;
- punto 3: chiuso sul perimetro caveau/provider visibili;
- punto 4: presidio continuo, non chiuso in senso definitivo;
- punto 5: chiuso sul perimetro tecnico interno; gli ex casi Gemini restano
  come verifica esterna opzionale tardiva, non come prerequisito di chiusura.

| Ordine | Intervento | Esito atteso |
| ---: | --- | --- |
| 1 | Applicare la policy D/R al portale effettivo rilevato dall'URL di ciascun record, non solo al portale selezionato nel menu. | I record `R` di portali `R_LIMITED` richiedono range esplicito anche se il menu e' rimasto su un altro portale. |
| 2 | Correggere il modulo Traduzione aggiungendo l'import mancante e un test minimo del worker. | Nessun errore tecnico `logging` durante traduzioni con chiavi da cassaforte o rotazione quota. |
| 3 | Riallineare cassaforte chiavi, provider AI mostrati e provider supportati. | Ogni provider visibile all'utente ha alias, riga CSV, lettura chiave e comportamento coerenti. |
| 4 | Mantenere aggiornato il registro dei riscontri tester RC. | Ogni feedback esterno e' tracciato con stato, decisione e collegamento ai PR. |
| 5 | Eseguire smoke mirati sui percorsi piu' sensibili: Antenati, BUB, FICLIT, BDT, BDL, Rovereto, Ricerca Assistita AI, OCR Gemini. | Le correzioni della fase 1 non introducono regressioni sui flussi gia' provati. |

## Fase 2 - Coerenza funzionale

Interventi per rendere il comportamento piu' prevedibile e leggibile.

Stato operativo 2026-06-30:

- punto 6: chiuso come nota di log;
- punto 7: avanzato ma non chiuso del tutto;
- punto 8: aperto;
- punto 9: aperto;
- punto 10: parziale.

| Ordine | Intervento | Esito atteso |
| ---: | --- | --- |
| 6 | Mostrare un messaggio o una nota di log chiara quando ATK-Pro corregge automaticamente il portale in base all'URL. | L'utente capisce perche' un input BUB/BDL/FICLIT funziona anche se il menu indicava un altro portale. |
| 7 | Uniformare l'uso dei provider AI tra Ricerca Assistita, OCR e Traduzione. | Meno divergenze fra moduli e meno punti da aggiornare quando cambia un provider. |
| 8 | Centralizzare modelli predefiniti, base URL e alias provider. | I default AI non sono duplicati in piu' file. |
| 9 | Rendere opzionali i file diagnostici OCR o spostarli in una sottocartella dedicata. | Gli output finali restano puliti; la diagnostica resta disponibile quando serve. |
| 10 | Migliorare i messaggi di errore AI per chiave non valida, quota, modello non disponibile e risposta non conforme. | Il tester o l'utente capisce cosa correggere senza leggere traceback tecnici. |

Ordine di lavoro consigliato da qui:

1. chiudere il punto 7, senza allargare ancora il perimetro funzionale;
2. affrontare il punto 8, che e' il primo vero nodo strutturale ancora aperto;
3. completare i punti 10 e 9, in quest'ordine, prima di entrare nella fase 3;
4. mantenere in parallelo solo eventuali riscontri esterni tardivi sui casi
   Gemini gia' registrati, senza riaprire la fase 1 salvo nuove regressioni.

## Fase 3 - Prestazioni e risorse

Interventi per ridurre peso percepito, consumo di memoria, CPU e I/O.

| Ordine | Intervento | Esito atteso |
| ---: | --- | --- |
| 11 | Introdurre un profilo risorse: Leggero, Bilanciato, Veloce. | Parallelismo e uso risorse diventano controllabili senza cambiare funzioni. |
| 12 | Ridurre il logging DEBUG nelle build pubbliche, mantenendolo attivabile per diagnosi. | Log piu' piccoli, meno I/O e meno rumore per tester e utenti. |
| 13 | Usare browser headless solo come fallback realmente necessario. | Meno avvii Playwright/Selenium e tempi piu' stabili. |
| 14 | Caricare in modo lazy moduli pesanti AI/OCR/browser quando l'utente apre la funzione relativa. | Avvio piu' leggero e memoria iniziale ridotta. |
| 15 | Salvare progressivamente OCR e PDF lunghi. | In caso di errore su lavori grandi, il lavoro gia' completato resta recuperabile. |

## Fase 4 - Architettura portali

Interventi strutturali da fare con prudenza, dopo la stabilizzazione.

| Ordine | Intervento | Esito atteso |
| ---: | --- | --- |
| 16 | Introdurre adapter per portale. | `elaborazione.py` delega le peculiarita' dei portali a componenti dedicati. |
| 17 | Separare resolver manifest, builder sintetici, downloader e normalizzatori IIIF. | `manifest_utils.py` diventa piu' leggibile e meno fragile. |
| 18 | Definire test comuni per ogni portale supportato. | Ogni nuovo portale deve superare una matrice minima offline/live. |
| 19 | Consolidare il re-check periodico delle policy tramite file locale. | Le policy possono essere aggiornate senza attendere una nuova release. |
| 20 | Riprendere lo scouting di nuovi portali italiani/italofoni. | L'espansione riparte su una base piu' stabile. |

## Fase 5 - Packaging e release

Interventi finali prima della v3.0.0 definitiva.

| Ordine | Intervento | Esito atteso |
| ---: | --- | --- |
| 21 | Audit del contenuto delle build Windows portable e installer. | Riduzione del peso dove possibile senza perdere funzioni. |
| 22 | Audit equivalente per macOS e Linux. | Comportamento coerente e note specifiche per piattaforma. |
| 23 | Verifica del percorso aggiornamento RC -> finale. | Chi ha installato una RC riceve correttamente la v3.0.0 stabile. |
| 24 | Preparazione note release definitive. | Limiti, portali, disclaimer, AI e OCR sono descritti in modo chiaro. |
| 25 | Valutare una RC ulteriore se le modifiche post-RC2 sono sostanziali. | La finale non incorpora modifiche rilevanti senza un ultimo riscontro esterno. |

## Criterio operativo

Procedere con PR piccoli e ordinati. Ogni PR deve includere:

- modifica limitata al punto in corso;
- segnalazione del modello Codex consigliato secondo
  `docs_generali/policy_modelli_codex_ATK-Pro.md`;
- test o verifica manuale mirata;
- aggiornamento documentale solo se cambia il comportamento utente;
- nessuna estensione funzionale non necessaria al punto trattato.
