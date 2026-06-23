# Note release ATK-Pro v3.0.0 RC1

Data snapshot: 2026-06-23

Questa nota accompagna la release candidate tecnica v3.0.0 RC1, generata dalla
baseline `main` dopo la chiusura della preparazione dei portali italiani e
italofoni e della metadata di versione RC1.

## Artefatti pubblicati

| Pacchetto | Tipo | SHA256 | Stato |
| --- | --- | --- | --- |
| `ATK-Pro_v3.0.0-rc1_windows-portable.zip` | Windows portable, build PyInstaller onedir | `52F05680C8FD0030AF8D55A58234B8B40FDF72403D9CC1FFD4A9A0C8CACAE111` | Validato manualmente su Windows |
| `ATK-Pro-Setup-v3.0.0-rc1.exe` | Windows installer Inno Setup | `A60B4FEC0BF38C453BA39A96D64D63F6A75AE60FF47A7028CB37FBD2D2555DA9` | Generato e verificato a livello build/test |
| `ATK-Pro-macOS-Intel-v3.0.0-rc1.dmg` | macOS Intel x86_64 DMG | `C1DC01CDF5FA907044CDE12C7479FF8EA8409B3D0E73AC46E080B077A5EA6979` | Workflow GitHub Actions passato |
| `ATK-Pro-macOS-AppleSilicon-v3.0.0-rc1.dmg` | macOS Apple Silicon arm64 DMG | `99AB294F390A1694C24A1036405715B56CF4198013E2F8CF82BCDC25A4CC4307` | Workflow GitHub Actions passato |
| `ATK-Pro-Linux.deb` | Pacchetto Linux DEB | `B26A536861ED308711519D5916533B3896C0BB532628E3440A00F32F79579408` | Workflow GitHub Actions passato |
| `ATK-Pro-Linux.tar.gz` | Archivio Linux tarball | `AC6A399265052A580717E2DAC0D98B03FC518631FE8743C8E9C40976EA6751EA` | Workflow GitHub Actions passato |

Versione mostrata nell'app: `ATK-Pro v3.0.0 RC1`.

La build richiede l'accettazione esplicita del disclaimer legale v3 prima di
mostrare la finestra principale. La mancata accettazione deve impedire l'avvio
dell'applicazione.

## Verifiche eseguite

| Area | Esito | Dettaglio |
| --- | --- | --- |
| Avvio applicazione | Pass | Avvio da build portable, disclaimer visualizzato e accettato, finestra principale aperta. |
| Informazioni versione | Pass | La finestra Informazioni mostra `RC1`. |
| Suite completa pytest | Pass | `559 passed, 38 skipped`. |
| Suite mirata RC1 | Pass | `28 passed`. |
| Build PyInstaller | Pass | Build onedir completata; esclusione `tkinter` attesa e gestita. |
| Build installer Windows | Pass | Installer Inno Setup RC1 generato da build `dist` fresca. |
| Build macOS | Pass | Workflow GitHub Actions passato per Intel x86_64 e Apple Silicon arm64. |
| Build Linux | Pass | Workflow GitHub Actions passato; pubblicati DEB e tarball con file SHA256. |
| Smoke Antenati | Pass | Documento Antenati scaricato correttamente. |
| Smoke BUB | Pass | Registro BUB Castenaso 1933 scaricato correttamente con range limitato. |
| Smoke BDL PDF | Pass | PDF Biblioteca Digitale Lombarda estratto correttamente. |
| Smoke BDT PDF | Pass | PDF Biblioteca Digitale Trentina estratto correttamente. |

## Output smoke manuali

Gli output manuali sono stati generati fuori dal repository, nella cartella
utente di lavoro di ATK-Pro:

- `w9vm2W9_RC1_Antenati_documento`
- `jpg_RC1_BUB_Castenaso_1933`
- `12404_RC1_Biblioteca_Digitale_Lombarda_PDF`
- `Testi-a-stampa_RC1_Biblioteca_Digitale_Trentina_PDF`

## Note per i tester

- Usare soltanto link pubblici e coerenti con la policy legale del portale.
- Per i portali con policy `R_LIMITED`, preferire range espliciti e contenuti.
- Segnalare eventuali differenze tra portale selezionato e portale rilevato dal
  link, indicando URL, tipo input (`D` o `R`) e cartella di output.
- Gallica resta un caso esterno da monitorare: il campione attuale risponde con
  blocco HTTP 403 sugli endpoint ufficiali usati dallo smoke automatico.

## Stato piattaforme

| Piattaforma | Stato RC1 |
| --- | --- |
| Windows portable | Validata |
| Windows installer | Generato; da provare manualmente |
| macOS Intel | DMG generato e pubblicato; da provare su hardware Intel |
| macOS Apple Silicon | DMG generato e pubblicato; da provare su hardware Apple Silicon |
| Linux DEB | Generato e pubblicato; da provare su distribuzione Debian/Ubuntu compatibile |
| Linux tarball | Generato e pubblicato; da provare su ambiente Linux compatibile |

La RC1 Windows portable non sostituisce la release pubblica multilingue
completa: prima della v3.0.0 finale restano da completare propagazione
multilingue, verifica manuale degli artefatti pubblici non Windows e
eventuali aggiustamenti emersi dai tester.
