# Matrice portali esistenti ATK-Pro

Data snapshot: 2026-05-26

Questa matrice fotografa i portali gia presenti nel selettore di ATK-Pro e il
modo in cui il codice li tratta oggi. Le colonne legali sono volutamente
prudenziali: prima di dichiarare un portale "supportato" per nuove evoluzioni
serve una verifica puntuale dei termini ufficiali correnti.

Fonti interne usate:

- `src/main_gui_qt.py`, selettore `PORTALI_GROUPED`;
- `src/manifest_utils.py`, builder e resolver manifest;
- `src/elaborazione.py`, fallback, referer e casi speciali;
- `src/tile_downloader.py`, download tile IIIF e rate-limit specifici.

## Legenda

- Metodo tecnico:
  - `IIIF diretto`: builder URL manifest o manifest gia fornito.
  - `IIIF discovery`: ricerca manifest da pagina/HTML con fallback.
  - `Sintetico`: manifest costruito da endpoint/HTML/servizi non standard.
  - `Diretto immagini`: download immagine senza normale manifest IIIF.
- Rischio manutenzione:
  - `Basso`: schema IIIF/API prevedibile nel codice.
  - `Medio`: regex, fallback o differenze portale da sorvegliare.
  - `Alto`: scraping-like, token, endpoint non standard o brute force.
- Stato legale:
  - `Da verificare`: controllare termini ufficiali prima di estendere.
  - `Solo manuale/link`: non automatizzare senza autorizzazione documentata.

## Matrice

| Chiave | Portale | Area | Metodo tecnico osservato | Rischio manutenzione | Stato legale operativo | Prossimo passo |
|---|---|---|---|---|---|---|
| `antenati` | Antenati (Cultura.gov.it) | Italia | IIIF discovery / manifest DAM | Medio | Consultazione gratuita senza registrazione; riuso immagini non automaticamente aperto | Mantenere come portale primario per ricerca personale/studio, con avviso su pubblicazione/riuso |
| `bnc_roma` | BNC Roma digitale | Italia | Manifest sintetico da pagina item-level | Alto | Consultazione libera/gratuita; materiali sotto diritto e alta risoluzione/pubblicazione hanno limiti | Mantenere solo per risorse libere pubbliche; non automatizzare accessi OpenAthens o materiali riservati |
| `bncf_teca` | BNCF Teca (Firenze) | Italia | Tentativo IIIF standard + manifest sintetico + fallback diretto immagini | Alto | Riproduzioni soggette ad autorizzazione/citazione; pubblicazione e commerciale richiedono percorso dedicato | Limitare a consultazione puntuale; documentare chiaramente citazione e divieto di ulteriore riproduzione |
| `museogalileo` | Museo Galileo Digiteca | Italia | Manifest sintetico da TecaService, token GetObject | Alto | Uso privato/non commerciale e autorizzazione per riproduzione materiale fotografico | Evitare estensioni finche non esiste endpoint stabile/documentato; usare solo accesso pubblico puntuale |
| `internetculturale_estense` | Internet Culturale / Estense / ICCU | Italia | Manifest sintetico da magparser | Medio-Alto | File web liberi e gratuiti non commerciali, CC BY-NC-SA; metadati CC0 | Consolidabile con citazione, no commerciale e rispetto dei fornitori; preferire endpoint ufficiali/IIIF se disponibili |
| `brixiana` | Brixiana / Jarvis | Italia | Alias Memooria/Jarvis IIIF | Medio | Accesso gratuito, ma alcune funzionalita sono legate a credenziali MLOL/Brixiana | Supportare solo risorse pubbliche/no-login e verificare condizioni del singolo ente |
| `memooria` | Memooria/Jarvis | Italia | IIIF da meta/iiif/{guid}/manifest | Medio | Piattaforma IIIF/API; diritti e accessi dipendono dall'ente che pubblica la collezione | Usare come capability tecnica, non come portale unico: richiedere verifica per ogni istanza |
| `vatlib` | DigiVatLib | Italia / Vaticano | IIIF diretto da view/mss/iiif | Basso-Medio | Solo studio/personale; riproduzione o pubblicazione richiede autorizzazione BAV | Mantenere con avviso forte e senza presentarlo come fonte liberamente riusabile |
| `findbuch` | Kirchenbuecher Suedtirol / findbuch.net | Alto Adige / Sudtirol | Manifest sintetico da HTML + gtpc.php | Alto | Da verificare; evitare se accesso/account/limitazioni | Verificare termini e valutare se mantenere solo con range puntuale |
| `matricula` | Matricula Online | Europa centrale | Manifest sintetico da viewer HTML e hosted-images | Alto | Da verificare | Verificare termini Matricula e ridurre dipendenza da HTML viewer |
| `gallica` | Gallica (BnF) | Francia | IIIF diretto da ARK + fallback Playwright per TLS/fingerprint | Medio | API IIIF aperta salvo abuso; riuso non commerciale libero con citazione, commerciale soggetto a licenza | Consolidare con citazione obbligatoria, rispetto del non commerciale e cautela sui partner |
| `heidelberg` | Heidelberg UB | Germania | IIIF diretto + rate-limit sequenziale | Basso-Medio | Licenza da verificare per volume: Public Domain, CC-BY-SA 4.0 o In Copyright | Consolidare con credito fonte e controllo licenza per singolo volume |
| `bodleian` | Bodleian Libraries Oxford | Regno Unito | IIIF diretto da object UUID | Basso | In prevalenza CC-BY-NC 4.0 con attribuzione; verificare restrizioni del singolo item | Consolidare IIIF con avviso non commerciale, attribuzione e niente re-hosting sistematico immagini |
| `e_rara` | e-rara | Svizzera | IIIF builder dedicato | Basso-Medio | Licenza dichiarata per documento: Public Domain Mark o CC BY-SA 4.0 | Consolidare con controllo licenza per documento e citazione della fonte |
| `e_codices` | e-codices (Unifr) | Svizzera | IIIF builder dedicato | Basso-Medio | Uso non commerciale libero con citazione; eccezioni Public Domain/Creative Commons per item marcati | Consolidare con citazione obbligatoria e avviso per usi commerciali/pubblicazioni |
| `e_manuscripta` | e-manuscripta | Svizzera | IIIF builder dedicato | Basso-Medio | Licenza dichiarata per documento; alcuni contenuti hanno diritti limitati di terzi | Consolidare con controllo licenza per documento; evitare copia sistematica/re-hosting |
| `internet_archive` | Internet Archive | Internazionale | Manifest sintetico da metadata/files/BookReaderImages | Medio-Alto | Da verificare per item/licenza | Preferire item pubblici con licenza chiara |
| `europeana` | Europeana IIIF | Internazionale | IIIF diretto da provider/record id | Basso-Medio | Diritti da leggere per record/provider; API soggetta a chiave, termini e limiti | Usare solo record con IIIF disponibile, rights statement chiaro e attribution ai provider |
| `manifest_diretto` | Manifest diretto (URL gia noto) | Avanzato | URL manifest fornito dall'utente | Variabile | Responsabilita utente + verifica termini origine | Mantenere con avviso/criteri chiari |

