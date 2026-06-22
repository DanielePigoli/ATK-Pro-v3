# Matrice portali candidati ATK-Pro

Data snapshot: 2026-06-06

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
| `archivi_nazionali` | Portale Archivi Nazionali / SIA / Sala Studio | Italia | `https://icar.cultura.gov.it/sistemi-e-portali/archivi-nazionali`; `https://archivinazionali.cultura.gov.it/`; `https://icar.cultura.gov.it/sistemi-e-portali/archivi-nazionali/sala-studio` | Molto alta: ricerca trasversale su fondi archivistici, Antenati, Archivi di Stato, Soprintendenze e progetti di digitalizzazione | Controllo 2026-06-05: il nuovo portale Archivi Nazionali risulta ancora in sviluppo; la pagina ICAR prevede accesso gratuito ma anche risorse fruibili solo previa identita digitale; Sala Studio richiede SPID/CIE/eIDAS per richieste e riproduzioni | C - candidato strategico solo per discovery/link assistito; nessun downloader finche il portale non e pubblico, stabile e dotato di API/IIIF e termini compatibili |
| `archivio_digitale_icar` | Archivio Digitale ICAR | Italia | `https://archiviodigitale-icar.cultura.gov.it/`; `https://archiviodigitale-icar.cultura.gov.it/it/172/termini-d-uso`; `https://archiviodigitale-icar.cultura.gov.it/it/163/guida-alla-ricerca` | Molto alta: 46 istituti sul portale, progetti di digitalizzazione, fondi, complessi e unita documentarie; contiene anche fonti genealogiche e archivistiche molto rilevanti | Consultazione gratuita e no-login; termini d'uso CC BY-NC-SA dove non diversamente specificato, ma divieto espresso di copia/estrazione massiva, robot o metodi analoghi, reverse engineering e aggiramento sicurezza. Tecnicamente utile come portale di ricerca, ma non compatibile con downloader ATK-Pro | C - link/discovery assistito; vietare builder/downloader e live smoke di download, salvo futuro endpoint ufficiale documentato e autorizzato |
| `sias` | Sistema Informativo degli Archivi di Stato | Italia | `https://archivi.cultura.gov.it/strumenti-di-ricerca-online/sistema-informativo-degli-archivi-di-stato-sias`; `https://icar.cultura.gov.it/sistemi-e-portali/sistemi-nazionali-di-descrizione-archivistica/sistema-informativo-degli-archivi-di-stato-sias-1`; `https://sias-archivi.cultura.gov.it/cgi-bin/pagina.pl?RicVM=inventari` | Alta: descrizioni di Archivi di Stato, inventari, strumenti di ricerca e possibili riproduzioni digitali collegate a schede | Controllo 2026-06-05: DGA/ICAR descrivono SIAS come sistema descrittivo; gli strumenti di ricerca online rimandano a inventari pubblicati nel web o nel portale SAN, in formato dinamico o PDF. ICAR segnala riproduzioni digitali collegate tramite metadati MAG-SIAS, ma non emerge una API/IIIF o policy downloader generale | C - link/discovery e apertura inventari; no download immagini o PDF massivo senza endpoint e termini specifici |
| `san_risorse_digitali` | SAN / CAT / Strumenti di ricerca online | Italia | `https://archivi.cultura.gov.it/strumenti-di-ricerca-online/il-sistema-archivistico-nazionale-san`; `https://inventari-san.cultura.gov.it/`; `https://www.san.beniculturali.it/oaicat/` | Alta: punto di accesso unificato a risorse archivistiche nazionali, catalogo CAT, inventari e risorse digitali collegate | Controllo 2026-06-05: DGA presenta SAN come catalogo/interoperabilita e accesso a fondi o serie consultabili digitalmente presso sistemi aderenti; Strumenti di ricerca online e orientato a inventari e descrizioni. Esiste una pista OAI/open data per metadati, ma immagini e diritti restano del sistema sorgente | B/C - possibile futura capability metadata/OAI se stabile e documentata; no downloader immagini diretto |
| `siusa` | SIUSA | Italia | `https://archivi.cultura.gov.it/strumenti-di-ricerca-online/il-sistema-informativo-unificato-per-le-soprintendenze-archivistiche-siusa`; `https://siusa-archivi.cultura.gov.it/cgi-bin/siusa/pagina.pl?TipoPag=informazioni`; `https://siusa-archivi.cultura.gov.it/cgi-bin/siusa/pagina.pl?RicVM=inventari` | Media-alta: censimento archivi pubblici e privati vigilati, soggetti conservatori/produttori, inventari e percorsi regionali/tematici | Controllo 2026-06-05: SIUSA e punto di accesso primario per patrimonio archivistico non statale; consente accesso a inventari online interni o esterni e dal 2011 esporta dati nel SAN. Il sito indica licenza CC BY-SA per i testi salvo diversa specificazione, ma non e un portale immagini/downloader | C - discovery, schede e link assistito; eventuale metadata solo via SAN/open data, nessun downloader |
| `beweb` | BeWeB - Beni ecclesiastici in web / CEI-Ar | Italia ecclesiastica | `https://www.beweb.chiesacattolica.it/subeweb/`; `https://www.beweb.chiesacattolica.it/beniarchivistici/aggregatore/30/Il%2Bprogetto%2BCEI-Ar`; `https://www.beweb.chiesacattolica.it/terminiduso/` | Molto alta per genealogia preunitaria e ricerca ecclesiastica: censimento di beni archivistici, istituti culturali, soggetti conservatori, persone, famiglie, enti e inventari ecclesiastici | Controllo 2026-06-05: BeWeB e la vetrina nazionale del censimento CEI; CEI-Ar pubblica banche dati/inventari di archivi ecclesiastici e puo collegare immagini a schede. I termini indicano CC BY-NC-SA per i contenuti, CC0 solo per dati catalografici di Persone, Famiglie e Istituti culturali; esistono area riservata e servizi di prenotazione. Non emerge una API/IIIF pubblica generalizzabile o una policy di download immagini | C - discovery/link assistito e, al massimo, futura metadata/search su dati catalografici compatibili; no downloader |
| `archivi_diocesani_italiani` | Archivi diocesani/parrocchiali italiani | Italia ecclesiastica | `https://www.beweb.chiesacattolica.it/beniarchivistici/aggregatore/3/Dove%2B-%2BI%2BSoggetti%2BConservatori%2B%3A%2BArchivio%2Bparrocchiale`; portali diocesani specifici da verificare caso per caso | Molto alta: registri di battesimo, matrimonio, defunti, stati delle anime, processetti matrimoniali e archivi parrocchiali non sempre coperti da Antenati | BeWeB conferma che gli archivi parrocchiali rientrano tra i soggetti conservatori e collega categorie genealogiche esplicite; tuttavia accesso, riproduzione, privacy, conservazione fisica e digitalizzazione dipendono dalla diocesi/parrocchia. Molte fonti possono richiedere contatto, appuntamento, autorizzazione o consultazione locale | C - mappa/link assistiti e schede di orientamento; vietare automazioni generiche, login, aree riservate e download senza fonte pubblica no-login con termini chiari |
| `archivio_stato_ticino` / `servizio_archivi_locali_ticino` | Archivio di Stato del Cantone Ticino / SAL | Svizzera italiana | `https://www4.ti.ch/decs/dcsu/asti/servizi/servizio-archivi-locali-sal/`; `https://www4.ti.ch/fileadmin/DECS/DCSU/ASTI/Documenti/Ricerche_genealogiche.pdf` | Molto alta per Ticino: fondi genealogici 1750-1960, archivi comunali, patriziali e parrocchiali, ruoli di popolazione, stato civile e microfilm ecclesiastici | Controllo 2026-06-05: ASTi/SAL censisce e riordina oltre 600 archivi locali, compresi archivi parrocchiali. Le disposizioni genealogiche indicano ricerche puntuali, formulari, costi dopo i primi 30 minuti, restrizioni su ruoli di popolazione/passaporti e divieto di riproduzione sistematica dei Ruoli di Popolazione. I registri parrocchiali ticinesi risultano disponibili online via FamilySearch e su microfilm presso Archivio diocesano di Lugano, non come endpoint pubblico ASTi | C - link/manuale e schede di orientamento; no downloader ATK-Pro |
| `archivio_diocesano_lugano` | Archivio storico diocesano di Lugano | Svizzera italiana ecclesiastica | `https://www.diocesilugano.ch/uffici-della-curia/`; `https://www4.ti.ch/decs/dcsu/uapcd/osservatorio/banca-dati-operatori-culturali/dettaglio/?tx_tichosservatorio_decsocoperatori%5Bid%5D=294` | Alta: microfilm e consultazione ecclesiastica per registri parrocchiali ticinesi, utile per fonti precedenti o complementari allo stato civile | La diocesi indica consultazione dell'Archivio storico su appuntamento; le disposizioni ASTi citano copie microfilm dei registri parrocchiali presso l'Archivio diocesano di Lugano. Non emerge portale pubblico con immagini scaricabili o API | C - solo contatto/link assistito e istruzioni di consultazione |
| `archivio_stato_grigioni` | Archivio di Stato dei Grigioni | Grigioni italofoni / area retica | `https://www.gr.ch/IT/istituzioni/amministrazione/ekud/afk/sag/servizi/fondi/familienforschung/Seiten/default.aspx`; `https://www.gr.ch/IT/istituzioni/amministrazione/ekud/afk/sag/servizi/fondi/Seiten/default.aspx` | Molto alta per valli italofone, mobilita alpina e fonti pre-1876: registri parrocchiali, stato civile, registri dei cittadini, schede genealogiche e strumenti di ricerca | Controllo 2026-06-05: l'Archivio di Stato indica microfilm di tutti i registri parrocchiali conosciuti, consultabili presso l'Archivio; registri di stato civile fino al 1929 in sala lettura; registri delle famiglie non visionabili; alcuni registri dei cittadini soggetti ad autorizzazione. Il sistema informativo e i PDF sono online, ma i documenti d'archivio sono in gran parte non accessibili online e vanno consultati in sala lettura | C - discovery/link assistito; no download, salvo eventuali fondi digitalizzati con condizioni specifiche |
| `diocesi_chur_coira` | Archivio vescovile di Coira / Bischöfliches Archiv Chur | Grigioni / area retica ecclesiastica | `https://www.archiv-bistum-chur.ch/`; `https://www.bistumsarchiv-chur.findbuch.net/` | Alta: diocesi storica antica, rilevante per fonti ecclesiastiche grigionesi e area retica | Il sito ufficiale documenta l'ordinamento, indicizzazione e apertura digitale del patrimonio storico e moderno e rimanda a un sistema Findbuch; non emerge una policy di download immagini/API generalizzabile. Da trattare come ricerca guidata e link a inventari | C - link/discovery assistito; non estendere come downloader generico |
| `biblioteca_digitale_siena` | Biblioteca Digitale Siena | Italia | `https://bds.comune.siena.it/`; `https://bds.comune.siena.it/it/169/` | Media-alta: manoscritti, periodici, disegni, archivi e carteggi senesi/toscani | Piattaforma pubblica IIIF; termini ufficiali consentono JPG web-resolution per uso personale, studio e ricerca con citazione, vietando uso commerciale e trasformazioni non autorizzate; smoke live 2026-06-05 passato su manifest da 106 canvas | A - builder viewer->manifest aggiunto e verificato live |
| `biblioteca_digitale_trentina` | Biblioteca Digitale Trentina | Italia / Trentino e area ex asburgica | `https://bdt.bibcom.trento.it/`; `https://bdt.bibcom.trento.it/Riuso`; `https://www.comune.trento.it/Servizi/Biblioteca-Digitale-Trentina-BDT` | Alta per storia locale, Trentino, mobilita alpina, cartoline, periodici, carte geografiche, stampe e fonti bibliografiche di contesto | Controllo 2026-06-06: fonte istituzionale pubblica, accesso libero, download gratuito delle immagini e pagina di riuso molto favorevole: materiali in pubblico dominio, riuso anche commerciale con citazione. La sonda ha trovato immagini dirette e PDF diretto, non manifest IIIF reale | A - promosso a supporto tecnico: manifest sintetico da immagini pubbliche e PDF diretto ufficiale per testi a stampa quando l'utente richiede solo PDF senza range |
| `beic_digitale` | BEIC digital library | Italia / Lombardia | `https://digital.beic.it/`; `https://digital.beic.it/termini-duso/`; `https://digital.beic.it/infrastruttura-e-standard/`; esempi tecnici Preserver `https://preserver.beic.it/delivery/DeliveryManagerServlet?dps_pid=IE7400509` | Alta per libri antichi, manoscritti, periodici, editoria lombarda e fonti bibliografiche utili alla ricerca genealogica e territoriale | Controllo 2026-06-08: termini ufficiali molto favorevoli per opere in pubblico dominio, immagini scaricabili/riutilizzabili e dati CC0; infrastruttura Rosetta/Alma/Primo VE con OAI-PMH documentato. Lato download non e ancora emerso un endpoint utilizzabile in modo ripetibile: il test live su Preserver `IE7400509` ha trovato solo il logo del viewer, mentre il record Primo `alma9925210904741` non ha esposto candidati manifest, PDF o immagini utili alla sonda. `verify_beic_technical_probe.py` resta lo strumento di raccolta campioni, ma senza integrazione nel menu | B/C - candidato forte per metadata e valore culturale, ma downloader sospeso finche non emergono campioni BEIC diretti con endpoint file/manifest stabile e policy item-level |
| `biblioteca_digitale_lombarda` | Biblioteca Digitale Lombarda | Italia / Lombardia | `https://www.bdl.servizirl.it/`; esempi record pubblici `https://www.bdl.servizirl.it/vufind/Record/BDL-OGGETTO-133442`; endpoint PDF pubblici `https://www.bdl.servizirl.it/bdl/public/rest/srv/item/12404/pdf` | Alta per storia locale lombarda, periodici, monografie, archivi e fondi civici | Controllo 2026-06-08: portale pubblico VuFind con record e PDF REST pubblici; il campione `item/12404/pdf` risponde come PDF reale ed e promosso a supporto puntuale `D_ONLY`. La pagina record espone anche una miniatura Cantaloupe/IIIF (`6823693`) ma insieme ad asset grafici del sito; l'`info.json` derivato ha dato timeout nel test live. Molti record dichiarano CC BY-NC-ND, quindi uso studio/ricerca con limiti non commerciale/no-derivati | A/B - promosso solo per PDF puntuale pubblico; niente supporto immagini/registro finche info.json, sequenze o manifest non risultano stabili |
| `ambrosiana_digitale` | Veneranda Biblioteca Ambrosiana - Digital Library | Italia / Lombardia ecclesiastica e manoscritti | `https://www.ambrosiana.it/en/discover/masterpieces/the-digital-library/`; `https://ambrosiana.comperio.it/library-digital/`; esempi Comperio `https://ambrosiana.comperio.it/opac/detail/view/ambro:catalog:24203` | Alta per manoscritti, codici, fondi storici e fonti culturali collegate a Milano e Lombardia | Controllo 2026-06-07: la pagina ufficiale descrive accesso libero e uso dello standard IIIF; fonte accademica conferma Mirador e Cantaloupe. Test live su `ambro:catalog:24203`: trovati solo record Comperio duplicati/correlati e asset grafico, nessun manifest, info.json, immagine Cantaloupe o viewer utile. I manifest trovati in fonti esterne possono essere aggregatori, non endpoint Ambrosiana diretti | B/C - valore alto ma integrazione sospesa: servono campioni Ambrosiana diretti con manifest stabile, termini item-level e pattern tecnico ripetibile |
| `rovereto_digital_library` | Rovereto Digital Library / Biblioteca Tartarotti | Italia / Trentino | `https://digitallibrary.bibliotecacivica.rovereto.tn.it/`; campioni `https://digitallibrary.bibliotecacivica.rovereto.tn.it/entities/publication/e4199e9b-c79b-4c3d-b157-be2dcfc0407f`, `https://digitallibrary.bibliotecacivica.rovereto.tn.it/entities/picture/2cbeaeab-833a-48c2-9b39-29484ed1c681`; termini `https://digitallibrary.bibliotecacivica.rovereto.tn.it/info/end-user-agreement` | Media-alta per storia locale trentina, fotografie, documenti d'archivio, riviste e contesto familiare | Controllo 2026-06-08: portale operativo DSpace-GLAM promosso a supporto tecnico prudente. ATK-Pro deriva l'endpoint REST item standard, segue la paginazione HAL/JSON di bundle e bitstream, costruisce un manifest sintetico solo dai bitstream pubblici classificati come pagine `iiifpdf-*.png` e conserva il PDF originale solo come riferimento `seeAlso`. Restano esclusi licenza, miniature/cover e derivati testuali/OCR. Termini ufficiali: accesso libero e gratuito ai file digitali in risoluzione web secondo licenze specifiche; alta definizione su richiesta | A - promosso a supporto tecnico `R_LIMITED` con range esplicito e controllo licenza item-level |
| `bub_digitale` | BUB Digitale / Biblioteca Universitaria di Bologna | Italia / Emilia-Romagna | `https://bub.unibo.it/it/bub-digitale`; `https://bub.unibo.it/it/bub-digitale/bollettini-parrocchiali`; campioni `Bondanello 1934` e `Castenaso 1933` | Media-alta: papiri, manoscritti greci/arabi/ebraici, opere a stampa, periodici storici, bollettini parrocchiali, fotografie e fondi bolognesi utili al contesto storico-familiare | Controllo 2026-06-08: fonte ufficiale BUB descrive accesso libero e gratuito per studio/ricerca, uso dello standard IIIF e visualizzatore Mirador. La landing page live espone soprattutto pagine del portale e immagini Plone `@@images`, ora classificate come `plone_page_image` per non confonderle con pagine documento. Test live mirato sul bollettino Bondanello 1934: manifest IIIF v2 pulito da `viewer_manifest_parameter`, codice 200, 44 canvas. Secondo campione Castenaso 1933: manifest diretto, codice 200, 32 canvas. Pattern manifest stabile su piu bollettini; promosso a supporto IIIF diretto prudente | A - promosso a supporto `R_LIMITED`: solo manifest BUB pubblici, range esplicito, referer BUB e verifica licenza item-level |
| `dl_ficlit` | FICLIT Digital Library / Universita di Bologna | Italia / Emilia-Romagna | `https://dl.ficlit.unibo.it/s/lib/page/progetto`; campioni `https://dl.ficlit.unibo.it/s/lib/item/199245`, `https://dl.ficlit.unibo.it/s/lib/item/28429` | Media: collezioni accademiche e umanistiche, fonti letterarie, bibliografiche e documentarie utili a ricerche storiche territoriali | Controllo 2026-06-08: fonte ufficiale descrive piattaforma Omeka S, tecnologia IIIF per immagini e visualizzazione con Mirador Viewer. Test live 2026-06-09: item Corbiere `199245` con immagine originale pubblica e manifest `https://dl.ficlit.unibo.it/iiif/2/199245/manifest`, codice 200 e 1 canvas; item Camporesi `28429` con immagine originale pubblica e manifest `https://dl.ficlit.unibo.it/iiif/2/28429/manifest`, codice 200 e 239 canvas. Il pattern Omeka/IIIF appare concreto; restano da verificare termini item set e distinzione tra collezioni liberamente scaricabili e sola consultazione | A - promosso a supporto tecnico `R_LIMITED`: solo item/manifest FICLIT pubblici, range esplicito, referer FICLIT e verifica termini item-level |
| `orientales_unior` | OrienTales / Biblioteca digitale Universita di Napoli L'Orientale | Italia / Campania | `https://www.unior.it/it/biblioteche/servizi-gli-utenti/biblioteca-digitale` | Media-alta: libri antichi, manoscritti in lingue orientali, materiale d'archivio, documentario, periodici, collane, carte geografiche e atlanti, con valore culturale e storico per ricerche italiane | Controllo 2026-06-08/10: fonte ufficiale indica licenze Creative Commons, framework IIIF, uso di Mirador, download laddove la licenza lo permetta, OCR e scarico metadati; la descrizione tecnica cita DSpace, mentre restano possibili tracce Omeka dai progetti precedenti. `verify_orientales_technical_probe.py` ora cerca sia pattern DSpace (`entities`, REST item, bundle, bitstream, handle e link JSON/HAL), sia record Omeka, viewer Mirador, manifest IIIF, info.json, immagini, OCR/testi e metadati candidati. Verifica manuale 2026-06-10: le pagine record finora viste mostrano "Il record non puo essere mostrato agli utenti ospiti" e contenuti riservati agli utenti affiliati; manca quindi il requisito minimo di accesso pubblico senza autenticazione. Il download non e generalizzabile senza record pubblici e licenza dell'oggetto | C - sospeso/escluso dal download automatico finche non emergono record pubblici consultabili da ospite con licenza visibile e endpoint manifest/bitstream senza autenticazione |
| `museu_imigracao_sp` | Museu da Imigracao do Estado de Sao Paulo - Acervo Digital | Brasile / diaspora italiana | `https://museudaimigracao.org.br/acervo/sobre-acervo`; `https://www.museudaimigracao.org.br/acervo/passageiros`; `https://museudaimigracao.org.br/acervo-e-pesquisa/acervo` | Molto alta per immigrati italiani in Brasile/Sao Paulo | Acervo digitale pubblico con piu di 250 mila immagini, registri di matricola, liste di bordo, carte di chiamata, richieste SACOP, iconografie, cartografie e giornali; le fonti ufficiali indicano uso/download non commerciale, ma il percorso tecnico appare basato su ricerca web e PDF/immagini pubbliche, non su IIIF/API documentata | B - candidato forte, ma non integrare finche non viene validata una capability `pdf_direct`/download diretto pubblica e testabile |
| `apesp_digitalizados` | Arquivo Publico do Estado de Sao Paulo - Acervo digitalizado | Brasile / diaspora italiana | `https://web.arquivoestado.sp.gov.br/web/acervo/digitalizados`; `https://www.arquivoestado.sp.gov.br/web/digitalizado/textual/nucleos_coloniais`; `https://web.arquivoestado.sp.gov.br/web/acervo/atendimento/reproducao_documentos`; `https://web.arquivoestado.sp.gov.br/web/acervo/solicitacao_certidoes/imigracao` | Molto alta: Hospedaria, Porto di Santos, nuclei coloniali, documenti di immigrazione e colonizzazione | Fonte ufficiale molto rilevante, ma l'acervo digitalizzato rimanda a registrazione/login e la pagina dei nuclei coloniali contiene avviso di servizio con login; la riproduzione e soggetta a credito, termini di responsabilita e valutazioni su diritto/autorizzazione. Nessun endpoint no-login/API/IIIF stabile verificato nel primo controllo | C - link/manuale e discovery; download diretto escluso finche non emerge una risorsa pubblica no-login con licenza e tecnica stabili |
| `arquivo_nacional_br_sian` | Arquivo Nacional do Brasil / SIAN | Brasile / diaspora italiana | `https://www.gov.br/arquivonacional/pt-br/canais_atendimento/imprensa/copy_of_noticias/a-imigracao-italiana-e-o-acervo-do-an`; `https://www.gov.br/arquivonacional/pt-br/canais_atendimento/imprensa/copy_of_noticias/quer-pesquisar-no-arquivo-nacional-acesse-o-sian`; `https://www.gov.br/arquivonacional/pt-br/servicos/acervos/copy_of_acervos-mais-consultados/entrada-de-estrangeiros`; `https://www.gov.br/arquivonacional/pt-br/servicos/bases-de-dados/bases` | Alta: ingresso di stranieri, vapori, acervo nazionale, Porto di Rio de Janeiro e Porto di Santos | SIAN e molto rilevante e offre documenti digitalizzati senza costo, ma le fonti ufficiali richiedono cadastro/login; la pagina SIAN espone anche controllo anti-spam/umano. La base separata Entrada de Estrangeiros - Porto do Rio de Janeiro e utile come ricerca nominale/dichiarazione, ma non e ancora un endpoint immagini/API verificato | C - link/manuale e discovery; non integrare download diretto SIAN per login/challenge. Rivalutare separatamente la base Rio solo se emerge un accesso pubblico documentato e testabile |
| `agn_argentina_inmigrantes` | Archivo General de la Nacion Argentina - buscador inmigrantes | Argentina / diaspora italiana | `https://www.argentina.gob.ar/interior/archivo-general-de-la-nacion`; `https://www.argentina.gob.ar/interior/archivo-general-de-la-nacion/consulta-de-antecedentes-migratorios`; `https://www.argentina.gob.ar/noticias/el-archivo-general-de-la-nacion-es-memoria-del-mundo`; `https://www.argentina.gob.ar/terminos-y-condiciones`; `https://www.unesco.org/es/memory-world/lac/passengers-entry-books-sea-1882-1937-national-registry-migrations-documentary-fond` | Molto alta: ingressi al porto di Buenos Aires 1882-1937, serie UNESCO Memoria del Mundo, oltre 4 milioni di ingressi in 808 libri | Buscador ufficiale pubblico: la pagina indica ricerca per date, nome, cognome e nave, con possibilita di scaricare una constancia PDF e, se digitalizzato, il PDF del libro completo. I termini generali Argentina.gob.ar indicano accesso libero/gratuito e contenuti CC BY 4.0 salvo diversa indicazione; non emergono pero API/IIIF o endpoint ufficiali documentati per automazione | B - candidato forte per futura capability metadata/PDF; per ora link assistito, no download diretto finche non viene validato un endpoint pubblico stabile con fixture |
| `cemla_buscador` | CEMLA buscador inmigrantes | Argentina / diaspora italiana | `https://cemla.com/`; `https://www.cemla.com/buscador/`; `https://cemla.com/faqs/`; `https://cemla.com/contacto/`; `https://cemla.com/terms-and-conditions/` | Alta: arrivi di immigrati in Argentina, con dati fino al 1960 e forte utilita per famiglie italiane | Fonte privata/non governativa molto usata; le FAQ chiariscono che CEMLA espone solo i dati presenti nel buscador, indica i campi disponibili e rimanda al certificato via email. Il buscador e incorporato come iframe, non espone API/IIIF o endpoint documentati, la pagina termini e un placeholder generico e il flusso pubblico richiede validazione tipo CAPTCHA | C - solo link/manuale; no download diretto e no interrogazione automatica senza autorizzazione/API esplicita |
| `agn_colombia_dataviva` | Archivo General de la Nacion Colombia - DataViva | Colombia / diaspora italiana | `https://www.archivogeneral.gov.co/agn/home/`; `https://dataviva.archivogeneral.gov.co/`; `https://www.datos.gov.co/Cultura/DATAVIVA/r5h9-7h58`; `https://www.archivogeneral.gov.co/dataviva-da-un-paso-historico-hacia-los-datos-abiertos-en-colombia`; `https://www.archivogeneral.gov.co/terminos-y-condiciones`; `https://www.archivogeneral.gov.co/sites/default/files/2025-07/MANUAL_DATAVIVA.pdf` | Media-alta: documenti storici digitalizzati, possibili fondi migrazione e contesto per presenze italiane in Colombia | Candidato tecnico forte per metadata/discovery: il dataset ufficiale Datos Abiertos Colombia dichiara DataViva come applicazione AGN per consulta, visualizzazione e descarga di piu di 25 milioni di immagini, con accesso OData/Socrata e dati aggiornati nel 2026. Tuttavia i termini generali AGN sono restrittivi su riproduzione/copia/distribuzione dei contenuti; distinguere metadati open data da immagini/documenti e verificare per item prima di qualunque download | B - forte per futura integrazione metadata/API; download immagini/PDF solo con policy specifica, range esplicito e fixture stabile |
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

