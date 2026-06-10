# Roadmap portali ATK-Pro

Data snapshot: 2026-06-06

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

Esito primo controllo Archivi Nazionali/Archivio Digitale (2026-06-05):

- `archivi_nazionali` resta strategico ma non implementabile come downloader in
  questa fase: il portale pubblico risulta ancora in sviluppo e la documentazione
  ICAR prevede anche risorse accessibili solo con identita digitale.
- `archivio_digitale_icar` e pubblico e consultabile senza registrazione, ma i
  termini d'uso vietano copia/estrazione massiva e robot o metodi analoghi.
  Deve quindi restare fuori dai builder/downloader di ATK-Pro.
- La funzione compatibile per questa famiglia e un supporto di orientamento:
  apertura link, ricerca assistita, note di contesto e, se utile in futuro,
  collegamento documentato verso pagine pubbliche, non scaricamento.

Esito primo controllo SAN/SIAS/SIUSA (2026-06-05):

- `san_risorse_digitali` e soprattutto catalogo, interoperabilita e strumenti
  di ricerca. La pista tecnica ammissibile e metadata/OAI, non immagini.
- `sias` resta utile per descrizioni archivistiche, inventari e rimandi a
  strumenti online; le riproduzioni digitali collegate non costituiscono una
  base per download generale.
- `siusa` resta utile per archivi non statali, soggetti conservatori/produttori
  e inventari interni o esterni; i testi hanno licenza aperta salvo diversa
  specificazione, ma il portale non e una fonte immagini.
- Il prossimo passo italiano non e un downloader nazionale, ma una eventuale
  capability di ricerca/metadati e apertura guidata di inventari, distinta dal
  motore di scaricamento immagini.

Esito primo controllo BeWeB/archivi ecclesiastici italiani (2026-06-05):

- `beweb` e fonte nazionale molto rilevante per beni archivistici ecclesiastici,
  inventari, soggetti conservatori, persone, famiglie e istituti culturali.
  Include categorie di alto valore genealogico, ma non va trattato come
  downloader.
- I termini BeWeB indicano CC BY-NC-SA per i contenuti e CC0 solo per alcune
  categorie catalografiche; esistono area riservata e servizi di prenotazione.
  Senza API/IIIF pubblica generalizzabile, la sola integrazione prudente e
  discovery/link assistito.
- Gli archivi diocesani e parrocchiali italiani restano fonti primarie per
  registri sacramentali e stati delle anime, ma accesso e riproduzione dipendono
  da diocesi, parrocchia, privacy e consultazione locale. ATK-Pro puo aiutare a
  orientarsi, non automatizzare.

Esito primo controllo Svizzera italiana / Grigioni / Coira (2026-06-05):

- `archivio_stato_ticino` e `servizio_archivi_locali_ticino` sono molto
  rilevanti per archivi comunali, patriziali e parrocchiali ticinesi. Le
  disposizioni genealogiche ASTi prevedono ricerche puntuali, formulari, costi,
  limiti su ruoli di popolazione e divieto di riproduzione sistematica di alcune
  serie: niente downloader.
- `archivio_diocesano_lugano` e fonte ecclesiastica di riferimento per
  microfilm e consultazione dei registri parrocchiali ticinesi, ma su
  appuntamento e senza portale immagini pubblico.
- `archivio_stato_grigioni` e molto forte per valli italofone e mobilita alpina:
  microfilm dei registri parrocchiali, registri di stato civile fino al 1929,
  strumenti online/PDF e sistema informativo. La consultazione resta pero in gran
  parte in sala lettura o soggetta ad autorizzazione.
- `diocesi_chur_coira` offre orientamento ecclesiastico e Findbuch; va trattata
  come link/discovery, non come downloader generico.

Esito primo scouting biblioteche digitali italiane (2026-06-05):

- Questo e il primo blocco italiano/italofono con reale potenziale di nuova
  integrazione di download, perche alcuni portali espongono pubblico dominio,
  immagini scaricabili, IIIF, OAI-PMH o endpoint PDF pubblici.