## Lettura operativa

Priorita tecnica dopo il primo controllo fonti ufficiali:

1. Portali con IIIF diretto e condizioni documentabili per item/volume:
   `bodleian`, `heidelberg`, `europeana`, `e_rara`, `e_codices`,
   `e_manuscripta`, `manifest_diretto`.
2. Portali tecnicamente IIIF ma con avviso legale piu forte: `vatlib`.
3. Portali con discovery/fallback ma valore alto: `antenati`, `gallica`,
   `memooria`, `brixiana`.
4. Portali sintetici o endpoint non standard da trattare con cautela:
   `bnc_roma`, `bncf_teca`, `museogalileo`, `internetculturale_estense`,
   `internet_archive`.
5. Portali con scraping-like/viewer speciali o rischio accesso/termini da
   chiarire prima di ogni estensione: `findbuch`, `matricula`.

## Regole prima di aggiungere nuovi portali

- Non aggiungere portali commerciali, chiusi, con login, abbonamento o paywall.
- Non automatizzare accessi autenticati o barriere tecniche.
- Preferire IIIF/API ufficiali e documentate.
- Limitare il supporto a documento, registro o range scelto dall'utente.
- Registrare per ogni nuovo portale: fonte tecnica, termini ufficiali, metodo,
  rischio manutenzione, test offline disponibili e decisione go/no-go.

## Prossima verifica richiesta

Per trasformare questa matrice in roadmap di integrazione serve una seconda
fase, con consultazione delle fonti ufficiali correnti:

1. pagina note legali/terms del portale;
2. documentazione IIIF/API;
3. eventuali limiti di download, rate limit, licenze e riuso;
4. decisione finale: integrare, consolidare, solo link esterno, non supportare.

## Fonti ufficiali consultate - batch 1

Data verifica: 2026-05-26.

Questa sezione non e una consulenza legale: registra solo le fonti ufficiali
consultate e la conseguente prudenza operativa per ATK-Pro.

