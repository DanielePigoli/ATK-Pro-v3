# Certificazione pratica post-release ATK-Pro v3.0.0

Data snapshot: 2026-09-10

Questo registro separa la validazione tecnica gia' conclusa per la release
stabile dalle prove pratiche svolte dopo la pubblicazione. Le prove usano solo
asset pubblici e URL campione coerenti con la policy dei portali. I risultati
non autorizzano scraping massivo o l'aggiramento di login, paywall e limiti di
riproduzione.

## Stato sintetico

| Area | Stato | Evidenza |
| --- | --- | --- |
| Release pubblicata | PASS | Tag `v3.0.0`, sei asset e digest presenti nella release GitHub. |
| Gate completo da sorgente | PASS | `python scripts\quality_gate.py release`: 11/11 step, 843 test passati e 39 skip attesi. |
| Portali live con immagini reali | PASS | `python verify_portal_live_smoke.py --fetch-images --strict`: 28/28 capability; immagini di inizio, centro e fine decodificabili e distinte nei documenti multipagina. |
| BDL multipagina | PASS | Item `12404`: 12 canvas; pagine 1, 7 e 12 scaricate e decodificate alle dimensioni attese. |
| Artefatti multipiattaforma | PASS in CI | Smoke post-pubblicazione Windows, Linux e macOS completati sui sei asset esatti, come registrato nella checklist release. |
| Uso pratico locale Windows | PASS avvio isolato | Portable stabile riscaricato, SHA-256 verificato, estratto e mantenuto in esecuzione offscreen per 20 secondi; chiusura e pulizia del solo processo di prova riuscite, senza aggiornare ATK-Pro 2.0. |
| Percorsi funzionali utente | PASS download; verifiche applicative residue | BDT PDF diretto, Rovereto DSpace, BDL BookReader/Cantaloupe, IIIF v2 e IIIF v3 con immagine diretta producono output reali. I due difetti emersi il 2026-09-10 sono corretti e controverificati; OCR, traduzione e GEDCOM restano da provare. |

## Esito del controllo live 2026-09-09

Tutte le 28 capability registrate hanno prodotto un manifest valido o un
manifest sintetico valido. Per i documenti multipagina lo smoke ha verificato
tre immagini equidistanti mediante dimensioni, decodifica e hash del contenuto.
Tra i campioni piu' significativi:

- Antenati: 34 canvas;
- BNC Roma: 170 canvas;
- BNCF Teca: 53 canvas;
- Brixiana: 317 canvas;
- Biblioteca Digitale Siena: 106 canvas;
- BUB: 32 canvas;
- FICLIT: 239 canvas;
- Biblioteca Digitale Trentina: 508 canvas;
- Biblioteca Digitale Lombarda: 12 canvas;
- Rovereto Digital Library: 129 canvas;
- DOGE: 373 canvas;
- Findbuch: 221 canvas;
- Matricula: 745 canvas;
- Internet Archive: 1294 canvas;
- Vatican Library: 526 canvas;
- Bodleian: 920 canvas.

Il report CSV locale e' generato in
`.codex_tmp/portal_live_smoke_report.csv` ed e' intenzionalmente ignorato da
Git.

## Smoke locale del portable stabile 2026-09-09

- asset: `ATK-Pro-v3.0.0-Windows-Portable.zip` dalla release stabile;
- dimensione scaricata: circa 0,961 GiB;
- SHA-256 atteso e rilevato:
  `fa96d34a99524b8eb51d75686b7d54d39a108b9e7d983dbd2885f4295022f23f`;
- struttura estratta valida, con `ATK-Pro.exe` e marcatore `portable.txt`;
- avvio isolato con piattaforma Qt offscreen: processo vivo dopo 20 secondi,
  `stderr` vuoto e log ordinario su `stdout`;
- terminato esclusivamente il processo dell'eseguibile estratto; nessun processo
  residuo;
- nessuna installazione di sistema e nessuna modifica all'installazione
  ATK-Pro 2.0 esistente.

Questo smoke prova integrita', estraibilita' e avvio dell'artefatto stabile.
L'interazione grafica reale resta una prova manuale distinta.

## Prove end-to-end da sorgente 2026-09-10

Le prove sono state limitate a campioni pubblici e a range minimi. Gli output
sono stati scritti sotto `.codex_tmp/postrelease-e2e-20260910/`, escluso da
Git.

