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
- Ogni baseline va dichiarata con comando effettivo, risultato osservato e
  data, senza riusare numeri storici fuori contesto.
