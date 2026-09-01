# Note release ATK-Pro v3.0.0 RC3

Data snapshot: 2026-09-02

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

Pre-release pubblicata: `v3.0.0-rc3` sul commit merge `cef8bac`.

| Piattaforma | Artefatto | Build | Smoke | SHA256 |
| --- | --- | --- | --- | --- |
| Windows | `ATK-Pro-Setup-v3.0.0-rc3.exe` | PASS | Verifica Inno Setup in CI; installazione locale da eseguire | `0BC81D631A6FE58E953567A8C5AFEAC585C4E85FA6969C12F386BEEC3253529D` |
| Windows | `ATK-Pro-v3.0.0-rc3-Windows-Portable.zip` | PASS | PASS: hash, struttura, 20 lingue e avvio offscreen locale responsivo | `CC98BDD1AED4184E23CBEE2106E384632E622A7529C1BC862CF5563A762EFBD2` |
| macOS Intel | `ATK-Pro-macOS-Intel-v3.0.0-rc3.dmg` | PASS | Firma ad-hoc e DMG verificati in CI; avvio su hardware da eseguire | `EC2D089CC850D732F7C479683B95D213C8EE3D2CF042D836316BC30A4886BF2C` |
| macOS Apple Silicon | `ATK-Pro-macOS-AppleSilicon-v3.0.0-rc3.dmg` | PASS | Firma ad-hoc e DMG verificati in CI; avvio su hardware da eseguire | `09DB09DDBEA014A1E2648FDB8AFB4746AAFE14282479BBBB971F4969C075E5CA` |
| Linux | `ATK-Pro-Linux.deb` | PASS | Binario PASS offscreen e Xvfb in CI; installazione DEB da eseguire | `F6EC76724CA5DA789A4515492E909B25737ABC95C5830AE554A8F8338B32C8AB` |
| Linux | `ATK-Pro-Linux.tar.gz` | PASS | Binario PASS offscreen e Xvfb in CI; estrazione pacchetto non rieseguita separatamente | `0449E1E83093173DF09A994AA7C319C7BDC330EECC72E225B0C243E519BE41AB` |

I workflow sono verdi: Windows 14m24s, Linux 6m50s piu' smoke nativo,
macOS Apple Silicon 11m31s e Intel 22m49s. I warning sulle action forzate da
Node 20 a Node 24 e sul tap Homebrew `aws/tap` ignorato non hanno inciso sulle
build.

## Go/no-go verso v3.0.0 stabile

La promozione resta bloccata in attesa di tre verifiche: installazione reale
dell'installer Windows, installazione dei pacchetti Linux e avvio dei due DMG
su hardware macOS compatibile. Le build macOS sono ad-hoc signed e non
notarizzate: questa limitazione deve restare esplicita nelle indicazioni ai
tester. Non e' emerso alcun regressivo bloccante dal codice sorgente, dal
portable Windows o dallo smoke nativo Linux.