| Chiave | Fonti ufficiali | Indicazioni operative emerse | Decisione provvisoria |
|---|---|---|---|
| `vatlib` | DigiVatLib item page: `https://digi.vatlib.it/view/MSS_Vat.lat.4330/0001`; BAV photographic reproductions: `https://www.vaticanlibrary.va/home.php?ling=eng&pag=riproduzioni_fotografiche` | La pagina DigiVatLib indica uso libero solo personale/studio e richiesta diritti per usi stampati o online; il footer dichiara contenuti protetti e riproduzione subordinata ad autorizzazione BAV. | Mantenere come accesso tecnico IIIF per studio, con avviso forte; non proporre come fonte liberamente riusabile. |
| `bodleian` | Terms: `https://digital.bodleian.ox.ac.uk/terms/`; IIIF API: `https://digital.bodleian.ox.ac.uk/developer/iiif/` | Digital Bodleian espone API IIIF documentata; i termini indicano in prevalenza CC-BY-NC 4.0, verifica del singolo item, attribuzione e preferenza a non scaricare/re-hostare immagini in modo significativo. | Buon candidato per consolidamento tecnico, con attribution, uso non commerciale e no bulk/re-host. |
| `heidelberg` | Terms: `https://www.ub.uni-heidelberg.de/Englisch/helios/digi/nutzung/` | UB Heidelberg non applica fee d'uso generali, ma ogni volume puo essere Public Domain, CC-BY-SA 4.0 o In Copyright; richiede credito immagine. | Consolidabile con controllo licenza sul volume e mantenimento del rate-limit sequenziale. |
| `e_rara` | Terms: `https://www.e-rara.ch/wiki/termsOfUse?lang=en`; interfaces/IIIF: `https://www.e-rara.ch/wiki/apiinfo` | e-rara documenta interfacce OAI/PDF/IIIF e licenze per documento: Public Domain Mark o CC BY-SA 4.0; richiede citazione della fonte e responsabilizza l'utente sul copyright. | Consolidabile per download puntuale, con lettura licenza per documento e citazione. |
| `e_codices` | Terms: `https://www.e-codices.unifr.ch/en/about/terms`; web application/IIIF: `https://www.e-codices.unifr.ch/en/about/webapplication` | e-codices documenta IIIF Image/Presentation API; l'uso non commerciale e libero con citazione, mentre usi commerciali o ripubblicazioni richiedono permesso salvo item marcati Public Domain o Creative Commons. | Consolidabile con avvisi su citazione, uso non commerciale e verifica item. |
| `e_manuscripta` | Terms: `https://www.e-manuscripta.ch/wiki/termsOfUse?lang=en`; interfaces/IIIF: `https://www.e-manuscripta.ch/wiki/apiinfo` | e-manuscripta documenta OAI/PDF/IIIF; le licenze sono per documento e includono Public Domain, CC BY-SA 4.0 e diritti limitati di terzi; la copia sistematica su altri server richiede consenso. | Consolidabile per uso puntuale con controllo licenza; evitare automazioni di copia sistematica. |
| `europeana` | Terms: `https://www.europeana.eu/en/rights/terms-of-use`; APIs: `https://api.europeana.eu/en`; IIIF docs: `https://europeana.atlassian.net/wiki/spaces/EF/pages/1627914244/Europeana%27s%2BIIIF%2BAPIs` | Europeana distingue metadata CC0 e oggetti digitali soggetti al rights statement del record/provider; le API richiedono chiave, possono essere limitate e rimandano alle condizioni associate al record. | Consolidabile solo record-by-record, con rights statement chiaro e rispetto dei limiti API. |

## Fonti ufficiali consultate - batch 2

Data verifica: 2026-05-26.

