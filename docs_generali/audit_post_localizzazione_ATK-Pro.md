# Audit post-localizzazione ATK-Pro

Data snapshot: 2026-05-25

Questo audit leggero fotografa lo stato del progetto dopo il completamento del
processo di localizzazione UI e prima di aprire una nuova fase sui portali.

Nota successiva 2026-05-26: i punti documentali indicati come prossime mosse
sono stati affrontati in PR successive. README macOS/Linux, `requirements.txt`,
`tests/roadmap_tests.md`, matrice portali e roadmap portali sono ora allineati
alla fase v3; questo file resta come snapshot storico post-localizzazione.

## Stato Git

- Al momento dello snapshot, `main` risultava allineato a `origin/main` dopo
  il primo ciclo post-localizzazione allora disponibile.
- La localizzazione e la policy portali risultavano gia integrate nel ramo
  principale.
- Il riferimento al ramo operativo di quel passaggio resta storico e non va
  letto come branch di lavoro corrente.

## Verifiche eseguite

Comandi eseguiti con esito positivo:

- `python verify_localization.py`
- `python validate_glossary.py`
- `python verify_glossary.py`
- `python -m py_compile src\main_gui_qt.py src\elaborazione.py src\manifest_utils.py src\tile_downloader.py src\qt_worker.py verify_localization.py`

Risultato rilevante della localizzazione:

- `No obvious hard-coded UI strings found.`

Subset test eseguito:

- `python -m pytest tests\test_manifest_utils.py tests\test_manifest_parser.py tests\test_tile_downloader.py tests\test_qt_worker_coverage.py -q`
- risultato dopo riallineamento test: `43 passed in 27.65s`

Durante il subset test e stato trovato un test obsoleto in `tests/test_tile_downloader.py`:
il mock di `download_tile` usava ancora la vecchia firma a 5 argomenti, mentre
la funzione oggi riceve anche qualita, dimensioni immagine e delay. Il test e
stato aggiornato con `*args`, senza modificare la logica applicativa.

## Stato tecnico sintetico

Punti solidi:

- la localizzazione e verificabile automaticamente e ora il report e pulito;
- il glossario JSON e coerente e copre le lingue supportate;
- i moduli centrali della pipeline portali compilano;
- il subset di test piu vicino a manifest, tile e worker passa;
- la policy portali e documentata in
  `docs_generali/valutazione_portali_ATK-Pro.md`.

Punti fragili o da sorvegliare:

- la logica portali e ancora accoppiata tra UI, `Elaborazione`, `manifest_utils`
  e `tile_downloader`;
- alcuni portali usano manifest sintetici o fallback da HTML/endpoint non
  standard: vanno classificati portale per portale prima di aggiungere nuove
  integrazioni;
- al momento dello snapshot, `README_MACOS.txt` e `README_LINUX.txt` erano
  ancora allineati a v2.2.0, citavano il repository v2 e un disclaimer piu
  vecchio basato su "Canvas LMS";
- al momento dello snapshot, `requirements.txt` mostrava ancora qualche
  incertezza documentale e andava ricontrollato in una fase dependency
  separata;
- al momento dello snapshot, `tests/roadmap_tests.md` descriveva una
  situazione v2.0 e poteva non rappresentare lo stato reale della suite v3.0;
- la root contiene molti file temporanei, log, output di test e script
  diagnostici: serve una passata di inventario prima di una release pulita.

Nota successiva 2026-07-26 sui punti sopra:

- i README macOS/Linux e `tests/roadmap_tests.md` non sono piu criticita
  aperte, perche sono stati riallineati in blocchi successivi;
- `requirements.txt` non presenta piu l'anomalia descritta in modo troppo
  specifico nello snapshot; resta al piu una manutenzione leggera dei commenti
  e delle note di contesto;
- questo file va quindi letto come fotografia del rischio emerso a fine maggio,
  non come elenco aggiornato dei debiti ancora aperti.

## Lettura architetturale portali

Flusso attuale:

1. `src/main_gui_qt.py` permette di scegliere `portale_attivo`.
2. Il portale viene passato a `ElaborazioneWorker`.
3. `src/elaborazione.py` usa il portale per risolvere manifest, referer,
   fallback Playwright e casi speciali.
4. `src/manifest_utils.py` contiene builder diretti e sintetici.
5. `src/tile_downloader.py` scarica tile IIIF e gestisce differenze operative
   come Gallica/Heidelberg.

Indicazione: prima di aggiungere altri portali conviene creare una matrice
esplicita con capability tecniche e rischio legale/manutentivo. Una piccola
tabella `portale -> metodo -> termini -> rischio -> priorita` ridurrebbe il
rischio di integrazioni fragili o non coerenti con il disclaimer.

## Prossime mosse consigliate

1. Eseguire una passata di inventario su file temporanei, log e output locali
   prima di una release pulita.
2. Continuare il consolidamento della matrice/roadmap portali come fonte di
   priorita, rischio e metodo tecnico.
3. Solo dopo, valutare nuovi portali pubblici/istituzionali con IIIF/API o
   documentazione tecnica chiara.
