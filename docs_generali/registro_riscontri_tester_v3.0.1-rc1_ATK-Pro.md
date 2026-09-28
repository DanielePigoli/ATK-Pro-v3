# Registro riscontri tester ATK-Pro v3.0.1 RC1

Data di apertura: 2026-09-28

Stato: **beta aperta**.

Canale centrale:
[#378 - Beta testing ATK-Pro v3.0.1-rc1](https://github.com/DanielePigoli/ATK-Pro-v3/issues/378).

Il registro raccoglie le prove esterne sugli asset pubblicati della
`v3.0.1-rc1`. Le verifiche CI costituiscono la baseline tecnica, ma non
sostituiscono i riscontri su sistemi, reti, antivirus, portali e provider IA
reali.

## Baseline prima dell'apertura

| Controllo | Stato | Evidenza |
| --- | --- | --- |
| Gate release | PASS | 12/12 step, 907 test passati e 3 skip attesi. |
| Build Windows | PASS | Run `36346694309`. |
| Build Linux | PASS | Run `36346694343`. |
| Build macOS Intel e Apple Silicon | PASS | Run `36346694319`. |
| Smoke Windows installer e portable | PASS | Run `36348107912`. |
| Smoke Linux DEB e tarball | PASS | Run `36348106596`. |
| Smoke macOS Intel e Apple Silicon | PASS | Run `36348106527`. |
| Pre-release e digest | PASS | Sei pacchetti, due sidecar Linux, otto asset complessivi. |

## Copertura beta richiesta

| Area | Priorita' | Stato esterno | Evidenza attesa |
| --- | ---: | --- | --- |
| Windows installer | Alta | Parziale | Installazione e avvio riusciti su macchina fisica; disclaimer aperto ma con difformita' estetica `BETA-001`; disinstallazione ancora da verificare. |
| Windows portable | Alta | Da eseguire | Estrazione, versione, avvio, configurazione portable e chiusura. |
| Linux DEB o tarball | Media | Da eseguire | Installazione/estrazione, avvio e rimozione. |
| macOS Intel o Apple Silicon | Media | Da eseguire | Mount, avvio, comportamento Gatekeeper e chiusura. |
| BDL multipagina | Alta | Da eseguire | Tutte le pagine attese, contenuti distinti, placeholder quantificati. |
| IIIF v3 | Alta | Da eseguire | Immagine o sequenza corretta senza fallback improprio. |
| Altri portali abituali | Media | Da eseguire | Almeno un campione pubblico riproducibile. |
| OCR e genealogia assistita | Alta | Da eseguire | Output completo, nessun duplicato o colonna persa. |
| Provider IA e modelli | Alta | Da eseguire | Discovery/fallback coerenti ed errori comprensibili. |
| Persistenza configurazione | Alta | Da eseguire | Impostazioni conservate dopo riavvio senza perdita di altri campi. |
| Interfaccia e documenti | Media | FAIL non bloccante | Il disclaimer usa il visualizzatore testuale semplice (`BETA-001`); la presentazione del progetto, datata 2 agosto 2026, deve essere riesaminata prima della stabile (`BETA-002`). |

La copertura di ogni piattaforma e' desiderabile ma non costituisce da sola un
blocco, poiche' gli smoke CI sono gia' passati su runner nativi. Sono invece
necessari almeno un riscontro esterno su Windows e una prova reale completa di
BDL, persistenza configurazione e funzioni IA assistite disponibili.

## Riscontri ricevuti

| ID | Data | Tester | Ambiente/asset | Area | Segnalazione | Severita' | Riproducibilita' | Stato | Esito/azione |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| BETA-001 | 2026-09-28 | Daniele Pigoli | Windows, installer `v3.0.1-rc1`, macchina fisica | Interfaccia e documenti | Il disclaimer viene visualizzato come testo semplice e non con lo stesso aspetto HTML in stile ATK-Pro degli altri documenti, come la presentazione dell'autore. Due schermate comparative disponibili nel riscontro originale. | Bassa | Riscontrato all'apertura del disclaimer nella build installata | Aperto non bloccante | Feedback registrato nell'[issue #378](https://github.com/DanielePigoli/ATK-Pro-v3/issues/378#issuecomment-5868836113); nessuna correzione immediata, da valutare insieme agli altri riscontri alla chiusura del ciclo beta. |
| BETA-002 | 2026-09-28 | Daniele Pigoli | Windows, installer `v3.0.1-rc1`, macchina fisica | Documentazione integrata | La presentazione del progetto mostra ancora la data di aggiornamento 2 agosto 2026; contenuto e data potrebbero non rappresentare compiutamente l'evoluzione successiva della serie 3 destinata alla stabile. Una schermata e' disponibile nel riscontro originale. La verifica nel repository conferma la stessa data nelle 20 versioni localizzate. | Bassa | Sempre, aprendo Documenti > Presentazione del progetto | Aperto non bloccante | Feedback registrato nell'[issue #378](https://github.com/DanielePigoli/ATK-Pro-v3/issues/378#issuecomment-5869104424) e integrato dalla [verifica multilingue](https://github.com/DanielePigoli/ATK-Pro-v3/issues/378#issuecomment-5869123753); prima della validazione stabile riesaminare il testo italiano e poi riallineare tutte le traduzioni, senza modificare ora la RC. |

## Regole di triage

- assegnare un ID progressivo `BETA-001`, `BETA-002` e successivi;
- conservare URL pubblici e passaggi minimi necessari alla riproduzione;
- non copiare nel registro chiavi, token, password o dati personali;
- collegare ogni correzione alla relativa PR e rieseguire il caso originale;
- un difetto bloccante o alto riproducibile sospende la promozione a stabile;
- difetti medi o bassi possono essere rinviati soltanto con decisione motivata.

## Criteri di uscita

La beta puo' essere proposta per la chiusura quando:

1. le prove minime indicate sopra hanno evidenza esterna sufficiente;
2. non restano difetti bloccanti o alti aperti;
3. ogni riscontro medio o basso e' chiuso oppure esplicitamente rinviato;
4. eventuali correzioni hanno superato test mirati, gate release e un nuovo
   controllo beta del caso interessato;
5. note di release, checklist e registro sono aggiornati;
6. viene assunta una decisione esplicita separata sulla release `v3.0.1`.

## Prossimo aggiornamento

Continuare la raccolta nell'issue #378. Alla chiusura del ciclo, valutare
`BETA-001` e `BETA-002` insieme agli altri riscontri. Prima della stabile,
decidere se includere le revisioni nella candidata successiva oppure rinviarle
motivatamente.
