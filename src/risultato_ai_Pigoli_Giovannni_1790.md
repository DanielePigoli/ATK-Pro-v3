**Legenda risultati AI:**


- **Provider**: il servizio AI che ha generato la risposta (es. Claude, Gemini,
  ecc.)
- **Slot**: la posizione della chiave usata nel caveau per quel provider
- **Tabella**: ogni colonna corrisponde a un'informazione richiesta dal prompt
  (es. Portale, Motivazione, Query di esempio, Periodo, Tipo atti,
  Filtri/Strategie)
- Se la modalità 'tutte le risposte' è attiva, vedrai una sezione per ogni
  provider che ha restituito risultati utili

-
| provider | raw                                                                  | results | slot |
| -------- | -------------------------------------------------------------------- | ------- | ---- |
| Gemini   | []                                                                   |   []    |   1  |
| Gemini   | \[ERRORE]: Tutti i modelli Gemini esauriti per - chiave (text-only). |   []    |   1  |
| Gemini   | [
{
"1": "\**FamilySearch**",
"2":
"**È il portale più importante per questa ricerca.** Possiede la più vasta
collezione al mondo di registri parrocchiali italiani microfilmati e
digitalizzati, inclusi quelli della Diocesi di Cremona. È gratuito, previa
registrazione.",
"3": "La ricerca per nome potrebbe non dare risultati. La
strategia migliore è navigare il catalogo: \`Cerca > Catalogo > Luogo: Italy,
Cremona > Cliccare su \\"Registri parrocchiali di Cremona (Diocesi)\\" >
Selezionare la parrocchia di interesse e l'anno.`",
"4": "~1560 - ~1910",
"5":
"\**Battesimi, Matrimoni, Morti (Sepolture)**, Stati delle Anime (censimenti
parrocchiali)."
},
{
"1": "\**Portale Antenati (SAN)**",
"2": "Portale
ufficiale degli Archivi di Stato Italiani. Fondamentale per trovare la famiglia
Pigoli nelle generazioni successive (figli, nipoti) e per contestualizzare la
ricerca. La sua copertura per Cremona parte dal periodo napoleonico.",
"3":
"Ricerca per nominativo: \`Cognome: Pigoli, Nome: Giovanni` (utile per trovare
un suo eventuale atto di morte se vissuto fino al 1806+). Oppure navigazione:
\`Sfoglia i registri > Cremona > Selezionare il comune > Stato Civile
Napoleonico.`",
"4": "1806 - 1942 (per Cremona)",
"5": "\**Stato Civile
Napoleonico e della Restaurazione** (Nascite, Matrimoni, Morti,
Pubblicazioni)."
},
{
"1": "\**Ancestry**",
"2": "Piattaforma commerciale con
un potente motore di ricerca. Può avere collezioni indicizzate che non si
trovano altrove o alberi genealogici di altri utenti che possono fornire indizi
preziosi. Spesso utilizza le stesse fonti di Antenati e FamilySearch, ma con
un'interfaccia di ricerca più immediata.",
"3": "Ricerca globale con filtri:
\`Nome: Giovanni Pigoli, Luogo di nascita: Cremona, Italy, Anno di nascita:
1790 ±5 anni.`",
"4": "Vario, principalmente dal 1806 in poi per gli atti
civili.",
"5": "Atti di Stato Civile, liste di leva, alberi genealogici
pubblici."
}
] | [{'1': '\**FamilySearch**', '2': '**È il portale più
importante per questa ricerca.** Possiede la più vasta collezione al mondo di
registri parrocchiali italiani microfilmati e digitalizzati, inclusi quelli
della Diocesi di Cremona. È gratuito, previa registrazione.', '3': 'La ricerca
per nome potrebbe non dare risultati. La strategia migliore è navigare il
catalogo: \`Cerca > Catalogo > Luogo: Italy, Cremona > Cliccare su "Registri
parrocchiali di Cremona (Diocesi)" > Selezionare la parrocchia di interesse e
l\\'anno.`', '4': '~1560 - ~1910', '5': '\**Battesimi, Matrimoni, Morti
(Sepolture)**, Stati delle Anime (censimenti parrocchiali).'}, {'1':
'\**Portale Antenati (SAN)**', '2': 'Portale ufficiale degli Archivi di Stato
Italiani. Fondamentale per trovare la famiglia Pigoli nelle generazioni
successive (figli, nipoti) e per contestualizzare la ricerca. La sua copertura
per Cremona parte dal periodo napoleonico.', '3': 'Ricerca per nominativo:
\`Cognome: Pigoli, Nome: Giovanni` (utile per trovare un suo eventuale atto di
morte se vissuto fino al 1806+). Oppure navigazione: \`Sfoglia i registri >
Cremona > Selezionare il comune > Stato Civile Napoleonico.`', '4': '1806 -
1942 (per Cremona)', '5': '\**Stato Civile Napoleonico e della Restaurazione**
(Nascite, Matrimoni, Morti, Pubblicazioni).'}, {'1': '\**Ancestry**', '2':
"Piattaforma commerciale con un potente motore di ricerca. Può avere collezioni
indicizzate che non si trovano altrove o alberi genealogici di altri utenti che
possono fornire indizi preziosi. Spesso utilizza le stesse fonti di Antenati e
FamilySearch, ma con un'interfaccia di ricerca più immediata.", '3': 'Ricerca
globale con filtri: \`Nome: Giovanni Pigoli, Luogo di nascita: Cremona, Italy,
Anno di nascita: 1790 ±5 anni.`', '4': 'Vario, principalmente dal 1806 in poi
per gli atti civili.', '5': 'Atti di Stato Civile, liste di leva, alberi
genealogici pubblici.'}] | 2 |
| Gemini | [
{
"1": "\**FamilySearch**",
"2": "È
il portale \**più importante** per questa ricerca. Ha digitalizzato (spesso
solo come immagini non indicizzate) una vastissima quantità di registri
parrocchiali italiani, inclusi quelli della Diocesi di Cremona. È gratuito.",
"3": "1. \**Ricerca indicizzata (se fortunati):** \`Nome: Giovanni` \`Cognome:
Pigoli` \`Luogo di nascita: Cremona, Italy` \`Periodo: 1785-1795`
2.
\**Navigazione manuale (più probabile):** \`Catalogo > Luoghi > Italy, Cremona
> \[Nome del Comune] > Church records` e sfogliare le immagini dei registri di
battesimo del periodo.",
"4": "Molto ampio, spesso dal tardo 1500 fino al 1900
inoltrato, a seconda della parrocchia. Ideale per il 1790.",
"5": "\**Registri
Parrocchiali** (Battesimi, Matrimoni, Morti, Stati delle Anime). Anche Stato
Civile per periodi successivi."
},
{
"1": "\**Portale Antenati (Archivi di
Stato)**",
"2": "Portale ufficiale degli Archivi di Stato italiani.
\**Fondamentale** per proseguire la ricerca sui discendenti di Giovanni Pigoli,
ma \**improbabile** che contenga il suo atto di nascita del 1790, poiché ospita
principalmente lo Stato Civile.",
"3": "La ricerca non è per nome, ma per fondo
archivistico. Il percorso è: \`Esplora gli archivi > Archivio di Stato di
Cremona > Stato civile napoleonico / Stato civile della restaurazione >
\[Comune] > Nati \[Anno]`",
"4": "Principalmente dal 1806/1809 fino al 1940
circa, a seconda dei fondi versati dagli archivi.",
"5": "\**Stato Civile**
(Atti di Nascita, Matrimonio, Morte, Pubblicazioni, Cittadinanza). Non contiene
registri parrocchiali."
},
{
"1": "\**Ancestry**",
"2": "Piattaforma
commerciale con un potente motore di ricerca e la funzione di
\\"suggerimenti\\" (hints). Spesso indicizza collezioni presenti anche su
FamilySearch, rendendo la ricerca più rapida. Utile anche per trovare alberi
genealogici di altri utenti.",
"3": "\`Nome: Giovanni Pigoli` \`Luogo di
nascita: Cremona, Lombardia, Italia` \`Anno di nascita: 1790 ±5 anni`",
"4":
"Simile a FamilySearch e Antenati, con un focus sui registri dello Stato Civile
(XIX-XX secolo) ma con accesso anche a collezioni parrocchiali.",
"5": "Stato
Civile indicizzato, liste di leva, censimenti, alberi genealogici pubblici."
},
{
"1": "\**Archivio Storico Diocesano di Cremona (come fonte)**",
"2": "È
l'ente che \**conserva fisicamente** i registri parrocchiali originali. Se la
ricerca online non dà frutti, questo è il punto di riferimento. Il loro sito
web può fornire inventari, contatti e modalità di accesso (in loco o per
corrispondenza).",
"3": "Non è un portale di ricerca, ma la \\"query\\" sarebbe
una richiesta formale via email o telefono: \\"Ricerca atto di battesimo per
Giovanni Pigoli, nato circa 1790, figlio di \[se noto], in una parrocchia del
comune di \[se noto]...\\"",
"4": "Dal Concilio di Trento (circa 1563) fino ai
giorni nostri. La fonte più completa in assoluto.",
"5": "Originali dei
\**Registri Parrocchiali**: Battesimi, Matrimoni, Morti, Cresime, Stati delle
Anime (censimenti parrocchiali)."
}
] | [{'1': '\**FamilySearch**', '2': 'È il
portale \**più importante** per questa ricerca. Ha digitalizzato (spesso solo
come immagini non indicizzate) una vastissima quantità di registri parrocchiali
italiani, inclusi quelli della Diocesi di Cremona. È gratuito.', '3': '1.
\**Ricerca indicizzata (se fortunati):** \`Nome: Giovanni` \`Cognome: Pigoli`
\`Luogo di nascita: Cremona, Italy` \`Periodo: 1785-1795`
2. \**Navigazione
manuale (più probabile):** \`Catalogo > Luoghi > Italy, Cremona > \[Nome del
Comune] > Church records` e sfogliare le immagini dei registri di battesimo del
periodo.', '4': 'Molto ampio, spesso dal tardo 1500 fino al 1900 inoltrato, a
seconda della parrocchia. Ideale per il 1790.', '5': '\**Registri
Parrocchiali** (Battesimi, Matrimoni, Morti, Stati delle Anime). Anche Stato
Civile per periodi successivi.'}, {'1': '\**Portale Antenati (Archivi di
Stato)**', '2': 'Portale ufficiale degli Archivi di Stato italiani.
\**Fondamentale** per proseguire la ricerca sui discendenti di Giovanni Pigoli,
ma \**improbabile** che contenga il suo atto di nascita del 1790, poiché ospita
principalmente lo Stato Civile.', '3': 'La ricerca non è per nome, ma per fondo
archivistico. Il percorso è: \`Esplora gli archivi > Archivio di Stato di
Cremona > Stato civile napoleonico / Stato civile della restaurazione >
\[Comune] > Nati \[Anno]`', '4': 'Principalmente dal 1806/1809 fino al 1940
circa, a seconda dei fondi versati dagli archivi.', '5': '\**Stato Civile**
(Atti di Nascita, Matrimonio, Morte, Pubblicazioni, Cittadinanza). Non contiene
registri parrocchiali.'}, {'1': '\**Ancestry**', '2': 'Piattaforma commerciale
con un potente motore di ricerca e la funzione di "suggerimenti" (hints).
Spesso indicizza collezioni presenti anche su FamilySearch, rendendo la ricerca
più rapida. Utile anche per trovare alberi genealogici di altri utenti.', '3':
'\`Nome: Giovanni Pigoli` \`Luogo di nascita: Cremona, Lombardia, Italia`
\`Anno di nascita: 1790 ±5 anni`', '4': 'Simile a FamilySearch e Antenati, con
un focus sui registri dello Stato Civile (XIX-XX secolo) ma con accesso anche a
collezioni parrocchiali.', '5': 'Stato Civile indicizzato, liste di leva,
censimenti, alberi genealogici pubblici.'}, {'1': '\**Archivio Storico
Diocesano di Cremona (come fonte)**', '2': "È l'ente che \**conserva
fisicamente** i registri parrocchiali originali. Se la ricerca online non dà
frutti, questo è il punto di riferimento. Il loro sito web può fornire
inventari, contatti e modalità di accesso (in loco o per corrispondenza).",
'3': 'Non è un portale di ricerca, ma la "query" sarebbe una richiesta formale
via email o telefono: "Ricerca atto di battesimo per Giovanni Pigoli, nato
circa 1790, figlio di \[se noto], in una parrocchia del comune di \[se
noto]..."', '4': 'Dal Concilio di Trento (circa 1563) fino ai giorni nostri. La
fonte più completa in assoluto.', '5': 'Originali dei \**Registri
Parrocchiali**: Battesimi, Matrimoni, Morti, Cresime, Stati delle Anime
(censimenti parrocchiali).'}] | 2 |
| Gemini | [
{
"1": "\**FamilySearch**",
"2": "**È il portale più importante per questa ricerca.** Possiede la più vasta
collezione al mondo di registri parrocchiali italiani microfilmati e
digitalizzati, inclusi quelli della Diocesi di Cremona. È gratuito, previa
registrazione.",
"3": "La ricerca per nome potrebbe non dare risultati. La
strategia migliore è navigare il catalogo: \`Cerca > Catalogo > Luogo: Italy,
Cremona > Cliccare su \\"Registri parrocchiali di Cremona (Diocesi)\\" >
Selezionare la parrocchia di interesse e l'anno.`",
"4": "~1560 - ~1910",
"5":
"\**Battesimi, Matrimoni, Morti (Sepolture)**, Stati delle Anime (censimenti
parrocchiali)."
},
{
"1": "\**Portale Antenati (SAN)**",
"2": "Portale
ufficiale degli Archivi di Stato Italiani. Fondamentale per trovare la famiglia
Pigoli nelle generazioni successive (figli, nipoti) e per contestualizzare la
ricerca. La sua copertura per Cremona parte dal periodo napoleonico.",
"3":
"Ricerca per nominativo: \`Cognome: Pigoli, Nome: Giovanni` (utile per trovare
un suo eventuale atto di morte se vissuto fino al 1806+). Oppure navigazione:
\`Sfoglia i registri > Cremona > Selezionare il comune > Stato Civile
Napoleonico.`",
"4": "1806 - 1942 (per Cremona)",
"5": "\**Stato Civile
Napoleonico e della Restaurazione** (Nascite, Matrimoni, Morti,
Pubblicazioni)."
},
{
"1": "\**Ancestry**",
"2": "Piattaforma commerciale con
un potente motore di ricerca. Può avere collezioni indicizzate che non si
trovano altrove o alberi genealogici di altri utenti che possono fornire indizi
preziosi. Spesso utilizza le stesse fonti di Antenati e FamilySearch, ma con
un'interfaccia di ricerca più immediata.",
"3": "Ricerca globale con filtri:
\`Nome: Giovanni Pigoli, Luogo di nascita: Cremona, Italy, Anno di nascita:
1790 ±5 anni.`",
"4": "Vario, principalmente dal 1806 in poi per gli atti
civili.",
"5": "Atti di Stato Civile, liste di leva, alberi genealogici
pubblici."
}
] | [{'1': '\**FamilySearch**', '2': '**È il portale più
importante per questa ricerca.** Possiede la più vasta collezione al mondo di
registri parrocchiali italiani microfilmati e digitalizzati, inclusi quelli
della Diocesi di Cremona. È gratuito, previa registrazione.', '3': 'La ricerca
per nome potrebbe non dare risultati. La strategia migliore è navigare il
catalogo: \`Cerca > Catalogo > Luogo: Italy, Cremona > Cliccare su "Registri
parrocchiali di Cremona (Diocesi)" > Selezionare la parrocchia di interesse e
l\\'anno.`', '4': '~1560 - ~1910', '5': '\**Battesimi, Matrimoni, Morti
(Sepolture)**, Stati delle Anime (censimenti parrocchiali).'}, {'1':
'\**Portale Antenati (SAN)**', '2': 'Portale ufficiale degli Archivi di Stato
Italiani. Fondamentale per trovare la famiglia Pigoli nelle generazioni
successive (figli, nipoti) e per contestualizzare la ricerca. La sua copertura
per Cremona parte dal periodo napoleonico.', '3': 'Ricerca per nominativo:
\`Cognome: Pigoli, Nome: Giovanni` (utile per trovare un suo eventuale atto di
morte se vissuto fino al 1806+). Oppure navigazione: \`Sfoglia i registri >
Cremona > Selezionare il comune > Stato Civile Napoleonico.`', '4': '1806 -
1942 (per Cremona)', '5': '\**Stato Civile Napoleonico e della Restaurazione**
(Nascite, Matrimoni, Morti, Pubblicazioni).'}, {'1': '\**Ancestry**', '2':
"Piattaforma commerciale con un potente motore di ricerca. Può avere collezioni
indicizzate che non si trovano altrove o alberi genealogici di altri utenti che
possono fornire indizi preziosi. Spesso utilizza le stesse fonti di Antenati e
FamilySearch, ma con un'interfaccia di ricerca più immediata.", '3': 'Ricerca
globale con filtri: \`Nome: Giovanni Pigoli, Luogo di nascita: Cremona, Italy,
Anno di nascita: 1790 ±5 anni.`', '4': 'Vario, principalmente dal 1806 in poi
per gli atti civili.', '5': 'Atti di Stato Civile, liste di leva, alberi
genealogici pubblici.'}] | 2 |
| Gemini | [
{
"1": "\**FamilySearch**",
"2": "È
la risorsa \**più importante e completa** per i registri parrocchiali italiani,
specialmente per il periodo pre-unitario (prima del 1866). La collezione per la
provincia di Cremona è vasta e la consultazione è gratuita.",
"3": "\**1.
Ricerca per nome:** \`Giovanni Pigoli`, Luogo di nascita: \`Cremona, Italy`,
Anno: \`1785-1795`.
**2. (Più efficace) Navigazione nel Catalogo:** Cerca per
Luogo > \`Italy, Cremona` > Seleziona il comune di interesse > Cerca nella
sezione \`Church records`.",
"4": "Molto variabile, ma per Cremona si trovano
registri parrocchiali che partono dal tardo \**1500** fino al primo **'900**.",
"5": "\**Battesimi, Matrimoni, Morti** (registri parrocchiali). In alcune aree
anche Stato Civile e Censimenti (Stati delle Anime)."
},
{
"1": "\**Portale
Antenati (SAN)**",
"2": "Portale ufficiale degli Archivi di Stato Italiani.
\**Fondamentale per il periodo successivo**, per trovare l'eventuale atto di
morte di Giovanni o gli atti di nascita/matrimonio dei suoi figli, che
potrebbero essere registrati nello Stato Civile.",
"3": "Usa la funzione
\\"Trova i nomi\\".
Nome: \`Giovanni`
Cognome: \`Pigoli`
Seleziona l'Archivio
di Stato di \`Cremona`.
*Nota: la ricerca sarà fruttuosa per atti successivi al
1806.*",
"4": "Principalmente \**Stato Civile Napoleonico** (ca. 1806-1815) e
\**Stato Civile Italiano** (1866-1940 ca.).",
"5": "\**Nascita, Matrimonio,
Morte, Cittadinanza** (Stato Civile). Allegati matrimoniali (processetti)."
},
{
"1": "\**Ancestry**",
"2": "Potente motore di ricerca e indicizzazione. Anche
se molti dati provengono da FamilySearch, la sua tecnologia può \**facilitare
il ritrovamento** di record e suggerire collegamenti familiari (\\"hints\\")
che potrebbero sfuggire a una ricerca manuale.",
"3": "Ricerca globale:
\`Giovanni Pigoli`
Nato in: \`Cremona, Italy`
Data di nascita: \`1790 ±5
years`",
"4": "Simile a FamilySearch, con un focus sui periodi con alta
indicizzazione (principalmente dal \**1800** in poi).",
"5": "Battesimi,
Matrimoni, Morti, Stato Civile, liste di leva, registri di immigrazione."
},
{
"1": "\**Archivio Diocesano di Cremona**",
"2": "È la \**fonte primaria** dei
registri parrocchiali. Il loro sito web è il punto di riferimento per capire
quali parrocchie sono state digitalizzate, quali no, e per ottenere contatti
diretti per una ricerca mirata su fondi non ancora online.",
"3": "Non è un
motore di ricerca. La \\"query\\" è una richiesta via email o la consultazione
dell'inventario online, es: \\"Ricerca atto di battesimo per Giovanni Pigoli,
nato circa 1790, presumibilmente nella parrocchia di \[Nome Comune, se
noto]\\".",
"4": "Dal \**Concilio di Trento (ca. 1564)** fino ai giorni nostri,
a seconda della parrocchia e dello stato di conservazione.",
"5": "Registri di
\**Battesimo, Cresima, Matrimonio, Morte**. Status Animarum (Stati delle
Anime)."
}
] | [{'1': '\**FamilySearch**', '2': 'È la risorsa \**più importante
e completa** per i registri parrocchiali italiani, specialmente per il periodo
pre-unitario (prima del 1866). La collezione per la provincia di Cremona è
vasta e la consultazione è gratuita.', '3': '\**1. Ricerca per nome:**
\`Giovanni Pigoli`, Luogo di nascita: \`Cremona, Italy`, Anno: \`1785-1795`.
\**2. (Più efficace) Navigazione nel Catalogo:** Cerca per Luogo > \`Italy,
Cremona` > Seleziona il comune di interesse > Cerca nella sezione \`Church
records`.', '4': "Molto variabile, ma per Cremona si trovano registri
parrocchiali che partono dal tardo \**1500** fino al primo **'900**.", '5':
'\**Battesimi, Matrimoni, Morti** (registri parrocchiali). In alcune aree anche
Stato Civile e Censimenti (Stati delle Anime).'}, {'1': '\**Portale Antenati
(SAN)**', '2': "Portale ufficiale degli Archivi di Stato Italiani.
\**Fondamentale per il periodo successivo**, per trovare l'eventuale atto di
morte di Giovanni o gli atti di nascita/matrimonio dei suoi figli, che
potrebbero essere registrati nello Stato Civile.", '3': 'Usa la funzione "Trova
i nomi".
Nome: \`Giovanni`
Cognome: \`Pigoli`
Seleziona l\\'Archivio di Stato
di \`Cremona`.
*Nota: la ricerca sarà fruttuosa per atti successivi al 1806.*',
'4': 'Principalmente \**Stato Civile Napoleonico** (ca. 1806-1815) e \**Stato
Civile Italiano** (1866-1940 ca.).', '5': '\**Nascita, Matrimonio, Morte,
Cittadinanza** (Stato Civile). Allegati matrimoniali (processetti).'}, {'1':
'\**Ancestry**', '2': 'Potente motore di ricerca e indicizzazione. Anche se
molti dati provengono da FamilySearch, la sua tecnologia può \**facilitare il
ritrovamento** di record e suggerire collegamenti familiari ("hints") che
potrebbero sfuggire a una ricerca manuale.', '3': 'Ricerca globale:
\`Giovanni
Pigoli`
Nato in: \`Cremona, Italy`
Data di nascita: \`1790 ±5 years`', '4':
'Simile a FamilySearch, con un focus sui periodi con alta indicizzazione
(principalmente dal \**1800** in poi).', '5': 'Battesimi, Matrimoni, Morti,
Stato Civile, liste di leva, registri di immigrazione.'}, {'1': '\**Archivio
Diocesano di Cremona**', '2': 'È la \**fonte primaria** dei registri
parrocchiali. Il loro sito web è il punto di riferimento per capire quali
parrocchie sono state digitalizzate, quali no, e per ottenere contatti diretti
per una ricerca mirata su fondi non ancora online.', '3': 'Non è un motore di
ricerca. La "query" è una richiesta via email o la consultazione
dell\\'inventario online, es: "Ricerca atto di battesimo per Giovanni Pigoli,
nato circa 1790, presumibilmente nella parrocchia di \[Nome Comune, se
noto]".', '4': 'Dal \**Concilio di Trento (ca. 1564)** fino ai giorni nostri, a
seconda della parrocchia e dello stato di conservazione.', '5': 'Registri di
\**Battesimo, Cresima, Matrimonio, Morte**. Status Animarum (Stati delle
Anime).'}] | 2 |
| Gemini | [
{
"1": "\**FamilySearch**",
"2": "È la risorsa
\**più importante e completa** per i registri parrocchiali italiani,
specialmente per il periodo pre-unitario (prima del 1866). La collezione per la
provincia di Cremona è vasta e la consultazione è gratuita.",
"3": "\**1.
Ricerca per nome:** \`Giovanni Pigoli`, Luogo di nascita: \`Cremona, Italy`,
Anno: \`1785-1795`.
**2. (Più efficace) Navigazione nel Catalogo:** Cerca per
Luogo > \`Italy, Cremona` > Seleziona il comune di interesse > Cerca nella
sezione \`Church records`.",
"4": "Molto variabile, ma per Cremona si trovano
registri parrocchiali che partono dal tardo \**1500** fino al primo **'900**.",
"5": "\**Battesimi, Matrimoni, Morti** (registri parrocchiali). In alcune aree
anche Stato Civile e Censimenti (Stati delle Anime)."
},
{
"1": "\**Portale
Antenati (SAN)**",
"2": "Portale ufficiale degli Archivi di Stato Italiani.
\**Fondamentale per il periodo successivo**, per trovare l'eventuale atto di
morte di Giovanni o gli atti di nascita/matrimonio dei suoi figli, che
potrebbero essere registrati nello Stato Civile.",
"3": "Usa la funzione
\\"Trova i nomi\\".
Nome: \`Giovanni`
Cognome: \`Pigoli`
Seleziona l'Archivio
di Stato di \`Cremona`.
*Nota: la ricerca sarà fruttuosa per atti successivi al
1806.*",
"4": "Principalmente \**Stato Civile Napoleonico** (ca. 1806-1815) e
\**Stato Civile Italiano** (1866-1940 ca.).",
"5": "\**Nascita, Matrimonio,
Morte, Cittadinanza** (Stato Civile). Allegati matrimoniali (processetti)."
},
{
"1": "\**Ancestry**",
"2": "Potente motore di ricerca e indicizzazione. Anche
se molti dati provengono da FamilySearch, la sua tecnologia può \**facilitare
il ritrovamento** di record e suggerire collegamenti familiari (\\"hints\\")
che potrebbero sfuggire a una ricerca manuale.",
"3": "Ricerca globale:
\`Giovanni Pigoli`
Nato in: \`Cremona, Italy`
Data di nascita: \`1790 ±5
years`",
"4": "Simile a FamilySearch, con un focus sui periodi con alta
indicizzazione (principalmente dal \**1800** in poi).",
"5": "Battesimi,
Matrimoni, Morti, Stato Civile, liste di leva, registri di immigrazione."
},
{
"1": "\**Archivio Diocesano di Cremona**",
"2": "È la \**fonte primaria** dei
registri parrocchiali. Il loro sito web è il punto di riferimento per capire
quali parrocchie sono state digitalizzate, quali no, e per ottenere contatti
diretti per una ricerca mirata su fondi non ancora online.",
"3": "Non è un
motore di ricerca. La \\"query\\" è una richiesta via email o la consultazione
dell'inventario online, es: \\"Ricerca atto di battesimo per Giovanni Pigoli,
nato circa 1790, presumibilmente nella parrocchia di \[Nome Comune, se
noto]\\".",
"4": "Dal \**Concilio di Trento (ca. 1564)** fino ai giorni nostri,
a seconda della parrocchia e dello stato di conservazione.",
"5": "Registri di
\**Battesimo, Cresima, Matrimonio, Morte**. Status Animarum (Stati delle
Anime)."
}
] | [{'1': '\**FamilySearch**', '2': 'È la risorsa \**più importante
e completa** per i registri parrocchiali italiani, specialmente per il periodo
pre-unitario (prima del 1866). La collezione per la provincia di Cremona è
vasta e la consultazione è gratuita.', '3': '\**1. Ricerca per nome:**
\`Giovanni Pigoli`, Luogo di nascita: \`Cremona, Italy`, Anno: \`1785-1795`.
\**2. (Più efficace) Navigazione nel Catalogo:** Cerca per Luogo > \`Italy,
Cremona` > Seleziona il comune di interesse > Cerca nella sezione \`Church
records`.', '4': "Molto variabile, ma per Cremona si trovano registri
parrocchiali che partono dal tardo \**1500** fino al primo **'900**.", '5':
'\**Battesimi, Matrimoni, Morti** (registri parrocchiali). In alcune aree anche
Stato Civile e Censimenti (Stati delle Anime).'}, {'1': '\**Portale Antenati
(SAN)**', '2': "Portale ufficiale degli Archivi di Stato Italiani.
\**Fondamentale per il periodo successivo**, per trovare l'eventuale atto di
morte di Giovanni o gli atti di nascita/matrimonio dei suoi figli, che
potrebbero essere registrati nello Stato Civile.", '3': 'Usa la funzione "Trova
i nomi".
Nome: \`Giovanni`
Cognome: \`Pigoli`
Seleziona l\\'Archivio di Stato
di \`Cremona`.
*Nota: la ricerca sarà fruttuosa per atti successivi al 1806.*',
'4': 'Principalmente \**Stato Civile Napoleonico** (ca. 1806-1815) e \**Stato
Civile Italiano** (1866-1940 ca.).', '5': '\**Nascita, Matrimonio, Morte,
Cittadinanza** (Stato Civile). Allegati matrimoniali (processetti).'}, {'1':
'\**Ancestry**', '2': 'Potente motore di ricerca e indicizzazione. Anche se
molti dati provengono da FamilySearch, la sua tecnologia può \**facilitare il
ritrovamento** di record e suggerire collegamenti familiari ("hints") che
potrebbero sfuggire a una ricerca manuale.', '3': 'Ricerca globale:
\`Giovanni
Pigoli`
Nato in: \`Cremona, Italy`
Data di nascita: \`1790 ±5 years`', '4':
'Simile a FamilySearch, con un focus sui periodi con alta indicizzazione
(principalmente dal \**1800** in poi).', '5': 'Battesimi, Matrimoni, Morti,
Stato Civile, liste di leva, registri di immigrazione.'}, {'1': '\**Archivio
Diocesano di Cremona**', '2': 'È la \**fonte primaria** dei registri
parrocchiali. Il loro sito web è il punto di riferimento per capire quali
parrocchie sono state digitalizzate, quali no, e per ottenere contatti diretti
per una ricerca mirata su fondi non ancora online.', '3': 'Non è un motore di
ricerca. La "query" è una richiesta via email o la consultazione
dell\\'inventario online, es: "Ricerca atto di battesimo per Giovanni Pigoli,
nato circa 1790, presumibilmente nella parrocchia di \[Nome Comune, se
noto]".', '4': 'Dal \**Concilio di Trento (ca. 1564)** fino ai giorni nostri, a
seconda della parrocchia e dello stato di conservazione.', '5': 'Registri di
\**Battesimo, Cresima, Matrimonio, Morte**. Status Animarum (Stati delle
Anime).'}] | 2 |
| Claude | [
{
"1": "\**FamilySearch.org**",
"2": "Più grande
archivio gratuito con registri parrocchiali lombardi digitalizzati.
Collaborazione diretta con diocesi italiane.",
"3": "\`Giovanni Pigoli Cremona
1780-1810` oppure navigare: Italia → Lombardia → Cremona → \[Parrocchia]",
"4":
"1560-1940 (variabile per parrocchia)",
"5": "Battesimi, matrimoni, sepolture,
stati delle anime"
},
{
"1": "\**Antenati.san.beniculturali.it**",
"2":
"Portale ufficiale degli Archivi di Stato italiani. Contiene duplicati
parrocchiali depositati presso l'Archivio di Stato di Cremona.",
"3": "Cerca:
\\"Pigoli\\" + Località + intervallo 1780-1810",
"4": "1790-1865 (registri
napoleonici e post)",
"5": "Nascite, matrimoni, morti (copie civili dei
registri parrocchiali)"
},
{
"1": "\**Diocesi di Cremona - Archivio Storico**",
"2": "Accesso diretto ai registri originali. Alcune parrocchie hanno inventari
online. Necessario contatto diretto.",
"3": "Contattare:
archivio@diocesidicremona.it specificando \\"Pigoli Giovanni, ~1790, parrocchia
di \[nome]\\"",
"4": "1545-1900+",
"5": "Registri parrocchiali originali, stati
delle anime, libri dei morti"
},
{
"1": "\**Ancestry.it**",
"2": "Database
commerciale con collezioni esclusive e strumenti di ricerca avanzati. Indici
nominativi facilitano la ricerca.",
"3": "\`Pigoli` + Cremona + 1785-1800
(filtro Italia Settentrionale)",
"4": "1700-1900",
"5": "Battesimi, matrimoni,
sepolture (selezione)"
},
{
"1": "\**MyHeritage.it**",
"2": "Buona copertura
nord Italia, tecnologia Smart Matching per collegamenti familiari automatici.",
"3": "Albero: inserire \\"Giovanni Pigoli\\" nato ~1790 Cremona → Record
Match",
"4": "1700-1920",
"5": "Registri parrocchiali, anagrafe civile"
},
{
"1": "\**Portale Lombardia Beni Culturali**",
"2": "Archivi storici lombardi
digitalizzati, include fondi parrocchiali e notarili della provincia di
Cremona.",
"3": "Cerca nel catalogo: \\"registri parrocchiali Cremona\\" +
cognome Pigoli",
"4": "1500-1860",
"5": "Inventari parrocchiali, atti notarili,
catasti"
},
{
"1": "\**Cognomix.it / Italia Genealogica**",
"2": "Utile per
mappare la distribuzione del cognome Pigoli e identificare le parrocchie più
probabili.",
"3": "Cerca: \\"Pigoli\\" → distribuzione geografica",
"4":
"Database moderno",
"5": "Distribuzione cognomi, forum genealogici"
}
] |
[{'1': '\**FamilySearch.org**', '2': 'Più grande archivio gratuito con registri
parrocchiali lombardi digitalizzati. Collaborazione diretta con diocesi
italiane.', '3': '\`Giovanni Pigoli Cremona 1780-1810` oppure navigare: Italia
→ Lombardia → Cremona → \[Parrocchia]', '4': '1560-1940 (variabile per
parrocchia)', '5': 'Battesimi, matrimoni, sepolture, stati delle anime'}, {'1':
'\**Antenati.san.beniculturali.it**', '2': "Portale ufficiale degli Archivi di
Stato italiani. Contiene duplicati parrocchiali depositati presso l'Archivio di
Stato di Cremona.", '3': 'Cerca: "Pigoli" + Località + intervallo 1780-1810',
'4': '1790-1865 (registri napoleonici e post)', '5': 'Nascite, matrimoni, morti
(copie civili dei registri parrocchiali)'}, {'1': '\**Diocesi di Cremona -
Archivio Storico**', '2': 'Accesso diretto ai registri originali. Alcune
parrocchie hanno inventari online. Necessario contatto diretto.', '3':
'Contattare: archivio@diocesidicremona.it specificando "Pigoli Giovanni, ~1790,
parrocchia di \[nome]"', '4': '1545-1900+', '5': 'Registri parrocchiali
originali, stati delle anime, libri dei morti'}, {'1': '\**Ancestry.it**', '2':
'Database commerciale con collezioni esclusive e strumenti di ricerca avanzati.
Indici nominativi facilitano la ricerca.', '3': '\`Pigoli` + Cremona +
1785-1800 (filtro Italia Settentrionale)', '4': '1700-1900', '5': 'Battesimi,
matrimoni, sepolture (selezione)'}, {'1': '\**MyHeritage.it**', '2': 'Buona
copertura nord Italia, tecnologia Smart Matching per collegamenti familiari
automatici.', '3': 'Albero: inserire "Giovanni Pigoli" nato ~1790 Cremona →
Record Match', '4': '1700-1920', '5': 'Registri parrocchiali, anagrafe
civile'}, {'1': '\**Portale Lombardia Beni Culturali**', '2': 'Archivi storici
lombardi digitalizzati, include fondi parrocchiali e notarili della provincia
di Cremona.', '3': 'Cerca nel catalogo: "registri parrocchiali Cremona" +
cognome Pigoli', '4': '1500-1860', '5': 'Inventari parrocchiali, atti notarili,
catasti'}, {'1': '\**Cognomix.it / Italia Genealogica**', '2': 'Utile per
mappare la distribuzione del cognome Pigoli e identificare le parrocchie più
probabili.', '3': 'Cerca: "Pigoli" → distribuzione geografica', '4': 'Database
moderno', '5': 'Distribuzione cognomi, forum genealogici'}] | 1 |
| DeepSeek |
\[ERRORE]: Error code: 402 - {'error': {'message': 'Insufficient Balance',
'type': 'unknown_error', 'param': None, 'code': 'invalid_request_error'}} | []
| 1 |


