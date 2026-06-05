# Matrice portali candidati ATK-Pro

Data snapshot: 2026-05-26

Questa matrice apre lo scouting dei portali non ancora integrati in ATK-Pro.
Non e una promessa di integrazione: ogni riga fotografa solo un primo controllo
su fonti ufficiali o istituzionali. Prima di trasformare un candidato in codice
servono verifica tecnica, verifica dei termini correnti, fixture offline e una
decisione esplicita go/no-go.

## Criteri rapidi

- `A`: candidato tecnico forte, da valutare presto.
- `B`: promettente, ma richiede verifica API/termini o test tecnico.
- `C`: utile come fonte o link, ma non ancora adatto a download diretto.
- `D`: non integrare direttamente.

Regola stabile: portali commerciali, login obbligatorio, paywall,
abbonamento, anti-bot o divieti di automazione restano fuori dal download
diretto. Possono comparire solo come riferimento esterno/manuale.

## Batch 1 - Italia, italofonia, diaspora e fonti istituzionali principali

| Chiave candidata | Portale | Area strategica | Fonte ufficiale consultata | Rilevanza genealogica | Prima lettura tecnica/legale | Decisione provvisoria |
|---|---|---|---|---|---|---|
| `archivi_nazionali` | Portale Archivi Nazionali | Italia | `https://www.territori.san.beniculturali.it/sistemi-e-portali/archivi-nazionali/portale-archivi-nazionali` | Molto alta: ricerca trasversale su fondi archivistici, Antenati e Partigiani d'Italia | Portale in evoluzione: promette dati descrittivi e risorse digitali del SIA; attendere stabilita pubblica e documentazione tecnica/API | B - monitorare e rivalutare appena il portale e stabile |
| `sias` | Sistema Informativo degli Archivi di Stato | Italia | `https://archivi.cultura.gov.it/strumenti-di-ricerca-online/sistema-informativo-degli-archivi-di-stato-sias`; `https://icar.cultura.gov.it/sistemi-e-portali/sistemi-nazionali-di-descrizione-archivistica/sistema-informativo-degli-archivi-di-stato-sias-1` | Alta: descrizioni di Archivi di Stato, inventari e talvolta immagini | Fonte piu descrittiva che downloader; utile per discovery, non per acquisizione massiva immagini | C - link/discovery prima di ogni download |
| `san_risorse_digitali` | SAN - documenti digitali / open data | Italia | `https://www.san.beniculturali.it/web/san/risorse-per-le-ricerche`; `https://cultura.gov.it/open-data-e-linked-data` | Alta: risorse digitali e metadati archivistici nazionali | Esistono metadati/OAI e risorse collegate a teche o sistemi aderenti; licenze e immagini dipendono dal sistema sorgente | B - valutare metadati/OAI, non scaricare immagini senza fonte specifica |
| `siusa` | SIUSA | Italia | `https://siusa-archivi.cultura.gov.it/cgi-bin/siusa/pagina.pl?RicLin=en&TipoPag=informazioni` | Media-alta: censimento archivi vigilati, contesto fondi e soggetti conservatori | Fonte descrittiva; non appare come portale primario di download immagini | C - ottimo supporto ricerca, non integrazione downloader |
| `biblioteca_digitale_siena` | Biblioteca Digitale Siena | Italia | `https://bds.comune.siena.it/`; `https://bds.comune.siena.it/it/169/` | Media-alta: manoscritti, periodici, disegni, archivi e carteggi senesi/toscani | Piattaforma pubblica IIIF; termini ufficiali consentono JPG web-resolution per uso personale, studio e ricerca con citazione, vietando uso commerciale e trasformazioni non autorizzate; smoke live 2026-06-05 passato su manifest da 106 canvas | A - builder viewer->manifest aggiunto e verificato live |
| `museu_imigracao_sp` | Museu da Imigracao do Estado de Sao Paulo - Acervo Digital | Brasile / diaspora italiana | `https://museudaimigracao.org.br/acervo/sobre-acervo`; `https://www.museudaimigracao.org.br/acervo/passageiros`; `https://museudaimigracao.org.br/acervo-e-pesquisa/acervo` | Molto alta per immigrati italiani in Brasile/Sao Paulo | Acervo digitale pubblico con piu di 250 mila immagini, registri di matricola, liste di bordo, carte di chiamata, richieste SACOP, iconografie, cartografie e giornali; le fonti ufficiali indicano uso/download non commerciale, ma il percorso tecnico appare basato su ricerca web e PDF/immagini pubbliche, non su IIIF/API documentata | B - candidato forte, ma non integrare finche non viene validata una capability `pdf_direct`/download diretto pubblica e testabile |
| `apesp_digitalizados` | Arquivo Publico do Estado de Sao Paulo - Acervo digitalizado | Brasile / diaspora italiana | `https://web.arquivoestado.sp.gov.br/web/acervo/digitalizados`; `https://www.arquivoestado.sp.gov.br/web/digitalizado/textual/nucleos_coloniais`; `https://web.arquivoestado.sp.gov.br/web/acervo/atendimento/reproducao_documentos`; `https://web.arquivoestado.sp.gov.br/web/acervo/solicitacao_certidoes/imigracao` | Molto alta: Hospedaria, Porto di Santos, nuclei coloniali, documenti di immigrazione e colonizzazione | Fonte ufficiale molto rilevante, ma l'acervo digitalizzato rimanda a registrazione/login e la pagina dei nuclei coloniali contiene avviso di servizio con login; la riproduzione e soggetta a credito, termini di responsabilita e valutazioni su diritto/autorizzazione. Nessun endpoint no-login/API/IIIF stabile verificato nel primo controllo | C - link/manuale e discovery; download diretto escluso finche non emerge una risorsa pubblica no-login con licenza e tecnica stabili |
| `arquivo_nacional_br_sian` | Arquivo Nacional do Brasil / SIAN | Brasile / diaspora italiana | `https://www.gov.br/arquivonacional/pt-br/canais_atendimento/imprensa/copy_of_noticias/a-imigracao-italiana-e-o-acervo-do-an`; `https://www.gov.br/arquivonacional/pt-br/canais_atendimento/imprensa/copy_of_noticias/quer-pesquisar-no-arquivo-nacional-acesse-o-sian`; `https://www.gov.br/arquivonacional/pt-br/servicos/acervos/copy_of_acervos-mais-consultados/entrada-de-estrangeiros`; `https://www.gov.br/arquivonacional/pt-br/servicos/bases-de-dados/bases` | Alta: ingresso di stranieri, vapori, acervo nazionale, Porto di Rio de Janeiro e Porto di Santos | SIAN e molto rilevante e offre documenti digitalizzati senza costo, ma le fonti ufficiali richiedono cadastro/login; la pagina SIAN espone anche controllo anti-spam/umano. La base separata Entrada de Estrangeiros - Porto do Rio de Janeiro e utile come ricerca nominale/dichiarazione, ma non e ancora un endpoint immagini/API verificato | C - link/manuale e discovery; non integrare download diretto SIAN per login/challenge. Rivalutare separatamente la base Rio solo se emerge un accesso pubblico documentato e testabile |
| `agn_argentina_inmigrantes` | Archivo General de la Nacion Argentina - buscador inmigrantes | Argentina / diaspora italiana | `https://www.argentina.gob.ar/interior/archivo-general-de-la-nacion`; `https://www.argentina.gob.ar/node/478702` | Molto alta: ingressi al porto di Buenos Aires 1882/1883-1937 | Buscador ufficiale; prima verificare se esistono API o endpoint consentiti, altrimenti solo link esterno | B/C - candidato informativo, non downloader finche non documentato |
| `cemla_buscador` | CEMLA buscador inmigrantes | Argentina / diaspora italiana | `https://cemla.com/`; `https://cemla.com/faqs/` | Alta: arrivi di immigrati in Argentina | Fonte privata/non governativa ma molto usata; non emergono API/termini per automazione | C - solo link/manuale, no download diretto |
| `agn_colombia_dataviva` | Archivo General de la Nacion Colombia - DataViva | Colombia / diaspora italiana | `https://www.archivogeneral.gov.co/agn/home/`; `https://dataviva.archivogeneral.gov.co/`; `https://www.datos.gov.co/en/en/Culture/DATAVIVA/r5h9-7h58` | Media-alta: documenti storici digitalizzati, possibili fondi migrazione | Fonte ufficiale con molte immagini digitalizzate; verificare API, download consentito, diritti e stabilita viewer | B - candidato tecnico da approfondire |
| `nara_catalog` | National Archives Catalog / NARA API | Stati Uniti / diaspora italiana | `https://www.archives.gov/research/catalog/help/api`; `https://www.archives.gov/research/immigration/overview` | Alta: naturalizzazioni, immigrazione, passenger records, A-files | API ufficiale per dati pubblici del Catalog; disponibilita immagini e diritti variano per record | A/B - candidato forte per metadata/record pubblici |
| `loc_chronicling_america` | Library of Congress - Chronicling America / loc.gov API | Stati Uniti / contesto diaspora | `https://www.loc.gov/apis/additional-apis/chronicling-america-api/` | Media: giornali storici utili per contesto familiare, non atti vitali | API ufficiale; utile come modulo di ricerca contestuale piu che downloader genealogico primario | B - valutare dopo fonti archivistiche |
| `naa_recordsearch` | National Archives of Australia - RecordSearch passenger arrivals | Australia / diaspora italiana | `https://www.naa.gov.au/explore-collection/immigration-and-citizenship/passenger-arrival-records` | Alta: arrivi passeggeri 1898-1972, dati migratori | Fonte ufficiale e molto rilevante; API non confermata, diritti/download da verificare | B/C - candidato prioritario, inizialmente link assistito |
| `papers_past_digitalnz` | Papers Past / DigitalNZ API | Nuova Zelanda / diaspora italiana | `https://natlib.govt.nz/about-us/open-data/papers-past-metadata/papers-past-data-using-the-digitalnz-api`; `https://paperspast.natlib.govt.nz/help/using-papers-past-material` | Media: giornali e avvisi utili per tracce migratorie e familiari | API metadata ufficiale via DigitalNZ; immagini/testi e copyright da verificare per item | B - candidato per ricerca contestuale |
| `francearchives` | FranceArchives open data | Francia / diaspora italiana | `https://francearchives.gouv.fr/fr/open_data` | Alta per ricerche in Francia e migrazioni confinanti | Dati aperti e aggregazione di inventari; immagini e archivi dipartimentali dipendono dai provider | B - ottimo per discovery, download solo per provider verificati |
| `belgium_state_archives` | State Archives of Belgium / AGATHA | Belgio / diaspora italiana | `https://archives.brussels.be/genealogy`; `https://news.belgium.be/fr/registres-paroissiaux-et-de-letat-civil-consultables-en-ligne-gratuitement` | Alta: stato civile e registri parrocchiali | Consultazione gratuita ma storicamente richiede account/login per archivi online; non automatizzare accessi autenticati | C - link/manuale, no integrazione diretta se login necessario |
| `deutsche_digitale_bibliothek` | Deutsche Digitale Bibliothek / DDB API | Germania / diaspora italiana | `https://www.deutsche-digitale-bibliothek.de/content/api-nutzungsbedingungen?lang=en`; `https://labs.deutsche-digitale-bibliothek.de/app/ddbapi/` | Media-alta: aggregatore culturale/archivistico tedesco | API ufficiale ma richiede API key; diritti e contenuti digitali dipendono dai provider | B/C - metadata possibile, immagini solo item-by-item |
| `austrian_state_archives_ais` | Oesterreichisches Staatsarchiv - AIS | Austria / area asburgica | `https://www.oesta.gv.at/benutzung/Recherche-zu-Hause/recherche/bestande-ais.html`; `https://www.statearchives.gv.at/user-information/holdings.html` | Alta per Lombardo-Veneto, Trentino-Alto Adige, Friuli Venezia Giulia e fonti militari/asburgiche | Sistema ufficiale di ricerca; utile per discovery e ordinazioni, non ancora candidato downloader | C - link/discovery assistito |
| `anno_onb` | ANNO - AustriaN Newspapers Online | Austria / area asburgica | `https://dbis.ur.de/detail.php?bib_id=FUH&lang=en&titel_id=2012`; `https://www.bundeskanzleramt.gv.at/en/services/federal-administrative-library/databases/general-access-databases.html` | Media: giornali storici per contesto migratorio, militare e civile | Fonte pubblica importante; API ufficiale non confermata nel primo passaggio, evitare scraping massivo | C/B - rivalutare se emerge API stabile o download consentito |