1. `archivi_nazionali`, `san_risorse_digitali`, `sias` e `siusa`, per riportare
   il lavoro sull'asse italiano/italofono e capire quali funzioni siano
   metadata/discovery e quali, eventualmente, download puntuale.
2. `beweb` e archivi diocesani/parrocchiali italiani, per verificare se esista
   un percorso di discovery utile senza automatizzare contenuti sensibili o
   soggetti a limitazioni pastorali, privacy o consultazione locale.
3. `archivio_stato_ticino`, `servizio_archivi_locali_ticino`,
   `archivio_stato_grigioni` e `diocesi_chur_coira`, per coprire l'area
   italofona svizzera e le zone storicamente connesse al contesto italiano.
4. Biblioteche digitali locali italiane con manifest IIIF pubblico, sul modello
   di `biblioteca_digitale_siena`.
5. Le piste internazionali gia valutate restano in memoria, ma sono sospese
   finche non si chiude il nuovo passaggio sull'ambito italiano/italofono.

## Shortlist italiana/italofona gia individuata

Questa lista e il punto di ripresa dopo la pausa dell'ambito internazionale.
Non implica integrazione automatica: ogni candidato va verificato con fonti
ufficiali, endpoint stabili, condizioni d'uso compatibili e almeno un campione
pubblico no-login.

