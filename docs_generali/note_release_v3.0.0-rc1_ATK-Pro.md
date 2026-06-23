# Note release ATK-Pro v3.0.0 RC1

Data snapshot: 2026-06-23

Questa nota accompagna la release candidate tecnica v3.0.0 RC1, generata dalla
baseline `main` dopo la chiusura della preparazione dei portali italiani e
italofoni e della metadata di versione RC1.

## Artefatto Windows portable

| Campo | Valore |
| --- | --- |
| Pacchetto | `ATK-Pro_v3.0.0-rc1_windows-portable.zip` |
| Tipo | Windows portable, build PyInstaller onedir |
| Versione mostrata nell'app | `ATK-Pro v3.0.0 RC1` |
| SHA256 | `52F05680C8FD0030AF8D55A58234B8B40FDF72403D9CC1FFD4A9A0C8CACAE111` |
| Stato | Validato manualmente su Windows |

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
| Windows installer | Da generare e provare |
| macOS | Da generare e provare |
| Linux | Da generare e provare |

La RC1 Windows portable non sostituisce la release pubblica multilingue
completa: prima della v3.0.0 finale restano da completare propagazione
multilingue, build multipiattaforma e verifica degli artefatti pubblici.
