# Note release ATK-Pro v3.0.0 RC3

Data snapshot: 2026-09-01

Questa release candidate consolida il lavoro successivo a RC2 e costituisce la
candidata da validare sulle tre piattaforme prima della promozione stabile.

## Principali novita rispetto a RC2

- Biblioteca Digitale Lombarda multipagina tramite
  `/bdl/public/rest/json/item/{id}/bookreader/pages` e immagini Cantaloupe IIIF.
- Ricostruzione PDF BDL da tutti i canvas, con retry dei download falliti e
  fallback al PDF REST diretto quando la sequenza BookReader non e' disponibile.
- Guide e documenti allineati nelle 20 lingue supportate.
- Preflight adattivo dei percorsi di output e cancellazione batch
  transazionale.
- Consolidamento dei portali pubblici supportati e delle relative policy.

## Audit portali pre-RC3

Il 2026-09-01 sono stati verificati tutti i 28 portali della matrice pubblica.
Per ciascun caso sono stati risolti il manifest reale o sintetico e, dove il
volume e' multipagina, tre canvas equidistanti (inizio, centro, fine). Le
immagini sono state scaricate, decodificate con Pillow e confrontate tramite
hash.

Esito finale: 28/28 portali PASS. BDL ha esposto 12 canvas reali; DOGE 373.
Antenati ha richiesto gli header `Referer` e `Origin` gia' utilizzati dal tile
downloader dell'app.

Comando di riferimento:

```powershell
python verify_portal_live_smoke.py --fetch-images --strict
```

## Verifiche sorgente

- `python scripts\quality_gate.py release` -> PASS.
- Suite completa: 834 test passati, 38 skip attesi.
- Asset documentali: 20 lingue, 9 moduli guida per lingua.
- Matrici: 28 portali esistenti e 37 candidati allineati.
- Policy: nessuna capability scaduta o override locale attivo.
- Igiene release: oltre 78.000 artefatti generati ignorati, nessuno committabile.

## Stato artefatti

Da compilare dopo il tag RC3:

| Piattaforma | Artefatto | Build | Smoke | SHA256 |
| --- | --- | --- | --- | --- |
| Windows | Installer Inno Setup | In attesa | In attesa | In attesa |
| Windows | Portable ZIP | In attesa | In attesa | In attesa |
| macOS Intel | DMG | In attesa | In attesa | In attesa |
| macOS Apple Silicon | DMG | In attesa | In attesa | In attesa |
| Linux | DEB | In attesa | In attesa | In attesa |
| Linux | tar.gz | In attesa | In attesa | In attesa |

## Go/no-go verso v3.0.0 stabile

La promozione resta bloccata fino a quando build, CI e smoke degli artefatti
RC3 non sono verdi. Le build macOS sono ad-hoc signed e non notarizzate: questa
limitazione deve restare esplicita nelle indicazioni ai tester.