| Chiave provvisoria | Area | Fonte o base di verifica | Prima decisione |
| --- | --- | --- | --- |
| `archivi_nazionali` / `archivio_digitale_icar` | Italia | `https://icar.cultura.gov.it/sistemi-e-portali/archivi-nazionali`; `https://archiviodigitale-icar.cultura.gov.it/`; termini d'uso Archivio Digitale | Priorita massima come discovery/link assistito; niente downloader per Archivio Digitale per divieto robot/estrazione massiva |
| `san_risorse_digitali` | Italia | `https://www.san.beniculturali.it/web/san/risorse-per-le-ricerche` | Discovery e collegamento alle risorse; immagini demandate al sistema sorgente |
| `sias` | Italia | `https://archivi.cultura.gov.it/strumenti-di-ricerca-online/sistema-informativo-degli-archivi-di-stato-sias` | Discovery sugli Archivi di Stato; non trattarlo come downloader |
| `siusa` | Italia | `https://siusa-archivi.cultura.gov.it/` | Discovery su soggetti conservatori e fondi vigilati; utile per orientare l'utente |
| `beweb` | Italia ecclesiastica | `https://www.beweb.chiesacattolica.it/subeweb/` | Alta priorita informativa; prima link/discovery, download solo se emergono immagini pubbliche e condizioni esplicite |
| `archivi_diocesani_italiani` | Italia ecclesiastica | BeWeB soggetti conservatori; portali diocesani/parrocchiali da verificare caso per caso | Candidato a schede/link assistiti; escludere aree riservate, dati recenti, consultazioni locali e download generici |
| `archivio_stato_ticino` / `servizio_archivi_locali_ticino` | Svizzera italiana | ASTi/SAL e disposizioni genealogiche ASTi | Molto rilevante per Ticino; solo discovery/link/manuale per limiti di riproduzione e fonti non esposte come endpoint pubblico |
| `archivio_diocesano_lugano` | Svizzera italiana ecclesiastica | Curia/Archivio storico diocesano e disposizioni ASTi | Link/manuale su appuntamento; nessun download senza portale pubblico autonomo e termini compatibili |
| `archivio_stato_grigioni` | Grigioni italofoni | Archivio di Stato GR, pagina ricerca genealogica e sistema informativo | Alta priorita per aree italofone e mobilita alpina; discovery/link, microfilm e sala lettura |
| `diocesi_chur_coira` | Grigioni / area retica ecclesiastica | Archivio vescovile Coira e Findbuch | Fonte ecclesiastica da trattare con cautela; link/manuale finche non emergono immagini pubbliche e termini chiari |
| `biblioteca_digitale_trentina` | Italia / Trentino | BDT, pagina Riuso e servizio Comune di Trento | Promosso a supporto: immagini dirette pubbliche e PDF diretto ufficiale per testi a stampa in modalita solo PDF |
| `beic_digitale` | Italia / Lombardia | BEIC termini d'uso, infrastruttura/OAI-PMH, Primo VE e Preserver/DeliveryManager | Forte per metadata e valore culturale; downloader sospeso dopo test live senza endpoint file/manifest stabile su Preserver/Primo |
| `biblioteca_digitale_lombarda` | Italia / Lombardia | BDL/VuFind, record pubblici e PDF REST | Promosso solo per documento singolo PDF da endpoint REST pubblico; immagini/IIIF sospesi per timeout su info.json e licenze item-level restrittive |
| `ambrosiana_digitale` | Italia / Lombardia ecclesiastica | Digital Library Ambrosiana, Comperio, Mirador/Cantaloupe e IIIF dichiarato | Test live Comperio senza manifest/info utili; valore alto, ma integrazione sospesa finche non emergono campioni Ambrosiana diretti |
| `rovereto_digital_library` | Italia / Trentino | portale DSpace-GLAM operativo, item pubblici, Mirador/IIIF, file PDF/JPEG e termini ufficiali | Promosso a supporto tecnico prudente: manifest sintetico da bitstream pagina pubblici, `R_LIMITED`, range esplicito e licenza item-level da verificare |
| `bub_digitale` | Italia / Emilia-Romagna | pagina ufficiale BUB Digitale, IIIF e Mirador dichiarati; `verify_bub_technical_probe.py`; `verify_manifest_url.py` | Promosso a supporto prudente `R_LIMITED`: due bollettini parrocchiali verificati con manifest IIIF v2, 44 e 32 canvas; licenza item-level e range esplicito restano obbligatori |
| `dl_ficlit` | Italia / Emilia-Romagna | pagina ufficiale DL FICLIT, Omeka S, IIIF e Mirador dichiarati; `verify_ficlit_technical_probe.py`; `verify_manifest_url.py` | Promosso a supporto prudente `R_LIMITED`: due campioni positivi, Corbiere `199245` con 1 canvas e Camporesi `28429` con 239 canvas; range esplicito e verifica termini item-level obbligatori |
| `orientales_unior` | Italia / Campania | pagina ufficiale OrienTales, IIIF, Mirador, OCR, metadati e download se licenza lo permette; sonda aggiornata per DSpace/Omeka con `verify_orientales_technical_probe.py` | Sospeso per download: i record visti sono riservati agli utenti affiliati, rivalutare solo con record pubblici da ospite |
| `biblioteche_digitali_locali_iiif` | Italia | esempi da selezionare da biblioteche civiche, universitarie, comunali o regionali | Buona pista tecnica se IIIF pubblico e policy prudente `R_LIMITED`; il primo sottoblocco ha prodotto BDT, BDL e Rovereto, mentre BEIC e Ambrosiana restano sospese |
| `memooria_jarvis_istanze_italiane` | Italia | istanze pubbliche Jarvis/Memooria da verificare per ente | Solo risorse pubbliche no-login, con diritti e referer specifici |

