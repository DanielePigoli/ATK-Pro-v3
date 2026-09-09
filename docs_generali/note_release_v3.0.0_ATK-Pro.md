# Note release ATK-Pro v3.0.0

Data snapshot: 2026-09-09

ATK-Pro v3.0.0 e' la prima release stabile della serie 3. Nasce dalla RC4,
validata sui sei artefatti Windows, Linux e macOS, ed e' stata ricostruita con
versione finale prima della pubblicazione.

## Funzioni principali

- Download e ricostruzione locale da 28 portali pubblici supportati, nel
  rispetto delle policy `R_OK`, `R_LIMITED`, `D_ONLY` e `VARIABLE`.
- Biblioteca Digitale Lombarda multipagina tramite BookReader/Cantaloupe IIIF,
  con ricostruzione PDF da tutti i canvas, retry e fallback PDF REST.
- Visualizzazione immagini e metadati, OCR avanzato, traduzione OCR, ricerca
  assistita AI ed esportazione GEDCOM.
- Interfaccia, glossario e documentazione in 20 lingue, con 9 moduli guida per
  lingua.
- Preflight adattivo dei percorsi di output e cancellazione batch
  transazionale.

## Correzioni consolidate

- Recupero BDL multipagina e riduzione dei placeholder mediante retry mirati.
- Header corretti per le immagini Antenati.
- Pulizia completa del pacchetto Debian durante `apt purge`, senza rimuovere
  file sconosciuti o configurazioni utente.
- Smoke ripetibili sugli asset pubblicati per installer e portable Windows,
  DEB e tar Linux, DMG Intel e Apple Silicon.

## Baseline verificata

Il sorgente stabile ha superato il gate release locale: 841 test passati,
39 skip attesi e 11/11 step verdi.

RC4 ha inoltre superato:

- build Windows, Linux e macOS;
- verifica dei digest di tutti i sei asset;
- installazione, avvio e disinstallazione dell'installer Windows;
- estrazione, 20 lingue/locales e avvio del portable Windows;
- installazione DEB, avvio DEB/tar e purge pulito;
- integrita', architettura e avvio dei DMG su runner nativi Intel e ARM.

Rapporto completo:
[`note_release_v3.0.0-rc4_ATK-Pro.md`](note_release_v3.0.0-rc4_ATK-Pro.md).

## Artefatti stabili

La release `v3.0.0` e' stata costruita dal commit
`a992f76470f1ab2aa8fd1ebcfa6a7bd1a1ed6c17`.

| Piattaforma | Asset | SHA-256 |
|---|---|---|
| Windows | `ATK-Pro-Setup-v3.0.0.exe` | `c62d9df0c52e0c183db5dd1ccb6154066ba12ee0e360062e8b62fdefac5a7832` |
| Windows | `ATK-Pro-v3.0.0-Windows-Portable.zip` | `fa96d34a99524b8eb51d75686b7d54d39a108b9e7d983dbd2885f4295022f23f` |
| Linux | `ATK-Pro-Linux.deb` | `b34a55db75339085464e885e53d0b1300e0dc771276feafef268be2fa8f684d6` |
| Linux | `ATK-Pro-Linux.tar.gz` | `0e1f8c3179f7e7344d8c0adf0bd260eff42d03220caa68bc7ed42e07c5fb9ded` |
| macOS Intel | `ATK-Pro-macOS-Intel-v3.0.0.dmg` | `35688882ff5db2937f4d4eb979188d11e21dbc08dedec04309df3bb9e8c53481` |
| macOS Apple Silicon | `ATK-Pro-macOS-AppleSilicon-v3.0.0.dmg` | `9d40f7f7a4cdc050ac76e46f17fe9f07b899b85acd37edffb72b658b18652a4d` |

Build:

- Windows: [run 34332390873](https://github.com/DanielePigoli/ATK-Pro-v3/actions/runs/34332390873);
- Linux: [run 34332391022](https://github.com/DanielePigoli/ATK-Pro-v3/actions/runs/34332391022);
- macOS Intel e Apple Silicon: [run 34332390761, tentativo 2](https://github.com/DanielePigoli/ATK-Pro-v3/actions/runs/34332390761).

Smoke pre-pubblicazione sugli artifact esatti dei run:

- installer e portable Windows: [run 34337670295](https://github.com/DanielePigoli/ATK-Pro-v3/actions/runs/34337670295);
- DEB e tar Linux, incluso purge pulito: [run 34337673289](https://github.com/DanielePigoli/ATK-Pro-v3/actions/runs/34337673289);
- DMG Intel e Apple Silicon su runner nativi: [run 34337676543](https://github.com/DanielePigoli/ATK-Pro-v3/actions/runs/34337676543).

La release stabile e' stata pubblicata il 9 settembre 2026:
[ATK-Pro v3.0.0](https://github.com/DanielePigoli/ATK-Pro-v3/releases/tag/v3.0.0).

Smoke post-pubblicazione sugli asset della release:

- installer e portable Windows: [run 34338686481](https://github.com/DanielePigoli/ATK-Pro-v3/actions/runs/34338686481), PASS al primo tentativo;
- DEB e tar Linux, incluso purge pulito: [run 34338689472](https://github.com/DanielePigoli/ATK-Pro-v3/actions/runs/34338689472), PASS al primo tentativo;
- DMG Intel e Apple Silicon su runner nativi: [run 34338692849](https://github.com/DanielePigoli/ATK-Pro-v3/actions/runs/34338692849), PASS al primo tentativo.

## Limitazioni note

- Le build macOS sono firmate ad-hoc e non notarizzate; macOS puo' richiedere
  una conferma esplicita dell'utente al primo avvio.
- I portali esterni possono modificare endpoint, policy o disponibilita';
  l'applicazione applica limiti prudenziali e il registro policy deve essere
  ricontrollato periodicamente.
- OCR, traduzioni e risultati AI richiedono verifica sulle fonti originali.

## Licenze e responsabilita'

Il codice e' distribuito secondo GNU AGPL v3 o successiva. La documentazione
originale e' distribuita secondo CC BY-NC-SA 4.0, salvo diversa indicazione.
Nome, logo e segni distintivi restano disciplinati da `TRADEMARKS.md`.

L'uso del software richiede l'accettazione del disclaimer legale revisione
`v3.0.0-legal-disclaimer-2026-08-02`.
