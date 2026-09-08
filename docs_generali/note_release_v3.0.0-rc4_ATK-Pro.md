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

## Artefatti RC4 da produrre

- `ATK-Pro-Setup-v3.0.0-rc4.exe`
- `ATK-Pro-v3.0.0-rc4-Windows-Portable.zip`
- `ATK-Pro-Linux.deb`
- `ATK-Pro-Linux.tar.gz`
- `ATK-Pro-macOS-Intel-v3.0.0-rc4.dmg`
- `ATK-Pro-macOS-AppleSilicon-v3.0.0-rc4.dmg`

Gli SHA-256 e gli esiti saranno inseriti dopo la pubblicazione. Gli smoke
devono ricevere esplicitamente il tag RC4 e gli hash calcolati sugli asset
pubblicati; i valori RC3 non devono essere riutilizzati.

## Criteri per il passaggio alla stabile

RC4 e' promuovibile verso `v3.0.0` solo se:

- i tre workflow di build del tag sono verdi;
- tutti e sei gli asset sono presenti e i digest pubblicati coincidono;
- installer e portable Windows superano i rispettivi smoke;
- DEB e tar Linux superano installazione, avvio e purge;
- entrambi i DMG superano integrita', architettura e avvio su runner nativi;
- il gate release resta verde e non emergono regressivi bloccanti.

La build macOS resta firmata ad-hoc e non notarizzata; la limitazione deve
essere dichiarata agli utenti anche nella release stabile.