## Shortlist operativa provvisoria

Questa shortlist ordina il lavoro senza derogare alla priorita italiana e
italofona. I portali di diaspora entrano in testa solo quando sono strettamente
legati alla ricerca genealogica italiana e hanno una base pubblica o
istituzionale verificabile.

Nota operativa 2026-06-05: dopo le valutazioni su Brasile, Argentina e Colombia,
il lavoro immediato torna alla shortlist italiana/italofona precedente. I blocchi
internazionali sotto restano come memoria delle decisioni gia prese, non come
prossimo sviluppo.

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

- `agn_argentina_inmigrantes`: molto rilevante per la diaspora italiana in
  Argentina. Il buscador ufficiale e pubblico e prevede download di constancia
  PDF e, se disponibile, del libro digitalizzato; manca pero una API/IIIF
  documentata. Valutarlo come futura integrazione metadata/PDF, con ricerca
  mirata dall'utente e senza interrogazioni ampie o scraping del form.
- `nara_catalog`: primo candidato tecnico per un prototipo metadata/discovery,
  perche dispone di API ufficiale e documentazione pubblica.
- `francearchives`: candidato forte per discovery archivistica; download di
  immagini solo quando il provider sorgente e verificato.
- `agn_colombia_dataviva`: candidato tecnico forte per metadata/discovery
  perche DataViva pubblica una base su Datos Abiertos Colombia con accesso
  OData/Socrata. La componente immagini/PDF resta separata: i termini generali
  AGN sono restrittivi sulla riproduzione dei contenuti, quindi nessun download
  diretto prima di una policy specifica o di un campione item-level verificato.
