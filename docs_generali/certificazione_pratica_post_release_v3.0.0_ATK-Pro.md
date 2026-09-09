# Certificazione pratica post-release ATK-Pro v3.0.0

Data snapshot: 2026-09-09

Questo registro separa la validazione tecnica gia' conclusa per la release
stabile dalle prove pratiche svolte dopo la pubblicazione. Le prove usano solo
asset pubblici e URL campione coerenti con la policy dei portali. I risultati
non autorizzano scraping massivo o l'aggiramento di login, paywall e limiti di
riproduzione.

## Stato sintetico

| Area | Stato | Evidenza |
| --- | --- | --- |
| Release pubblicata | PASS | Tag `v3.0.0`, sei asset e digest presenti nella release GitHub. |
| Gate completo da sorgente | PASS | `python scripts\quality_gate.py release`: 11/11 step, 841 test passati e 39 skip attesi. |
| Portali live con immagini reali | PASS | `python verify_portal_live_smoke.py --fetch-images --strict`: 28/28 capability; immagini di inizio, centro e fine decodificabili e distinte nei documenti multipagina. |
| BDL multipagina | PASS | Item `12404`: 12 canvas; pagine 1, 7 e 12 scaricate e decodificate alle dimensioni attese. |
| Artefatti multipiattaforma | PASS in CI | Smoke post-pubblicazione Windows, Linux e macOS completati sui sei asset esatti, come registrato nella checklist release. |
| Uso pratico locale Windows | PASS avvio isolato | Portable stabile riscaricato, SHA-256 verificato, estratto e mantenuto in esecuzione offscreen per 20 secondi; chiusura e pulizia del solo processo di prova riuscite, senza aggiornare ATK-Pro 2.0. |
| Percorsi funzionali utente | Da completare | Download reale controllato, apertura output, OCR, traduzione ed esportazione GEDCOM su campioni piccoli. |

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

## Sequenza pratica residua

1. Avviare visibilmente il portable dalla copia temporanea gia' verificata e
   controllare consenso legale, lingua, apertura dei documenti e chiusura
   pulita senza interferire con ATK-Pro 2.0 installato.
2. Eseguire download end-to-end piccoli su almeno cinque famiglie tecniche:
   IIIF nativo, manifest sintetico da HTML, PDF diretto, DSpace bitstream e BDL
   BookReader/Cantaloupe.
3. Per ciascun output controllare numero di file, pagine iniziale/intermedia/
   finale, apertura del PDF, assenza di placeholder e cartelle vuote residue.
4. Eseguire un OCR breve, una traduzione breve e un'esportazione GEDCOM con dati
   non sensibili; riaprire i file prodotti e verificarne il contenuto.
5. Provare errori controllati: URL non riconosciuto, pagina inesistente,
   interruzione rete e annullamento. L'app deve conservare gli output validi e
   mostrare un messaggio utile.
6. Registrare qui data, artefatto, campione, risultato e anomalie. Le anomalie
   riproducibili vanno corrette in una release successiva, salvo problema di
   sicurezza o perdita dati che richieda una patch urgente.

## Confini della certificazione

- Il controllo live dimostra che i campioni pubblici funzionano alla data
  indicata; non garantisce l'immutabilita' futura dei portali esterni.
- Gli smoke CI verificano gli asset pubblicati, ma non sostituiscono tutte le
  combinazioni di hardware, antivirus, proxy e configurazione utente.
- SAG e ASTi non fanno parte della `v3.0.0`: sono registrati esclusivamente come
  candidati della prossima release nel documento dedicato.
