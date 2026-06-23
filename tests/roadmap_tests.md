# Roadmap test - ATK-Pro v3.0

Data snapshot: 2026-05-27

Questa roadmap sostituisce la precedente fotografia v2.0. I numeri storici
249/296 non vengono piu usati come baseline, perche non descrivono lo stato
post-localizzazione e post-audit del progetto v3.

## Baseline verificata

Verifiche generali gia verdi:

- `python verify_localization.py`
- `python validate_glossary.py`
- `python verify_glossary.py`
- `python verify_disclaimer_consent.py`
- `python verify_document_assets.py`
- `python verify_italian_guide_content.py`
- `python verify_portal_matrix_workbook.py`
- `python verify_portal_policy.py --strict`
- `python -m py_compile src\main_gui_qt.py src\elaborazione.py src\manifest_utils.py src\tile_downloader.py src\qt_worker.py src\portal_registry.py verify_localization.py verify_disclaimer_consent.py verify_document_assets.py verify_italian_guide_content.py verify_portal_matrix_workbook.py verify_portal_live_smoke.py verify_manifest_url.py verify_portal_policy.py`

Nota pre-release: `verify_document_assets.py` controlla presenza e link locali
dei documenti, non la qualita contenutistica della guida. L'audit contenutistico
pre-RC e tracciato in `docs_generali/audit_contenuti_guida_v3_ATK-Pro.md`.
La checklist di go/no-go per RC tecnica e release pubblica v3 e tracciata in
`docs_generali/checklist_release_v3_ATK-Pro.md`.

Baseline portali italiani/italofoni del 2026-06-22:

- suite completa: 556 test passati, 38 skip attesi;
- policy registry: 25 capability valide, nessun re-check scaduto;
- smoke live: tutti i portali italiani superati; matrice globale 24/25, con
  Gallica ancora aperta per risposta HTTP 403 del manifest campione.

Subset portali/manifest/tile/worker:

- comando:
  `python -m pytest tests\test_manifest_utils.py tests\test_manifest_parser.py tests\test_tile_downloader.py tests\test_qt_worker_coverage.py tests\test_portal_registry.py tests\test_portal_live_smoke_matrix.py -q`

Probe manifest diretto:

- `python verify_manifest_url.py --url "<manifest-url>" --referer "<referer-opzionale>"`
  verifica un manifest IIIF diretto fuori dalla matrice live smoke, scaricandolo
  con la stessa utility usata da ATK-Pro e contando canvas/items.
- risultato verificato:
  `66 passed`

Aggiornamento 2026-06-02: il subset include fixture offline per manifest IIIF
v3 image-only e link viewer Mirador con parametro `manifestId`, normalizzati
verso la pipeline interna `sequences/canvases`.

Aggiornamento 2026-06-02: `tests/test_portal_registry.py` copre anche le policy
`R_OK`, `R_LIMITED`, `D_ONLY`, `VARIABLE`, gli override locali
`portal_policy_overrides.json` e il re-check periodico indipendente dalla
release.

Nota: durante l'audit post-localizzazione e stato riallineato il mock di
`tests/test_tile_downloader.py` alla firma attuale di `download_tile`.

## Suite ampia

Comando standard:

```powershell
python -m pytest -q
```

Stato snapshot 2026-05-27:

- Discovery limitata a `tests/` tramite `pytest.ini`, per evitare che script di
  diagnostica locali ignorati nella root vengano raccolti come test.
- Prima correzione eseguita: import logger ripristinati in `src/image_rebuilder.py`
  e `src/pdf_utils.py`.
- Risultato iniziale osservato: `427 passed, 25 failed, 36 skipped`.

I fallimenti residui sono concentrati in test storici o non ancora riallineati
alla v3:

- test Playwright/canvas che assumono percorsi abilitati anche quando
  l'estrazione via browser e' disabilitata;
- mock non aggiornati alle firme v3 con parametri `source_url` e `portale`;
- test che cercano asset v2 o posizioni storiche, come glossario in root o
  installer precedenti alla v3;
- aspettative UI datate su titolo applicazione e testo del progress dialog.

Primo riallineamento successivo:

- test glossario aggiornati al percorso `docs_generali/glossario_multilingua_ATK-Pro.json`;
- test glossario aggiornati al formato v3 basato su chiavi voce e liste di
  traduzioni, senza metadata v2;
- test artifact build aggiornati al layout v3 e saltati quando i pacchetti non
  sono stati ancora generati;
- aspettative UI v2 piu' semplici aggiornate per titolo app e progress dialog.

Risultato dopo il riallineamento dei test v2 oggettivi: `432 passed, 18 failed,
38 skipped`.

Secondo riallineamento successivo:

- mock di pipeline canvas/PDF aggiornati alle firme v3 con `source_url` e
  `portale`;
- fake `Elaborazione` del worker aggiornato per accettare keyword future senza
  bloccare il test di conferma PDF.

Risultato dopo il riallineamento dei mock pipeline v3: `443 passed, 7 failed,
38 skipped`.