- `papers_past_digitalnz`: utile per ricerca contestuale su stampa storica, da
  trattare come integrazione metadata/search prima di qualsiasi download.

### Blocco C - Italia e fonti istituzionali nazionali

- `archivi_nazionali`: dopo il controllo 2026-06-05 resta il candidato
  strategico piu importante per orientamento e ricerca, ma il portale unico
  risulta ancora in sviluppo e alcune risorse saranno accessibili solo previa
  identita digitale. Trattarlo come link/discovery assistito, non come
  downloader.
- `archivio_digitale_icar`: portale pubblico e no-login, molto utile per la
  ricerca, ma i termini vietano copia/estrazione massiva e robot. Escludere
  builder/downloader; mantenere solo apertura guidata e supporto alla ricerca.
- `biblioteca_digitale_siena`: candidato IIIF italiano compatibile con
  risoluzione manifest da URL viewer; smoke live passato su manifest da 106
  canvas. Prima della RC restano fixture offline e test UI/manuale di download
  con range esplicito.
- `san_risorse_digitali`: catalogo/interoperabilita e strumenti di ricerca; puo
  diventare una pista metadata/OAI se l'endpoint resta stabile e documentato,
  ma le immagini dipendono dai sistemi sorgente.
- `sias`: strumento descrittivo degli Archivi di Stato, utile per inventari e
  contesto; le riproduzioni digitali eventualmente collegate non bastano per un
  downloader generale.