## Lettura del batch 1

Prime piste da approfondire tecnicamente:

1. `nara_catalog`, per API ufficiale e rilevanza su immigrazione/naturalizzazioni.
2. `museu_imigracao_sp` e `apesp_digitalizados`, per altissimo valore sulla
   diaspora italiana in Brasile.
3. `agn_colombia_dataviva`, per volume di immagini digitali e accesso pubblico
   dichiarato.
4. `francearchives` e `papers_past_digitalnz`, per API/open data e utilita di
   discovery/contesto.
5. `archivi_nazionali`, da monitorare perche potrebbe diventare centrale per
   l'area italiana.

## Shortlist operativa provvisoria

Questa shortlist ordina il lavoro senza derogare alla priorita italiana e
italofona. I portali di diaspora entrano in testa solo quando sono strettamente
legati alla ricerca genealogica italiana e hanno una base pubblica o
istituzionale verificabile.

### Blocco A - Diaspora italiana ad alto valore

- `museu_imigracao_sp`: valore genealogico molto alto per la diaspora italiana
  in Brasile. Le pagine ufficiali descrivono accesso pubblico, download
  gratuito e uso non commerciale dell'acervo digitale; la tecnica, pero, non e
  IIIF/API documentata. Prima di integrarlo serve una capability separata e
  prudente per PDF/immagini dirette pubbliche, con policy `D_ONLY` o al massimo
  `R_LIMITED` su range esplicito, fixture offline e smoke live su un esempio
  istituzionale stabile. In assenza di questo passaggio resta link assistito.
