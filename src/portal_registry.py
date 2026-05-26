from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PortalInfo:
    key: str
    label: str
    group: str
    area: str
    method: str
    maintenance_risk: str
    roadmap_priority: str
    operational_note: str
    default_referer: str | None = None
    public_only: bool = True
    requires_rights_check: bool = True


_PORTALS: tuple[PortalInfo, ...] = (
    PortalInfo(
        key="antenati",
        label="Antenati (Cultura.gov.it)",
        group="\u2500\u2500 Italia \u2500\u2500",
        area="Italia",
        method="IIIF discovery / manifest DAM",
        maintenance_risk="Medio",
        roadmap_priority="maintain_with_warning",
        operational_note="Consultazione gratuita; riuso immagini non automaticamente aperto.",
    ),
    PortalInfo(
        key="bnc_roma",
        label="BNC Roma digitale",
        group="\u2500\u2500 Italia \u2500\u2500",
        area="Italia",
        method="Manifest sintetico da pagina item-level",
        maintenance_risk="Alto",
        roadmap_priority="do_not_extend",
        operational_note="Solo risorse pubbliche/no-login; escludere OpenAthens e alta risoluzione.",
        default_referer="http://digitale.bnc.roma.sbn.it",
    ),
    PortalInfo(
        key="bncf_teca",
        label="BNCF Teca (Firenze)",
        group="\u2500\u2500 Italia \u2500\u2500",
        area="Italia",
        method="IIIF standard con fallback sintetico",
        maintenance_risk="Alto",
        roadmap_priority="do_not_extend",
        operational_note="Consultazione puntuale con cautela su pubblicazione e riproduzione.",
    ),
    PortalInfo(
        key="museogalileo",
        label="Museo Galileo Digiteca",
        group="\u2500\u2500 Italia \u2500\u2500",
        area="Italia",
        method="Manifest sintetico da TecaService",
        maintenance_risk="Alto",
        roadmap_priority="do_not_extend",
        operational_note="Endpoint non documentato/stabile; niente nuove automazioni.",
        default_referer="https://opac.museogalileo.it",
    ),
    PortalInfo(
        key="internetculturale_estense",
        label="Internet Culturale (Estense/ICCU)",
        group="\u2500\u2500 Italia \u2500\u2500",
        area="Italia",
        method="Manifest sintetico da magparser",
        maintenance_risk="Medio-Alto",
        roadmap_priority="consolidate",
        operational_note="Contenuti pubblici web non commerciali con citazione.",
        default_referer="https://www.internetculturale.it",
    ),
    PortalInfo(
        key="brixiana",
        label="Brixiana (Biblioteca Queriniana Brescia)",
        group="\u2500\u2500 Italia \u2500\u2500",
        area="Italia",
        method="Alias Memooria/Jarvis IIIF",
        maintenance_risk="Medio",
        roadmap_priority="maintain_with_warning",
        operational_note="Solo risorse pubbliche/no-login e condizioni del singolo ente.",
    ),
    PortalInfo(
        key="memooria",
        label="Memooria/Jarvis (qualsiasi biblioteca)",
        group="\u2500\u2500 Italia \u2500\u2500",
        area="Italia",
        method="IIIF da meta/iiif/{guid}/manifest",
        maintenance_risk="Medio",
        roadmap_priority="maintain_with_warning",
        operational_note="Capability tecnica; verificare ente, accesso pubblico e licenza.",
    ),
    PortalInfo(
        key="vatlib",
        label="DigiVatLib (Biblioteca Apostolica Vaticana)",
        group="\u2500\u2500 Italia \u2500\u2500",
        area="Italia / Vaticano",
        method="IIIF diretto da view/mss/iiif",
        maintenance_risk="Basso-Medio",
        roadmap_priority="maintain_with_warning",
        operational_note="Uso studio/personale; riproduzione o pubblicazione richiede autorizzazione BAV.",
        default_referer="https://digi.vatlib.it",
    ),
    PortalInfo(
        key="findbuch",
        label="Kirchenb\u00fccher S\u00fcdtirol (findbuch.net)",
        group="\u2500\u2500 Alto Adige / S\u00fcdtirol \u2500\u2500",
        area="Alto Adige / Sudtirol",
        method="Manifest sintetico da HTML + gtpc.php",
        maintenance_risk="Alto",
        roadmap_priority="do_not_extend",
        operational_note="Solo istanze pubbliche gia verificate e range puntuale.",
        default_referer="https://www.findbuch.net",
    ),
    PortalInfo(
        key="matricula",
        label="Matricula Online (Kirchenb\u00fccher AT/DE/SI/LU)",
        group="\u2500\u2500 Europa Centrale (AT/DE/SI/...) \u2500\u2500",
        area="Europa centrale",
        method="Manifest sintetico da viewer HTML e hosted-images",
        maintenance_risk="Alto",
        roadmap_priority="do_not_extend",
        operational_note="CC BY-NC-ND 2.0: no commerciale, no derivati, no bulk.",
        default_referer="https://data.matricula-online.eu",
    ),
    PortalInfo(
        key="gallica",
        label="Gallica (BnF)",
        group="\u2500\u2500 Francia \u2500\u2500",
        area="Francia",
        method="IIIF diretto da ARK + fallback Playwright",
        maintenance_risk="Medio",
        roadmap_priority="consolidate",
        operational_note="Riuso non commerciale con citazione; cautela sui partner.",
        default_referer="https://gallica.bnf.fr",
    ),
    PortalInfo(
        key="heidelberg",
        label="Heidelberg UB",
        group="\u2500\u2500 Germania \u2500\u2500",
        area="Germania",
        method="IIIF diretto + rate-limit sequenziale",
        maintenance_risk="Basso-Medio",
        roadmap_priority="consolidate",
        operational_note="Controllare licenza per volume e mantenere rate limit.",
        default_referer="https://digi.ub.uni-heidelberg.de",
    ),
    PortalInfo(
        key="bodleian",
        label="Bodleian Libraries Oxford",
        group="\u2500\u2500 Regno Unito \u2500\u2500",
        area="Regno Unito",
        method="IIIF diretto da object UUID",
        maintenance_risk="Basso",
        roadmap_priority="consolidate",
        operational_note="Attribuzione, uso non commerciale e no re-hosting sistematico.",
        default_referer="https://digital.bodleian.ox.ac.uk",
    ),
    PortalInfo(
        key="e_rara",
        label="e-rara",
        group="\u2500\u2500 Svizzera \u2500\u2500",
        area="Svizzera",
        method="IIIF builder dedicato",
        maintenance_risk="Basso-Medio",
        roadmap_priority="consolidate",
        operational_note="Controllare licenza per documento e citare la fonte.",
        default_referer="https://www.e-rara.ch",
    ),
    PortalInfo(
        key="e_codices",
        label="e-codices (Unifr)",
        group="\u2500\u2500 Svizzera \u2500\u2500",
        area="Svizzera",
        method="IIIF builder dedicato",
        maintenance_risk="Basso-Medio",
        roadmap_priority="consolidate",
        operational_note="Uso non commerciale con citazione salvo item Public Domain/CC.",
        default_referer="https://www.e-codices.unifr.ch",
    ),
    PortalInfo(
        key="e_manuscripta",
        label="e-manuscripta",
        group="\u2500\u2500 Svizzera \u2500\u2500",
        area="Svizzera",
        method="IIIF builder dedicato",
        maintenance_risk="Basso-Medio",
        roadmap_priority="consolidate",
        operational_note="Controllare licenza per documento; evitare copia sistematica.",
        default_referer="https://www.e-manuscripta.ch",
    ),
    PortalInfo(
        key="internet_archive",
        label="Internet Archive",
        group="\u2500\u2500 Internazionale \u2500\u2500",
        area="Internazionale",
        method="Manifest sintetico da metadata/files/BookReaderImages",
        maintenance_risk="Medio-Alto",
        roadmap_priority="maintain_with_warning",
        operational_note="Solo item pubblici scaricabili con diritti chiari.",
        default_referer="https://archive.org",
    ),
    PortalInfo(
        key="europeana",
        label="Europeana IIIF",
        group="\u2500\u2500 Internazionale \u2500\u2500",
        area="Internazionale",
        method="IIIF diretto da provider/record id",
        maintenance_risk="Basso-Medio",
        roadmap_priority="consolidate",
        operational_note="Verificare rights statement e attribuzione ai provider.",
    ),
    PortalInfo(
        key="manifest_diretto",
        label="Manifest diretto (URL gi\u00e0 noto)",
        group="\u2500\u2500 Avanzato \u2500\u2500",
        area="Avanzato",
        method="URL manifest fornito dall'utente",
        maintenance_risk="Variabile",
        roadmap_priority="consolidate",
        operational_note="Termini e diritti dipendono dal sito di origine scelto dall'utente.",
    ),
)