- `siusa`: ottimo per fondi non statali, soggetti conservatori/produttori e
  inventari online; resta discovery/link assistito.
- `beweb`: fonte nazionale molto utile per archivi ecclesiastici, soggetti
  conservatori, persone, famiglie e istituti culturali. I contenuti non sono una
  base downloader: CC BY-NC-SA generale, CC0 solo per alcune categorie
  catalografiche e assenza di API/IIIF pubblica generalizzabile.
- `archivi_diocesani_italiani`: valore genealogico altissimo, ma condizioni e
  accesso cambiano per diocesi/parrocchia. Trattarli come mappa assistita e
  non come automazione.
- `archivio_stato_ticino` / `servizio_archivi_locali_ticino`: fonti molto
  importanti, ma con consultazione, formulari, restrizioni e divieto di
  riproduzione sistematica per alcune serie. Non downloader.
- `archivio_diocesano_lugano`: consultazione su appuntamento e microfilm citati
  da ASTi; solo link/manuale.
- `archivio_stato_grigioni`: fortissimo per genealogia, con microfilm e
  strumenti online/PDF; la maggior parte dei documenti resta in sala lettura.
- `diocesi_chur_coira`: Findbuch e orientamento ecclesiastico; no downloader
  senza immagini pubbliche e termini chiari.

