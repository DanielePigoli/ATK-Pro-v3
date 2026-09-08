# Note release ATK-Pro v3.0.0 RC4

Data snapshot: 2026-09-08

RC4 ricostruisce tutti gli artefatti da `main` dopo il collaudo
multipiattaforma di RC3. Non introduce nuove funzioni applicative rispetto a
RC3: chiude il difetto di pulizia del pacchetto Debian e rende ripetibili gli
smoke sugli asset pubblicati.

## Motivo della nuova candidata

L'asset `ATK-Pro-Linux.deb` di RC3 si installa e si avvia correttamente, ma
`apt purge` lascia due file di configurazione di sistema:

- `/etc/atk-pro/defaults.json`
- `/etc/atk-pro/disclaimer_revision`

La correzione aggiunge un `postrm` conservativo, eseguito solo durante
`purge`: elimina esclusivamente i file ATK-Pro noti, usa `rmdir` non
ricorsivo per non rimuovere contenuti sconosciuti e non tocca le configurazioni
utente nelle directory home.

## Verifiche gia' concluse

- Gate release su `main`: 837 test passati, 39 skip attesi, 11/11 step verdi.
- Test mirati del packaging Debian: 3 passati e 1 skip atteso su Windows; la
  validazione POSIX e' eseguita dal runner Linux.
- Build Linux corretta: run
  [`33987692717`](https://github.com/DanielePigoli/ATK-Pro-v3/actions/runs/33987692717).
- Smoke dei nuovi artefatti Linux: run
  [`33988091039`](https://github.com/DanielePigoli/ATK-Pro-v3/actions/runs/33988091039),
  con installazione, due avvii da 20 secondi e purge pulito.
- Installer Windows RC3: run
  [`33986729587`](https://github.com/DanielePigoli/ATK-Pro-v3/actions/runs/33986729587),
  con installazione, avvio e disinstallazione pulita.
- DMG RC3 Intel e Apple Silicon: run
  [`33989794600`](https://github.com/DanielePigoli/ATK-Pro-v3/actions/runs/33989794600),
  entrambi avviati su runner nativi.

## Artefatti RC4 pubblicati

Pre-release: [`v3.0.0-rc4`](https://github.com/DanielePigoli/ATK-Pro-v3/releases/tag/v3.0.0-rc4),
tag sul commit `598124f`.

| Piattaforma | Artefatto | SHA-256 |
| --- | --- | --- |
| Windows | `ATK-Pro-Setup-v3.0.0-rc4.exe` | `EB57B2DC933DC106DB79352D3E9F89F3B451EE902F28DD1EBE5B23311EEF57CF` |
| Windows | `ATK-Pro-v3.0.0-rc4-Windows-Portable.zip` | `204333D2AEAB38D67AD937FD54CD2A4C83AA7B220275594F2EA7C695357ACB33` |
| Linux | `ATK-Pro-Linux.deb` | `56C16950576487FA7B7A3117B063D2B42AC87275C03E252FAB0AE7F821286D3E` |
| Linux | `ATK-Pro-Linux.tar.gz` | `799A6EB8DAFF1BB287D25D76F014D9535CA709DD107D774C1DF400116BE4A65D` |
| macOS Intel | `ATK-Pro-macOS-Intel-v3.0.0-rc4.dmg` | `A3B9A31111C82BCF2147BFD39BEC9B305ECF69D213E31FA3986F65A7C967A38A` |
| macOS Apple Silicon | `ATK-Pro-macOS-AppleSilicon-v3.0.0-rc4.dmg` | `4381D4547CCEBFCAF56AEF8AA2741253DAC9D8A0A89958E142BABD261C358AB2` |

Sono pubblicati anche i sidecar SHA-256 del DEB e del tarball.

## Build e smoke RC4

Build del tag:

- Windows: [`34222899141`](https://github.com/DanielePigoli/ATK-Pro-v3/actions/runs/34222899141), PASS.
- Linux: [`34222899176`](https://github.com/DanielePigoli/ATK-Pro-v3/actions/runs/34222899176), PASS al tentativo 2; il primo download dell'artefatto standalone era transitoriamente tronco, mentre build, pacchetti e upload erano gia' verdi.
- macOS Intel e Apple Silicon: [`34222899126`](https://github.com/DanielePigoli/ATK-Pro-v3/actions/runs/34222899126), PASS.

Smoke sugli asset pubblicati esatti:

- installer e portable Windows: [`34226761186`](https://github.com/DanielePigoli/ATK-Pro-v3/actions/runs/34226761186), PASS; include hash, 20 lingue/locales, installazione o estrazione, avvio 20 s e pulizia;
- DEB e tar Linux: [`34224910666`](https://github.com/DanielePigoli/ATK-Pro-v3/actions/runs/34224910666), PASS; include entrambi gli avvii e purge pulito;
- DMG Intel e Apple Silicon: [`34224913543`](https://github.com/DanielePigoli/ATK-Pro-v3/actions/runs/34224913543), PASS su runner nativi.

## Criteri per il passaggio alla stabile

Tutti i criteri definiti sono soddisfatti:

- i tre workflow di build del tag sono verdi;
- tutti e sei gli asset sono presenti e i digest pubblicati coincidono;
- installer e portable Windows hanno superato i rispettivi smoke;
- DEB e tar Linux hanno superato installazione, avvio e purge;
- entrambi i DMG hanno superato integrita', architettura e avvio su runner nativi;
- il gate release e' verde e non sono emersi regressivi bloccanti.

Decisione: go tecnico alla preparazione di `v3.0.0` stabile. La stabile deve
essere ricostruita con versione finale e sottoposta agli stessi smoke sugli
asset pubblicati; non deve limitarsi a rinominare i binari RC4.

La build macOS resta firmata ad-hoc e non notarizzata; la limitazione deve
essere dichiarata agli utenti anche nella release stabile.
