# Valutazione portali ATK-Pro

Data snapshot: 2026-05-25

Questa nota raccoglie i criteri legali e tecnici da usare prima di proporre o
integrare nuovi portali in ATK-Pro. Non sostituisce una valutazione legale
professionale: serve come regola interna di progetto e come promemoria operativo.

## Paletti legali da mantenere

Fonte interna principale: `assets/it/testuali/disclaimer_legale_ATK-Pro.txt`.

Il disclaimer stabilisce che:

- la finalita primaria resta il supporto alla consultazione del Portale Antenati;
- l'accesso a risorse di terzi e accessorio e dipende dalla loro accessibilita
  tecnica e giuridica;
- l'utente deve rispettare note legali, licenze, copyright, condizioni di
  accesso e regole di riutilizzo del singolo ente o fornitore;
- ATK-Pro non e destinato a estrazione automatizzata, raccolta massiva,
  download sistematici, aggiramento di accessi autenticati, abbonamenti, pass
  temporanei, paywall, limitazioni tecniche, misure di sicurezza o divieti
  contrattuali;
- i portali genealogici commerciali o riservati ad accesso con account non
  rientrano, salvo diversa indicazione espressa e documentata, tra gli usi
  supportati del software.

Regola pratica: un portale chiuso, commerciale, con login obbligatorio,
abbonamento, paywall o divieti tecnici/contrattuali non va integrato come
download diretto. Al massimo puo essere trattato come link esterno/manuale,
senza automazione di accesso o scaricamento.

## Nota di indirizzo sugli accessi autenticati

Riflessione consolidata il 2026-07-27: la disponibilita, da parte dell'utente,
di credenziali valide, account o abbonamento non rende di per se un portale
idoneo all'integrazione diretta. Una simile integrazione potrebbe essere
tecnicamente realizzabile per singoli portali, soprattutto in presenza di API
ufficiali e autenticazione OAuth o tramite token, ma richiederebbe anche:

- un caveau sicuro e multipiattaforma, distinto dall'attuale gestione CSV delle
  chiavi dei provider;
- gestione del ciclo di vita di token e sessioni, revoca, scadenza, logout e
  protezione dei segreti;
- verifica specifica dei termini d'uso, dei diritti dell'account e delle
  possibilita effettive di accesso o download offerte dall'API;
- test, documentazione e manutenzione continuativa per ciascun portale.

Nel perimetro attuale di ATK-Pro, tale costo e rischio risultano normalmente
sproporzionati rispetto al beneficio. La scelta di escludere login, account,
abbonamenti e paywall resta quindi confermata anche da una valutazione di
sostenibilita tecnica e manutentiva, oltre che dai paletti legali gia indicati.
Per questi portali si preferiscono apertura esterna, autenticazione e download
manuali da parte dell'utente, seguiti dall'eventuale elaborazione locale dei
file ottenuti legittimamente.

Una futura eccezione potra essere rivalutata solo per un portale ad alto valore
che offra un'API ufficiale stabile, autorizzi esplicitamente applicazioni di
terze parti, esponga davvero le risorse utili ad ATK-Pro e presenti un rapporto
costo/beneficio documentato e favorevole. Non sono comunque ammissibili
aggiramenti di CAPTCHA, MFA, DRM, anti-bot, paywall o divieti contrattuali.

## Criteri go/no-go per nuovi portali

Integrare solo se sono soddisfatti tutti i requisiti minimi:

- accesso pubblico o comunque legittimamente accessibile senza aggiramenti;
- API, IIIF manifest, endpoint documentati o struttura tecnica stabile e
  consentita;
- termini d'uso compatibili con consultazione puntuale e uso locale;
- nessun login, abbonamento, paywall o barriera tecnica da superare;
- niente raccolta massiva: supporto limitato a documento, registro o range
  selezionato dall'utente;
- possibilita di impostare User-Agent, Referer, rate limit e fallback in modo
  rispettoso del servizio.

Classificazione consigliata:

- A: integrare presto - pubblico, IIIF/API, termini compatibili, alto valore;
- B: integrare dopo verifica - promettente, ma richiede controllo tecnico o
  legale puntuale;
- C: solo apertura esterna - utile, ma login/permessi/termini non permettono
  automazione sicura;
- D: non supportare - commerciale/chiuso/paywall/anti-bot/divieto esplicito.

## Stato tecnico attuale

Punti principali osservati nel codice:

- il portale attivo e scelto in `src/main_gui_qt.py` (`cambia_portale`) e
  salvato in configurazione come `portale_attivo`;
- il valore viene passato a `ElaborazioneWorker` e poi a `Elaborazione`;
- `src/elaborazione.py` contiene la logica di orchestration, fetch manifest,
  fallback Playwright, manifest sintetici e gestione speciale di alcuni portali;
- `src/manifest_utils.py` contiene builder diretti, builder sintetici e
  `resolve_manifest_url`;
- `src/tile_downloader.py` gestisce i tile IIIF e alcune differenze tra portali
  come Gallica/Heidelberg;
- il supporto portali e funzionale ma ancora molto accoppiato alla pipeline
  principale: prima di aggiungere molti portali conviene valutare una tabella
  esplicita di adapter/capability.

Portali gia presenti nel selettore:

- area italiana: Antenati, BNC Roma digitale, BNCF Teca, Museo Galileo
  Digiteca, Internet Culturale/Estense, Brixiana, Memooria/Jarvis, DigiVatLib;
- area italofona/centro-europea: Kirchenbuecher Suedtirol/findbuch.net,
  Matricula Online;
- area internazionale: Gallica, Heidelberg UB, Bodleian Libraries Oxford,
  e-rara, e-codices, e-manuscripta, Internet Archive, Europeana IIIF;
- avanzato: manifest diretto.

## Stato documentale dopo la matrice

Le verifiche preliminari previste sono state completate in documenti separati:

- audit post-localizzazione:
  `docs_generali/audit_post_localizzazione_ATK-Pro.md`;
- matrice dei portali gia presenti:
  `docs_generali/matrice_portali_esistenti_ATK-Pro.md`;
- roadmap operativa:
  `docs_generali/roadmap_portali_ATK-Pro.md`;
- roadmap test v3:
  `tests/roadmap_tests.md`.

Debiti residui:

- la logica specifica dei portali vive ancora in piu punti e va ridotta con una
  registry/adapter progressiva;
- i portali con manifest sintetici o scraping-like devono restare congelati o
  limitati finche non esiste una fonte tecnica piu stabile;
- prima di una release pubblica conviene inventariare file temporanei, log e
  script diagnostici rimasti nella root.

## Prossima sequenza proposta

1. Consolidare i portali in priorita 1 della roadmap con avvisi e fixture
   offline.
2. Introdurre una tabella interna di capability per portale.
3. Proteggere con test i builder diretti e i casi piu stabili.
4. Solo dopo valutare nuovi portali pubblici/istituzionali con IIIF/API e
   termini chiari.
