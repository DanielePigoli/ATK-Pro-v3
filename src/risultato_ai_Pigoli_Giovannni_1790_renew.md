**Legenda risultati AI:**


- **Provider**: il servizio AI che ha generato la risposta (es. Claude, Gemini,
  ecc.)
- **Slot**: la posizione della chiave usata nel caveau per quel provider
- **Tabella**: ogni colonna corrisponde a un'informazione richiesta dal prompt
  (es. Portale, Motivazione, Query di esempio, Periodo, Tipo atti,
  Filtri/Strategie)
- Se la modalità 'tutte le risposte' è attiva, vedrai una sezione per ogni
  provider che ha restituito risultati utili


| provider | raw | results | slot |
| --- | --- | --- | --- |
| Gemini | [
{
"1": "\**FamilySearch.org**",
"2": "È la risorsa più vasta e gratuita per i
registri parrocchiali italiani, spesso digitalizzati direttamente dalle
diocesi. Molto probabile trovare i registri di battesimo, matrimonio e morte
per Olmeneta e Casalbuttano ed Uniti.",
"3": "1. \**Ricerca per luogo:**
\`Italy, Cremona, Olmeneta, Catholic Church Records` (per sfogliare i
registri). 
2. \**Ricerca per nome (se indicizzato):** \`Giovanni Pigoli,
Olmeneta, Cremona, Italy, birth ~1790` 
3. \**Per i figli:** \`Giuseppe Antonio
Maria Pigoli, Olmeneta, Cremona, Italy, birth 1810`",
"4": "Generalmente dal
XVI secolo fino a metà/fine XIX secolo, a volte inizio XX. Perfetto per il
periodo ~1790 e i primi decenni del 1800.",
"5": "Registri di Battesimo,
Matrimonio, Morte, Cresima, Stati d'anime."
},
{
"1": "\**Portale degli
Antenati (Archivi di Stato)**",
"2": "È il portale ufficiale degli Archivi di
Stato italiani. Sebbene si concentri principalmente sullo Stato Civile
(post-napoleonico), è fondamentale per il periodo di transizione e per i figli.
Potrebbe contenere anche fondi parrocchiali digitalizzati per alcune
province.",
"3": "1. \**Per Giovanni (se sposato dopo 1809/1815):** \`Stato
Civile, Olmeneta, Matrimoni, 1809-1815` (per lo Stato Civile Napoleonico). 
2.
\**Per i figli:** \`Stato Civile, Olmeneta, Nati, 1810` (per Giuseppe). 
3.
\**Per Pietro:** \`Stato Civile, Casalbuttano ed Uniti, Morti, 1891`",
"4":
"Principalmente dal 1809/1815 (Stato Civile Napoleonico) fino a circa 1940
(Stato Civile Italiano). Alcuni fondi parrocchiali possono estendersi prima.",
"5": "Stato Civile (Nati, Matrimoni, Morti, Allegati), Liste di Leva, Ruoli
Matricolari."
},
{
"1": "\**Ancestry.com**",
"2": "Offre un'ampia collezione di
registri italiani, inclusi molti registri parrocchiali e di stato civile,
spesso con indici di nomi che facilitano la ricerca. È un servizio a
pagamento.",
"3": "1. \**Per Giovanni:** \`Giovanni Pigoli, born ~1790,
Olmeneta, Cremona, Italy` (cercando nella collezione \\"Italy, Catholic Church
Records, 1570-1978\\"). 
2. \**Per i figli:** \`Giuseppe Antonio Maria Pigoli,
born 1810, Olmeneta, Cremona, Italy` (cercando anche in \\"Italy, Civil
Registration, 1809-1900s\\").",
"4": "Varia, ma spesso dal XVI secolo fino a
metà/fine XIX secolo per i parrocchiali; dal 1809/1815 per lo stato civile.",
"5": "Registri di Battesimo, Matrimonio, Morte (parrocchiali); Nati, Matrimoni,
Morti (stato civile)."
},
{
"1": "\**MyHeritage.it**",
"2": "Simile ad
Ancestry, MyHeritage ha collezioni significative di registri italiani, sia
parrocchiali che di stato civile, con una buona capacità di ricerca e indici. È
un servizio a pagamento.",
"3": "1. \**Per Giovanni:** \`Giovanni Pigoli,
Olmeneta, Cremona, Italy, birth year ~1790` (cercando nelle collezioni
\\"Italy, Catholic Church Records\\" o \\"Italy, Civil Registration\\"). 
2.
\**Per la moglie:** \`Rosa Scolari, Olmeneta, Cremona, Italy, marriage year
~1809`",
"4": "Varia, ma spesso dal XVI secolo fino a metà/fine XIX secolo per
i parrocchiali; dal 1809/1815 per lo stato civile.",
"5": "Registri di
Battesimo, Matrimonio, Morte (parrocchiali); Nati, Matrimoni, Morti (stato
civile)."
}
] | [{'1': '\**FamilySearch.org**', '2': 'È la risorsa più vasta e
gratuita per i registri parrocchiali italiani, spesso digitalizzati
direttamente dalle diocesi. Molto probabile trovare i registri di battesimo,
matrimonio e morte per Olmeneta e Casalbuttano ed Uniti.', '3': '1. \**Ricerca
per luogo:** \`Italy, Cremona, Olmeneta, Catholic Church Records` (per
sfogliare i registri). 
2. \**Ricerca per nome (se indicizzato):** \`Giovanni
Pigoli, Olmeneta, Cremona, Italy, birth ~1790` 
3. \**Per i figli:** \`Giuseppe
Antonio Maria Pigoli, Olmeneta, Cremona, Italy, birth 1810`', '4':
'Generalmente dal XVI secolo fino a metà/fine XIX secolo, a volte inizio XX.
Perfetto per il periodo ~1790 e i primi decenni del 1800.', '5': "Registri di
Battesimo, Matrimonio, Morte, Cresima, Stati d'anime."}, {'1': '\**Portale
degli Antenati (Archivi di Stato)**', '2': 'È il portale ufficiale degli
Archivi di Stato italiani. Sebbene si concentri principalmente sullo Stato
Civile (post-napoleonico), è fondamentale per il periodo di transizione e per i
figli. Potrebbe contenere anche fondi parrocchiali digitalizzati per alcune
province.', '3': '1. \**Per Giovanni (se sposato dopo 1809/1815):** \`Stato
Civile, Olmeneta, Matrimoni, 1809-1815` (per lo Stato Civile Napoleonico). 
2.
\**Per i figli:** \`Stato Civile, Olmeneta, Nati, 1810` (per Giuseppe). 
3.
\**Per Pietro:** \`Stato Civile, Casalbuttano ed Uniti, Morti, 1891`', '4':
'Principalmente dal 1809/1815 (Stato Civile Napoleonico) fino a circa 1940
(Stato Civile Italiano). Alcuni fondi parrocchiali possono estendersi prima.',
'5': 'Stato Civile (Nati, Matrimoni, Morti, Allegati), Liste di Leva, Ruoli
Matricolari.'}, {'1': '\**Ancestry.com**', '2': "Offre un'ampia collezione di
registri italiani, inclusi molti registri parrocchiali e di stato civile,
spesso con indici di nomi che facilitano la ricerca. È un servizio a
pagamento.", '3': '1. \**Per Giovanni:** \`Giovanni Pigoli, born ~1790,
Olmeneta, Cremona, Italy` (cercando nella collezione "Italy, Catholic Church
Records, 1570-1978"). 
2. \**Per i figli:** \`Giuseppe Antonio Maria Pigoli,
born 1810, Olmeneta, Cremona, Italy` (cercando anche in "Italy, Civil
Registration, 1809-1900s").', '4': 'Varia, ma spesso dal XVI secolo fino a
metà/fine XIX secolo per i parrocchiali; dal 1809/1815 per lo stato civile.',
'5': 'Registri di Battesimo, Matrimonio, Morte (parrocchiali); Nati, Matrimoni,
Morti (stato civile).'}, {'1': '\**MyHeritage.it**', '2': 'Simile ad Ancestry,
MyHeritage ha collezioni significative di registri italiani, sia parrocchiali
che di stato civile, con una buona capacità di ricerca e indici. È un servizio
a pagamento.', '3': '1. \**Per Giovanni:** \`Giovanni Pigoli, Olmeneta,
Cremona, Italy, birth year ~1790` (cercando nelle collezioni "Italy, Catholic
Church Records" o "Italy, Civil Registration"). 
2. \**Per la moglie:** \`Rosa
Scolari, Olmeneta, Cremona, Italy, marriage year ~1809`', '4': 'Varia, ma
spesso dal XVI secolo fino a metà/fine XIX secolo per i parrocchiali; dal
1809/1815 per lo stato civile.', '5': 'Registri di Battesimo, Matrimonio, Morte
(parrocchiali); Nati, Matrimoni, Morti (stato civile).'}] | 1 |
| Gemini | [
{
"1": "\**Antenati (Portale degli Archivi di Stato)**",
"2": "È il portale
ufficiale italiano per la ricerca genealogica. Contiene fondi di Stato Civile
(post-napoleonico) e, per molte località, anche i \**fondi parrocchiali
digitalizzati** dagli Archivi di Stato. Essenziale per la ricerca in Italia.",
"3": "1. Cerca per comune: \\"Olmeneta, Cremona, Parrocchia\\" o
\\"Casalbuttano ed Uniti, Cremona, Parrocchia\\" e poi sfoglia i registri. 
2.
Cerca per nome (se indicizzato): \\"Pigoli Giovanni, Cremona\\" (meno probabile
per il periodo parrocchiale). 
3. \**Strategia migliore:** Cerca i figli:
\\"Giuseppe Antonio Maria Pigoli, Olmeneta, 1810\\" (per trovare il suo atto di
nascita e risalire ai genitori) o \\"Pietro Pigoli, Casalbuttano ed Uniti,
1891\\" (per l'atto di morte che spesso indica i genitori).",
"4": "\**Registri
Parrocchiali:** Spesso dal XVI-XVII secolo fino all'inizio dello Stato Civile
(primi anni del XIX secolo). 
\**Stato Civile:** Principalmente 1809/1815 -
~1940.",
"5": "\**Registri Parrocchiali:** Battesimo, Matrimonio,
Morte/Sepoltura, Cresima, Stati d'Anime. 
\**Stato Civile:** Nascita,
Matrimonio, Morte, Cittadinanza, Leva."
},
{
"1": "\**FamilySearch**",
"2":
"Enorme database mondiale, gratuito, con una vasta collezione di microfilmi e
immagini digitalizzate di registri parrocchiali e di stato civile italiani.
Spesso ha collezioni non ancora presenti su Antenati o con indicizzazione più
dettagliata. Molto forte per la Lombardia.",
"3": "1. \**Ricerca nel
Catalogo:** \\"Italy, Cremona, Olmeneta, Church records\\" o \\"Italy, Cremona,
Casalbuttano ed Uniti, Church records\\" (poi sfoglia le immagini). 
2.
\**Ricerca per persona:** \\"Giovanni Pigoli, born ~1790, Cremona, Italy\\"
(potrebbe trovare collegamenti in alberi genealogici o record indicizzati). 
3.
\**Strategia migliore:** Cerca i figli: \\"Giuseppe Antonio Maria Pigoli, born
1810, Olmeneta\\" o \\"Pietro Pigoli, died 1891, Casalbuttano ed Uniti\\".",
"4": "\**Registri Parrocchiali:** Molto ampio, spesso dal XVI secolo fino al
XIX/XX secolo. 
\**Stato Civile:** Dal primo XIX secolo al XX secolo.",
"5":
"\**Registri Parrocchiali:** Battesimo, Matrimonio, Morte/Sepoltura, Cresima,
Stati d'Anime. 
\**Stato Civile:** Nascita, Matrimonio, Morte."
},
{
"1":
"\**Ancestry.com**",
"2": "Portale commerciale con collezioni significative per
l'Italia, inclusi registri parrocchiali e di stato civile. Spesso ha
indicizzazioni diverse o collezioni uniche rispetto a FamilySearch, o una
migliore interfaccia di ricerca per alcune collezioni.",
"3": "1. \**Ricerca
per persona:** \\"Giovanni Pigoli, born ~1790, Cremona, Italy\\". 
2.
\**Ricerca per collezione:** \\"Italy, Cremona, Civil Registration (State
Archives)\\" o \\"Italy, Catholic Church Records, 1809-1900\\" (poi filtra per
località). 
3. \**Strategia migliore:** Cerca i figli: \\"Giuseppe Antonio
Maria Pigoli, born 1810, Olmeneta\\" o \\"Pietro Pigoli, died 1891,
Casalbuttano ed Uniti\\".",
"4": "Varia per collezione, ma per i registri
parrocchiali e di stato civile, copre periodi simili a FamilySearch (dal
XVI-XVII secolo al XX secolo).",
"5": "\**Registri Parrocchiali:** Battesimo,
Matrimonio, Morte/Sepoltura. 
\**Stato Civile:** Nascita, Matrimonio, Morte."
},
{
"1": "\**MyHeritage**",
"2": "Portale commerciale con una forte presenza
in Europa. Offre un buon motore di ricerca e funzionalità come Smart Matches e
Record Matches che possono aiutare a trovare collegamenti in alberi genealogici
altrui o in collezioni di record.",
"3": "1. \**Ricerca per persona:**
\\"Giovanni Pigoli, born ~1790, Cremona, Italy\\". 
2. \**Ricerca per
collezione:** \\"Italy, Civil Registration, 1809-1900\\" (poi filtra per
Cremona). 
3. \**Strategia migliore:** Cerca i figli: \\"Pietro Pigoli, died
1891, Casalbuttano ed Uniti\\" (per trovare l'atto di morte che potrebbe
indicare i genitori e il luogo di nascita).",
"4": "Simile ad Ancestry e
FamilySearch per le collezioni di stato civile e parrocchiali.",
"5":
"\**Registri Parrocchiali:** Battesimo, Matrimonio, Morte/Sepoltura. 
\**Stato
Civile:** Nascita, Matrimonio, Morte."
}
] | [{'1': '\**Antenati (Portale degli
Archivi di Stato)**', '2': 'È il portale ufficiale italiano per la ricerca
genealogica. Contiene fondi di Stato Civile (post-napoleonico) e, per molte
località, anche i \**fondi parrocchiali digitalizzati** dagli Archivi di Stato.
Essenziale per la ricerca in Italia.', '3': '1. Cerca per comune: "Olmeneta,
Cremona, Parrocchia" o "Casalbuttano ed Uniti, Cremona, Parrocchia" e poi
sfoglia i registri. 
2. Cerca per nome (se indicizzato): "Pigoli Giovanni,
Cremona" (meno probabile per il periodo parrocchiale). 
3. \**Strategia
migliore:** Cerca i figli: "Giuseppe Antonio Maria Pigoli, Olmeneta, 1810" (per
trovare il suo atto di nascita e risalire ai genitori) o "Pietro Pigoli,
Casalbuttano ed Uniti, 1891" (per l\\'atto di morte che spesso indica i
genitori).', '4': "\**Registri Parrocchiali:** Spesso dal XVI-XVII secolo fino
all'inizio dello Stato Civile (primi anni del XIX secolo). 
\**Stato Civile:**
Principalmente 1809/1815 - ~1940.", '5': "\**Registri Parrocchiali:**
Battesimo, Matrimonio, Morte/Sepoltura, Cresima, Stati d'Anime. 
\**Stato
Civile:** Nascita, Matrimonio, Morte, Cittadinanza, Leva."}, {'1':
'\**FamilySearch**', '2': 'Enorme database mondiale, gratuito, con una vasta
collezione di microfilmi e immagini digitalizzate di registri parrocchiali e di
stato civile italiani. Spesso ha collezioni non ancora presenti su Antenati o
con indicizzazione più dettagliata. Molto forte per la Lombardia.', '3': '1.
\**Ricerca nel Catalogo:** "Italy, Cremona, Olmeneta, Church records" o "Italy,
Cremona, Casalbuttano ed Uniti, Church records" (poi sfoglia le immagini). 
2.
\**Ricerca per persona:** "Giovanni Pigoli, born ~1790, Cremona, Italy"
(potrebbe trovare collegamenti in alberi genealogici o record indicizzati). 
3.
\**Strategia migliore:** Cerca i figli: "Giuseppe Antonio Maria Pigoli, born
1810, Olmeneta" o "Pietro Pigoli, died 1891, Casalbuttano ed Uniti".', '4':
'\**Registri Parrocchiali:** Molto ampio, spesso dal XVI secolo fino al XIX/XX
secolo. 
\**Stato Civile:** Dal primo XIX secolo al XX secolo.', '5':
"\**Registri Parrocchiali:** Battesimo, Matrimonio, Morte/Sepoltura, Cresima,
Stati d'Anime. 
\**Stato Civile:** Nascita, Matrimonio, Morte."}, {'1':
'\**Ancestry.com**', '2': "Portale commerciale con collezioni significative per
l'Italia, inclusi registri parrocchiali e di stato civile. Spesso ha
indicizzazioni diverse o collezioni uniche rispetto a FamilySearch, o una
migliore interfaccia di ricerca per alcune collezioni.", '3': '1. \**Ricerca
per persona:** "Giovanni Pigoli, born ~1790, Cremona, Italy". 
2. \**Ricerca
per collezione:** "Italy, Cremona, Civil Registration (State Archives)" o
"Italy, Catholic Church Records, 1809-1900" (poi filtra per località). 
3.
\**Strategia migliore:** Cerca i figli: "Giuseppe Antonio Maria Pigoli, born
1810, Olmeneta" o "Pietro Pigoli, died 1891, Casalbuttano ed Uniti".', '4':
'Varia per collezione, ma per i registri parrocchiali e di stato civile, copre
periodi simili a FamilySearch (dal XVI-XVII secolo al XX secolo).', '5':
'\**Registri Parrocchiali:** Battesimo, Matrimonio, Morte/Sepoltura. 
\**Stato
Civile:** Nascita, Matrimonio, Morte.'}, {'1': '\**MyHeritage**', '2': 'Portale
commerciale con una forte presenza in Europa. Offre un buon motore di ricerca e
funzionalità come Smart Matches e Record Matches che possono aiutare a trovare
collegamenti in alberi genealogici altrui o in collezioni di record.', '3': '1.
\**Ricerca per persona:** "Giovanni Pigoli, born ~1790, Cremona, Italy". 
2.
\**Ricerca per collezione:** "Italy, Civil Registration, 1809-1900" (poi filtra
per Cremona). 
3. \**Strategia migliore:** Cerca i figli: "Pietro Pigoli, died
1891, Casalbuttano ed Uniti" (per trovare l\\'atto di morte che potrebbe
indicare i genitori e il luogo di nascita).', '4': 'Simile ad Ancestry e
FamilySearch per le collezioni di stato civile e parrocchiali.', '5':
'\**Registri Parrocchiali:** Battesimo, Matrimonio, Morte/Sepoltura. 
\**Stato
Civile:** Nascita, Matrimonio, Morte.'}] | 1 |
| Gemini | [
{
"1":
"\**FamilySearch.org**",
"2": "È la risorsa più vasta e gratuita per i registri
parrocchiali italiani, spesso digitalizzati direttamente dalle diocesi. Molto
probabile trovare i registri di battesimo, matrimonio e morte per Olmeneta e
Casalbuttano ed Uniti.",
"3": "1. \**Ricerca per luogo:** \`Italy, Cremona,
Olmeneta, Catholic Church Records` (per sfogliare i registri). 
2. \**Ricerca
per nome (se indicizzato):** \`Giovanni Pigoli, Olmeneta, Cremona, Italy, birth
~1790` 
3. \**Per i figli:** \`Giuseppe Antonio Maria Pigoli, Olmeneta,
Cremona, Italy, birth 1810`",
"4": "Generalmente dal XVI secolo fino a
metà/fine XIX secolo, a volte inizio XX. Perfetto per il periodo ~1790 e i
primi decenni del 1800.",
"5": "Registri di Battesimo, Matrimonio, Morte,
Cresima, Stati d'anime."
},
{
"1": "\**Portale degli Antenati (Archivi di
Stato)**",
"2": "È il portale ufficiale degli Archivi di Stato italiani.
Sebbene si concentri principalmente sullo Stato Civile (post-napoleonico), è
fondamentale per il periodo di transizione e per i figli. Potrebbe contenere
anche fondi parrocchiali digitalizzati per alcune province.",
"3": "1. \**Per
Giovanni (se sposato dopo 1809/1815):** \`Stato Civile, Olmeneta, Matrimoni,
1809-1815` (per lo Stato Civile Napoleonico). 
2. \**Per i figli:** \`Stato
Civile, Olmeneta, Nati, 1810` (per Giuseppe). 
3. \**Per Pietro:** \`Stato
Civile, Casalbuttano ed Uniti, Morti, 1891`",
"4": "Principalmente dal
1809/1815 (Stato Civile Napoleonico) fino a circa 1940 (Stato Civile Italiano).
Alcuni fondi parrocchiali possono estendersi prima.",
"5": "Stato Civile (Nati,
Matrimoni, Morti, Allegati), Liste di Leva, Ruoli Matricolari."
},
{
"1":
"\**Ancestry.com**",
"2": "Offre un'ampia collezione di registri italiani,
inclusi molti registri parrocchiali e di stato civile, spesso con indici di
nomi che facilitano la ricerca. È un servizio a pagamento.",
"3": "1. \**Per
Giovanni:** \`Giovanni Pigoli, born ~1790, Olmeneta, Cremona, Italy` (cercando
nella collezione \\"Italy, Catholic Church Records, 1570-1978\\"). 
2. \**Per i
figli:** \`Giuseppe Antonio Maria Pigoli, born 1810, Olmeneta, Cremona, Italy`
(cercando anche in \\"Italy, Civil Registration, 1809-1900s\\").",
"4": "Varia,
ma spesso dal XVI secolo fino a metà/fine XIX secolo per i parrocchiali; dal
1809/1815 per lo stato civile.",
"5": "Registri di Battesimo, Matrimonio, Morte
(parrocchiali); Nati, Matrimoni, Morti (stato civile)."
},
{
"1":
"\**MyHeritage.it**",
"2": "Simile ad Ancestry, MyHeritage ha collezioni
significative di registri italiani, sia parrocchiali che di stato civile, con
una buona capacità di ricerca e indici. È un servizio a pagamento.",
"3": "1.
\**Per Giovanni:** \`Giovanni Pigoli, Olmeneta, Cremona, Italy, birth year
~1790` (cercando nelle collezioni \\"Italy, Catholic Church Records\\" o
\\"Italy, Civil Registration\\"). 
2. \**Per la moglie:** \`Rosa Scolari,
Olmeneta, Cremona, Italy, marriage year ~1809`",
"4": "Varia, ma spesso dal XVI
secolo fino a metà/fine XIX secolo per i parrocchiali; dal 1809/1815 per lo
stato civile.",
"5": "Registri di Battesimo, Matrimonio, Morte (parrocchiali);
Nati, Matrimoni, Morti (stato civile)."
}
] | [{'1': '\**FamilySearch.org**',
'2': 'È la risorsa più vasta e gratuita per i registri parrocchiali italiani,
spesso digitalizzati direttamente dalle diocesi. Molto probabile trovare i
registri di battesimo, matrimonio e morte per Olmeneta e Casalbuttano ed
Uniti.', '3': '1. \**Ricerca per luogo:** \`Italy, Cremona, Olmeneta, Catholic
Church Records` (per sfogliare i registri). 
2. \**Ricerca per nome (se
indicizzato):** \`Giovanni Pigoli, Olmeneta, Cremona, Italy, birth ~1790` 
3.
\**Per i figli:** \`Giuseppe Antonio Maria Pigoli, Olmeneta, Cremona, Italy,
birth 1810`', '4': 'Generalmente dal XVI secolo fino a metà/fine XIX secolo, a
volte inizio XX. Perfetto per il periodo ~1790 e i primi decenni del 1800.',
'5': "Registri di Battesimo, Matrimonio, Morte, Cresima, Stati d'anime."},
{'1': '\**Portale degli Antenati (Archivi di Stato)**', '2': 'È il portale
ufficiale degli Archivi di Stato italiani. Sebbene si concentri principalmente
sullo Stato Civile (post-napoleonico), è fondamentale per il periodo di
transizione e per i figli. Potrebbe contenere anche fondi parrocchiali
digitalizzati per alcune province.', '3': '1. \**Per Giovanni (se sposato dopo
1809/1815):** \`Stato Civile, Olmeneta, Matrimoni, 1809-1815` (per lo Stato
Civile Napoleonico). 
2. \**Per i figli:** \`Stato Civile, Olmeneta, Nati,
1810` (per Giuseppe). 
3. \**Per Pietro:** \`Stato Civile, Casalbuttano ed
Uniti, Morti, 1891`', '4': 'Principalmente dal 1809/1815 (Stato Civile
Napoleonico) fino a circa 1940 (Stato Civile Italiano). Alcuni fondi
parrocchiali possono estendersi prima.', '5': 'Stato Civile (Nati, Matrimoni,
Morti, Allegati), Liste di Leva, Ruoli Matricolari.'}, {'1':
'\**Ancestry.com**', '2': "Offre un'ampia collezione di registri italiani,
inclusi molti registri parrocchiali e di stato civile, spesso con indici di
nomi che facilitano la ricerca. È un servizio a pagamento.", '3': '1. \**Per
Giovanni:** \`Giovanni Pigoli, born ~1790, Olmeneta, Cremona, Italy` (cercando
nella collezione "Italy, Catholic Church Records, 1570-1978"). 
2. \**Per i
figli:** \`Giuseppe Antonio Maria Pigoli, born 1810, Olmeneta, Cremona, Italy`
(cercando anche in "Italy, Civil Registration, 1809-1900s").', '4': 'Varia, ma
spesso dal XVI secolo fino a metà/fine XIX secolo per i parrocchiali; dal
1809/1815 per lo stato civile.', '5': 'Registri di Battesimo, Matrimonio, Morte
(parrocchiali); Nati, Matrimoni, Morti (stato civile).'}, {'1':
'\**MyHeritage.it**', '2': 'Simile ad Ancestry, MyHeritage ha collezioni
significative di registri italiani, sia parrocchiali che di stato civile, con
una buona capacità di ricerca e indici. È un servizio a pagamento.', '3': '1.
\**Per Giovanni:** \`Giovanni Pigoli, Olmeneta, Cremona, Italy, birth year
~1790` (cercando nelle collezioni "Italy, Catholic Church Records" o "Italy,
Civil Registration"). 
2. \**Per la moglie:** \`Rosa Scolari, Olmeneta,
Cremona, Italy, marriage year ~1809`', '4': 'Varia, ma spesso dal XVI secolo
fino a metà/fine XIX secolo per i parrocchiali; dal 1809/1815 per lo stato
civile.', '5': 'Registri di Battesimo, Matrimonio, Morte (parrocchiali); Nati,
Matrimoni, Morti (stato civile).'}] | 1 |
| Gemini | [
{
"1": "\**Antenati
(Portale degli Archivi di Stato)**",
"2": "È il portale ufficiale italiano per
la ricerca genealogica. Contiene fondi di Stato Civile (post-napoleonico) e,
per molte località, anche i \**fondi parrocchiali digitalizzati** dagli Archivi
di Stato. Essenziale per la ricerca in Italia.",
"3": "1. Cerca per comune:
\\"Olmeneta, Cremona, Parrocchia\\" o \\"Casalbuttano ed Uniti, Cremona,
Parrocchia\\" e poi sfoglia i registri. 
2. Cerca per nome (se indicizzato):
\\"Pigoli Giovanni, Cremona\\" (meno probabile per il periodo parrocchiale). 
3\. \**Strategia migliore:** Cerca i figli: \\"Giuseppe Antonio Maria Pigoli,
Olmeneta, 1810\\" (per trovare il suo atto di nascita e risalire ai genitori) o
\\"Pietro Pigoli, Casalbuttano ed Uniti, 1891\\" (per l'atto di morte che
spesso indica i genitori).",
"4": "\**Registri Parrocchiali:** Spesso dal
XVI-XVII secolo fino all'inizio dello Stato Civile (primi anni del XIX secolo).

\**Stato Civile:** Principalmente 1809/1815 - ~1940.",
"5": "\**Registri
Parrocchiali:** Battesimo, Matrimonio, Morte/Sepoltura, Cresima, Stati d'Anime.

\**Stato Civile:** Nascita, Matrimonio, Morte, Cittadinanza, Leva."
},
{
"1":
"\**FamilySearch**",
"2": "Enorme database mondiale, gratuito, con una vasta
collezione di microfilmi e immagini digitalizzate di registri parrocchiali e di
stato civile italiani. Spesso ha collezioni non ancora presenti su Antenati o
con indicizzazione più dettagliata. Molto forte per la Lombardia.",
"3": "1.
\**Ricerca nel Catalogo:** \\"Italy, Cremona, Olmeneta, Church records\\" o
\\"Italy, Cremona, Casalbuttano ed Uniti, Church records\\" (poi sfoglia le
immagini). 
2. \**Ricerca per persona:** \\"Giovanni Pigoli, born ~1790,
Cremona, Italy\\" (potrebbe trovare collegamenti in alberi genealogici o record
indicizzati). 
3. \**Strategia migliore:** Cerca i figli: \\"Giuseppe Antonio
Maria Pigoli, born 1810, Olmeneta\\" o \\"Pietro Pigoli, died 1891,
Casalbuttano ed Uniti\\".",
"4": "\**Registri Parrocchiali:** Molto ampio,
spesso dal XVI secolo fino al XIX/XX secolo. 
\**Stato Civile:** Dal primo XIX
secolo al XX secolo.",
"5": "\**Registri Parrocchiali:** Battesimo, Matrimonio,
Morte/Sepoltura, Cresima, Stati d'Anime. 
\**Stato Civile:** Nascita,
Matrimonio, Morte."
},
{
"1": "\**Ancestry.com**",
"2": "Portale commerciale
con collezioni significative per l'Italia, inclusi registri parrocchiali e di
stato civile. Spesso ha indicizzazioni diverse o collezioni uniche rispetto a
FamilySearch, o una migliore interfaccia di ricerca per alcune collezioni.",
"3": "1. \**Ricerca per persona:** \\"Giovanni Pigoli, born ~1790, Cremona,
Italy\\". 
2. \**Ricerca per collezione:** \\"Italy, Cremona, Civil
Registration (State Archives)\\" o \\"Italy, Catholic Church Records,
1809-1900\\" (poi filtra per località). 
3. \**Strategia migliore:** Cerca i
figli: \\"Giuseppe Antonio Maria Pigoli, born 1810, Olmeneta\\" o \\"Pietro
Pigoli, died 1891, Casalbuttano ed Uniti\\".",
"4": "Varia per collezione, ma
per i registri parrocchiali e di stato civile, copre periodi simili a
FamilySearch (dal XVI-XVII secolo al XX secolo).",
"5": "\**Registri
Parrocchiali:** Battesimo, Matrimonio, Morte/Sepoltura. 
\**Stato Civile:**
Nascita, Matrimonio, Morte."
},
{
"1": "\**MyHeritage**",
"2": "Portale
commerciale con una forte presenza in Europa. Offre un buon motore di ricerca e
funzionalità come Smart Matches e Record Matches che possono aiutare a trovare
collegamenti in alberi genealogici altrui o in collezioni di record.",
"3": "1.
\**Ricerca per persona:** \\"Giovanni Pigoli, born ~1790, Cremona, Italy\\". 
2\. \**Ricerca per collezione:** \\"Italy, Civil Registration, 1809-1900\\" (poi
filtra per Cremona). 
3. \**Strategia migliore:** Cerca i figli: \\"Pietro
Pigoli, died 1891, Casalbuttano ed Uniti\\" (per trovare l'atto di morte che
potrebbe indicare i genitori e il luogo di nascita).",
"4": "Simile ad Ancestry
e FamilySearch per le collezioni di stato civile e parrocchiali.",
"5":
"\**Registri Parrocchiali:** Battesimo, Matrimonio, Morte/Sepoltura. 
\**Stato
Civile:** Nascita, Matrimonio, Morte."
}
] | [{'1': '\**Antenati (Portale degli
Archivi di Stato)**', '2': 'È il portale ufficiale italiano per la ricerca
genealogica. Contiene fondi di Stato Civile (post-napoleonico) e, per molte
località, anche i \**fondi parrocchiali digitalizzati** dagli Archivi di Stato.
Essenziale per la ricerca in Italia.', '3': '1. Cerca per comune: "Olmeneta,
Cremona, Parrocchia" o "Casalbuttano ed Uniti, Cremona, Parrocchia" e poi
sfoglia i registri. 
2. Cerca per nome (se indicizzato): "Pigoli Giovanni,
Cremona" (meno probabile per il periodo parrocchiale). 
3. \**Strategia
migliore:** Cerca i figli: "Giuseppe Antonio Maria Pigoli, Olmeneta, 1810" (per
trovare il suo atto di nascita e risalire ai genitori) o "Pietro Pigoli,
Casalbuttano ed Uniti, 1891" (per l\\'atto di morte che spesso indica i
genitori).', '4': "\**Registri Parrocchiali:** Spesso dal XVI-XVII secolo fino
all'inizio dello Stato Civile (primi anni del XIX secolo). 
\**Stato Civile:**
Principalmente 1809/1815 - ~1940.", '5': "\**Registri Parrocchiali:**
Battesimo, Matrimonio, Morte/Sepoltura, Cresima, Stati d'Anime. 
\**Stato
Civile:** Nascita, Matrimonio, Morte, Cittadinanza, Leva."}, {'1':
'\**FamilySearch**', '2': 'Enorme database mondiale, gratuito, con una vasta
collezione di microfilmi e immagini digitalizzate di registri parrocchiali e di
stato civile italiani. Spesso ha collezioni non ancora presenti su Antenati o
con indicizzazione più dettagliata. Molto forte per la Lombardia.', '3': '1.
\**Ricerca nel Catalogo:** "Italy, Cremona, Olmeneta, Church records" o "Italy,
Cremona, Casalbuttano ed Uniti, Church records" (poi sfoglia le immagini). 
2.
\**Ricerca per persona:** "Giovanni Pigoli, born ~1790, Cremona, Italy"
(potrebbe trovare collegamenti in alberi genealogici o record indicizzati). 
3.
\**Strategia migliore:** Cerca i figli: "Giuseppe Antonio Maria Pigoli, born
1810, Olmeneta" o "Pietro Pigoli, died 1891, Casalbuttano ed Uniti".', '4':
'\**Registri Parrocchiali:** Molto ampio, spesso dal XVI secolo fino al XIX/XX
secolo. 
\**Stato Civile:** Dal primo XIX secolo al XX secolo.', '5':
"\**Registri Parrocchiali:** Battesimo, Matrimonio, Morte/Sepoltura, Cresima,
Stati d'Anime. 
\**Stato Civile:** Nascita, Matrimonio, Morte."}, {'1':
'\**Ancestry.com**', '2': "Portale commerciale con collezioni significative per
l'Italia, inclusi registri parrocchiali e di stato civile. Spesso ha
indicizzazioni diverse o collezioni uniche rispetto a FamilySearch, o una
migliore interfaccia di ricerca per alcune collezioni.", '3': '1. \**Ricerca
per persona:** "Giovanni Pigoli, born ~1790, Cremona, Italy". 
2. \**Ricerca
per collezione:** "Italy, Cremona, Civil Registration (State Archives)" o
"Italy, Catholic Church Records, 1809-1900" (poi filtra per località). 
3.
\**Strategia migliore:** Cerca i figli: "Giuseppe Antonio Maria Pigoli, born
1810, Olmeneta" o "Pietro Pigoli, died 1891, Casalbuttano ed Uniti".', '4':
'Varia per collezione, ma per i registri parrocchiali e di stato civile, copre
periodi simili a FamilySearch (dal XVI-XVII secolo al XX secolo).', '5':
'\**Registri Parrocchiali:** Battesimo, Matrimonio, Morte/Sepoltura. 
\**Stato
Civile:** Nascita, Matrimonio, Morte.'}, {'1': '\**MyHeritage**', '2': 'Portale
commerciale con una forte presenza in Europa. Offre un buon motore di ricerca e
funzionalità come Smart Matches e Record Matches che possono aiutare a trovare
collegamenti in alberi genealogici altrui o in collezioni di record.', '3': '1.
\**Ricerca per persona:** "Giovanni Pigoli, born ~1790, Cremona, Italy". 
2.
\**Ricerca per collezione:** "Italy, Civil Registration, 1809-1900" (poi filtra
per Cremona). 
3. \**Strategia migliore:** Cerca i figli: "Pietro Pigoli, died
1891, Casalbuttano ed Uniti" (per trovare l\\'atto di morte che potrebbe
indicare i genitori e il luogo di nascita).', '4': 'Simile ad Ancestry e
FamilySearch per le collezioni di stato civile e parrocchiali.', '5':
'\**Registri Parrocchiali:** Battesimo, Matrimonio, Morte/Sepoltura. 
\**Stato
Civile:** Nascita, Matrimonio, Morte.'}] | 1 |
| Gemini | [
{
"1":
"\**FamilySearch.org**",
"2": "È la risorsa più vasta e gratuita per i registri
parrocchiali italiani, spesso digitalizzati direttamente dalle diocesi. Molto
probabile trovare i registri di battesimo, matrimonio e morte per Olmeneta e
Casalbuttano ed Uniti.",
"3": "1. \**Ricerca per luogo:** \`Italy, Cremona,
Olmeneta, Catholic Church Records` (per sfogliare i registri). 
2. \**Ricerca
per nome (se indicizzato):** \`Giovanni Pigoli, Olmeneta, Cremona, Italy, birth
~1790` 
3. \**Per i figli:** \`Giuseppe Antonio Maria Pigoli, Olmeneta,
Cremona, Italy, birth 1810`",
"4": "Generalmente dal XVI secolo fino a
metà/fine XIX secolo, a volte inizio XX. Perfetto per il periodo ~1790 e i
primi decenni del 1800.",
"5": "Registri di Battesimo, Matrimonio, Morte,
Cresima, Stati d'anime."
},
{
"1": "\**Portale degli Antenati (Archivi di
Stato)**",
"2": "È il portale ufficiale degli Archivi di Stato italiani.
Sebbene si concentri principalmente sullo Stato Civile (post-napoleonico), è
fondamentale per il periodo di transizione e per i figli. Potrebbe contenere
anche fondi parrocchiali digitalizzati per alcune province.",
"3": "1. \**Per
Giovanni (se sposato dopo 1809/1815):** \`Stato Civile, Olmeneta, Matrimoni,
1809-1815` (per lo Stato Civile Napoleonico). 
2. \**Per i figli:** \`Stato
Civile, Olmeneta, Nati, 1810` (per Giuseppe). 
3. \**Per Pietro:** \`Stato
Civile, Casalbuttano ed Uniti, Morti, 1891`",
"4": "Principalmente dal
1809/1815 (Stato Civile Napoleonico) fino a circa 1940 (Stato Civile Italiano).
Alcuni fondi parrocchiali possono estendersi prima.",
"5": "Stato Civile (Nati,
Matrimoni, Morti, Allegati), Liste di Leva, Ruoli Matricolari."
},
{
"1":
"\**Ancestry.com**",
"2": "Offre un'ampia collezione di registri italiani,
inclusi molti registri parrocchiali e di stato civile, spesso con indici di
nomi che facilitano la ricerca. È un servizio a pagamento.",
"3": "1. \**Per
Giovanni:** \`Giovanni Pigoli, born ~1790, Olmeneta, Cremona, Italy` (cercando
nella collezione \\"Italy, Catholic Church Records, 1570-1978\\"). 
2. \**Per i
figli:** \`Giuseppe Antonio Maria Pigoli, born 1810, Olmeneta, Cremona, Italy`
(cercando anche in \\"Italy, Civil Registration, 1809-1900s\\").",
"4": "Varia,
ma spesso dal XVI secolo fino a metà/fine XIX secolo per i parrocchiali; dal
1809/1815 per lo stato civile.",
"5": "Registri di Battesimo, Matrimonio, Morte
(parrocchiali); Nati, Matrimoni, Morti (stato civile)."
},
{
"1":
"\**MyHeritage.it**",
"2": "Simile ad Ancestry, MyHeritage ha collezioni
significative di registri italiani, sia parrocchiali che di stato civile, con
una buona capacità di ricerca e indici. È un servizio a pagamento.",
"3": "1.
\**Per Giovanni:** \`Giovanni Pigoli, Olmeneta, Cremona, Italy, birth year
~1790` (cercando nelle collezioni \\"Italy, Catholic Church Records\\" o
\\"Italy, Civil Registration\\"). 
2. \**Per la moglie:** \`Rosa Scolari,
Olmeneta, Cremona, Italy, marriage year ~1809`",
"4": "Varia, ma spesso dal XVI
secolo fino a metà/fine XIX secolo per i parrocchiali; dal 1809/1815 per lo
stato civile.",
"5": "Registri di Battesimo, Matrimonio, Morte (parrocchiali);
Nati, Matrimoni, Morti (stato civile)."
}
] | [{'1': '\**FamilySearch.org**',
'2': 'È la risorsa più vasta e gratuita per i registri parrocchiali italiani,
spesso digitalizzati direttamente dalle diocesi. Molto probabile trovare i
registri di battesimo, matrimonio e morte per Olmeneta e Casalbuttano ed
Uniti.', '3': '1. \**Ricerca per luogo:** \`Italy, Cremona, Olmeneta, Catholic
Church Records` (per sfogliare i registri). 
2. \**Ricerca per nome (se
indicizzato):** \`Giovanni Pigoli, Olmeneta, Cremona, Italy, birth ~1790` 
3.
\**Per i figli:** \`Giuseppe Antonio Maria Pigoli, Olmeneta, Cremona, Italy,
birth 1810`', '4': 'Generalmente dal XVI secolo fino a metà/fine XIX secolo, a
volte inizio XX. Perfetto per il periodo ~1790 e i primi decenni del 1800.',
'5': "Registri di Battesimo, Matrimonio, Morte, Cresima, Stati d'anime."},
{'1': '\**Portale degli Antenati (Archivi di Stato)**', '2': 'È il portale
ufficiale degli Archivi di Stato italiani. Sebbene si concentri principalmente
sullo Stato Civile (post-napoleonico), è fondamentale per il periodo di
transizione e per i figli. Potrebbe contenere anche fondi parrocchiali
digitalizzati per alcune province.', '3': '1. \**Per Giovanni (se sposato dopo
1809/1815):** \`Stato Civile, Olmeneta, Matrimoni, 1809-1815` (per lo Stato
Civile Napoleonico). 
2. \**Per i figli:** \`Stato Civile, Olmeneta, Nati,
1810` (per Giuseppe). 
3. \**Per Pietro:** \`Stato Civile, Casalbuttano ed
Uniti, Morti, 1891`', '4': 'Principalmente dal 1809/1815 (Stato Civile
Napoleonico) fino a circa 1940 (Stato Civile Italiano). Alcuni fondi
parrocchiali possono estendersi prima.', '5': 'Stato Civile (Nati, Matrimoni,
Morti, Allegati), Liste di Leva, Ruoli Matricolari.'}, {'1':
'\**Ancestry.com**', '2': "Offre un'ampia collezione di registri italiani,
inclusi molti registri parrocchiali e di stato civile, spesso con indici di
nomi che facilitano la ricerca. È un servizio a pagamento.", '3': '1. \**Per
Giovanni:** \`Giovanni Pigoli, born ~1790, Olmeneta, Cremona, Italy` (cercando
nella collezione "Italy, Catholic Church Records, 1570-1978"). 
2. \**Per i
figli:** \`Giuseppe Antonio Maria Pigoli, born 1810, Olmeneta, Cremona, Italy`
(cercando anche in "Italy, Civil Registration, 1809-1900s").', '4': 'Varia, ma
spesso dal XVI secolo fino a metà/fine XIX secolo per i parrocchiali; dal
1809/1815 per lo stato civile.', '5': 'Registri di Battesimo, Matrimonio, Morte
(parrocchiali); Nati, Matrimoni, Morti (stato civile).'}, {'1':
'\**MyHeritage.it**', '2': 'Simile ad Ancestry, MyHeritage ha collezioni
significative di registri italiani, sia parrocchiali che di stato civile, con
una buona capacità di ricerca e indici. È un servizio a pagamento.', '3': '1.
\**Per Giovanni:** \`Giovanni Pigoli, Olmeneta, Cremona, Italy, birth year
~1790` (cercando nelle collezioni "Italy, Catholic Church Records" o "Italy,
Civil Registration"). 
2. \**Per la moglie:** \`Rosa Scolari, Olmeneta,
Cremona, Italy, marriage year ~1809`', '4': 'Varia, ma spesso dal XVI secolo
fino a metà/fine XIX secolo per i parrocchiali; dal 1809/1815 per lo stato
civile.', '5': 'Registri di Battesimo, Matrimonio, Morte (parrocchiali); Nati,
Matrimoni, Morti (stato civile).'}] | 1 |
| Gemini | [
{
"1": "\**Antenati
(Portale degli Archivi di Stato)**",
"2": "È il portale ufficiale italiano per
la ricerca genealogica. Contiene fondi di Stato Civile (post-napoleonico) e,
per molte località, anche i \**fondi parrocchiali digitalizzati** dagli Archivi
di Stato. Essenziale per la ricerca in Italia.",
"3": "1. Cerca per comune:
\\"Olmeneta, Cremona, Parrocchia\\" o \\"Casalbuttano ed Uniti, Cremona,
Parrocchia\\" e poi sfoglia i registri. 
2. Cerca per nome (se indicizzato):
\\"Pigoli Giovanni, Cremona\\" (meno probabile per il periodo parrocchiale). 
3\. \**Strategia migliore:** Cerca i figli: \\"Giuseppe Antonio Maria Pigoli,
Olmeneta, 1810\\" (per trovare il suo atto di nascita e risalire ai genitori) o
\\"Pietro Pigoli, Casalbuttano ed Uniti, 1891\\" (per l'atto di morte che
spesso indica i genitori).",
"4": "\**Registri Parrocchiali:** Spesso dal
XVI-XVII secolo fino all'inizio dello Stato Civile (primi anni del XIX secolo).

\**Stato Civile:** Principalmente 1809/1815 - ~1940.",
"5": "\**Registri
Parrocchiali:** Battesimo, Matrimonio, Morte/Sepoltura, Cresima, Stati d'Anime.

\**Stato Civile:** Nascita, Matrimonio, Morte, Cittadinanza, Leva."
},
{
"1":
"\**FamilySearch**",
"2": "Enorme database mondiale, gratuito, con una vasta
collezione di microfilmi e immagini digitalizzate di registri parrocchiali e di
stato civile italiani. Spesso ha collezioni non ancora presenti su Antenati o
con indicizzazione più dettagliata. Molto forte per la Lombardia.",
"3": "1.
\**Ricerca nel Catalogo:** \\"Italy, Cremona, Olmeneta, Church records\\" o
\\"Italy, Cremona, Casalbuttano ed Uniti, Church records\\" (poi sfoglia le
immagini). 
2. \**Ricerca per persona:** \\"Giovanni Pigoli, born ~1790,
Cremona, Italy\\" (potrebbe trovare collegamenti in alberi genealogici o record
indicizzati). 
3. \**Strategia migliore:** Cerca i figli: \\"Giuseppe Antonio
Maria Pigoli, born 1810, Olmeneta\\" o \\"Pietro Pigoli, died 1891,
Casalbuttano ed Uniti\\".",
"4": "\**Registri Parrocchiali:** Molto ampio,
spesso dal XVI secolo fino al XIX/XX secolo. 
\**Stato Civile:** Dal primo XIX
secolo al XX secolo.",
"5": "\**Registri Parrocchiali:** Battesimo, Matrimonio,
Morte/Sepoltura, Cresima, Stati d'Anime. 
\**Stato Civile:** Nascita,
Matrimonio, Morte."
},
{
"1": "\**Ancestry.com**",
"2": "Portale commerciale
con collezioni significative per l'Italia, inclusi registri parrocchiali e di
stato civile. Spesso ha indicizzazioni diverse o collezioni uniche rispetto a
FamilySearch, o una migliore interfaccia di ricerca per alcune collezioni.",
"3": "1. \**Ricerca per persona:** \\"Giovanni Pigoli, born ~1790, Cremona,
Italy\\". 
2. \**Ricerca per collezione:** \\"Italy, Cremona, Civil
Registration (State Archives)\\" o \\"Italy, Catholic Church Records,
1809-1900\\" (poi filtra per località). 
3. \**Strategia migliore:** Cerca i
figli: \\"Giuseppe Antonio Maria Pigoli, born 1810, Olmeneta\\" o \\"Pietro
Pigoli, died 1891, Casalbuttano ed Uniti\\".",
"4": "Varia per collezione, ma
per i registri parrocchiali e di stato civile, copre periodi simili a
FamilySearch (dal XVI-XVII secolo al XX secolo).",
"5": "\**Registri
Parrocchiali:** Battesimo, Matrimonio, Morte/Sepoltura. 
\**Stato Civile:**
Nascita, Matrimonio, Morte."
},
{
"1": "\**MyHeritage**",
"2": "Portale
commerciale con una forte presenza in Europa. Offre un buon motore di ricerca e
funzionalità come Smart Matches e Record Matches che possono aiutare a trovare
collegamenti in alberi genealogici altrui o in collezioni di record.",
"3": "1.
\**Ricerca per persona:** \\"Giovanni Pigoli, born ~1790, Cremona, Italy\\". 
2\. \**Ricerca per collezione:** \\"Italy, Civil Registration, 1809-1900\\" (poi
filtra per Cremona). 
3. \**Strategia migliore:** Cerca i figli: \\"Pietro
Pigoli, died 1891, Casalbuttano ed Uniti\\" (per trovare l'atto di morte che
potrebbe indicare i genitori e il luogo di nascita).",
"4": "Simile ad Ancestry
e FamilySearch per le collezioni di stato civile e parrocchiali.",
"5":
"\**Registri Parrocchiali:** Battesimo, Matrimonio, Morte/Sepoltura. 
\**Stato
Civile:** Nascita, Matrimonio, Morte."
}
] | [{'1': '\**Antenati (Portale degli
Archivi di Stato)**', '2': 'È il portale ufficiale italiano per la ricerca
genealogica. Contiene fondi di Stato Civile (post-napoleonico) e, per molte
località, anche i \**fondi parrocchiali digitalizzati** dagli Archivi di Stato.
Essenziale per la ricerca in Italia.', '3': '1. Cerca per comune: "Olmeneta,
Cremona, Parrocchia" o "Casalbuttano ed Uniti, Cremona, Parrocchia" e poi
sfoglia i registri. 
2. Cerca per nome (se indicizzato): "Pigoli Giovanni,
Cremona" (meno probabile per il periodo parrocchiale). 
3. \**Strategia
migliore:** Cerca i figli: "Giuseppe Antonio Maria Pigoli, Olmeneta, 1810" (per
trovare il suo atto di nascita e risalire ai genitori) o "Pietro Pigoli,
Casalbuttano ed Uniti, 1891" (per l\\'atto di morte che spesso indica i
genitori).', '4': "\**Registri Parrocchiali:** Spesso dal XVI-XVII secolo fino
all'inizio dello Stato Civile (primi anni del XIX secolo). 
\**Stato Civile:**
Principalmente 1809/1815 - ~1940.", '5': "\**Registri Parrocchiali:**
Battesimo, Matrimonio, Morte/Sepoltura, Cresima, Stati d'Anime. 
\**Stato
Civile:** Nascita, Matrimonio, Morte, Cittadinanza, Leva."}, {'1':
'\**FamilySearch**', '2': 'Enorme database mondiale, gratuito, con una vasta
collezione di microfilmi e immagini digitalizzate di registri parrocchiali e di
stato civile italiani. Spesso ha collezioni non ancora presenti su Antenati o
con indicizzazione più dettagliata. Molto forte per la Lombardia.', '3': '1.
\**Ricerca nel Catalogo:** "Italy, Cremona, Olmeneta, Church records" o "Italy,
Cremona, Casalbuttano ed Uniti, Church records" (poi sfoglia le immagini). 
2.
\**Ricerca per persona:** "Giovanni Pigoli, born ~1790, Cremona, Italy"
(potrebbe trovare collegamenti in alberi genealogici o record indicizzati). 
3.
\**Strategia migliore:** Cerca i figli: "Giuseppe Antonio Maria Pigoli, born
1810, Olmeneta" o "Pietro Pigoli, died 1891, Casalbuttano ed Uniti".', '4':
'\**Registri Parrocchiali:** Molto ampio, spesso dal XVI secolo fino al XIX/XX
secolo. 
\**Stato Civile:** Dal primo XIX secolo al XX secolo.', '5':
"\**Registri Parrocchiali:** Battesimo, Matrimonio, Morte/Sepoltura, Cresima,
Stati d'Anime. 
\**Stato Civile:** Nascita, Matrimonio, Morte."}, {'1':
'\**Ancestry.com**', '2': "Portale commerciale con collezioni significative per
l'Italia, inclusi registri parrocchiali e di stato civile. Spesso ha
indicizzazioni diverse o collezioni uniche rispetto a FamilySearch, o una
migliore interfaccia di ricerca per alcune collezioni.", '3': '1. \**Ricerca
per persona:** "Giovanni Pigoli, born ~1790, Cremona, Italy". 
2. \**Ricerca
per collezione:** "Italy, Cremona, Civil Registration (State Archives)" o
"Italy, Catholic Church Records, 1809-1900" (poi filtra per località). 
3.
\**Strategia migliore:** Cerca i figli: "Giuseppe Antonio Maria Pigoli, born
1810, Olmeneta" o "Pietro Pigoli, died 1891, Casalbuttano ed Uniti".', '4':
'Varia per collezione, ma per i registri parrocchiali e di stato civile, copre
periodi simili a FamilySearch (dal XVI-XVII secolo al XX secolo).', '5':
'\**Registri Parrocchiali:** Battesimo, Matrimonio, Morte/Sepoltura. 
\**Stato
Civile:** Nascita, Matrimonio, Morte.'}, {'1': '\**MyHeritage**', '2': 'Portale
commerciale con una forte presenza in Europa. Offre un buon motore di ricerca e
funzionalità come Smart Matches e Record Matches che possono aiutare a trovare
collegamenti in alberi genealogici altrui o in collezioni di record.', '3': '1.
\**Ricerca per persona:** "Giovanni Pigoli, born ~1790, Cremona, Italy". 
2.
\**Ricerca per collezione:** "Italy, Civil Registration, 1809-1900" (poi filtra
per Cremona). 
3. \**Strategia migliore:** Cerca i figli: "Pietro Pigoli, died
1891, Casalbuttano ed Uniti" (per trovare l\\'atto di morte che potrebbe
indicare i genitori e il luogo di nascita).', '4': 'Simile ad Ancestry e
FamilySearch per le collezioni di stato civile e parrocchiali.', '5':
'\**Registri Parrocchiali:** Battesimo, Matrimonio, Morte/Sepoltura. 
\**Stato
Civile:** Nascita, Matrimonio, Morte.'}] | 1 |
| Gemini | [
{
"1":
"\**FamilySearch.org**",
"2": "È la risorsa più vasta e gratuita per i registri
parrocchiali italiani, spesso digitalizzati direttamente dalle diocesi. Molto
probabile trovare i registri di battesimo, matrimonio e morte per Olmeneta e
Casalbuttano ed Uniti.",
"3": "1. \**Ricerca per luogo:** \`Italy, Cremona,
Olmeneta, Catholic Church Records` (per sfogliare i registri). 
2. \**Ricerca
per nome (se indicizzato):** \`Giovanni Pigoli, Olmeneta, Cremona, Italy, birth
~1790` 
3. \**Per i figli:** \`Giuseppe Antonio Maria Pigoli, Olmeneta,
Cremona, Italy, birth 1810`",
"4": "Generalmente dal XVI secolo fino a
metà/fine XIX secolo, a volte inizio XX. Perfetto per il periodo ~1790 e i
primi decenni del 1800.",
"5": "Registri di Battesimo, Matrimonio, Morte,
Cresima, Stati d'anime."
},
{
"1": "\**Portale degli Antenati (Archivi di
Stato)**",
"2": "È il portale ufficiale degli Archivi di Stato italiani.
Sebbene si concentri principalmente sullo Stato Civile (post-napoleonico), è
fondamentale per il periodo di transizione e per i figli. Potrebbe contenere
anche fondi parrocchiali digitalizzati per alcune province.",
"3": "1. \**Per
Giovanni (se sposato dopo 1809/1815):** \`Stato Civile, Olmeneta, Matrimoni,
1809-1815` (per lo Stato Civile Napoleonico). 
2. \**Per i figli:** \`Stato
Civile, Olmeneta, Nati, 1810` (per Giuseppe). 
3. \**Per Pietro:** \`Stato
Civile, Casalbuttano ed Uniti, Morti, 1891`",
"4": "Principalmente dal
1809/1815 (Stato Civile Napoleonico) fino a circa 1940 (Stato Civile Italiano).
Alcuni fondi parrocchiali possono estendersi prima.",
"5": "Stato Civile (Nati,
Matrimoni, Morti, Allegati), Liste di Leva, Ruoli Matricolari."
},
{
"1":
"\**Ancestry.com**",
"2": "Offre un'ampia collezione di registri italiani,
inclusi molti registri parrocchiali e di stato civile, spesso con indici di
nomi che facilitano la ricerca. È un servizio a pagamento.",
"3": "1. \**Per
Giovanni:** \`Giovanni Pigoli, born ~1790, Olmeneta, Cremona, Italy` (cercando
nella collezione \\"Italy, Catholic Church Records, 1570-1978\\"). 
2. \**Per i
figli:** \`Giuseppe Antonio Maria Pigoli, born 1810, Olmeneta, Cremona, Italy`
(cercando anche in \\"Italy, Civil Registration, 1809-1900s\\").",
"4": "Varia,
ma spesso dal XVI secolo fino a metà/fine XIX secolo per i parrocchiali; dal
1809/1815 per lo stato civile.",
"5": "Registri di Battesimo, Matrimonio, Morte
(parrocchiali); Nati, Matrimoni, Morti (stato civile)."
},
{
"1":
"\**MyHeritage.it**",
"2": "Simile ad Ancestry, MyHeritage ha collezioni
significative di registri italiani, sia parrocchiali che di stato civile, con
una buona capacità di ricerca e indici. È un servizio a pagamento.",
"3": "1.
\**Per Giovanni:** \`Giovanni Pigoli, Olmeneta, Cremona, Italy, birth year
~1790` (cercando nelle collezioni \\"Italy, Catholic Church Records\\" o
\\"Italy, Civil Registration\\"). 
2. \**Per la moglie:** \`Rosa Scolari,
Olmeneta, Cremona, Italy, marriage year ~1809`",
"4": "Varia, ma spesso dal XVI
secolo fino a metà/fine XIX secolo per i parrocchiali; dal 1809/1815 per lo
stato civile.",
"5": "Registri di Battesimo, Matrimonio, Morte (parrocchiali);
Nati, Matrimoni, Morti (stato civile)."
}
] | [{'1': '\**FamilySearch.org**',
'2': 'È la risorsa più vasta e gratuita per i registri parrocchiali italiani,
spesso digitalizzati direttamente dalle diocesi. Molto probabile trovare i
registri di battesimo, matrimonio e morte per Olmeneta e Casalbuttano ed
Uniti.', '3': '1. \**Ricerca per luogo:** \`Italy, Cremona, Olmeneta, Catholic
Church Records` (per sfogliare i registri). 
2. \**Ricerca per nome (se
indicizzato):** \`Giovanni Pigoli, Olmeneta, Cremona, Italy, birth ~1790` 
3.
\**Per i figli:** \`Giuseppe Antonio Maria Pigoli, Olmeneta, Cremona, Italy,
birth 1810`', '4': 'Generalmente dal XVI secolo fino a metà/fine XIX secolo, a
volte inizio XX. Perfetto per il periodo ~1790 e i primi decenni del 1800.',
'5': "Registri di Battesimo, Matrimonio, Morte, Cresima, Stati d'anime."},
{'1': '\**Portale degli Antenati (Archivi di Stato)**', '2': 'È il portale
ufficiale degli Archivi di Stato italiani. Sebbene si concentri principalmente
sullo Stato Civile (post-napoleonico), è fondamentale per il periodo di
transizione e per i figli. Potrebbe contenere anche fondi parrocchiali
digitalizzati per alcune province.', '3': '1. \**Per Giovanni (se sposato dopo
1809/1815):** \`Stato Civile, Olmeneta, Matrimoni, 1809-1815` (per lo Stato
Civile Napoleonico). 
2. \**Per i figli:** \`Stato Civile, Olmeneta, Nati,
1810` (per Giuseppe). 
3. \**Per Pietro:** \`Stato Civile, Casalbuttano ed
Uniti, Morti, 1891`', '4': 'Principalmente dal 1809/1815 (Stato Civile
Napoleonico) fino a circa 1940 (Stato Civile Italiano). Alcuni fondi
parrocchiali possono estendersi prima.', '5': 'Stato Civile (Nati, Matrimoni,
Morti, Allegati), Liste di Leva, Ruoli Matricolari.'}, {'1':
'\**Ancestry.com**', '2': "Offre un'ampia collezione di registri italiani,
inclusi molti registri parrocchiali e di stato civile, spesso con indici di
nomi che facilitano la ricerca. È un servizio a pagamento.", '3': '1. \**Per
Giovanni:** \`Giovanni Pigoli, born ~1790, Olmeneta, Cremona, Italy` (cercando
nella collezione "Italy, Catholic Church Records, 1570-1978"). 
2. \**Per i
figli:** \`Giuseppe Antonio Maria Pigoli, born 1810, Olmeneta, Cremona, Italy`
(cercando anche in "Italy, Civil Registration, 1809-1900s").', '4': 'Varia, ma
spesso dal XVI secolo fino a metà/fine XIX secolo per i parrocchiali; dal
1809/1815 per lo stato civile.', '5': 'Registri di Battesimo, Matrimonio, Morte
(parrocchiali); Nati, Matrimoni, Morti (stato civile).'}, {'1':
'\**MyHeritage.it**', '2': 'Simile ad Ancestry, MyHeritage ha collezioni
significative di registri italiani, sia parrocchiali che di stato civile, con
una buona capacità di ricerca e indici. È un servizio a pagamento.', '3': '1.
\**Per Giovanni:** \`Giovanni Pigoli, Olmeneta, Cremona, Italy, birth year
~1790` (cercando nelle collezioni "Italy, Catholic Church Records" o "Italy,
Civil Registration"). 
2. \**Per la moglie:** \`Rosa Scolari, Olmeneta,
Cremona, Italy, marriage year ~1809`', '4': 'Varia, ma spesso dal XVI secolo
fino a metà/fine XIX secolo per i parrocchiali; dal 1809/1815 per lo stato
civile.', '5': 'Registri di Battesimo, Matrimonio, Morte (parrocchiali); Nati,
Matrimoni, Morti (stato civile).'}] | 1 |
| Claude | [
{
"1":
"\**FamilySearch.org**",
"2": "Principale archivio digitale con microfilm dei
registri parrocchiali lombardi. Ha indicizzazioni parziali per la diocesi di
Cremona e accesso gratuito",
"3": "\`Pigoli Giovanni Cremona` oppure sfoglia:
Italia > Lombardia > Cremona > Olmeneta",
"4": "1565-1900 (variabile per
parrocchia)",
"5": "Battesimi, matrimoni, morti, stati d'anime"
},
{
"1":
"\**Antenati.san.it**",
"2": "Portale degli Archivi di Stato italiani. Contiene
digitalizzazioni dello Stato Civile napoleonico e post-unitario per Cremona",
"3": "\`Pigoli` + filtro Cremona; sfoglia Comune Olmeneta/Casalbuttano",
"4":
"1806-1900 (Stato Civile); registri parrocchiali limitati",
"5": "Nascite,
matrimoni, morti, allegati (atti notori)"
},
{
"1": "\**Archivio Diocesano di
Cremona** (diocesidicremona.it)",
"2": "Conserva gli originali dei registri
parrocchiali. Alcuni inventari online, consultazione su richiesta",
"3":
"Contatto diretto per parrocchia di Olmeneta e Casalbuttano",
"4":
"1545-1900+",
"5": "Battesimi, cresime, matrimoni, morti, stati d'anime"
},
{
"1": "\**Lombardia Beni Culturali** (lombardiabeniculturali.it)",
"2": "Portale
regionale con inventari e alcune digitalizzazioni di archivi parrocchiali
lombardi",
"3": "\`Parrocchia Olmeneta` nella sezione Archivi",
"4": "Inventari
vari, digitalizzazioni limitate",
"5": "Inventari archivistici, alcuni
registri"
},
{
"1": "\**Ancestry.it**",
"2": "Database a pagamento con
collezioni italiane, inclusi alcuni registri lombardi e indici nominativi",
"3": "\`Giovanni Pigoli` + luogo Cremona",
"4": "1700-1900 (copertura
parziale)",
"5": "Battesimi, matrimoni, morti, emigrazione"
},
{
"1":
"\**MyHeritage.it**",
"2": "Aggregatore con Record Matching e collezioni
italiane, utile per incrociare dati con altri ricercatori",
"3": "\`Pigoli
Giovanni born 1790 Cremona`",
"4": "Variabile",
"5": "Alberi genealogici, atti
vari"
},
{
"1": "\**Cognomix.it / Gens Loci**",
"2": "Utile per distribuzione
geografica del cognome Pigoli e possibili varianti ortografiche (Pigola,
Pigolli)",
"3": "\`Pigoli distribuzione`",
"4": "Statistiche moderne,
riferimenti storici",
"5": "Mappe cognomi, etimologia"
}
] | [{'1':
'\**FamilySearch.org**', '2': 'Principale archivio digitale con microfilm dei
registri parrocchiali lombardi. Ha indicizzazioni parziali per la diocesi di
Cremona e accesso gratuito', '3': '\`Pigoli Giovanni Cremona` oppure sfoglia:
Italia > Lombardia > Cremona > Olmeneta', '4': '1565-1900 (variabile per
parrocchia)', '5': "Battesimi, matrimoni, morti, stati d'anime"}, {'1':
'\**Antenati.san.it**', '2': 'Portale degli Archivi di Stato italiani. Contiene
digitalizzazioni dello Stato Civile napoleonico e post-unitario per Cremona',
'3': '\`Pigoli` + filtro Cremona; sfoglia Comune Olmeneta/Casalbuttano', '4':
'1806-1900 (Stato Civile); registri parrocchiali limitati', '5': 'Nascite,
matrimoni, morti, allegati (atti notori)'}, {'1': '\**Archivio Diocesano di
Cremona** (diocesidicremona.it)', '2': 'Conserva gli originali dei registri
parrocchiali. Alcuni inventari online, consultazione su richiesta', '3':
'Contatto diretto per parrocchia di Olmeneta e Casalbuttano', '4':
'1545-1900+', '5': "Battesimi, cresime, matrimoni, morti, stati d'anime"},
{'1': '\**Lombardia Beni Culturali** (lombardiabeniculturali.it)', '2':
'Portale regionale con inventari e alcune digitalizzazioni di archivi
parrocchiali lombardi', '3': '\`Parrocchia Olmeneta` nella sezione Archivi',
'4': 'Inventari vari, digitalizzazioni limitate', '5': 'Inventari archivistici,
alcuni registri'}, {'1': '\**Ancestry.it**', '2': 'Database a pagamento con
collezioni italiane, inclusi alcuni registri lombardi e indici nominativi',
'3': '\`Giovanni Pigoli` + luogo Cremona', '4': '1700-1900 (copertura
parziale)', '5': 'Battesimi, matrimoni, morti, emigrazione'}, {'1':
'\**MyHeritage.it**', '2': 'Aggregatore con Record Matching e collezioni
italiane, utile per incrociare dati con altri ricercatori', '3': '\`Pigoli
Giovanni born 1790 Cremona`', '4': 'Variabile', '5': 'Alberi genealogici, atti
vari'}, {'1': '\**Cognomix.it / Gens Loci**', '2': 'Utile per distribuzione
geografica del cognome Pigoli e possibili varianti ortografiche (Pigola,
Pigolli)', '3': '\`Pigoli distribuzione`', '4': 'Statistiche moderne,
riferimenti storici', '5': 'Mappe cognomi, etimologia'}] | 1 |
| DeepSeek | [
{
"1": "\**Antenati (Archivio di Stato)**",
"2": "Portale ufficiale italiano con
digitalizzazione massiva dei registri parrocchiali e di stato civile. Per
Cremona copre ampiamente il periodo e l'area di Olmeneta.",
"3": "\`Pigoli
Giovanni` + filtro \\"Cremona\\" + \\"Registri parrocchiali\\" (usare il motore
interno o navigare per comune)",
"4": "~1790-1900 (con lacune locali)",
"5":
"Battesimi, matrimoni, morti, stati d'anime."
},
{
"1": "\**FamilySearch**",
"2": "Piattaforma mondiale gratuita con la più vasta collezione di microfilm
parrocchiali italiani, spesso non indicizzati ma navigabili per immagine.",
"3": "\`Giovanni Pigoli` , luogo \`Olmeneta, Cremona`, eventi 1790-1820",
"4":
"XVI sec. – 1929",
"5": "Battesimi, matrimoni, morti, processetti matrimoniali
(dipende dalla parrocchia)."
},
{
"1": "\**Archivio Storico Diocesano di
Cremona**",
"2": "Archivio ecclesiale che conserva i registri originali di
molte parrocchie della diocesi, spesso digitalizzati o consultabili su
richiesta.",
"3": "Cerca \`Pigoli Giovanni` nel database diocesano o richiedi
\`Registri parrocchiali di Olmeneta, battesimi 1810`",
"4": "XVI sec. – metà XX
sec.",
"5": "Battesimi, cresime, matrimoni, morti, stati delle anime."
},
{
"1": "\**Geneanet**",
"2": "Piattaforma collaborativa con alberi e atti
digitalizzati. Utile per trovare alberi altrui su Pigoli/Scolari e per atti già
caricati da altri ricercatori.",
"3": "\`Pigoli Giovanni` + \`Scolari Rosa` +
\`Olmeneta` + \`1790`",
"4": "Variabile (atti caricati dagli utenti)",
"5":
"Battesimi, matrimoni, morti (da trascrizioni o digitalizzazioni private)."
},
{
"1": "\**Portale Antenati (stato civile napoleonico)**",
"2": "Sezione
specifica del portale Antenati per il periodo 1806-1815, dove spesso sono
conservati atti di nascita/matrimonio/morte con dettagli anagrafici.",
"3":
"Cerca \`Pigoli` a \`Olmeneta` nel fondo \\"Stato civile napoleonico di
Cremona\\" (1806-1815)",
"4": "1806-1815",
"5": "Nascite, matrimoni, morti (con
note a margine)."
},
{
"1": "\**Archivio di Stato di Cremona**",
"2": "Archivio
territoriale che conserva anche supplementi parrocchiali e documenti non
digitalizzati, ma consultabili in sede o tramite richiesta.",
"3": "Richiedi
\`Parrocchia di Olmeneta, Registro battesimi 1790-1810 volume X`",
"4": "XVI
sec. – 1865 (poi stato civile)",
"5": "Originali parrocchiali, spesso non
digitalizzati."
},
{
"1": "\**Registro.it (Anagrafe Nazionale)**",
"2":
"Portale anagrafico ufficiale, utile per verificare esistenza di atti
digitalizzati recenti e per collegamenti con l'Archivio di Stato.",
"3":
"\`Pigoli Giovanni` + filtro \`Comune di Casalbuttano ed Uniti` per atti
recenti (1800-1900)",
"4": "1800-oggi (atti più recenti)",
"5": "Nascita,
matrimonio, morte (da stato civile post-unitario)."
}
] | [{'1': '\**Antenati
(Archivio di Stato)**', '2': "Portale ufficiale italiano con digitalizzazione
massiva dei registri parrocchiali e di stato civile. Per Cremona copre
ampiamente il periodo e l'area di Olmeneta.", '3': '\`Pigoli Giovanni` + filtro
"Cremona" + "Registri parrocchiali" (usare il motore interno o navigare per
comune)', '4': '~1790-1900 (con lacune locali)', '5': "Battesimi, matrimoni,
morti, stati d'anime."}, {'1': '\**FamilySearch**', '2': 'Piattaforma mondiale
gratuita con la più vasta collezione di microfilm parrocchiali italiani, spesso
non indicizzati ma navigabili per immagine.', '3': '\`Giovanni Pigoli` , luogo
\`Olmeneta, Cremona`, eventi 1790-1820', '4': 'XVI sec. – 1929', '5':
'Battesimi, matrimoni, morti, processetti matrimoniali (dipende dalla
parrocchia).'}, {'1': '\**Archivio Storico Diocesano di Cremona**', '2':
'Archivio ecclesiale che conserva i registri originali di molte parrocchie
della diocesi, spesso digitalizzati o consultabili su richiesta.', '3': 'Cerca
\`Pigoli Giovanni` nel database diocesano o richiedi \`Registri parrocchiali di
Olmeneta, battesimi 1810`', '4': 'XVI sec. – metà XX sec.', '5': 'Battesimi,
cresime, matrimoni, morti, stati delle anime.'}, {'1': '\**Geneanet**', '2':
'Piattaforma collaborativa con alberi e atti digitalizzati. Utile per trovare
alberi altrui su Pigoli/Scolari e per atti già caricati da altri ricercatori.',
'3': '\`Pigoli Giovanni` + \`Scolari Rosa` + \`Olmeneta` + \`1790`', '4':
'Variabile (atti caricati dagli utenti)', '5': 'Battesimi, matrimoni, morti (da
trascrizioni o digitalizzazioni private).'}, {'1': '\**Portale Antenati (stato
civile napoleonico)**', '2': 'Sezione specifica del portale Antenati per il
periodo 1806-1815, dove spesso sono conservati atti di nascita/matrimonio/morte
con dettagli anagrafici.', '3': 'Cerca \`Pigoli` a \`Olmeneta` nel fondo "Stato
civile napoleonico di Cremona" (1806-1815)', '4': '1806-1815', '5': 'Nascite,
matrimoni, morti (con note a margine).'}, {'1': '\**Archivio di Stato di
Cremona**', '2': 'Archivio territoriale che conserva anche supplementi
parrocchiali e documenti non digitalizzati, ma consultabili in sede o tramite
richiesta.', '3': 'Richiedi \`Parrocchia di Olmeneta, Registro battesimi
1790-1810 volume X`', '4': 'XVI sec. – 1865 (poi stato civile)', '5':
'Originali parrocchiali, spesso non digitalizzati.'}, {'1': '\**Registro.it
(Anagrafe Nazionale)**', '2': "Portale anagrafico ufficiale, utile per
verificare esistenza di atti digitalizzati recenti e per collegamenti con
l'Archivio di Stato.", '3': '\`Pigoli Giovanni` + filtro \`Comune di
Casalbuttano ed Uniti` per atti recenti (1800-1900)', '4': '1800-oggi (atti più
recenti)', '5': 'Nascita, matrimonio, morte (da stato civile post-unitario).'}]
| 1 |


