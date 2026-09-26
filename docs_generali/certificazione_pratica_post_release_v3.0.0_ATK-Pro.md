# Certificazione pratica post-release ATK-Pro v3.0.0

Data snapshot: 2026-09-26

Questo registro separa la validazione tecnica gia' conclusa per la release
stabile dalle prove pratiche svolte dopo la pubblicazione. Le prove usano solo
asset pubblici e URL campione coerenti con la policy dei portali. I risultati
non autorizzano scraping massivo o l'aggiramento di login, paywall e limiti di
riproduzione.

## Stato sintetico

| Area | Stato | Evidenza |
| --- | --- | --- |
| Release pubblicata | PASS | Tag `v3.0.0`, sei asset e digest presenti nella release GitHub. |
| Gate completo da sorgente | PASS | `python scripts\quality_gate.py release`: 11/11 step, 865 test passati e 39 skip attesi. |
| Portali live con immagini reali | PASS | `python verify_portal_live_smoke.py --fetch-images --strict`: 28/28 capability; immagini di inizio, centro e fine decodificabili e distinte nei documenti multipagina. |
| Pipeline completa dei portali | PASS | 28/28 portali hanno prodotto da una pagina pubblica PNG, PDF leggibile e JSON; nessun placeholder 800 x 1200 o temporaneo residuo nei casi riusciti. |
| BDL multipagina | PASS | Item `12404`: 12 canvas; pagine 1, 7 e 12 scaricate e decodificate alle dimensioni attese. |
| Artefatti multipiattaforma | PASS in CI | Smoke post-pubblicazione Windows, Linux e macOS completati sui sei asset esatti, come registrato nella checklist release. |
| Uso pratico locale Windows | PASS avvio e smoke grafico | Portable stabile riscaricato, SHA-256 verificato, avviato prima offscreen e poi visibilmente. Finestra, disclaimer, interfaccia italiana, menu, guida e chiusura sono stati verificati. |
| Percorsi funzionali utente | PASS | Download, manifest sintetico da HTML, OCR, traduzione, GEDCOM ed errori controllati sono verificati. Il disclaimer del menu Documenti usa ora lo stile ATK-Pro condiviso. |
| Funzioni IA live | PASS sui provider configurati | Traduzione e ricerca assistita: Gemini, OpenAI, Claude e DeepSeek; OCR multimodale: 4/4 con TXT, DOCX e TEI; genealogia: pipeline completa Gemini verso GEDCOM e due CSV. |

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

## Smoke grafico manuale del portable stabile 2026-09-11

Esito complessivo: **PASS**.

- eseguibile:
  `.codex_tmp/postrelease-v3.0.0/portable/ATK-Pro/ATK-Pro.exe`;
- finestra principale `ATK-Pro` aperta e reattiva;
- disclaimer visualizzato, interfaccia italiana e menu utilizzabili;
- guida aperta correttamente;
- chiusura regolare, senza interferenze con ATK-Pro 2.0.

La difformita' estetica inizialmente osservata nel disclaimer richiamato dal
menu Documenti e' stata corretta il 2026-09-25. Il visualizzatore testuale usa
ora tema scuro, cornice e pulsante ATK-Pro condivisi, mantenendo invariati testo
legale e flusso di consenso iniziale. La regressione UI e la verifica dedicata
del consenso sono passate; il gate release completo ha concluso con
`850 passed, 39 skipped`.

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

## Prove pratiche successive 2026-09-25

Gli output sono stati scritti sotto
`.codex_tmp/postrelease-e2e-20260925/`, escluso da Git. I test dei servizi IA
hanno usato esclusivamente dati sintetici non sensibili; nessuna credenziale e'
stata registrata nei report.

| Percorso | Campione | Esito | Evidenza |
| --- | --- | --- | --- |
| Manifest sintetico da HTML | Findbuch pubblico, 221 canvas rilevati; range 1-2, PNG + PDF | PASS | Due PNG reali e distinti da 6416 x 4640 e 6432 x 4656 pixel; PDF di due pagine; nessun placeholder, suffisso `_rec`, temporaneo o directory vuota. |
| OCR breve | Gemini, immagine sintetica con tre righe | PASS dopo correzione | File TXT prodotto e riaperto; nomi, data e luogo sono corretti e `ATTO DI PROVA` compare una sola volta. Lo split viene ora attivato soltanto dai prompt che dichiarano esplicitamente `DOPPIA PAGINA`. |
| Traduzione breve | Gemini, italiano verso inglese | PASS | Traduzione corretta di tre righe, nomi e data preservati; file TXT salvato e riaperto senza differenze. |
| Esportazione GEDCOM | Gemini, trascrizione sintetica di un atto di nascita | PASS dopo correzione | Il payload semantico `atti` e' preservato fino a `GedcomGenerator`; il GEDCOM contiene Giovanni Rossi, Luigi Rossi, Maria Bianchi e Trento, con conteggio estratto pari a 1. |
| Errori controllati | URL non valido, timeout/rete, annullamento e rollback | PASS | Suite mirata: `54 passed`. Una prova live Findbuch con range 999-1000 restituisce `False`, non crea PNG/PDF/placeholder/temporanei e conserva soltanto il manifest diagnostico valido. |

