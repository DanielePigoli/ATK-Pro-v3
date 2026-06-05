# Roadmap portali ATK-Pro

Data snapshot: 2026-05-26

Questa roadmap traduce la matrice dei portali esistenti in una sequenza pratica
di lavoro. Non e una consulenza legale: applica al progetto i paletti gia
documentati in `docs_generali/valutazione_portali_ATK-Pro.md` e le fonti
ufficiali raccolte in `docs_generali/matrice_portali_esistenti_ATK-Pro.md`.

## Decisione generale

La priorita non e aggiungere subito altri portali, ma consolidare quelli gia
presenti separando tre piani:

1. supporto tecnico del manifest o delle immagini;
2. avvisi chiari su licenza, citazione, non commerciale e no-login;
3. test offline per evitare regressioni senza dipendere dai siti esterni.

Nuovi portali vanno valutati solo dopo questa fase, e solo se sono pubblici,
istituzionali, senza login/paywall e con IIIF/API o documentazione tecnica
stabile.

## Indirizzo strategico

ATK-Pro deve restare prima di tutto uno strumento di ausilio alla ricerca
genealogica in area italiana e italofona. La priorita non coincide pero con i
confini amministrativi attuali: per la storia migratoria italiana vanno
considerate anche le fonti pubbliche dei paesi di destinazione e delle aree
storicamente collegate alla documentazione italiana.

Ordine strategico di ricerca e valutazione:

1. Italia, Stato della Citta del Vaticano, San Marino e aree italofone o
   storicamente connesse alla ricerca italiana, incluse Svizzera italiana,
   Trentino-Alto Adige/Sudtirol, Friuli Venezia Giulia e territori legati alla
   storia asburgica o austro-ungarica.
2. Paesi di emigrazione italiana ad alta rilevanza genealogica: Brasile,
   Argentina, Colombia, Stati Uniti, Australia, Nuova Zelanda, Francia, Belgio
   e Germania.
3. Altri portali internazionali solo quando sono molto rilevanti, istituzionali,
   tecnicamente stabili e utili anche per ricerche connesse all'area italiana o
   italofona.

Questa ambizione va trattata come una pipeline di scouting, non come promessa di
integrazione automatica: ogni portale candidato deve superare i criteri
go/no-go gia documentati e deve poter essere mantenuto senza aggirare login,
paywall, restrizioni tecniche o limiti contrattuali.

Aggiornamento operativo 2026-06-05: il ciclo internazionale resta sospeso dopo
le prime valutazioni su Brasile, Argentina e Colombia. Il lavoro torna
all'ambito italiano e italofono, con precedenza a Archivi Nazionali/SIA,
Archivio Digitale, SAN, SIAS, SIUSA, fonti ecclesiastiche italiane e aree
italofone o storicamente connesse.

Sequenza di ripresa italiana/italofona:

1. completare la mappa tecnica di Archivi Nazionali/SIA, Archivio Digitale,
   SAN, SIAS e SIUSA, separando ricerca, metadati e scaricamento;
2. valutare BeWeB e archivi diocesani/parrocchiali italiani come discovery o
   link assistito, senza automatizzare materiali sensibili o non chiaramente
   pubblici;
3. valutare Ticino, Grigioni e Diocesi di Coira per fonti italofone svizzere e
   storico-ecclesiastiche, con attenzione a registri parrocchiali, microfilm,
   inventari e condizioni di riproduzione;
4. cercare altri portali italiani IIIF pubblici simili a Biblioteca Digitale
   Siena, preferendo `R_LIMITED` con range esplicito e fonti ufficiali;
5. riprendere le piste diaspora non italiane solo dopo avere chiuso questo
   blocco o dopo una decisione esplicita di priorita.

## Priorita 1 - Consolidare

Portali da trattare per primi per rapporto favorevole tra valore, metodo
tecnico e verificabilita delle fonti:

- `manifest_diretto`: mantenere come percorso avanzato, con avviso che termini
  e diritti dipendono dal sito di origine. Dal 2026-06-02 supporta anche
  manifest IIIF Presentation v3 image-only tramite normalizzazione interna.
- `bodleian`, `heidelberg`, `e_rara`, `e_codices`, `e_manuscripta`: IIIF
  diretto/builder dedicati, ma sempre con controllo licenza per item o volume.
- `europeana`: utile come aggregatore IIIF, solo record con rights statement
  chiaro e attribuzione ai provider.
- `gallica`: API IIIF documentata, riuso non commerciale con citazione e
  attenzione ai documenti partner.
- `internetculturale_estense`: consolidabile su contenuti pubblici web,
  non commerciali, con citazione e preferenza per IIIF ufficiale quando
  disponibile.

Stato operativo:

- la capability `record_mode_policy` e' centralizzata in `src/portal_registry.py`;
- `R_OK` consente registro completo con avviso;
- `R_LIMITED` richiede range canvas esplicito e blocca batch `R` senza range;
- `D_ONLY` blocca i record `R` prima dell'avvio;
- `VARIABLE` richiede conferma esplicita per il manifest diretto;
- `portal_policy_overrides.json` permette aggiornamenti locali della policy
  senza attendere una nuova release;
- `verify_portal_policy.py` segnala policy da riverificare e puo' generare un
  template locale di override.

Interventi consigliati:

- mantenere avvisi sintetici nel flusso UI prima del download;
- creare fixture offline di manifest/item rappresentativi;
- mantenere rate limit espliciti dove gia previsti.

## Priorita 2 - Mantenere con avvisi forti

Portali ad alto valore ma con limiti di riuso o variabilita per ente:

- `antenati`: portale primario per ricerca e studio; non trattare le immagini
  come automaticamente open reuse.
- `vatlib`: tecnicamente IIIF, ma uso libero solo personale/studio e
  riproduzione/pubblicazione soggetta ad autorizzazione BAV.
- `memooria`, `brixiana`: capability tecnica Jarvis/IIIF, ma accesso e diritti
  dipendono dall'ente; solo risorse pubbliche no-login.
- `internet_archive`: item-by-item; solo materiale pubblico, scaricabile e con
  licenza/diritti chiari.

Interventi consigliati:

- mostrare un avviso specifico per portale;
- bloccare ogni percorso che richieda credenziali o aree riservate;
- documentare nel codice le assunzioni per singola istanza.

## Priorita 3 - Non estendere per ora

Portali da mantenere solo se il supporto esistente resta utile e non viola i
paletti, ma da non ampliare senza nuove fonti ufficiali o autorizzazioni:

- `bnc_roma`: solo contenuti pubblici e no-login; escludere OpenAthens, alta
  risoluzione, materiali sotto diritto e pubblicazione automatizzata.
- `bncf_teca`: consultazione puntuale, citazione e cautela su riproduzione o
  pubblicazione.
- `museogalileo`: endpoint non documentato/stabile; niente nuove automazioni.
- `findbuch`: piattaforma per molte istanze; non estendere genericamente.
- `matricula`: CC BY-NC-ND 2.0, quindi no commerciale, no derivati e no bulk.

Interventi consigliati:

- evitare nuove feature basate su scraping-like o HTML fragile;
- aggiungere test solo per proteggere il comportamento gia presente;
- rivalutare solo se compare una API/IIIF ufficiale o una policy piu chiara.

## Nuovi portali

Ordine di valutazione consigliato:

1. area italiana/italofona solo se il portale e pubblico, istituzionale,
   no-login e con API/IIIF ufficiale;
2. area internazionale IIIF/API con licenze per item chiare;
3. aggregatori solo se espongono rights statement e provider in modo leggibile;
4. esclusione diretta per portali commerciali, chiusi, paywall, abbonamento,
   login obbligatorio, anti-bot o divieto di automazione.

Scheda minima prima di proporre un nuovo portale:

- nome portale e area;
- URL ufficiale;
- fonte termini/licenza;
- fonte API/IIIF o documentazione tecnica;
- metodo previsto: IIIF diretto, API, discovery, sintetico;
- limiti: login, rate limit, copyright, riuso, non commerciale, no-derivati;
- fixture offline prevista;
- decisione: integrare, verificare ancora, solo link, non supportare.

Per Archivi Nazionali/SIA il primo obiettivo non e il download, ma la mappatura
delle capability: il portale unico Archivi Nazionali risulta ancora in sviluppo,
mentre Archivio Digitale e gia consultabile come aggregatore di progetti e
risorse digitalizzate. Qualunque download diretto va quindi deciso su singole
risorse pubbliche, non sul nome generico del portale nazionale.

Per candidati non-IIIF ma con download pubblico dichiarato, come il Museu da
Imigracao de Sao Paulo, non usare builder HTML improvvisati. Prima serve una
capability tecnica esplicita per PDF/immagini dirette pubbliche, separata dagli
adapter IIIF, con blocco prudente dei registri completi quando la policy non
consente un download ampio.

Per candidati ad alto valore ma con accesso registrato o login, come APESP nel
primo controllo 2026-06-05, mantenere solo schede di orientamento e link
assistiti. La presenza di una base pubblica consultabile non basta per
abilitare download diretto se la consultazione effettiva passa da autenticazione
o da regole di riproduzione non compatibili con automazione.

Se il sito espone CAPTCHA, challenge anti-spam o verifica umana, come osservato
su SIAN nel controllo 2026-06-05, il candidato resta escluso dal download
diretto anche quando i documenti sono gratuiti o disponibili dopo registrazione.
Eventuali basi parallele no-login vanno valutate separatamente, senza riusare
credenziali, sessioni o percorsi autenticati.

Per fonti private/non governative con buscador pubblico e possibile CAPTCHA,
come CEMLA nel controllo 2026-06-05, mantenere link assistito e note di ricerca.
La grande utilita genealogica non basta per automatizzare interrogazioni o
scarichi quando non esistono API, endpoint documentati o termini espliciti.

Se un portale pubblico consente download PDF tramite form di ricerca ma non
espone API, IIIF o endpoint documentati, come il buscador inmigrantes AGN
Argentina nel controllo 2026-06-05, trattarlo prima come integrazione
metadata/link assistito. Il passaggio a download diretto richiede un campione
pubblico stabile, limiti di interrogazione espliciti, fixture offline e blocco
di ricerche ampie non richieste dall'utente.

Per portali con metadati pubblicati su piattaforme open data e contenuti
digitali soggetti a termini separati, come DataViva Colombia nel controllo
2026-06-05, separare le due capability: metadata/API puo essere valutata come
integrazione prioritaria, mentre download immagini/PDF richiede una verifica
item-level dei diritti, dei termini specifici e dei limiti operativi.

Matrice iniziale di scouting:

- `docs_generali/matrice_portali_candidati_ATK-Pro.md`.
- `docs_generali/Matrice_portali.xlsx`, come vista tabellare di lavoro dei
  portali esistenti e candidati. I file Markdown restano la fonte primaria da
  aggiornare. Dopo ogni modifica alla vista Excel, eseguire
  `python verify_portal_matrix_workbook.py`.

## Sequenza tecnica consigliata

1. Mantenere allineata la registry `portale -> capability`; gruppi UI,
   avvisi operativi, referer HTTP, famiglia tecnica, policy tile e policy
   `D/R` sono centralizzati.
2. Spostare progressivamente nella registry le altre capability tecniche
   ancora implicite in `elaborazione`, `manifest_utils` e `tile_downloader`.
3. Estendere gli adapter IIIF diretti senza creare scraping: link Mirador con
   `manifestId`, manifest v2 e manifest v3 image-only devono restare coperti
   da fixture offline.
4. Aggiungere fixture offline per i portali in priorita 1.
5. Spostare progressivamente i builder verso adapter testabili.
6. Usare la shortlist operativa nella matrice candidati per scegliere i
   prossimi portali da verificare.
