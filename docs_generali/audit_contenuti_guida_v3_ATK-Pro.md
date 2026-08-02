# Audit contenutistico guida ATK-Pro v3.0.0

Data audit iniziale: 2026-05-26
Ultimo aggiornamento controllato: 2026-08-01

## Aggiornamento pre-release del 2026-08-01

La guida italiana e' confermata come fonte editoriale canonica per le localizzazioni. Con approvazione esplicita sono stati riallineati i seguenti punti:

- aggiunti Archivio Storico UniBO, PHAIDRA Universita' di Padova e DOGE Universita' di Genova, promossi nella fase 3 con accesso pubblico prudenziale;
- chiarita la distinzione tra compatibilita' tecnica del portale e autorizzazione al download;
- documentato `Impostazioni -> Profilo risorse` con i profili Leggero, Bilanciato e Veloce;
- corretta l'indicazione sul proxy: non esiste un menu interno per le credenziali;
- riallineato OCR a provider, modello opzionale, tipi documentali personalizzati, istruzioni salvate, calibrazione, diagnostica, revisione e salvataggio progressivo;
- eliminate dalla sezione OCR promesse stabili su prezzi, gratuita', quote e disponibilita' dei modelli;
- chiarita la natura locale CSV della Cassaforte IA;
- corretti troubleshooting, log e permessi, eliminando il ricorso consigliato a privilegi amministrativi;
- aggiunti casi FAQ per restrizioni dei portali e recupero delle trascrizioni OCR parziali.

Per decisione editoriale del responsabile restano invariati: le valutazioni sociologiche che motivano le 20 lingue e la stima di copertura del 98%; la dicitura macOS, da riesaminare dopo packaging e collaudo su hardware reale. Le altre lingue non sono state ancora propagate e devono partire da questa fonte italiana approvata.

Nota successiva 2026-05-26: la sotto-guida italiana `assets/it/testuali/guida_03_ricerca_assistita_ai.html` e' stata aggiunta e collegata dall'indice italiano. La guida italiana `assets/it/testuali/guida_07_traduzione.html` e' stata riallineata al dialog v3 di Traduzione OCR. La guida italiana `assets/it/testuali/guida_08_esportazione_gedcom.html` e' stata riscritta per descrivere il flusso reale di analisi genealogica/GEDCOM. La guida principale italiana e `assets/it/testuali/guida_02_operazioni_base.html` sono state aggiornate nella sezione Servizi per descrivere i sei moduli v3 come operativi. I percorsi menu residui in guida 03, 04 e 05 sono stati aggiornati al menu attuale, e le FAQ italiane sono state ripulite dai riferimenti obsoleti individuati. Il file esempio e' ora normalizzato come `input_link_base.txt`. Resta da valutare la propagazione multilingue.

Nota successiva 2026-05-27: `assets/it/testuali/guida.html` e' stato riportato alla funzione corretta di indice modulare. Il corpo operativo duplicato e' stato rimosso dalla guida principale, lasciando il contenuto dettagliato nei file `guida_01...guida_09`. Il verificatore `verify_italian_guide_content.py` ora controlla che l'indice linki tutti i moduli italiani e non torni a contenere blocchi estesi duplicati.

Nota successiva 2026-05-31: la guida italiana e' stata rinumerata per rispecchiare l'ordine reale del menu `Servizi`: Ricerca assistita AI e' ora `guida_03_ricerca_assistita_ai.html`, seguita da immagini, metadati, OCR, traduzione, GEDCOM e supporto/FAQ. Il verificatore controlla anche l'ordine dei link nell'indice.

## Esito sintetico aggiornato

La verifica strutturale dei documenti del menu Documenti e dei link locali e' verde. Dopo gli interventi successivi all'audit iniziale, la guida italiana copre ora i tre blocchi che erano release blocker immediati: Ricerca assistita AI, Traduzione OCR e analisi genealogica/GEDCOM.

La scansione dei marker critici sulla guida italiana non trova piu' riferimenti obsoleti nei file trattati. La revisione editoriale dedicata di OCR Avanzato e FAQ e' completata. La guida italiana puo' essere trattata come fonte v3 canonica; resta da eseguire la propagazione controllata nelle altre lingue prima di una release pubblica multilingue completa.

## Fonti di confronto

- Menu reale applicazione: `src/main_gui_qt.py`, azioni dei menu File, Output, Servizi, Documenti e Impostazioni.
- Ricerca assistita AI: `src/RicercaAssistitaAI.py`.
- Analisi genealogica / GEDCOM: `src/genealogy_dialog.py`, `src/genealogy_prompts.py`.
- OCR avanzato: modulo aperto da `src/main_gui_qt.py` tramite `advanced_ocr`.
- Traduzione OCR: `src/translation_dialog.py`.
- Viewer immagini e metadati: `src/image_metadata_viewer.py`.
- Verifica asset/link: `verify_document_assets.py`.

## Stato dei blocchi iniziali

1. Guida principale `assets/it/testuali/guida.html`.
   - Riallineata come indice/portale della guida italiana.
   - Linka i nove moduli sezionali e contiene solo sommari brevi, stato guida e perimetro v3.
   - Il corpo operativo resta nei file sezionali dedicati, evitando duplicazioni.

