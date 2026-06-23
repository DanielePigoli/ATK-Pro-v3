# Note release ATK-Pro v3.0.0 RC2

Data snapshot: 2026-06-23

Questa release candidate aggiorna la RC1 dopo il primo riscontro esterno sulla
build Windows portable.

## Correzioni rispetto a RC1

| Area | Correzione |
| --- | --- |
| Ricerca Assistita AI | Corretto l'errore `cannot access local variable 'json' where it is not associated with a value`, emerso con provider Gemini in caso di errore prima della serializzazione del risultato. |
| OCR Gemini | Reso piu' robusto il merge TOP/BOTTOM sulle immagini divise con sovrapposizione, evitando doppioni nell'area comune e recuperando colonne vuote dal segmento sovrapposto superiore. |

## Stato

- La RC2 sostituisce la RC1 per i tester.
- La RC1 resta come storico di pre-release, ma non dovrebbe piu' essere
  distribuita come build di prova principale.
- La revisione del disclaimer legale non cambia: chi ha gia' accettato il
  disclaimer v3 non deve riaccettarlo per il solo passaggio RC1 -> RC2.

## Verifiche locali

- `python -m py_compile src\RicercaAssistitaAI.py src\ocr_processor.py`
- `python -m pytest tests\test_ai_ocr_regressions.py -q`
- `python -m pytest tests\test_ai_ocr_regressions.py tests\test_qt_worker_coverage.py -q`
- `python -m pytest tests\test_atk_version.py tests\test_ui_info.py -q`
- `git diff --check`

## Da verificare sui pacchetti RC2

- Avvio, disclaimer e finestra Informazioni: deve comparire `ATK-Pro v3.0.0 RC2`.
- Ricerca Assistita AI con chiave Gemini.
- OCR Gemini su immagine doppia/registro con split TOP/BOTTOM.
- Smoke rapido su almeno un download gia' validato in RC1.
