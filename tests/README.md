# Test Suite - ATK-Pro v3

Questa cartella contiene la suite di test attiva del progetto ATK-Pro.
La fonte operativa aggiornata per baseline, smoke suite, fasi di
riallineamento e criteri di esecuzione e `tests/roadmap_tests.md`.

## Esecuzione rapida

Per la smoke suite consigliata e i verifier collegati, usare i comandi
documentati in `tests/roadmap_tests.md` e in
`docs_generali/checklist_release_v3_ATK-Pro.md`.

Per eseguire l'intera suite raccolta da `pytest.ini`:

```powershell
python -m pytest -q
```

## Note

- La suite attiva e' allineata al perimetro v3, non alla vecchia baseline v2.
- I test che toccano portali esterni devono preferire fixture offline, salvo
  verifiche manuali esplicitamente autorizzate.
- I marker `unit`, `integration`, `gui` e `playwright` sono assegnati in fase
  di raccolta da `tests/conftest.py`, per mantenere stabile la classificazione
  senza disseminare decoratori manuali.
- Il marker `network` esiste per usi futuri, ma allo stato attuale non viene
  usato dalla suite `pytest`: i controlli con rete reale restano nei verifier
  manuali come `verify_portal_live_smoke.py` e `verify_manifest_url.py`.
- Ogni baseline va dichiarata con comando effettivo, risultato osservato e
  data, senza riusare numeri storici fuori contesto.