- `apesp_digitalizados`: fonte molto importante per Hospedaria, Porto di
  Santos, nuclei coloniali e documentazione di immigrazione. Il primo controllo
  conferma pero una barriera operativa: l'acervo digitalizzato rimanda a
  registrazione/login e le regole di riproduzione richiedono credito,
  responsabilita dell'utente e attenzione ai diritti. Mantenerlo come link
  assistito/discovery; non aggiungere download diretto senza un campione
  pubblico no-login, licenza compatibile e endpoint stabile.
- `arquivo_nacional_br_sian`: SIAN e strategicamente rilevante per liste di
  ingresso, porti, vapori e acervo federale, ma richiede cadastro/login e
  presenta controllo anti-spam/umano. Tenerlo fuori dal download diretto e
  usarlo come link/discovery. La base separata Entrada de Estrangeiros - Porto
  do Rio de Janeiro puo essere rivalutata come integrazione informativa o
  metadata solo con endpoint pubblico, no-login e documentabile.

### Blocco B - API ufficiali e metadati stabili

- `nara_catalog`: primo candidato tecnico per un prototipo metadata/discovery,
  perche dispone di API ufficiale e documentazione pubblica.
- `francearchives`: candidato forte per discovery archivistica; download di
  immagini solo quando il provider sorgente e verificato.