PORTAL_REGISTRY: dict[str, PortalInfo] = {portal.key: portal for portal in _PORTALS}

PORTAL_WARNING_MESSAGE_KEYS: dict[str, str] = {
    "consolidate": "Portale con priorità di consolidamento: verifica comunque licenze e condizioni del singolo documento.",
    "maintain_with_warning": "Portale da usare con avviso: verifica accesso pubblico, diritti e condizioni prima del download.",
    "do_not_extend": "Portale da non estendere per ora: usa solo risorse pubbliche puntuali e senza accessi riservati.",
}


def normalize_portal_key(portale: str | None) -> str:
    if not portale:
        return ""
    return portale.lower().replace("-", "_").replace(" ", "_")


def get_portal(portale: str | None) -> PortalInfo | None:
    return PORTAL_REGISTRY.get(normalize_portal_key(portale))


def get_portal_warning_message_key(portale: str | None) -> str | None:
    portal = get_portal(portale)
    if not portal:
        return None
    return PORTAL_WARNING_MESSAGE_KEYS.get(portal.roadmap_priority)


def get_portal_referer(portale: str | None, source_url: str | None = None) -> str | None:
    portal = get_portal(portale)
    if portal and portal.default_referer:
        return portal.default_referer

    source_url_lower = str(source_url).lower() if source_url else ""
    if "bncf.firenze.sbn.it" in source_url_lower or "teca.bncf.firenze.sbn.it" in source_url_lower:
        return "https://teca.bncf.firenze.sbn.it"

    return None


def iter_portals() -> tuple[PortalInfo, ...]:
    return _PORTALS


def portal_keys() -> tuple[str, ...]:
    return tuple(portal.key for portal in _PORTALS)


def get_portal_groups() -> tuple[tuple[str, tuple[tuple[str, str], ...]], ...]:
    groups: list[tuple[str, list[tuple[str, str]]]] = []
    for portal in _PORTALS:
        if not groups or groups[-1][0] != portal.group:
            groups.append((portal.group, []))
        groups[-1][1].append((portal.key, portal.label))
    return tuple((label, tuple(portals)) for label, portals in groups)
