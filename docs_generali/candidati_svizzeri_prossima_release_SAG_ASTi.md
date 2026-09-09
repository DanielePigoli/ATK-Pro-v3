# Candidati svizzeri per la prossima release: SAG e ASTi

Data snapshot: 2026-09-09

Questa nota conserva le verifiche tecniche utili emerse dopo la pubblicazione
di ATK-Pro `v3.0.0`. Non modifica il perimetro della release stabile e non
costituisce ancora una decisione finale di integrazione. Prima del codice
servono una verifica aggiornata dei termini, fixture offline, test mirati e una
policy runtime esplicita.

## SAG - Archivio di Stato dei Grigioni

### Esito

Il precedente giudizio "prevalentemente consultativo" e' superato. Il sistema
CMI AIS pubblico espone metadati, ricerca di file e allegati originali senza
login. Sono presenti veri PDF di registri parrocchiali della serie
`A I 21 b 2`, oltre a fotografie, piante, pubblicazioni ufficiali e altri fondi
digitalizzati.

Fonti istituzionali:

- sistema archivistico: `https://staatsarchiv-findsystem.gr.ch/home/`;
- fondi digitalizzati:
  `https://www.gr.ch/DE/institutionen/verwaltung/ekud/afk/sag/dienstleistungen/bestaende/digitalisiertebestaende/Seiten/default.aspx`;
- ricerca e condizioni generali di accesso:
  `https://www.gr.ch/DE/institutionen/verwaltung/ekud/afk/sag/dienstleistungen/bestaende/Seiten/default.aspx`.

### Interfaccia tecnica verificata

- configurazione pubblica:
  `/home/api/Public/GetSettings?tenant=home`;
- ricerca CMI AIS:
  `/home/api/Data/Search?search={json-url-encoded}`;
- dettaglio unita':
  `/home/api/Data/GetEntity/{guid}?language=de`;
- file originale:
  `/home/api/File/GetFile/?id={file-id}&version={version}&rendition=Original`.

Verifica 2026-09-09:

- la ricerca `Kirchenbücher` ha restituito 657 risultati nella sezione file;
- la ricerca `Taufen Ehen Todesfälle` ne ha restituiti 338;
- tra i risultati compaiono PDF originali di Surrein, Lantsch/Lenz, Bivio,
  Zizers, Stampa e altri comuni;
- il campione Surrein `A I 21 b 2/113.5` espone un file `.pdf` originale e
  l'endpoint `GetFile` risponde `200 application/pdf` senza autenticazione;
- il server non onora la richiesta HTTP Range provata e invia il PDF con
  trasferimento chunked. L'eventuale downloader deve quindi usare streaming su
  disco, limiti di dimensione, timeout, annullamento e pulizia atomica dei file
  incompleti.

I numeri 657 e 338 sono conteggi dei risultati delle due ricerche campione, non
la consistenza ufficiale complessiva dei registri digitalizzati.

### Vincoli obbligatori

L'integrazione non deve assumere che un'intera serie sia liberamente
scaricabile. Prima di esporre il file occorre leggere il record padre e
verificare almeno:

- `Benutzbarkeit`;
- `AblaufSchutzfrist` e `Schutzfrist`;
- `Zugang.Verwertungsrecht`;
- presenza effettiva di una rendition `Original` pubblica.

Le serie con protezione, dati personali o riproduzione condizionata devono
restare escluse. La classificazione iniziale consigliata e' `D_ONLY`: download
del singolo PDF esplicitamente scelto dall'utente, senza enumerazione o
acquisizione massiva della serie.

### Proposta per la prossima release

Priorita' alta. Preparare un adapter `sag_cmi_ais` con:

1. riconoscimento degli URL `#/content/{guid}`;
2. risoluzione del record tramite `GetEntity`;
3. selezione esplicita dell'allegato;
4. controllo dei campi di accesso e diritti;
5. download streaming del PDF originale;
6. fixture per record libero, record senza file e record non autorizzabile;
7. smoke live leggero che non scarichi integralmente file di grandi dimensioni.

## ASTi - Archivio di Stato del Cantone Ticino

### Esito