Terzo riallineamento successivo:

- test headless aggiornato per passare uno stato esplicito a
  `esegui_elaborazione`;
- corretto il log iniziale di `esegui_elaborazione`, che usava variabili prima
  dell'assegnazione;
- mock `Image.new` in `test_image_rebuilder.py` aggiornato alla firma PIL usata
  dalla ricostruzione con colore di sfondo.

Risultato dopo il riallineamento headless/rebuilder: `445 passed, 5 failed,
38 skipped`.

Quarto riallineamento successivo:

- percorso Playwright di `extract_ud_canvas_id_from_infojson_xhr` riattivato in
  ambiente sviluppo/test e mantenuto disabilitato in PyInstaller compilato;
- fallback su URL XHR, HTML pagina e frame coperti dai test;
- marker `gui` registrato in `pytest.ini` per eliminare warning di raccolta.

Risultato dopo il riallineamento canvas/Playwright: `450 passed, 38 skipped`.

La suite ampia e' ora verde; gli skip residui sono test dichiarati non
applicabili o dipendenti da componenti non implementati/esterni.

Questa suite non e' ancora criterio bloccante per RC tecnica; va trasformata in
baseline completa tramite riallineamenti mirati e PR dedicate.

## Obiettivi v3

- Mantenere verde il controllo di localizzazione e glossario.
- Stabilizzare la pipeline portali: manifest, tile, worker e fallback.
- Distinguere test unitari puri da test che richiedono rete, GUI, browser o
  servizi esterni.
- Limitare la discovery standard di pytest a `tests/`, evitando che script di
  diagnostica locali ignorati nella root vengano raccolti come test.
- Evitare baseline numeriche obsolete: ogni milestone deve dichiarare comando,
  risultato e data.
- Preparare una suite smoke veloce da eseguire prima di ogni PR tecnica.

## Suite smoke consigliata

Usare come controllo rapido dopo modifiche a localizzazione, portali o pipeline:

```powershell
python verify_localization.py
python validate_glossary.py
python verify_glossary.py
python verify_document_assets.py
python verify_italian_guide_content.py
python verify_portal_matrix_workbook.py
python -m py_compile src\main_gui_qt.py src\elaborazione.py src\manifest_utils.py src\tile_downloader.py src\qt_worker.py verify_localization.py verify_document_assets.py verify_italian_guide_content.py verify_portal_matrix_workbook.py verify_portal_live_smoke.py
python -m pytest tests\test_manifest_utils.py tests\test_manifest_parser.py tests\test_tile_downloader.py tests\test_qt_worker_coverage.py tests\test_portal_live_smoke_matrix.py -q
```

## Piano di riallineamento

### Fase 1 - Baseline stabile

- [x] Confermare localizzazione e glossario.
- [x] Confermare documenti consultabili dal menu Documenti e guida articolata.
- [x] Riallineare contenutisticamente la guida italiana alla v3 reale.
- [x] Confermare compilazione dei moduli centrali.
- [x] Confermare subset portali/manifest/tile/worker.
- [x] Eseguire una suite piu ampia in ambiente controllato.
- [x] Documentare numero totale di test pass/fail/skip aggiornato a v3.

### Fase 2 - Classificazione test

- [ ] Marcare test che richiedono rete reale.
- [ ] Marcare test che richiedono GUI/Qt visibile.
- [ ] Marcare test che richiedono Playwright/browser.
- [ ] Separare test unitari puri da test di integrazione.
- [ ] Ridurre dipendenze da percorsi locali storici in `tests/conftest.py`.

### Fase 3 - Portali

- [ ] Estendere i test su `manifest_utils` per i portali gia presenti.
- [x] Aggiungere fixture offline per manifest IIIF v2/v3 rappresentativi.
- [ ] Aggiungere test per fallback sintetici solo dove legalmente e
  tecnicamente giustificati.
- [ ] Collegare ogni nuovo portale alla matrice di valutazione tecnica/legale.

### Fase 4 - Release hygiene

- [ ] Inventariare file temporanei, log e output generati nella root.
- [ ] Aggiornare documentazione test in base alla suite realmente eseguita.
- [ ] Definire un comando smoke per PR e un comando completo per release.

## Note operative

- Non aggiornare questa roadmap con numeri stimati.
- Ogni baseline deve riportare il comando effettivo e il risultato osservato.
- Baseline RC1 Windows portable del 2026-06-23: `python -m pytest -q` ha
  restituito 559 test passati e 38 skip; la suite mirata RC1 ha restituito 28
  test passati.
- La guida italiana e' la fonte contenutistica v3 primaria; le altre lingue
  restano da riallineare o dichiarare esplicitamente come traduzioni successive
  prima di una release pubblica multilingue completa.
- I test che toccano portali esterni devono preferire fixture offline, salvo
  quando si sta eseguendo una verifica manuale esplicitamente autorizzata.
- Le integrazioni con portali chiusi, commerciali, login, abbonamenti o paywall
  restano fuori dallo scope supportato, salvo autorizzazione espressa e
  documentata.
