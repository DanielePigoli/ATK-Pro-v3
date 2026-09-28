# Istruzioni beta ATK-Pro v3.0.1 RC1

Data di apertura: 2026-09-28

Questa beta verifica la candidata di manutenzione `v3.0.1-rc1` prima di una
eventuale release stabile. La candidata ha gia' superato build e smoke
automatici su Windows, Linux e macOS; il beta test serve a rilevare problemi
legati ad ambienti reali, dati differenti, provider IA e flussi utente.

## Download verificato

Usare esclusivamente la
[pre-release GitHub v3.0.1-rc1](https://github.com/DanielePigoli/ATK-Pro-v3/releases/tag/v3.0.1-rc1).

Scegliere l'asset adatto:

- Windows: installer `ATK-Pro-Setup-v3.0.1-rc1.exe` oppure portable ZIP;
- Linux: pacchetto DEB oppure tarball;
- macOS: DMG Intel oppure Apple Silicon secondo l'architettura.

I digest SHA-256 ufficiali sono riportati nelle note della pre-release. Non
usare pacchetti rinominati, ricompressi o ricevuti da fonti diverse.

## Prove prioritarie

Eseguire prima le prove applicabili al proprio ambiente:

1. installazione o estrazione, avvio e controllo della versione
   `ATK-Pro v3.0.1 RC1`;
2. apertura e accettazione del disclaimer, verificandone lo stile grafico;
3. download multipagina dalla Biblioteca Digitale Lombarda, controllando
   numero e contenuto delle pagine e segnalando eventuali placeholder;
4. un download IIIF v3 e un download da un altro portale usato abitualmente;
5. OCR e funzione genealogica assistita su materiale privo di dati sensibili;
6. discovery e selezione del modello per i provider IA disponibili al tester,
   compresi errori leggibili per modello, quota o chiave non validi;
7. chiusura e riapertura dell'app per verificare la persistenza delle
   impostazioni;
8. disinstallazione o rimozione, controllando che non rimangano processi o
   configurazioni di sistema inattese.

Non e' necessario eseguire tutte le prove. E' piu' utile documentare bene i
casi realmente utilizzati che dichiarare un controllo generico.

## Segnalazione dei risultati

Usare l'issue
[#378 - Beta testing ATK-Pro v3.0.1-rc1](https://github.com/DanielePigoli/ATK-Pro-v3/issues/378)
e indicare:

- sistema operativo, versione e architettura;
- asset utilizzato;
- funzione, portale e URL pubblico del campione, se pertinente;
- passaggi esatti per riprodurre;
- risultato atteso e risultato ottenuto;
- provider e modello IA, senza riportare chiavi API;
- frequenza: sempre, intermittente o una sola volta;
- log e schermate ripuliti da segreti e dati personali.

Per un esito positivo e' sufficiente indicare ambiente, asset, prove concluse
e risultato `PASS`.

## Severita' proposta

| Livello | Criterio |
| --- | --- |
| Bloccante | Crash, perdita dati, impossibilita' sistematica di avvio o funzione principale inutilizzabile. |
| Alta | Regressione importante e riproducibile senza workaround affidabile. |
| Media | Difetto circoscritto con workaround praticabile. |
| Bassa | Problema estetico o documentale, oppure miglioramento non necessario alla stabilita'. |

## Riservatezza e sicurezza

- non pubblicare chiavi API, password, cookie, token o file di configurazione
  completi;
- non allegare documenti archivistici riservati o contenenti dati personali;
- mascherare percorsi utente, nomi e metadati non necessari;
- se una segnalazione richiede dati sensibili, descriverla senza allegati e
  concordare separatamente un canale adatto.

## Chiusura della beta

La beta non promuove automaticamente la candidata a stabile. Prima di
`v3.0.1` ogni riscontro deve essere riprodotto e classificato come chiuso,
rinviato consapevolmente o bloccante; la decisione finale resta esplicita.
