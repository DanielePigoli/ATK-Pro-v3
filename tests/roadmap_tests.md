# Roadmap test - ATK-Pro v3.0

Data snapshot: 2026-05-26

Questa roadmap sostituisce la precedente fotografia v2.0. I numeri storici
249/296 non vengono piu usati come baseline, perche non descrivono lo stato
post-localizzazione e post-audit del progetto v3.

## Baseline verificata

Verifiche generali gia verdi:

- `python verify_localization.py`
- `python validate_glossary.py`
- `python verify_glossary.py`
- `python -m py_compile src\main_gui_qt.py src\elaborazione.py src\manifest_utils.py src\tile_downloader.py src\qt_worker.py verify_localization.py`

Subset portali/manifest/tile/worker:

- comando:
  `python -m pytest tests\test_manifest_utils.py tests\test_manifest_parser.py tests\test_tile_downloader.py tests\test_qt_worker_coverage.py -q`
- risultato verificato:
  `43 passed`

Nota: durante l'audit post-localizzazione e stato riallineato il mock di
`tests/test_tile_downloader.py` alla firma attuale di `download_tile`.

## Obiettivi v3

- Mantenere verde il controllo di localizzazione e glossario.
- Stabilizzare la pipeline portali: manifest, tile, worker e fallback.
- Distinguere test unitari puri da test che richiedono rete, GUI, browser o
  servizi esterni.
- Evitare baseline numeriche obsolete: ogni milestone deve dichiarare comando,
  risultato e data.
- Preparare una suite smoke veloce da eseguire prima di ogni PR tecnica.

## Suite smoke consigliata

Usare come controllo rapido dopo modifiche a localizzazione, portali o pipeline:

```powershell
python verify_localization.py
python validate_glossary.py
python verify_glossary.py
python -m py_compile src\main_gui_qt.py src\elaborazione.py src\manifest_utils.py src\tile_downloader.py src\qt_worker.py verify_localization.py
python -m pytest tests\test_manifest_utils.py tests\test_manifest_parser.py tests\test_tile_downloader.py tests\test_qt_worker_coverage.py -q
```

## Piano di riallineamento

### Fase 1 - Baseline stabile

- [x] Confermare localizzazione e glossario.
- [x] Confermare compilazione dei moduli centrali.
- [x] Confermare subset portali/manifest/tile/worker.
- [ ] Eseguire una suite piu ampia in ambiente controllato.
- [ ] Documentare numero totale di test pass/fail/skip aggiornato a v3.

### Fase 2 - Classificazione test

- [ ] Marcare test che richiedono rete reale.
- [ ] Marcare test che richiedono GUI/Qt visibile.
- [ ] Marcare test che richiedono Playwright/browser.
- [ ] Separare test unitari puri da test di integrazione.
- [ ] Ridurre dipendenze da percorsi locali storici in `tests/conftest.py`.

### Fase 3 - Portali

- [ ] Estendere i test su `manifest_utils` per i portali gia presenti.
- [ ] Aggiungere fixture offline per manifest IIIF v2/v3 rappresentativi.
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
- I test che toccano portali esterni devono preferire fixture offline, salvo
  quando si sta eseguendo una verifica manuale esplicitamente autorizzata.
- Le integrazioni con portali chiusi, commerciali, login, abbonamenti o paywall
  restano fuori dallo scope supportato, salvo autorizzazione espressa e
  documentata.