### Difetti riproducibili rilevati il 2026-09-25

1. `AdvancedOCRWorker` considera doppia pagina ogni immagine Gemini con rapporto
   larghezza/altezza almeno 1,6. Su un documento orizzontale semplice lo split
   sovrapposto puo' duplicare l'intestazione nel merge finale.
2. `GeminiHandler._extract_text_only_gemini()` usa `_parse_rows_from_text()` e
   restituisce una lista anche quando la risposta e' un oggetto semantico con
   chiave `atti`. `GenealogyWorker` avvolge poi la lista in `righe`, impedendo al
   generatore GEDCOM di usare il dispatcher `_process_atti()` gia' disponibile.

### Correzione verificata 2026-09-25

Entrambi i difetti IA sono stati corretti e sottoposti a controverifica:

- il dispatcher OCR usa lo split Gemini soltanto quando il prompt dichiara
  esplicitamente `DOPPIA PAGINA`; la prova reale sull'immagine sintetica
  1600 x 500 ha prodotto tre righe non vuote con una sola occorrenza
  dell'intestazione;
- i parser genealogici preservano l'oggetto JSON semantico completo, incluso
  `atti`, mantenendo il fallback per le tabelle legacy; il contatore del worker
  riconosce `atti`, `righe`, `records` e `famiglie`;
- la controprova Gemini testo-only ha prodotto un GEDCOM con soggetto, entrambi
  i genitori e luogo attesi, e conteggio estratto pari a 1;
- la suite mirata ha concluso con `33 passed, 14 skipped`, la suite IA estesa
  con `53 passed` e il gate release completo con `849 passed, 39 skipped`;
  tutti gli 11 step del gate sono stati superati.

## Verifica pratica completa dei 28 portali 2026-09-25

La prova ha attraversato l'intera pipeline di `Elaborazione`, non soltanto la
risoluzione del manifest o la decodifica di un'immagine campione. Per ciascuno
dei 28 portali registrati e' stata elaborata una sola pagina pubblica, nel
rispetto della policy `D`, `R_LIMITED`, `R_OK` o variabile applicabile. Ogni
PASS richiede contemporaneamente:

- almeno un PNG decodificabile e diverso dal placeholder 800 x 1200;
- un PDF leggibile di una pagina;
- il manifest o i metadati JSON attesi;
- assenza di cartelle temporanee o vuote residue.

La prima diagnosi completa ha concluso con 24/28 PASS e ha individuato quattro
difetti riproducibili:

1. BNCF Teca espone il documento `D` come JPEG diretto, ma il percorso tentava
   impropriamente di aggiungere `/info.json`;
2. Museo Galileo scaricava correttamente il JPEG, ma passava al generatore PDF
   una stringa di directory invece della lista delle immagini;
3. Internet Culturale derivava dal riferimento OAI un segmento di percorso non
   valido su Windows;
4. PHAIDRA derivava il segmento `o:327971`, non valido su Windows, e dopo il
   preflight tentava una ricostruzione completa tramite un numero eccessivo di
   tasselli IIIF.

Le correzioni mantengono rigorosa la validazione dei nomi inseriti dall'utente,
ma rendono sicuri i soli segmenti generati da identificativi remoti. BNCF usa
ora il JPEG ufficiale del canvas; Museo Galileo genera il PDF dalla lista
corretta; Internet Culturale e PHAIDRA usano nomi locali validi; PHAIDRA scarica
in un'unica richiesta l'immagine IIIF completa dichiarata dal canvas, con host
ufficiale verificato, invece di richiedere centinaia di tasselli.

La controprova finale ha prodotto 27/28 PASS nel giro unico. Findbuch non ha
risposto entro il timeout durante la prima acquisizione HTML, poi ha superato
il retry isolato in 6,94 secondi: l'esito effettivo consolidato e' quindi
28/28 PASS. Il complesso degli output riusciti occupa circa 305 MB. BDL ha
prodotto una pagina reale, PNG, PDF e JSON senza placeholder residui; PHAIDRA
ha concluso in 12,36 secondi usando una singola immagine completa. I report
locali sono:

- `.codex_tmp/portal_e2e_report_20260925_run4.csv` per il giro completo;
- `.codex_tmp/portal_e2e_report_20260925_run5.csv` per il retry Findbuch.

La suite mirata ha concluso con `59 passed`. Il gate release completo ha
concluso con `861 passed, 39 skipped`; tutti gli 11 step sono stati superati.

## Certificazione pratica delle funzioni IA 2026-09-26

Le prove live hanno usato esclusivamente un atto sintetico con nomi, luogo e
data inventati. Gli output e i report sono stati scritti sotto
`.codex_tmp/ai_certification/`, escluso da Git. Nessuna chiave o risposta
integrale del provider e' registrata nella certificazione.

| Funzione | Provider/campione | Esito | Evidenza |
| --- | --- | --- | --- |
| Traduzione OCR | Gemini, OpenAI, Claude e DeepSeek; italiano verso inglese | PASS 4/4 | Tutti i worker hanno concluso con successo preservando Giovanni Rossi, Trento e 1882. |
| OCR multimodale | Immagine sintetica 1800 x 1000; Gemini, OpenAI, Claude e DeepSeek | PASS 4/4 dopo correzione | Ogni provider ha trascritto nomi, luogo e data. Per ciascuno sono stati prodotti e riaperti TXT, DOCX e XML TEI-P5 validi. |
| Ricerca assistita comparativa | Query genealogica sintetica, modalita' `show_all` | PASS 4/4 | Gemini, OpenAI, Claude e DeepSeek hanno restituito ciascuno una riga strutturata; nessun errore del worker. |
| Estrazione genealogica | Trascrizione sintetica di atto di nascita, Gemini | PASS | GEDCOM UTF-8 con soggetto, genitori e trailer `0 TRLR`; prodotti e riaperti entrambi i CSV; conteggio estratto pari a 1. |
| Errori e sicurezza | Suite deterministica e ispezione log | PASS | Le chiavi non sono riportate nei log: gli errori genealogici identificano soltanto lo slot. |

La verifica ha individuato e corretto quattro difetti riproducibili:

1. i modelli predefiniti Claude e DeepSeek non erano piu' disponibili presso i
   rispettivi provider; sono ora `claude-sonnet-4-6` e `deepseek-flash`;
2. DeepSeek era ancora classificato come solo testo e l'OCR non gli inoltrava
   l'immagine; il percorso multimodale e' ora attivo anche nell'estrazione
   genealogica;
3. `gpt-4o` ha rifiutato l'immagine sintetica nello smoke OCR, mentre
   `gpt-4.1` ha trascritto correttamente lo stesso input; il default OpenAI e'
   stato aggiornato soltanto per il servizio OCR;
4. un errore del worker genealogico riportava nei log i primi caratteri della
   chiave; ora registra esclusivamente il numero dello slot.

Le prove OpenAI e DeepSeek sono state ripetute con `openai==2.33.0`, la versione
vincolata dal progetto: il vecchio SDK presente nell'ambiente Python globale
non rappresenta il runtime previsto dalla build. Le guide OCR italiana e le
19 traduzioni descrivono ora gli stessi default e la capacita' multimodale
DeepSeek.

La suite deterministica IA iniziale ha concluso con `108 passed`; la suite
mirata finale per IA, documenti e localizzazione con `84 passed, 2 skipped`
attesi. Il gate release completo ha concluso con `865 passed, 39 skipped`;
tutti gli 11 step sono stati superati.

Il PASS live riguarda i quattro provider per cui il caveau locale contiene
credenziali. Mistral, xAI, Groq, HuggingFace e Transkribus restano coperti dai
test deterministici ma non sono dichiarati verificati live senza credenziali;
Ollama richiede inoltre un servizio locale e un modello installato.

## Attivita' pratica residua

Nessuna anomalia funzionale o estetica nota resta aperta nelle prove registrate.
Resta facoltativa una prova live dei provider non configurati quando saranno
disponibili le relative credenziali o, per Ollama, un modello locale.

## Confini della certificazione

- Il controllo live dimostra che i campioni pubblici funzionano alla data
  indicata; non garantisce l'immutabilita' futura dei portali esterni.
- Gli smoke CI verificano gli asset pubblicati, ma non sostituiscono tutte le
  combinazioni di hardware, antivirus, proxy e configurazione utente.
- SAG e ASTi non fanno parte della `v3.0.0`: sono registrati esclusivamente come
  candidati della prossima release nel documento dedicato.