- `biblioteca_digitale_trentina` e il candidato piu pulito del blocco: accesso
  pubblico, download gratuito e riuso dichiarato anche commerciale con
  citazione. La sonda tecnica ha confermato che il metodo stabile non e IIIF,
  ma immagine/PDF diretti dalla pagina pubblica. La sonda
  `verify_bdt_technical_probe.py` serve a raccogliere candidati manifest,
  immagini e PDF da una pagina pubblica prima di qualsiasi integrazione.
  Prima esecuzione su `Iconografia/4052`: trovati JPEG diretti su storage S3,
  nessun manifest IIIF reale; l'implementazione piu probabile e quindi un
  adapter per immagini dirette da pagina pubblica, non un adapter IIIF. La
  sonda distingue ora immagini di contenuto da asset del sito, per evitare di
  trattare loghi/header come pagine scaricabili.
  Seconda esecuzione su `Testi-a-stampa/113`: trovati PDF diretto e immagini
  pagina-per-pagina. Per i testi a stampa, il percorso tecnico piu prudente e
  prima il PDF diretto pubblico; le immagini restano utili per download puntuali
  o per casi senza PDF. ATK-Pro usa manifest sintetico da immagini pubbliche e,
  quando l'utente richiede solo PDF e non imposta un range di pagine, scarica il
  PDF diretto ufficiale invece di ricostruirlo dalle immagini. La richiesta di
  range obbligatorio per i portali `r_limited` resta attiva, con eccezione
  mirata per BDT `Testi-a-stampa` in modalita solo PDF.
- `beic_digitale` resta un candidato forte per metadata, pubblico dominio e
  valore culturale, ma non ancora per download. I termini sono favorevoli per
  opere in pubblico dominio, immagini scaricabili/riutilizzabili e dati CC0;
  l'infrastruttura pubblica usa Primo VE/Rosetta/Preserver e OAI-PMH
  documentato. I primi test live non hanno pero individuato un endpoint
  ripetibile: su Preserver `IE7400509` la sonda ha trovato solo il logo del
  viewer, mentre sul record Primo `alma9925210904741` non sono emersi manifest,
  PDF o immagini utili. La sonda `verify_beic_technical_probe.py` resta attiva
  per raccogliere nuovi campioni, ma BEIC non entra nel menu finche non emerge
  un endpoint file/manifest stabile con policy item-level chiara.
- `biblioteca_digitale_lombarda` e promossa solo per PDF puntuale pubblico.
  ATK-Pro accetta endpoint REST del tipo
  `https://www.bdl.servizirl.it/bdl/public/rest/srv/item/{id}/pdf`, costruisce
  un manifest sintetico minimale e salva il PDF quando l'utente richiede un
  documento singolo in formato PDF. La policy resta `D_ONLY`: niente record
  `R`, niente immagini e niente sequenze IIIF finche `info.json`, manifest o
  ordinamento pagine non risultano stabili su piu campioni. Molti record
  dichiarano licenze non commerciale/no-derivati, quindi resta necessaria la
  verifica item-level.
- `biblioteca_digitale_siena` e integrata come IIIF diretto prudente. I test
  manuali su BDS hanno mostrato possibili interruzioni dello stream tile:
  ATK-Pro usa quindi download sequenziale con breve pausa e ritenta gli stream
  incompleti senza conservare file parziali.
- `ambrosiana_digitale` resta una sonda importante: dichiara IIIF, ma servono
  campioni diretti e termini item-level prima di qualsiasi integrazione. Per Ambrosiana,
  il controllo 2026-06-07 conferma il valore della pista IIIF: la pagina
  ufficiale parla di accesso libero e standard IIIF, e la letteratura tecnica
  cita Mirador e Cantaloupe. Tuttavia i campioni facilmente reperibili possono
  passare da Comperio o da manifest esterni/aggregatori: la sonda
  `verify_ambrosiana_technical_probe.py` va usata prima di decidere qualunque
  supporto nel menu. Il primo test live su `ambro:catalog:24203` non ha trovato
  manifest, info.json, immagini Cantaloupe o viewer utili: per ora Ambrosiana
  resta in scouting, senza integrazione downloader.
- `rovereto_digital_library` e promosso a supporto tecnico prudente. Il
  controllo 2026-06-08 usa l'API pubblica DSpace-GLAM:
  ATK-Pro deriva l'endpoint REST item da URL entity/API, segue la paginazione
  HAL/JSON di bundle e bitstream e costruisce un manifest sintetico solo dai
  bitstream pubblici classificati come pagine `iiifpdf-*.png`. PDF originale,
  licenza, derivati testuali/OCR e miniature/cover non vengono scaricati come
  pagine; il PDF puo restare come riferimento `seeAlso`. La policy e
  `R_LIMITED`: record completi solo con range esplicito e sempre con verifica
  della licenza item-level.
