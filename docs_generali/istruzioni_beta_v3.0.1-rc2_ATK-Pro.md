# Istruzioni beta ATK-Pro v3.0.1 RC2

Data di preparazione: 2026-10-18

Stato: **ciclo beta aperto il 2026-10-18; smoke multipiattaforma PASS**.

Questa beta verifica la candidata correttiva `v3.0.1-rc2` prima di una
eventuale release stabile. L'issue
[#385](https://github.com/DanielePigoli/ATK-Pro-v3/issues/385) e' il canale
centrale per gli esiti e i nuovi riscontri.

## Download verificato

Usare esclusivamente la
[pre-release GitHub v3.0.1-rc2](https://github.com/DanielePigoli/ATK-Pro-v3/releases/tag/v3.0.1-rc2).

Scegliere l'asset adatto:

- Windows: installer `ATK-Pro-Setup-v3.0.1-rc2.exe` oppure portable ZIP;
- Linux: pacchetto DEB oppure tarball;
- macOS: DMG Intel oppure Apple Silicon secondo l'architettura.

Verificare i digest SHA-256 pubblicati nelle note della pre-release. Non usare
pacchetti rinominati, ricompressi o ricevuti da fonti diverse.

## Prove prioritarie

1. Installare o estrarre, avviare e verificare `ATK-Pro v3.0.1 RC2`.
2. Aprire il disclaimer dal menu Documenti e verificarne lo stile HTML ATK-Pro.
3. Aprire Guida e Presentazione del progetto e controllare versione e contenuti.
4. Scaricare i registri BDL `10527` e `10530`, controllando fisicamente tutte
   le pagine dei PDF. Se rimane anche un solo placeholder, il riepilogo deve
   indicare output incompleto, conteggio e pagine non recuperate.
5. Controllare che non restino directory vuote `_tmp_pdf_images` o
   `tiles_canvas_*` nella cartella di output.
6. Eseguire OCR su PDF con calibrazione assistita sia attiva sia disattiva. Non
   devono comparire `cannot identify image file` o `No output specified.`.
7. Se disponibile, ripetere avvio e chiusura su Linux e su un Mac fisico,
   annotando architettura e comportamento Gatekeeper.

Non e' necessario eseguire tutte le prove. E' piu' utile documentare bene i
casi realmente verificati che dichiarare un controllo generico.

## Segnalazione dei risultati

Usare l'issue
[#385 - Beta testing ATK-Pro v3.0.1-rc2](https://github.com/DanielePigoli/ATK-Pro-v3/issues/385)
e indicare:

- sistema operativo, versione e architettura;
- asset utilizzato;
- funzione, portale e URL pubblico del campione, se pertinente;
- passaggi esatti, risultato atteso e risultato ottenuto;
- provider e modello IA, senza riportare chiavi API;
- frequenza e log o schermate ripuliti da segreti e dati personali.

Per un esito positivo sono sufficienti ambiente, asset, prove concluse e
risultato `PASS`.

## Riservatezza e chiusura

Non pubblicare chiavi API, password, cookie, token, configurazioni complete o
documenti archivistici riservati. La beta non promuove automaticamente la
candidata: prima di `v3.0.1` ogni riscontro deve essere chiuso oppure rinviato
con motivazione e la decisione finale deve essere esplicita.
