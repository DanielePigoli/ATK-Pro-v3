# Checklist release ATK-Pro v3.0.0

Data snapshot: 2026-05-27

Questa checklist raccoglie i criteri minimi per decidere se ATK-Pro puo' passare
da baseline pre-release a RC tecnica v3.0.0, e distingue quel passaggio da una
release pubblica multilingue completa.

## Decisione sintetica

| Stato | Esito | Motivazione |
| --- | --- | --- |
| RC tecnica v3.0.0 | Possibile dopo verifica finale | Localizzazione, glossario, documenti menu, guida italiana v3, portali e suite smoke risultano gia' tracciati e verificati. |
| Release pubblica multilingue completa | Non ancora | La guida italiana e' la fonte v3 primaria, ma la propagazione multilingue completa va eseguita dopo il consolidamento del perimetro finale. |
| Nuove integrazioni portali | Non bloccanti per RC | La roadmap portali e il registro tecnico sono pronti per evoluzioni progressive senza bloccare la prima RC. |

## Criteri go/no-go per RC tecnica

| Area | Stato | Criterio |
| --- | --- | --- |
| Git e branch | Go | `main` deve essere allineato a `origin/main`, senza modifiche pendenti. |
| Localizzazione UI | Go | `verify_localization.py`, `validate_glossary.py` e `verify_glossary.py` devono essere verdi. |
| Glossario HTML | Go | Ogni modifica al glossario JSON deve avere HTML allineato oppure nota esplicita di follow-up prima del merge release. |
| Documenti menu | Go | `verify_document_assets.py` deve confermare presenza e link locali per disclaimer, presentazioni e guida. |
| Guida italiana | Go con rilettura finale | La guida italiana e' la baseline v3; Ricerca assistita AI, Traduzione OCR, GEDCOM e capability dei nuovi portali italiani sono documentate. Resta consigliata una rilettura editoriale di OCR Avanzato e FAQ. |
| Altre lingue | Go solo con dichiarazione | Per RC tecnica e' accettabile dichiarare che la guida italiana e' la fonte v3 primaria. Per release pubblica multilingue serve propagazione o nota visibile di stato. |
| Disclaimer e policy portali | Go con consenso revisionato | Il disclaimer esclude scraping massivo, aggiramento login/paywall e portali commerciali chiusi; la revisione v3 deve essere accettata esplicitamente prima di installazione, aggiornamento automatico o avvio portable/bundle. Fino alla propagazione multilingue, il testo legale vincolante e' quello italiano. |
| Policy runtime D/R portali | Go con re-check periodico | `src/portal_registry.py` applica `R_OK`, `R_LIMITED`, `D_ONLY` e `VARIABLE`; `verify_portal_policy.py` controlla scadenza delle policy e genera `portal_policy_overrides.json` per aggiornamenti locali senza nuova release. |
| Portali esistenti | Go italiano; verifica globale aperta | Registry e policy comprendono 25 capability. Lo smoke live del 2026-06-22 passa su tutti i portali italiani e su 24/25 campioni complessivi; Gallica resta da riallineare per risposta HTTP 403 del manifest campione. |
| Test tecnici | Go | Suite completa del 2026-06-22: 556 test passati e 38 skip attesi; verificatori guida italiana, asset documentali e policy portali superati. |
| Packaging | Go con build da eseguire | Audit non distruttivo eseguito: spec PyInstaller, script Inno e README workflow sono allineati a v3.0.0; prima della RC restano da generare e provare le build. |
| File temporanei | Go con controllo finale | Inventario root eseguito: artefatti locali, cache, build, log, screenshot e output test risultano ignorati o coperti da regole di esclusione; prima del tag resta da confermare `git status --short --ignored`. |

## Suite smoke pre-RC

Da eseguire su `main` pulito:

```powershell
python verify_localization.py
python validate_glossary.py
python verify_glossary.py
python verify_disclaimer_consent.py
python verify_document_assets.py
python verify_italian_guide_content.py
python verify_portal_matrix_workbook.py
python verify_portal_policy.py --strict
python -m py_compile src\main_gui_qt.py src\elaborazione.py src\manifest_utils.py src\tile_downloader.py src\qt_worker.py src\portal_registry.py verify_localization.py verify_disclaimer_consent.py verify_document_assets.py verify_italian_guide_content.py verify_portal_matrix_workbook.py verify_portal_live_smoke.py verify_portal_policy.py
python -m pytest tests\test_manifest_utils.py tests\test_manifest_parser.py tests\test_tile_downloader.py tests\test_qt_worker_coverage.py tests\test_portal_registry.py tests\test_portal_live_smoke_matrix.py -q
```

Controllo live portali, manuale e non sostitutivo dei test offline:

```powershell
python verify_portal_live_smoke.py --fetch-manifest --strict
```

Il comando richiede rete, usa `docs_generali/portal_live_smoke_samples.md` e
deve restare limitato a URL campione pubblici, no-login e coerenti con la
policy legale del portale.

## Verifiche manuali prima di RC

- Avvio dell'applicazione da build locale.
- Apertura del menu Documenti: guida, disclaimer, presentazione progetto e presentazione autore.
- Apertura della guida italiana e delle sotto-guide principali.
- Smoke dei sei servizi: Ricerca assistita AI, Visualizzazione Immagini,
  Visualizzazione Metadati JSON, OCR Avanzato, Traduzione OCR, Esportazione
  GEDCOM.
- Selezione portale e verifica degli avvisi per portali a cautela o da non
  estendere.
- Compilazione degli URL campione in `docs_generali/portal_live_smoke_samples.md`
  ed esecuzione dello smoke live dei portali implementati.
- Controllo che non siano inclusi file temporanei, lock file, output di test o
  log locali.
- Conferma che gli artefatti locali ignorati non siano necessari alla build o
  alla documentazione pubblica.
- Conferma che installer Windows, portable Windows, DMG/app macOS, pacchetto
  DEB, tarball Linux e aggiornamento automatico richiedano la revisione corrente
  del disclaimer prima di procedere.

## Bloccanti per release pubblica completa

- Propagazione multilingue della guida v3 oppure avviso chiaro e coerente nelle
  lingue non ancora riallineate.
- Propagazione multilingue del disclaimer legale v3; fino al completamento
  delle traduzioni, le build pubbliche devono mostrare e richiedere
  l'accettazione del testo legale italiano come fonte primaria.
- Verifica delle build pubbliche Windows, Linux e macOS, con note specifiche per
  eventuali piattaforme non testate su hardware reale.
- Aggiornamento changelog o note di rilascio v3.0.0.
- Tag e pacchetti generati da `main` pulito, dopo suite smoke verde.

## Documenti collegati

- `docs_generali/audit_contenuti_guida_v3_ATK-Pro.md`
- `docs_generali/audit_post_localizzazione_ATK-Pro.md`
- `docs_generali/roadmap_portali_ATK-Pro.md`
- `docs_generali/matrice_portali_esistenti_ATK-Pro.md`
- `docs_generali/matrice_portali_candidati_ATK-Pro.md`
- `docs_generali/portal_live_smoke_samples.md`
- `tests/roadmap_tests.md`