### Blocco D - Solo link o verifica sospesa

- `cemla_buscador`: valore alto, ma niente download diretto senza termini/API
  espliciti. Dopo il controllo 2026-06-05 resta una fonte manuale forte: FAQ
  utili, dati indicizzati nel buscador e certificato richiedibile via email, ma
  nessuna API/IIIF o autorizzazione tecnica all'interrogazione automatica.
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

- Considerare chiuso il primo controllo su `archivi_nazionali` e
  `archivio_digitale_icar`: entrambi restano discovery/link assistito, non
  downloader.
- Considerare chiuso il primo controllo su `san_risorse_digitali`, `sias` e
  `siusa`: sono candidati discovery/metadati, non downloader. La sola pista
  tecnica aperta e una futura capability metadata/OAI per SAN, se endpoint,
  licenza e formati vengono verificati con campioni stabili.
- Valutare `beweb` e una prima mappa degli archivi diocesani/parrocchiali
  italiani, restando su link/discovery finche non emergono immagini pubbliche
  con termini compatibili.
- Considerare chiuso il primo controllo su `beweb`: discovery/link assistito e
  possibile metadata leggero sulle sole categorie compatibili, non downloader.
- Preparare, se utile, una mappa di archivi diocesani italiani prioritari per
  area geografica, ma solo come orientamento/manuale.