ASTi pubblica documenti digitalizzati, ma su sottosistemi distinti. Non emerge
un equivalente unico del catalogo SAG con serie di registri PDF scaricabili.
La candidatura deve essere divisa per famiglia tecnica.

### `asti_scopearchiv`

Il catalogo generale descrive i fondi e indicizza anche inventari PDF collegati:
`https://www.archiviodistato.ti.ch/Query/volltextsuche.aspx`.
Resta una capability di discovery/link. Gli inventari non vanno scambiati per
le riproduzioni dei documenti archivistici descritti.

Classificazione proposta: `C`, nessun downloader generale.

### `asti_mappe_catastali_recuperando`

L'ASTi dichiara liberamente consultabili le copie digitali delle mappe
catastali ottocentesche di 179 comuni, circa 5200 fogli:
`https://www4.ti.ch/decs/dcsu/asti/patrimonio/mappe-catastali/`.

Verifica tecnica su Agno, fascicolo 1:

- pagina pubblica:
  `https://www.recuperando.ch/documenti/agno/agno-fascicolo-1/`;
- indice Zoomify:
  `https://recuperando.ch/doc-progetti/piramidalizzati/Images/archivio-di-stato/Agno_1_Fasc_01.xml`;
- l'indice elenca 18 immagini;
- ogni immagine espone `ImageProperties.xml`; la corografia campione dichiara
  `8486 x 6700`, tile da 256 pixel e 1248 tasselli;
- un tile campione `TileGroup0/0-0-0.jpg` risponde pubblicamente come JPEG.

La ricostruzione da tile Zoomify e' tecnicamente possibile. Deve restare
limitata alla risoluzione offerta dal viewer: le copie ufficiali a 300 dpi sono
rilasciate dall'Archivio solo su richiesta secondo il regolamento.

Classificazione proposta: candidato `A/B`, policy iniziale `R_LIMITED`, range
esplicito e attribuzione della fonte. Prima dell'integrazione verificare i
termini specifici di Recuperando e costruire fixture senza incorporare immagini
protette.

### `asti_fondi_fotografici`

L'ASTi conferma che le immagini catalogate sono consultabili direttamente sul
web:
`https://www4.ti.ch/decs/dcsu/asti/patrimonio/fondi-fotografici`.
Il catalogo pubblico e' disponibile come ospite:
`https://www3.ti.ch/DECS/dcsu/ac/asti/cff/`.

La scheda campione `id_immagine=148` mostra immagine e metadati, ma non e'
ancora stato qualificato un endpoint stabile per il derivato web ne' il diritto
di scaricare automaticamente l'originale TIFF indicato nei metadati.

Classificazione proposta: `B`, sonda tecnica e verifica dei termini prima di
qualsiasi downloader.

### `asti_pergamene`

Il servizio offre regesti, ricerca e PDF stampabili dei risultati. Nei campioni
esaminati l'immagine del documento non era disponibile. Non va quindi trattato
come corpus omogeneo di riproduzioni.

Classificazione proposta: `C`, metadata/discovery; immagini solo dopo verifica
item-level.

### Fonti genealogiche riservate

Ruoli della popolazione, stato civile e registri parrocchiali non costituiscono
un archivio ASTi liberamente scaricabile. I ruoli contengono dati sensibili e
la riproduzione sistematica, integrale o parziale, non e' consentita. I
microfilm dei registri parrocchiali sono indicati soprattutto presso l'Archivio
diocesano di Lugano.

Fonte:
`https://www4.ti.ch/fileadmin/DECS/DCSU/ASTI/Documenti/Ricerche_genealogiche.pdf`.

## Ordine proposto

1. SAG CMI AIS, per i PDF originali pubblici e la forte utilita' genealogica.
2. ASTi mappe catastali, come adapter Zoomify separato.
3. ASTi fondi fotografici, dopo sonda endpoint e diritti.
4. ASTi scopeArchiv e pergamene solo come discovery, salvo nuove evidenze.

La destinazione naturale e' una release funzionale successiva, indicativamente
`v3.1.0`, non una modifica retroattiva della `v3.0.0` stabile.
