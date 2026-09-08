# Note release ATK-Pro v3.0.0 RC3

Data snapshot: 2026-09-08

Questa release candidate consolida il lavoro successivo a RC2. Il ciclo di
validazione post-pubblicazione e' stato completato sulle tre piattaforme; i suoi
risultati definiscono il percorso verso la candidata successiva.

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

- Baseline RC3 al tag: `python scripts\quality_gate.py release` -> PASS,
  834 test passati e 38 skip attesi.
- Verifica ripetuta su `main` dopo il fix DEB, il 2026-09-08: PASS,
  837 test passati e 39 skip attesi.
- Asset documentali: 20 lingue, 9 moduli guida per lingua.
- Matrici: 28 portali esistenti e 37 candidati allineati.
- Policy: nessuna capability scaduta o override locale attivo.
- Igiene release: oltre 78.000 artefatti generati ignorati, nessuno committabile.

## Stato artefatti

Pre-release pubblicata: `v3.0.0-rc3` sul commit merge `cef8bac`.

| Piattaforma | Artefatto | Build | Smoke | SHA256 |
| --- | --- | --- | --- | --- |
| Windows | `ATK-Pro-Setup-v3.0.0-rc3.exe` | PASS | PASS: hash, installazione silenziosa con consenso, registro/versione/percorso, avvio 20 s e disinstallazione pulita | `0BC81D631A6FE58E953567A8C5AFEAC585C4E85FA6969C12F386BEEC3253529D` |
| Windows | `ATK-Pro-v3.0.0-rc3-Windows-Portable.zip` | PASS | PASS: hash, struttura, 20 lingue e avvio offscreen locale responsivo | `CC98BDD1AED4184E23CBEE2106E384632E622A7529C1BC862CF5563A762EFBD2` |
| macOS Intel | `ATK-Pro-macOS-Intel-v3.0.0-rc3.dmg` | PASS | PASS su runner Intel nativo: hash, integrita' DMG, mount, x86_64, firma embedded, plist e avvio 20 s | `EC2D089CC850D732F7C479683B95D213C8EE3D2CF042D836316BC30A4886BF2C` |
| macOS Apple Silicon | `ATK-Pro-macOS-AppleSilicon-v3.0.0-rc3.dmg` | PASS | PASS su runner ARM nativo: hash, integrita' DMG, mount, arm64, firma embedded, plist e avvio 20 s | `09DB09DDBEA014A1E2648FDB8AFB4746AAFE14282479BBBB971F4969C075E5CA` |
| Linux | `ATK-Pro-Linux.deb` | PASS build/install/avvio; FAIL purge | L'asset RC3 si installa e si avvia 20 s, ma il purge lascia `/etc/atk-pro/defaults.json` e `disclaimer_revision`; fix verificato su nuovi artefatti da `main` | `F6EC76724CA5DA789A4515492E909B25737ABC95C5830AE554A8F8338B32C8AB` |
| Linux | `ATK-Pro-Linux.tar.gz` | PASS | PASS: hash, struttura, documenti e avvio 20 s con Xvfb | `0449E1E83093173DF09A994AA7C319C7BDC330EECC72E225B0C243E519BE41AB` |

Evidenze post-pubblicazione:

- Windows installer RC3: run [`33986729587`](https://github.com/DanielePigoli/ATK-Pro-v3/actions/runs/33986729587), completamente verde.
- Linux asset RC3: run [`33987191663`](https://github.com/DanielePigoli/ATK-Pro-v3/actions/runs/33987191663); installazione e avvii verdi, unico
  fallimento sul residuo dopo purge.
- Linux build corretta da `main`: run [`33987692717`](https://github.com/DanielePigoli/ATK-Pro-v3/actions/runs/33987692717); smoke dei relativi
  artefatti: run [`33988091039`](https://github.com/DanielePigoli/ATK-Pro-v3/actions/runs/33988091039), completamente verde incluso il purge.
- macOS RC3 Intel e Apple Silicon: run [`33989794600`](https://github.com/DanielePigoli/ATK-Pro-v3/actions/runs/33989794600), completamente verde su
  runner nativi dal workflow integrato in `main`.

I warning sulle action forzate da Node 20 a Node 24 non hanno inciso sui test.
Le build macOS restano firmate ad-hoc e non notarizzate.

## Go/no-go verso v3.0.0 stabile

Le verifiche Windows, Linux e macOS sono concluse. Non sono emersi regressivi
bloccanti nell'applicazione; e' emerso un difetto reale ma circoscritto nel
pacchetto DEB RC3: `apt purge` non elimina due file di configurazione di
sistema.

Il difetto e' corretto su `main` tramite lo script `postrm`, con test mirati
e un nuovo ciclo build/installazione/avvio/purge completamente verde. Di
conseguenza non e' corretto promuovere o rinominare gli asset RC3 invariati:
la prossima candidata deve essere ricostruita da un tag che includa il fix e
sottoposta agli smoke sugli asset esatti.

Decisione: no-go alla promozione diretta di RC3; go tecnico alla preparazione di
RC4. Se anche i sei asset RC4 superano gli smoke, RC4 potra' essere promossa a
`v3.0.0` stabile mediante una nuova build finale. La firma macOS ad-hoc e la
mancata notarizzazione devono restare esplicite nelle indicazioni agli utenti.