| Chiave | Fonti ufficiali | Indicazioni operative emerse | Decisione provvisoria |
|---|---|---|---|
| `antenati` | Scheda ICAR: `https://icar.cultura.gov.it/sistemi-e-portali/antenati`; Portale Antenati: `https://antenati.cultura.gov.it/`; buone pratiche Digital Library MiC: `https://digitallibrary.cultura.gov.it/buone-pratiche/` | ICAR descrive Antenati come accesso gratuito e senza registrazione ai contenuti disponibili. Non emerge pero una licenza aperta esplicita sulle immagini; le linee MiC distinguono l'accesso libero dal vero open access, che richiede licenze aperte e riuso. | Consolidabile per consultazione e ricerca personale/studio; per pubblicazione, export massivo o riuso pubblico serve avviso e verifica puntuale. |
| `gallica` | API IIIF BnF: `https://api.bnf.fr/fr/api-iiif-de-recuperation-des-images-de-gallica`; data.gouv API Gallica IIIF: `https://www.data.gouv.fr/dataservices/api-gallica-iiif/`; conditions Gallica: `https://gallica.bnf.fr/accueil/fr/html/conditions-dutilisation-de-gallica?mode=tablet` | BnF documenta Image e Presentation API IIIF. L'accesso API e aperto salvo uso abusivo; il riuso non commerciale dei contenuti e libero con citazione, mentre il riuso commerciale richiede licenza e i partner possono avere condizioni specifiche. | Consolidabile con citazione obbligatoria, limite non commerciale e controllo sui documenti partner/sotto diritti. |
| `brixiana` | Pagina Comune di Brescia: `https://www.comune.brescia.it/it/servizi/piattaforma-brixiana`; condizioni di servizio linkate dalla pagina comunale | Il Comune descrive Brixiana come piattaforma gratuita per ricerca/studio, accessibile anche senza registrazione, ma segnala credenziali MLOL/Brixiana e funzionalita disponibili solo dopo login. | Mantenere solo per risorse pubbliche raggiungibili senza login; non automatizzare funzioni o contenuti autenticati. |
| `memooria` | Memooria: `https://www.memooria.org/`; OpenJarvis: `https://www.memooria.org/servizi-openjarvis/`; IIIF Search Engine: `https://iiifsearch.jarvis.memooria.org/` | OpenJarvis e presentato come DAM open source compatibile con IIIF Image/Presentation API e WebAPI, ma l'architettura puo includere gateway autenticativo, ruoli, watermark e policy dell'ente pubblicatore. | Trattare Memooria/Jarvis come famiglia tecnica: ogni istanza va verificata per ente, accesso pubblico e licenza del contenuto. |

## Fonti ufficiali consultate - batch 3

Data verifica: 2026-05-26.

| Chiave | Fonti ufficiali | Indicazioni operative emerse | Decisione provvisoria |
|---|---|---|---|
| `bnc_roma` | Biblioteca Digitale BNCR: `https://www.bncrm.beniculturali.it/it/32/biblioteca-digitale?language=it` | La consultazione delle immagini libere e gratuita, ma alcuni materiali sotto diritto richiedono autorizzazione o accesso da postazioni interne/OpenAthens; alta risoluzione, fini commerciali e pubblicazione passano dall'Ufficio Riproduzioni. | Mantenere solo contenuti pubblici/no-login; escludere accessi autenticati, materiali sotto diritto e download ad alta risoluzione. |
| `bncf_teca` | Riproduzioni BNCF: `https://bncf.cultura.gov.it/servizi/riproduzioni/`; regolamento/tariffari linkati dalla pagina | La riproduzione per studio e pubblicazione e soggetta a regole, citazione obbligatoria, consegna copia pubblicazione e, per certi usi, autorizzazione/canoni. | Non estendere oltre consultazione puntuale; aggiungere avviso su citazione, pubblicazione e ulteriore riproduzione. |
| `museogalileo` | Biblioteca digitale: `https://www2.museogalileo.it/it/biblioteca-e-istituto-di-ricerca/biblioteca-digitale/catalogo-biblioteca-digitale.html`; riproduzioni fotografiche: `https://www2.museogalileo.it/it/16-visita/876-riprese-filmate-e-riproduzioni-fotografiche.html` | La biblioteca digitale e descritta come sistema di consultazione; il Museo richiede autorizzazione per riproduzioni professionali e materiale fotografico, e limita foto/video dei visitatori a uso privato non commerciale. | Mantenere con rischio alto e senza nuove automazioni finche non e documentato un endpoint pubblico stabile. |
| `internetculturale_estense` | Termini Internet Culturale: `https://www.internetculturale.it/it/15/termini-d-uso`; pagina EDL Digital Library MiC: `https://digitallibrary.cultura.gov.it/progetti/estense-digital-library-edl/`; nota IIIF Gallerie Estensi: `https://gallerie-estensi.beniculturali.it/blog/la-piattaforma-iiif-di-estense-digital-library/` | Internet Culturale dichiara contenuti digitali in risoluzione web liberi/gratuiti non commerciali con licenza CC BY-NC-SA; metadati CC0. EDL e descritta come piattaforma interoperabile/IIIF. | Buon candidato da consolidare solo su accessi pubblici e non commerciali, citando portale/ente e preferendo IIIF ufficiale quando disponibile. |