2. Ricerca assistita AI.
   - Fatto per la guida italiana con `assets/it/testuali/guida_03_ricerca_assistita_ai.html`.
   - Il menu reale espone `Servizi -> Ricerca assistita AI`.
   - Il dialog consente query genealogica, scelta provider, modello opzionale, prompt standard, elaborazione multi-provider, note personali, salvataggio risultati testuali e HTML, e gestione del caveau chiavi.

3. `assets/it/testuali/guida_08_esportazione_gedcom.html`.
   - Fatto per la guida italiana.
   - La pagina ora descrive il dialog di analisi genealogica con input universale, base GEDCOM/CSV opzionale, note paleografiche, provider IA, caveau chiavi e output `genealogia_*.ged`.

4. Percorsi di menu nelle sotto-guide operative.
   - Fatto per la guida italiana: i moduli 03-09 seguono ora l'ordine reale del menu `Servizi` e della guida.
   - `guida_07_traduzione.html` usa ora `Servizi -> Traduzione OCR`.

5. `assets/it/testuali/guida_07_traduzione.html`.
   - Fatto per la guida italiana.
   - La pagina ora descrive il percorso `Servizi -> Traduzione OCR`, tipologia documento, modello opzionale, Cassaforte chiavi, pulsante `Traduci Testo ORA` e salvataggio TXT/DOCX.

6. `assets/it/testuali/guida_02_operazioni_base.html`.
   - Fatto per la sezione Servizi italiana.
   - La pagina descrive ora le 6 funzioni attuali: Ricerca assistita AI, Visualizzazione Immagini, Visualizzazione Metadati JSON, OCR Avanzato, Traduzione OCR, Esportazione GEDCOM.

7. `assets/it/testuali/guida_09_supporto_faq.html`.
   - Fatto per i riferimenti piu' critici nella guida italiana.
   - Rimane consigliata una revisione editoriale completa della FAQ, ma non risultano piu' riferimenti diretti ai marker obsoleti controllati.

8. Contenuti instabili su provider IA, modelli e costi.
   - Le guide OCR e Traduzione citano provider e modelli specifici.
   - Le promesse piu' specifiche su costi/modelli sono state rese piu' prudenti nei passaggi gia fatti.
   - Prima della RC resta consigliata una rilettura editoriale, evitando promesse su prezzi, disponibilita' o nomi modello soggetti a variazione.

## Stato per file italiano

| File | Stato | Problema principale | Azione prima di RC |
| --- | --- | --- | --- |
| `guida.html` | Riallineata come indice | La guida principale non duplica piu' i moduli sezionali; linka `guida_01...guida_09` | Verificare propagazione futura |
| `guida_01_installazione_configurazione.html` | Riallineata in italiano | Documentati profilo risorse e configurazione proxy effettiva; contenuti lingue e macOS conservati per decisione editoriale | Verificare dopo collaudo macOS |
| `guida_02_operazioni_base.html` | Riallineata in italiano | Aggiunti i tre portali della fase 3 e chiarito il perimetro tecnico-legale | Verificare propagazione futura |
| `guida_03_ricerca_assistita_ai.html` | Riallineata in italiano | Posizionata come primo servizio, coerente con il menu `Servizi` | Verificare propagazione futura |
| `guida_04_visualizzazione_immagini.html` | Riallineata in italiano | Percorso menu aggiornato | Verificare propagazione futura |
| `guida_05_visualizzazione_metadati.html` | Riallineata in italiano | Percorso menu aggiornato | Verificare propagazione futura |
| `guida_06_ocr_avanzato.html` | Riallineata in italiano | Provider e funzioni correnti documentati senza promesse commerciali instabili | Verificare propagazione futura |
| `guida_07_traduzione.html` | Riallineata in italiano | Copertura aggiornata al dialog v3; resta da propagare alle altre lingue quando si fara' il riallineamento multilingue | Verificare link e propagazione futura |
| `guida_08_esportazione_gedcom.html` | Riallineata in italiano | Copertura aggiornata al dialog v3; resta da propagare alle altre lingue quando si fara' il riallineamento multilingue | Verificare link e propagazione futura |
| `guida_09_supporto_faq.html` | Riallineata in italiano | Corretti log, permessi, restrizioni portali e recupero OCR parziale | Verificare propagazione futura |

## Sequenza consigliata

1. Sottoporre il diff italiano al controllo finale del responsabile.
2. Dopo approvazione, propagare o riallineare le altre lingue dalla fonte italiana canonica.
3. Riesaminare la dicitura macOS dopo packaging e collaudo su hardware reale.

## Criterio RC

La prima RC v3.0.0 puo' partire quando:

- La guida italiana non presenta piu' moduli reali come funzioni future.
- Ricerca assistita AI, Traduzione OCR e analisi genealogica/GEDCOM sono documentate nella guida italiana.
- I percorsi di menu corrispondono alla UI attuale.
- Le sezioni su provider IA evitano informazioni commerciali o tecniche non verificate.
- La guida principale resta un indice modulare e non duplica il contenuto dei file sezionali.
- E' chiaro lo stato delle altre lingue: aggiornate, oppure esplicitamente dichiarate come traduzioni da riallineare dopo la fonte italiana.
- `verify_document_assets.py`, `verify_localization.py`, `validate_glossary.py` e `verify_glossary.py` restano verdi.
