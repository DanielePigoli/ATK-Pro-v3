# Prossima release: ottimizzazioni IA e Biblioteca di Cremona

Data di registrazione: 27 settembre 2026.

Stato: destinazione della prossima release funzionale; nessuna modifica al
perimetro della RC di manutenzione `v3.0.1-rc1`.

Questo documento raccoglie due destinazioni esplicitamente rinviate alla
release funzionale successiva alla RC corrente, indicativamente `v3.1.0`:

1. miglioramento dell'efficienza, robustezza e verificabilità delle funzionalità assistite da IA;
2. valutazione e possibile integrazione delle raccolte digitali della Biblioteca Statale di Cremona pubblicate tramite Synology File Station.

## Funzionalità assistite da IA

Le funzionalità attuali restano idonee alla RC e non presentano blocchi noti. Gli interventi seguenti sono rinviati alla prossima release perché richiedono modifiche trasversali e una nuova certificazione mirata.

Ordine consigliato:

1. introdurre benchmark riproducibili e metriche locali rispettose della riservatezza: modello effettivo, latenza, consumo di token, fallback ed errori, senza memorizzare contenuti o chiavi;
2. aggiungere annullamento cooperativo e ripresa reale dell'OCR da elaborazioni parziali;
3. centralizzare timeout adattivi, tentativi, backoff e budget di token;
4. segmentare le traduzioni lunghe e introdurre una cache locale basata sull'hash del contenuto;
5. consentire concorrenza OCR limitata e configurabile;
6. usare output strutturati nativi e validazione tramite schema per genealogia e ricerca assistita;
7. unificare l'accesso ai provider IA mediante un gateway comune per OCR, traduzione, ricerca e genealogia.

La realizzazione dovrà procedere per incrementi piccoli, ciascuno accompagnato da test mirati, benchmark comparativi e verifica di regressione delle funzioni esistenti.

Questa linea di lavoro e' coordinata, ma non confusa, con la priorita' portali
descritta in
[`candidati_svizzeri_prossima_release_SAG_ASTi.md`](candidati_svizzeri_prossima_release_SAG_ASTi.md).

## Biblioteca Statale di Cremona

### Esito preliminare

Classificazione: **candidato tecnicamente implementabile, da mantenere in revisione per la prossima release**.

Identificativo proposto: `biblioteca_cremona_filestation`.

Famiglia tecnica proposta: `synology_file_station`.

Politica iniziale proposta: `R_LIMITED`.

Priorità proposta: B.

### Evidenze tecniche

La pagina istituzionale dedicata a *La Provincia (1883-1923)* rimanda a un'istanza Synology File Station e pubblica credenziali di consultazione. Una verifica pratica, limitata alla lettura, ha confermato:

- disponibilità delle API ufficiali `SYNO.API.Auth`, `SYNO.FileStation.List` e `SYNO.FileStation.Download`;
- presenza delle condivisioni `IL REGIME FASCISTA`, `LA PROVINCIA`, `LIS` e `MATERIALE DIGITALIZZATO`;
- struttura regolare per anno, fascicolo e formato;
- per un fascicolo campione de *La Provincia* disponibilità di quattro pagine in JPEG, PDF e XML;
- download riuscito di un XML campione;
- XML strutturato con dati di testata, data, numero, pagina, articoli, titolo, autore, sommario e testo, quindi potenzialmente utilizzabile senza nuovo OCR.

L'esito rende plausibile un connettore che presenti una selezione esplicita di raccolta, anno, fascicolo e pagina, preferisca i metadati e i testi XML e consenta il recupero di PDF o JPEG quando autorizzato.

Il perimetro proposto e' un solo connettore con quattro profili di raccolta:

1. *La Provincia*;
2. *Il Regime Fascista*;
3. *Materiale digitalizzato*;
4. *Scaffale LIS*.

Le altre risorse elencate nel sito della Biblioteca, tra cui manoscritti
miniati, Fondo Cozio, storie soresinesi, ebook, periodici e banche dati, non
sono automaticamente comprese: possono dipendere da piattaforme esterne,
diritti o famiglie tecniche differenti e richiedono una valutazione separata.

### Condizioni da risolvere prima dell'implementazione

Il candidato non deve essere promosso a portale supportato finché non sono risolti i punti seguenti:

