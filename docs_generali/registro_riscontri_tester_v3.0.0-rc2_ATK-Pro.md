# Registro riscontri tester ATK-Pro v3.0.0 RC2

Questo registro raccoglie i riscontri esterni sulla RC2 e li trasforma in una
traccia operativa: cosa e' stato segnalato, quanto e' riproducibile, se blocca
la release pubblica e quale azione e' stata decisa.

## Stato sintetico

| Area | Stato | Note |
|---|---|---|
| Packaging Windows portable | In osservazione | RC1 avviata correttamente dopo disclaimer; ZIP molto grande e lento da estrarre su alcuni sistemi. |
| Packaging Windows installer | Da verificare | RC2 pubblicata anche come installer; serve smoke manuale mirato. |
| Ricerca Assistita AI | Fix in RC2, conferma esterna non pervenuta | Corretto errore Gemini `cannot access local variable 'json' where it is not associated with a value`; regressioni tecniche interne non emerse nel consolidamento del 2026-06-30. |
| OCR Gemini su immagini divise | Fix in RC2, conferma esterna non pervenuta | Corretto merge TOP/BOTTOM con deduplicazione righe sovrapposte e riempimento colonne vuote; regressioni tecniche interne non emerse nel consolidamento del 2026-06-30. |
| Prestazioni download | In osservazione | Segnalata sensazione di maggiore lentezza; serve caso riproducibile con portale, link e tempi indicativi. |
| Antivirus Windows | Non bloccante | AVG segnala inizialmente l'eseguibile, poi lo considera sicuro. Tema atteso per binari non firmati/notarizzati. |

## Riscontri ricevuti

| ID | Data | Tester | Ambiente | Area | Segnalazione | Stato | Esito/azione |
|---|---|---|---|---|---|---|---|
| RC2-001 | 2026-06-23 | Enrico Davini | Windows, portable RC1, AVG | Packaging | ZIP molto grande, estrazione molto lenta con Express Zip. | Aperto non bloccante | Tenere presente per ottimizzazione futura; non blocca RC2. |
| RC2-002 | 2026-06-23 | Enrico Davini | Windows, portable RC1, AVG | Sicurezza locale | Eseguibile inizialmente bloccato da AVG, poi considerato sicuro. | Aperto non bloccante | Atteso per build non firmate; valutare firma/codice reputazionale per release pubblica. |
| RC2-003 | 2026-06-23 | Enrico Davini | Windows, portable RC1 | Prestazioni | Download percepito piu' lento, senza timing di confronto. | Da qualificare | Chiedere, se ricapita, link, portale, modalita' D/R e tempi indicativi. |
| RC2-004 | 2026-06-23 | Enrico Davini | Windows, portable RC1, Gemini paid | Ricerca Assistita AI | Errore `cannot access local variable 'json' where it is not associated with a value`. | Fix in RC2 | Corretto in RC2; nessuna regressione emersa nel consolidamento interno del 2026-06-30; conferma esterna non pervenuta. |
| RC2-005 | 2026-06-23 | Enrico Davini | Windows, portable RC1, Gemini paid | OCR Gemini | OCR su censimento Toscana 1841 produce due file testo con righe 8-14 duplicate nel merge finale. | Fix in RC2 | Corretto in RC2; nessuna regressione emersa nel consolidamento interno del 2026-06-30; conferma esterna non pervenuta. |
| RC2-006 | 2026-06-23 | Enrico Davini | Windows, portable RC1, Gemini paid | OCR Gemini | Gemini non legge/scrive la penultima colonna dell'immagine. | In osservazione | Probabile limite modello/prompt o qualita' immagine; distinguere da bug di merge. |

## Casi da riprovare in RC2

| Caso | Priorita' | Input richiesto | Atteso |
|---|---:|---|---|
| Ricerca Assistita AI con Gemini | Media | Stessa chiave Gemini usata in RC1, query semplice | Nessun errore `json`; risultato o errore provider gestito in modo leggibile. Verifica utile ma non bloccante se non ripetuta dal tester. |
| OCR Gemini su censimento Toscana 1841 | Media | Stessa immagine usata in RC1 da Enrico | File finale senza righe duplicate da sovrapposizione TOP/BOTTOM. Verifica utile ma non bloccante se non ripetuta dal tester. |
| Download campione Antenati | Media | Link Antenati gia' usato nei test RC | Output completo e tempi ragionevoli. |
| Download campione BUB/FICLIT/BDT/BDL | Media | Uno o due link gia' validati in RC1/RC2 | Output completo, nessun regressione sui portali prudenti. |
| Windows installer RC2 | Media | Installazione pulita su macchina Windows | Disclaimer, avvio, Informazioni `ATK-Pro v3.0.0 RC2`, disinstallazione corretta. |

## Criteri di decisione

| Categoria | Esempio | Decisione |
|---|---|---|
| Bloccante release pubblica | Crash all'avvio, download nullo su funzioni principali, perdita dati, errore sistematico AI/OCR non gestito | Fix prima della v3.0.0 finale. |
| Bloccante RC successiva | Regressione importante ma circoscritta, riproducibile in RC2 | RC3 o hotfix RC prima di allargare il test. |
| Follow-up post release | Migliorie prestazionali non critiche, qualita' OCR dipendente dal modello, riduzione dimensione pacchetto | Documentare e pianificare dopo v3.0.0. |

## Prossimi aggiornamenti

- Registrare conferma o mancata conferma di Enrico sui fix RC2.
- Aggiungere eventuali altri tester con ambiente, pacchetto usato e link di prova.
- Prima della release finale, chiudere o riclassificare ogni voce aperta.