- Su `biblioteca_digitale_trentina` la capability tecnica resta specifica del
  portale: immagini dirette pubbliche e PDF diretto per testi a stampa, senza
  trasformarla in un adapter generico per tutte le biblioteche digitali.

Secondo mini-scouting biblioteche digitali italiane IIIF (2026-06-08):

- `bub_digitale` entra come candidato forte da sondare. La pagina ufficiale
  della Biblioteca Universitaria di Bologna dichiara accesso libero e gratuito
  per studio/ricerca, standard IIIF e visualizzatore Mirador; le collezioni
  includono anche bollettini parrocchiali bolognesi, fotografie, periodici,
  manoscritti e opere a stampa. La sonda `verify_bub_technical_probe.py` e
  pronta per cercare pagine/record BUB, viewer Mirador, manifest IIIF,
  info.json e immagini candidate. Prossimo passo: eseguirla su item reali e
  verificare licenze item-level prima di qualsiasi supporto nel menu.
  Primo test live sulla landing `https://bub.unibo.it/it/bub-digitale`: utile
  come discovery, ma non come prova di download, perche espone soprattutto
  pagine del portale e immagini Plone `@@images`. La sonda classifica ora tali
  immagini come `plone_page_image`. Il test successivo va fatto su una pagina
  di bollettino/anno con parametro `manifest=`, ad esempio il campione
  Bondanello 1934 emerso dalla ricerca pubblica. Test live mirato sul campione:
  trovato manifest IIIF v2 come `viewer_manifest_parameter` verso
  `https://bub.unibo.it/iiif/2/manifest/bub/bollettiniparrocchiali/_castelmaggiore_-_s_bartolomeo_di_bondanello/jpg/1934.json`.
  `download_manifest` scarica il manifest con codice 200 e rileva 44 canvas.
  Secondo test live su Castenaso 1933:
  `https://bub.unibo.it/iiif/2/manifest/bub/bollettiniparrocchiali/_castenaso_-_s_giovanni_battista/jpg/1933.json`
  scaricato con codice 200 e 32 canvas. Il pattern manifest appare stabile su
  piu bollettini. `bub_digitale` viene promosso a supporto IIIF diretto
  prudente: solo manifest BUB pubblici, referer BUB, policy `R_LIMITED`, range
  esplicito e avviso di verifica licenza item-level.
- `dl_ficlit` entra come candidato Omeka S/IIIF. La pagina ufficiale FICLIT
  indica uso di tecnologia IIIF e Mirador Viewer; puo servire anche a capire se
  esiste un pattern riusabile per altri portali Omeka italiani. La sonda
  `verify_ficlit_technical_probe.py` e pronta per cercare pagine Omeka,
  item/media/API, viewer Mirador, manifest IIIF, info.json e immagini
  candidate. Primo test live 2026-06-09 su item Corbiere `199245`: la sonda
  trova immagine originale e manifest IIIF v2
  `https://dl.ficlit.unibo.it/iiif/2/199245/manifest`; `verify_manifest_url.py`
  lo scarica con codice 200 e rileva 1 canvas. Secondo test live su item
  Camporesi `28429`: stesso pattern immagine originale + manifest
  `https://dl.ficlit.unibo.it/iiif/2/28429/manifest`, codice 200 e 239 canvas.
  Il candidato viene promosso a supporto tecnico prudente con adapter ristretto
  a host FICLIT, referer FICLIT, policy `R_LIMITED`, range esplicito e verifica
  dei termini di riuso item-level. Test app 2026-06-09: il manifest FICLIT e
  corretto, ma il tile service risponde HTTP 500 sui ritagli 256px; ATK-Pro usa
  quindi l'immagine diretta `resource.@id` del canvas, senza tassellare.
- `orientales_unior` entra come candidato IIIF/Mirador con download condizionato
  alla licenza dell'oggetto. La fonte ufficiale cita licenze Creative Commons,
  framework IIIF, Mirador, OCR e scarico metadati; la stessa fonte descrive la
  piattaforma come DSpace, pur richiamando anche l'evoluzione dai progetti
  precedenti. La sonda `verify_orientales_technical_probe.py` riconosce quindi
  sia pattern DSpace (`entities`, REST item, bundle, bitstream, handle e link
  JSON/HAL), sia record Omeka se presenti, viewer Mirador, manifest IIIF,
  info.json, immagini, OCR/testi e metadati candidati; per ATK-Pro la policy
  potra essere solo prudente e item-level.

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
