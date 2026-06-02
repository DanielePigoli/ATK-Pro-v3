# Campioni smoke live portali

Questa matrice serve solo per la verifica manuale pre-RC dei portali gia
implementati. Gli URL campione devono essere pubblici, no-login e coerenti con
la policy legale del singolo portale. I test live non sostituiscono le fixture
offline e non devono essere eseguiti come suite automatica ordinaria.

| portal_key | label | roadmap_priority | technical_family | sample_url | release_status | notes |
| --- | --- | --- | --- | --- | --- | --- |
| antenati | Antenati (Cultura.gov.it) | maintain_with_warning | iiif_discovery | https://antenati.cultura.gov.it/ark:/12657/an_ud16591873/ | SAMPLE | Registro pubblico Antenati; verifica discovery manifest, non diritti di riuso. |
| bnc_roma | BNC Roma digitale | do_not_extend | synthetic_manifest | http://digitale.bnc.roma.sbn.it/printedbooks/bncr_142624/bncr_142624_001 | SAMPLE | Risorsa pubblica/no-login BNC Roma; niente OpenAthens o materiali riservati. |
| bncf_teca | BNCF Teca (Firenze) | do_not_extend | hybrid_manifest | https://teca.bncf.firenze.sbn.it/ImageViewer/servlet/ImageViewer?idr=BNCF00004140909&azione=readBook | SAMPLE | Consultazione puntuale pubblica; verificare citazione e limiti di riproduzione. |
| museogalileo | Museo Galileo Digiteca | do_not_extend | synthetic_manifest | https://bibdig.museogalileo.it/Teca/Viewer?an=000000006600 | SAMPLE | Opera pubblica raggiungibile senza login; endpoint non documentato. |
| internetculturale_estense | Internet Culturale (Estense/ICCU) | consolidate | synthetic_manifest | https://www.internetculturale.it/jmms/iccuviewer/iccu.jsp?id=oai:www.internetculturale.sbn.it/Teca:20:NT0000:N:ALI_00002111&mode=all&teca=MagTeca+-+ICCU | SAMPLE | Item MagTeca/ICCU pubblico; uso non commerciale e citazione secondo condizioni del portale. |
| brixiana | Brixiana (Biblioteca Queriniana Brescia) | maintain_with_warning | iiif_direct | https://brixiana.jarvis.memooria.org/schedadl.aspx?id=a030f44e-9e0e-4d89-8e2f-c911df2ca1cc | SAMPLE | Risorsa Jarvis pubblica/no-login usata come campione Brixiana. |
| memooria | Memooria/Jarvis (qualsiasi biblioteca) | maintain_with_warning | iiif_direct | https://brixiana.jarvis.memooria.org/schedadl.aspx?id=a030f44e-9e0e-4d89-8e2f-c911df2ca1cc | SAMPLE | Campione Jarvis pubblico; la famiglia Memooria va verificata per singola istanza. |
| vatlib | DigiVatLib (Biblioteca Apostolica Vaticana) | maintain_with_warning | iiif_direct | https://digi.vatlib.it/view/MSS_Vat.lat.4330/0001 | SAMPLE | Campione gia documentato; uso solo studio/personale. |
| findbuch | Kirchenbücher Südtirol (findbuch.net) | do_not_extend | synthetic_manifest | https://www.xn--kirchenbcher-sdtirol-wecg.findbuch.net/php/view.php?link=4b425f424f5a454e5f424f4c5a414e4fx49&force_html=1 | SAMPLE | Solo istanza pubblica gia verificata e range puntuale. |
| matricula | Matricula Online (Kirchenbücher AT/DE/SI/LU) | do_not_extend | synthetic_manifest | https://data.matricula-online.eu/de/oesterreich/wien/01-st-stephan/01-084/?pg=653 | SAMPLE | Solo controllo puntuale, non commerciale, no bulk. |
| gallica | Gallica (BnF) | consolidate | iiif_direct | https://gallica.bnf.fr/ark:/12148/bpt6k97989381 | SAMPLE | ARK pubblico Gallica con IIIF disponibile; citazione e condizioni Gallica. |
| heidelberg | Heidelberg UB | consolidate | iiif_direct | https://digi.ub.uni-heidelberg.de/diglit/cpg389 | SAMPLE | Volume pubblico usato negli esempi IIIF Heidelberg; mantenere rate limit sequenziale. |
| bodleian | Bodleian Libraries Oxford | consolidate | iiif_direct | https://digital.bodleian.ox.ac.uk/objects/390fd0e8-9eae-475d-9564-ed916ab9035c/ | SAMPLE | Object URL pubblico; verificare attribuzione/non commerciale sul singolo item. |
| e_rara | e-rara | consolidate | iiif_direct | https://www.e-rara.ch/zut/content/titleinfo/29762142 | SAMPLE | Titleinfo pubblico con licenza dichiarata Public Domain Mark. |
| e_codices | e-codices (Unifr) | consolidate | iiif_direct | https://www.e-codices.unifr.ch/en/csg/0390/1r/max | SAMPLE | Manoscritto pubblico; verificare licenza/item prima del riuso. |
| e_manuscripta | e-manuscripta | consolidate | iiif_direct | https://www.e-manuscripta.ch/bau/content/titleinfo/63438 | SAMPLE | Titleinfo pubblico con licenza dichiarata Public Domain Mark. |
| internet_archive | Internet Archive | maintain_with_warning | synthetic_manifest | https://archive.org/details/b29000427_0001/page/n13/mode/2up | SAMPLE | Item pubblico indicato nella guida IIIF; no lending/no-download. |
| europeana | Europeana IIIF | consolidate | iiif_direct | https://www.europeana.eu/en/item/92023/images_billed_2010_okt_billeder_object488811 | SAMPLE | Record con manifest IIIF documentato; verificare rights statement del provider. |
| manifest_diretto | Manifest diretto (URL già noto) | consolidate | user_supplied_manifest | https://iiif.io/api/cookbook/recipe/0001-mvm-image/manifest.json | SAMPLE | Manifest IIIF v3 pubblico no-login per test del percorso avanzato. |