- `papers_past_digitalnz`: utile per ricerca contestuale su stampa storica, da
  trattare come integrazione metadata/search prima di qualsiasi download.

### Blocco C - Italia e fonti istituzionali nazionali

- `archivi_nazionali`: monitorare lo sviluppo del portale perche potrebbe
  diventare l'asse pubblico piu importante per l'area italiana.
- `biblioteca_digitale_siena`: candidato IIIF italiano compatibile con
  risoluzione manifest da URL viewer; smoke live passato su manifest da 106
  canvas. Prima della RC restano fixture offline e test UI/manuale di download
  con range esplicito.
- `san_risorse_digitali`, `sias`, `siusa`: considerarli prima come discovery e
  orientamento archivistico, non come downloader immagini.

### Blocco D - Solo link o verifica sospesa

- `cemla_buscador`: valore alto, ma niente download diretto senza termini/API
  espliciti.
- `belgium_state_archives`: mantenere su percorso manuale se l'accesso richiede
  account.
- `austrian_state_archives_ais`: utile per ricerca guidata, non ancora per
  acquisizione automatica.
- `anno_onb`: rivalutare solo se emerge una API ufficiale o una policy tecnica
  compatibile.

Portali da non automatizzare in questa fase:

- `belgium_state_archives`, se l'accesso richiede account;
- `cemla_buscador`, finche non esistono termini/API chiari per automazione;
- `austrian_state_archives_ais`, utile come ricerca guidata ma non downloader;
- `anno_onb`, finche non viene verificata una API ufficiale o una policy tecnica
  compatibile.

## Prossimo batch suggerito

- Uruguay, Venezuela, Canada e Regno Unito, se lo scouting diaspora viene
  ampliato.
- Archivi regionali/diocesani italiani non gia coperti da Antenati.
- Portali IIIF nazionali o regionali con API documentate.