- Valutare Ticino, Grigioni e Diocesi di Coira come area italofona svizzera,
  distinguendo inventari pubblici, consultazione locale e possibili risorse
  digitali.
- Considerare chiuso il primo controllo su Ticino, Lugano, Grigioni e Coira:
  ambito ad alto valore genealogico ma da trattare come orientamento assistito,
  non come integrazione di download.
- Cercare ulteriori biblioteche digitali italiane con IIIF pubblico, partendo da
  esempi tecnicamente simili a Biblioteca Digitale Siena.
- Considerare concluso il primo sottoblocco biblioteche digitali italiane:
  `biblioteca_digitale_trentina`, `biblioteca_digitale_lombarda` e
  `rovereto_digital_library` sono entrate con policy puntuali; `beic_digitale`
  e `ambrosiana_digitale` restano sospese per mancanza di endpoint stabili.
- Considerare chiuso il secondo sottoblocco IIIF italiano: `bub_digitale` e
  `dl_ficlit` sono supportati con policy `R_LIMITED`, mentre
  `orientales_unior` resta escluso dal download finche i record pubblici non
  risultano accessibili agli utenti ospiti.
- Congelare l'aggiunta di ulteriori portali italiani prima della RC, salvo
  endpoint pubblico stabile, policy compatibile e verifica tecnica a basso
  rischio; BEIC e Ambrosiana restano nella roadmap futura.
- Riprendere Uruguay, Venezuela, Canada, Regno Unito e altre piste diaspora solo
  dopo questo passaggio italiano/italofono.
