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
| Windows installer | Alta | Da eseguire | Installazione, versione, avvio, disclaimer e disinstallazione. |
| Windows portable | Alta | Da eseguire | Estrazione, versione, avvio, configurazione portable e chiusura. |
| Linux DEB o tarball | Media | Da eseguire | Installazione/estrazione, avvio e rimozione. |
| macOS Intel o Apple Silicon | Media | Da eseguire | Mount, avvio, comportamento Gatekeeper e chiusura. |
| BDL multipagina | Alta | Da eseguire | Tutte le pagine attese, contenuti distinti, placeholder quantificati. |
| IIIF v3 | Alta | Da eseguire | Immagine o sequenza corretta senza fallback improprio. |
| Altri portali abituali | Media | Da eseguire | Almeno un campione pubblico riproducibile. |
| OCR e genealogia assistita | Alta | Da eseguire | Output completo, nessun duplicato o colonna persa. |
| Provider IA e modelli | Alta | Da eseguire | Discovery/fallback coerenti ed errori comprensibili. |
| Persistenza configurazione | Alta | Da eseguire | Impostazioni conservate dopo riavvio senza perdita di altri campi. |
| Interfaccia e documenti | Media | Da eseguire | Disclaimer e documenti coerenti con lo stile ATK-Pro. |

La copertura di ogni piattaforma e' desiderabile ma non costituisce da sola un
blocco, poiche' gli smoke CI sono gia' passati su runner nativi. Sono invece
necessari almeno un riscontro esterno su Windows e una prova reale completa di
BDL, persistenza configurazione e funzioni IA assistite disponibili.

## Riscontri ricevuti

| ID | Data | Tester | Ambiente/asset | Area | Segnalazione | Severita' | Riproducibilita' | Stato | Esito/azione |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| - | - | - | - | - | Nessun riscontro ancora registrato. | - | - | Aperto | In attesa dei primi test esterni. |

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

Registrare il primo esito esterno ricevuto nell'issue #378, aggiornare la
copertura e avviare il triage soltanto su evidenze riproducibili.