| Famiglia | Campione | Esito | Evidenza |
| --- | --- | --- | --- |
| BDL BookReader/Cantaloupe | Item `12404`, pagine 1-3, PNG + PDF | PARZIALE | Un HTTP 502 sulla prima pagina e' stato recuperato al secondo passaggio. Il PDF finale contiene tre pagine reali, ma nella cartella resta anche il PNG placeholder iniziale accanto al recupero `_rec2`. |
| PDF REST diretto | BDT `Testi-a-stampa/113` | PASS | PDF da 45.944.018 byte, 510 pagine; apertura e rendering riusciti su pagina 1, 256 e 510. |
| DSpace-GLAM | Rovereto item `e4199e9b-c79b-4c3d-b157-be2dcfc0407f`, pagine 1-2 | PASS | Due PNG reali e PDF di due pagine, senza cartelle temporanee vuote. |
| IIIF v2 | Archivio Storico UniBo `0131.016.003`, pagina 1 | PASS | PNG reale e PDF di una pagina generati e renderizzati. |
| IIIF v3 con immagine diretta | IIIF Cookbook `0001-mvm-image`, pagina 1 | FAIL | Manifest normalizzato correttamente, ma il canvas senza `service` causa tre retry falliti; nessuna immagine o PDF, due directory vuote residue e ritorno errato `True`. |

Il PASS dello smoke live 28/28 non e' contraddetto: quel controllo valida
risoluzione, trasporto e decodifica delle immagini campione, mentre questa prova
attraversa anche salvataggio, retry, cleanup, PDF e valore di ritorno finale.

### Difetti riproducibili rilevati

1. Nel recupero BDL, il salvataggio univoco crea `_rec2` invece di sostituire
   il placeholder con il nome canonico. Il PDF usa la pagina recuperata, ma il
   placeholder rimane visibile all'utente.
2. I manifest IIIF v3 con una risorsa immagine diretta e priva di Image Service
   non sono gestiti dal percorso registro. Se non viene prodotto alcun output,
   `_process_register()` deve inoltre restituire fallimento e rimuovere le
   directory temporanee vuote.

### Correzione verificata 2026-09-10

Entrambi i difetti sono stati corretti e sottoposti a controverifica:

- il secondo passaggio BDL sostituisce ora il placeholder usando il nome
  canonico, senza creare suffissi `_rec*`; la prova forzata copre il retry e la
  prova live sull'item `12404`, pagine 1-3, ha prodotto tre PNG reali da
  2681 x 3987 pixel e un PDF di tre pagine, senza placeholder o directory
  vuote residue;
- i canvas IIIF v3 con corpo immagine diretto e senza Image Service sono gestiti
  dal relativo adapter; il Cookbook `0001-mvm-image` ha prodotto un PNG reale
  da 1200 x 1800 pixel e un PDF di una pagina, senza directory residue;
- se mancano gli output richiesti il percorso registro restituisce ora
  fallimento; gli spazi temporanei completamente vuoti vengono rimossi.

La suite mirata ha concluso con `126 passed`. Il gate release completo ha
concluso con `843 passed, 39 skipped` e tutti gli 11 step superati.

## Sequenza pratica residua

1. Avviare visibilmente il portable dalla copia temporanea gia' verificata e
   controllare consenso legale, lingua, apertura dei documenti e chiusura
   pulita senza interferire con ATK-Pro 2.0 installato.
2. Completare il quinto percorso con un manifest sintetico da HTML. Per ciascun
   output ricontrollare numero di file, pagine, apertura PDF, placeholder e
   cartelle vuote residue.
3. Eseguire un OCR breve, una traduzione breve e un'esportazione GEDCOM con dati
   non sensibili; riaprire i file prodotti e verificarne il contenuto.
4. Provare errori controllati: URL non riconosciuto, pagina inesistente,
   interruzione rete e annullamento. L'app deve conservare gli output validi e
   mostrare un messaggio utile.
5. Registrare qui data, artefatto, campione, risultato e anomalie. Le anomalie
   riproducibili vanno corrette in una release successiva, salvo problema di
   sicurezza o perdita dati che richieda una patch urgente.

## Confini della certificazione

- Il controllo live dimostra che i campioni pubblici funzionano alla data
  indicata; non garantisce l'immutabilita' futura dei portali esterni.
- Gli smoke CI verificano gli asset pubblicati, ma non sostituiscono tutte le
  combinazioni di hardware, antivirus, proxy e configurazione utente.
- SAG e ASTi non fanno parte della `v3.0.0`: sono registrati esclusivamente come
  candidati della prossima release nel documento dedicato.
