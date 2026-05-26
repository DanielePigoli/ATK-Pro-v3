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
| `antenati` | Antenati (Cultura.gov.it) | Italia | IIIF discovery / manifest DAM | Medio | Da verificare rispetto alle note legali MiC | Mantenere come portale primario e verificare limiti d'uso correnti |
| `bnc_roma` | BNC Roma digitale | Italia | Manifest sintetico da pagina item-level | Alto | Da verificare | Verificare termini e stabilita HTML prima di estendere |
| `bncf_teca` | BNCF Teca (Firenze) | Italia | Tentativo IIIF standard + manifest sintetico + fallback diretto immagini | Alto | Da verificare | Separare capability e documentare limiti/range |
| `museogalileo` | Museo Galileo Digiteca | Italia | Manifest sintetico da TecaService, token GetObject | Alto | Da verificare | Controllare policy TecaService e robustezza token |
| `internetculturale_estense` | Internet Culturale / Estense / ICCU | Italia | Manifest sintetico da magparser | Medio-Alto | Da verificare | Verificare endpoint ufficiali e condizioni ICCU |
| `brixiana` | Brixiana / Jarvis | Italia | Alias Memooria/Jarvis IIIF | Medio | Da verificare | Confermare dominio e termini della biblioteca/fornitore |
| `memooria` | Memooria/Jarvis | Italia | IIIF da meta/iiif/{guid}/manifest | Medio | Da verificare | Documentare pattern supportati e biblioteche compatibili |
| `vatlib` | DigiVatLib | Italia / Vaticano | IIIF diretto da view/mss/iiif | Basso-Medio | Da verificare | Verificare termini DigiVatLib e limiti di riuso |
| `findbuch` | Kirchenbuecher Suedtirol / findbuch.net | Alto Adige / Sudtirol | Manifest sintetico da HTML + gtpc.php | Alto | Da verificare; evitare se accesso/account/limitazioni | Verificare termini e valutare se mantenere solo con range puntuale |
| `matricula` | Matricula Online | Europa centrale | Manifest sintetico da viewer HTML e hosted-images | Alto | Da verificare | Verificare termini Matricula e ridurre dipendenza da HTML viewer |
| `gallica` | Gallica (BnF) | Francia | IIIF diretto da ARK + fallback Playwright per TLS/fingerprint | Medio | Da verificare | Verificare condizioni Gallica/BnF e fallback necessario |
| `heidelberg` | Heidelberg UB | Germania | IIIF diretto + rate-limit sequenziale | Basso-Medio | Da verificare | Mantenere delay esplicito e verificare policy download |
| `bodleian` | Bodleian Libraries Oxford | Regno Unito | IIIF diretto da object UUID | Basso | Da verificare | Verificare licenze per singoli oggetti |
| `e_rara` | e-rara | Svizzera | IIIF builder dedicato | Basso-Medio | Da verificare | Verificare condizioni per download puntuale |
| `e_codices` | e-codices (Unifr) | Svizzera | IIIF builder dedicato | Basso-Medio | Da verificare | Verificare condizioni e licenze dei manoscritti |
| `e_manuscripta` | e-manuscripta | Svizzera | IIIF builder dedicato | Basso-Medio | Da verificare | Verificare condizioni per raccolte specifiche |
| `internet_archive` | Internet Archive | Internazionale | Manifest sintetico da metadata/files/BookReaderImages | Medio-Alto | Da verificare per item/licenza | Preferire item pubblici con licenza chiara |
| `europeana` | Europeana IIIF | Internazionale | IIIF diretto da provider/record id | Basso-Medio | Da verificare per provider e record | Usare solo record con IIIF disponibile e licenza chiara |
| `manifest_diretto` | Manifest diretto (URL gia noto) | Avanzato | URL manifest fornito dall'utente | Variabile | Responsabilita utente + verifica termini origine | Mantenere con avviso/criteri chiari |

## Lettura operativa

Priorita tecnica provvisoria per consolidamento:

1. Portali con IIIF diretto o manifest diretto: `vatlib`, `bodleian`,
   `heidelberg`, `europeana`, `e_rara`, `e_codices`, `e_manuscripta`,
   `manifest_diretto`.
2. Portali con discovery/fallback ma valore alto: `antenati`, `gallica`,
   `memooria`, `brixiana`.
3. Portali sintetici o endpoint non standard da trattare con cautela:
   `bnc_roma`, `bncf_teca`, `museogalileo`, `internetculturale_estense`,
   `internet_archive`.
4. Portali con scraping-like/viewer speciali o rischio accesso/termini da
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