- l'endpoint attuale è esposto tramite indirizzo IP con un certificato Synology privo di nome host valido; il client non deve disabilitare la verifica TLS;
- le credenziali pubblicate potrebbero cambiare e non devono essere incorporate nel codice o nei pacchetti distribuiti;
- le pagine istituzionali consultate non forniscono condizioni sufficientemente esplicite per automatizzazione, limiti di scaricamento, attribuzione e redistribuzione dei file;
- ciascuna delle quattro condivisioni dovrà essere valutata separatamente per contenuti, diritti e struttura.

### Chiarimenti da richiedere alla Biblioteca

Prima dello sviluppo occorre chiedere:

1. un nome DNS stabile con certificato TLS pubblicamente valido;
2. un collegamento condiviso o un accesso API stabile e di sola lettura, preferibile a credenziali generiche soggette a rotazione;
3. conferma scritta dell'ammissibilità dell'accesso automatizzato e degli eventuali limiti di frequenza o volume;
4. regole di attribuzione, riuso e redistribuzione dei file e dei dati estratti;
5. indicazione delle raccolte effettivamente comprese nel servizio pubblico.

### Vincoli progettuali proposti

Se i chiarimenti saranno positivi, il connettore dovrà:

- mantenere sempre attiva la verifica TLS;
- acquisire le credenziali dall'utente o da configurazione sicura, senza valori predefiniti nel sorgente;
- evitare scansioni integrali o download massivi impliciti;
- richiedere una selezione consapevole di raccolta, anno e fascicolo;
- applicare limiti di concorrenza, timeout, backoff e messaggi di errore chiari;
- privilegiare XML e metadati quando bastano allo scopo;
- registrare la provenienza e le condizioni d'uso insieme ai risultati;
- includere test unitari con risposte simulate e un collaudo live strettamente controllato prima della promozione.

### Fonti istituzionali

- Biblioteca Statale di Cremona, *La Provincia (1883-1923)*: <https://bibliocremona.it/patrimonio/biblioteca-digitale/risorse-elettroniche/la-provincia-1883-1923/>
- Biblioteca Statale di Cremona, *Biblioteca digitale*: <https://bibliocremona.it/patrimonio/biblioteca-digitale/>
- Biblioteca Statale di Cremona, *Fotoriproduzioni*: <https://bibliocremona.it/informazioni/servizi/fotoriproduzioni/>
- Synology, *File Station API Guide*: <https://global.download.synology.com/download/Document/Software/DeveloperGuide/Package/FileStation/All/enu/Synology_File_Station_API_Guide.pdf>

## Ordine coordinato della prossima release funzionale

L'ordine proposto per `v3.1.0` e':

1. SAG tramite adapter `sag_cmi_ais`, per PDF originali pubblici e forte
   utilita' genealogica;
2. Biblioteca Statale di Cremona tramite `synology_file_station`, soltanto
   dopo la risoluzione dei blocchi TLS e delle condizioni d'uso;
3. ASTi mappe catastali Zoomify, quindi fondi fotografici; scopeArchiv e
   pergamene restano discovery finche' non emergono riproduzioni e condizioni
   compatibili;
4. ottimizzazioni IA per incrementi misurabili, ciascuna con benchmark e test
   di regressione.

## Credenziali utente per portali autenticati

Una cassaforte per login e password di portali autenticati e' tecnicamente
realizzabile, ma non appartiene ne' a `v3.0.1-rc1` ne' alla prima release
funzionale successiva. La sua valutazione e' rinviata alla release seguente a
`v3.1.0`, per non intrecciare l'espansione dei portali con un nuovo perimetro
di sicurezza.

Requisiti minimi della futura progettazione:

- backend sicuro multipiattaforma basato sui servizi del sistema operativo
  (per esempio Credential Manager/DPAPI, Keychain o Secret Service);
- namespace distinto dalla cassaforte delle chiavi dei provider IA, pur
  riusando un'eventuale astrazione comune;
- nessun segreto in `config.json`, log, diagnostica, export o pacchetti;
- adapter di autenticazione specifico per portale, scadenza della sessione,
  logout e revoca verificabili;
- verifica preventiva di termini d'uso, automazione consentita, limiti e
  trattamento dei dati per ciascun portale;
- test di migrazione, indisponibilita' del keyring, cancellazione sicura e
  comportamento su Windows, macOS e Linux.
