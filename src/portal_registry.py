from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta
import json
from pathlib import Path


@dataclass(frozen=True)
class PortalInfo:
    key: str
    label: str
    group: str
    area: str
    technical_family: str
    method: str
    maintenance_risk: str
    roadmap_priority: str
    operational_note: str
    default_referer: str | None = None
    tile_max_workers: int | None = None
    tile_inter_delay: float = 0.0
    public_only: bool = True
    requires_rights_check: bool = True
    record_mode_policy: str = "r_limited"
    policy_checked_at: str = "2026-05-26"
    policy_recheck_days: int = 180
    policy_source_urls: tuple[str, ...] = ()


@dataclass(frozen=True)
class EffectivePortalPolicy:
    portal_key: str
    label: str
    record_mode_policy: str
    policy_checked_at: str
    policy_recheck_days: int
    policy_source_urls: tuple[str, ...]
    policy_source: str
    recheck_due: bool


TECHNICAL_FAMILIES: frozenset[str] = frozenset(
    {
        "iiif_direct",
        "iiif_discovery",
        "synthetic_manifest",
        "hybrid_manifest",
        "user_supplied_manifest",
    }
)

RECORD_MODE_POLICIES: frozenset[str] = frozenset(
    {
        "r_ok",
        "r_limited",
        "d_only",
        "variable",
    }
)

R_POLICY_LABELS: dict[str, str] = {
    "r_ok": "Registro completo consentito con avviso",
    "r_limited": "Registro consentito solo con range esplicito",
    "d_only": "Solo documento singolo",
    "variable": "Dipende dal manifest fornito dall'utente",
}


_PORTALS: tuple[PortalInfo, ...] = (
    PortalInfo(
        key="antenati",
        label="Antenati (Cultura.gov.it)",
        group="\u2500\u2500 Italia \u2500\u2500",
        area="Italia",
        technical_family="iiif_discovery",
        method="IIIF discovery / manifest DAM",
        maintenance_risk="Medio",
        roadmap_priority="maintain_with_warning",
        operational_note="Consultazione gratuita; riuso immagini non automaticamente aperto.",
        record_mode_policy="r_ok",
        policy_source_urls=(
            "https://icar.cultura.gov.it/sistemi-e-portali/antenati",
            "https://antenati.cultura.gov.it/",
        ),
    ),
    PortalInfo(
        key="bnc_roma",
        label="BNC Roma digitale",
        group="\u2500\u2500 Italia \u2500\u2500",
        area="Italia",
        technical_family="synthetic_manifest",
        method="Manifest sintetico da pagina item-level",
        maintenance_risk="Alto",
        roadmap_priority="do_not_extend",
        operational_note="Solo risorse pubbliche/no-login; escludere OpenAthens e alta risoluzione.",
        default_referer="http://digitale.bnc.roma.sbn.it",
        record_mode_policy="r_limited",
        policy_source_urls=(
            "https://www.bncrm.beniculturali.it/it/32/biblioteca-digitale",
        ),
    ),
    PortalInfo(
        key="bncf_teca",
        label="BNCF Teca (Firenze)",
        group="\u2500\u2500 Italia \u2500\u2500",
        area="Italia",
        technical_family="hybrid_manifest",
        method="IIIF standard con fallback sintetico",
        maintenance_risk="Alto",
        roadmap_priority="do_not_extend",
        operational_note="Consultazione puntuale con cautela su pubblicazione e riproduzione.",
        record_mode_policy="d_only",
        policy_source_urls=(
            "https://bncf.cultura.gov.it/servizi/riproduzioni/",
        ),
    ),
    PortalInfo(
        key="museogalileo",
        label="Museo Galileo Digiteca",
        group="\u2500\u2500 Italia \u2500\u2500",
        area="Italia",
        technical_family="synthetic_manifest",
        method="Manifest sintetico da TecaService",
        maintenance_risk="Alto",
        roadmap_priority="do_not_extend",
        operational_note="Endpoint non documentato/stabile; niente nuove automazioni.",
        default_referer="https://opac.museogalileo.it",
        record_mode_policy="d_only",
        policy_source_urls=(
            "https://www2.museogalileo.it/it/16-visita/876-riprese-filmate-e-riproduzioni-fotografiche.html",
        ),
    ),
    PortalInfo(
        key="internetculturale_estense",
        label="Internet Culturale (Estense/ICCU)",
        group="\u2500\u2500 Italia \u2500\u2500",
        area="Italia",
        technical_family="synthetic_manifest",
        method="Manifest sintetico da magparser",
        maintenance_risk="Medio-Alto",
        roadmap_priority="consolidate",
        operational_note="Contenuti pubblici web non commerciali con citazione.",
        default_referer="https://www.internetculturale.it",
        record_mode_policy="r_ok",
        policy_source_urls=(
            "https://www.internetculturale.it/it/15/termini-d-uso",
        ),
    ),
    PortalInfo(
        key="brixiana",
        label="Brixiana (Biblioteca Queriniana Brescia)",
        group="\u2500\u2500 Italia \u2500\u2500",
        area="Italia",
        technical_family="iiif_direct",
        method="Alias Memooria/Jarvis IIIF",
        maintenance_risk="Medio",
        roadmap_priority="maintain_with_warning",
        operational_note="Solo risorse pubbliche/no-login e condizioni del singolo ente.",
        record_mode_policy="r_limited",
        policy_source_urls=(
            "https://www.comune.brescia.it/it/servizi/piattaforma-brixiana",
            "https://www.memooria.org/servizi-openjarvis/",
        ),
    ),
    PortalInfo(
        key="biblioteca_digitale_siena",
        label="Biblioteca Digitale Siena",
        group="\u2500\u2500 Italia \u2500\u2500",
        area="Italia",
        technical_family="iiif_direct",
        method="IIIF diretto da vieweriiif id/type",
        maintenance_risk="Basso-Medio",
        roadmap_priority="maintain_with_warning",
        operational_note="JPG web-resolution per uso personale, studio e ricerca; citazione BDS obbligatoria e niente uso commerciale.",
        default_referer="https://bds.comune.siena.it",
        record_mode_policy="r_limited",
        policy_checked_at="2026-06-05",
        policy_source_urls=(
            "https://bds.comune.siena.it/",
            "https://bds.comune.siena.it/it/169/",
        ),
    ),
    PortalInfo(
        key="biblioteca_digitale_trentina",
        label="Biblioteca Digitale Trentina",
        group="\u2500\u2500 Italia \u2500\u2500",
        area="Italia / Trentino",
        technical_family="synthetic_manifest",
        method="Manifest sintetico da immagini pubbliche in pagina",
        maintenance_risk="Basso-Medio",
        roadmap_priority="maintain_with_warning",
        operational_note="Materiali in pubblico dominio con riuso e citazione; per testi a stampa preferire il PDF diretto quando disponibile.",
        default_referer="https://bdt.bibcom.trento.it",
        record_mode_policy="r_limited",
        policy_checked_at="2026-06-06",
        policy_source_urls=(
            "https://bdt.bibcom.trento.it/",
            "https://bdt.bibcom.trento.it/Riuso",
            "https://www.comune.trento.it/Servizi/Biblioteca-Digitale-Trentina-BDT",
        ),
    ),
    PortalInfo(
        key="memooria",
        label="Memooria/Jarvis (qualsiasi biblioteca)",
        group="\u2500\u2500 Italia \u2500\u2500",
        area="Italia",
        technical_family="iiif_direct",
        method="IIIF da meta/iiif/{guid}/manifest",
        maintenance_risk="Medio",
        roadmap_priority="maintain_with_warning",
        operational_note="Capability tecnica; verificare ente, accesso pubblico e licenza.",
        record_mode_policy="r_limited",
        policy_source_urls=(
            "https://www.memooria.org/servizi-openjarvis/",
        ),
    ),
    PortalInfo(
        key="vatlib",
        label="DigiVatLib (Biblioteca Apostolica Vaticana)",
        group="\u2500\u2500 Italia \u2500\u2500",
        area="Italia / Vaticano",
        technical_family="iiif_direct",
        method="IIIF diretto da view/mss/iiif",
        maintenance_risk="Basso-Medio",
        roadmap_priority="maintain_with_warning",
        operational_note="Uso studio/personale; riproduzione o pubblicazione richiede autorizzazione BAV.",
        default_referer="https://digi.vatlib.it",
        record_mode_policy="r_limited",
        policy_source_urls=(
            "https://www.vaticanlibrary.va/en/information-for-readers/photographic-reproductions.html",
            "https://digi.vatlib.it/",
        ),
    ),
    PortalInfo(
        key="findbuch",
        label="Kirchenb\u00fccher S\u00fcdtirol (findbuch.net)",
        group="\u2500\u2500 Alto Adige / S\u00fcdtirol \u2500\u2500",
        area="Alto Adige / Sudtirol",
        technical_family="synthetic_manifest",
        method="Manifest sintetico da HTML + gtpc.php",
        maintenance_risk="Alto",
        roadmap_priority="do_not_extend",
        operational_note="Solo istanze pubbliche gia verificate e range puntuale.",
        default_referer="https://www.findbuch.net",
        record_mode_policy="r_limited",
        policy_source_urls=(
            "https://www.findbuch.net/hp/Funktionen/",
            "https://beni-culturali.provincia.bz.it/de/landesarchiv/kirchenbucher-sudtirol",
        ),
    ),
    PortalInfo(
        key="matricula",
        label="Matricula Online (Kirchenb\u00fccher AT/DE/SI/LU)",
        group="\u2500\u2500 Europa Centrale (AT/DE/SI/...) \u2500\u2500",
        area="Europa centrale",
        technical_family="synthetic_manifest",
        method="Manifest sintetico da viewer HTML e hosted-images",
        maintenance_risk="Alto",
        roadmap_priority="do_not_extend",
        operational_note="CC BY-NC-ND 2.0: no commerciale, no derivati, no bulk.",
        default_referer="https://data.matricula-online.eu",
        record_mode_policy="r_limited",
        policy_source_urls=(
            "https://data.matricula-online.eu/de/nutzungsbedingungen/",
        ),
    ),
    PortalInfo(
        key="gallica",
        label="Gallica (BnF)",
        group="\u2500\u2500 Francia \u2500\u2500",
        area="Francia",
        technical_family="iiif_direct",
        method="IIIF diretto da ARK + fallback Playwright",
        maintenance_risk="Medio",
        roadmap_priority="consolidate",
        operational_note="Riuso non commerciale con citazione; cautela sui partner.",
        default_referer="https://gallica.bnf.fr",
        record_mode_policy="r_ok",
        policy_source_urls=(
            "https://api.bnf.fr/fr/api-iiif-de-recuperation-des-images-de-gallica",
            "https://gallica.bnf.fr/accueil/fr/html/conditions-dutilisation-de-gallica",
        ),
    ),
    PortalInfo(
        key="heidelberg",
        label="Heidelberg UB",
        group="\u2500\u2500 Germania \u2500\u2500",
        area="Germania",
        technical_family="iiif_direct",
        method="IIIF diretto + rate-limit sequenziale",
        maintenance_risk="Basso-Medio",
        roadmap_priority="consolidate",
        operational_note="Controllare licenza per volume e mantenere rate limit.",
        default_referer="https://digi.ub.uni-heidelberg.de",
        tile_max_workers=1,
        tile_inter_delay=0.3,
        record_mode_policy="r_ok",
        policy_source_urls=(
            "https://www.ub.uni-heidelberg.de/Englisch/helios/digi/nutzung/",
        ),
    ),
    PortalInfo(
        key="bodleian",
        label="Bodleian Libraries Oxford",
        group="\u2500\u2500 Regno Unito \u2500\u2500",
        area="Regno Unito",
        technical_family="iiif_direct",
        method="IIIF diretto da object UUID",
        maintenance_risk="Basso",
        roadmap_priority="consolidate",
        operational_note="Attribuzione, uso non commerciale e no re-hosting sistematico.",
        default_referer="https://digital.bodleian.ox.ac.uk",
        record_mode_policy="r_ok",
        policy_source_urls=(
            "https://digital.bodleian.ox.ac.uk/terms/",
            "https://digital.bodleian.ox.ac.uk/developer/iiif/",
        ),
    ),
    PortalInfo(
        key="e_rara",
        label="e-rara",
        group="\u2500\u2500 Svizzera \u2500\u2500",
        area="Svizzera",
        technical_family="iiif_direct",
        method="IIIF builder dedicato",
        maintenance_risk="Basso-Medio",
        roadmap_priority="consolidate",
        operational_note="Controllare licenza per documento e citare la fonte.",
        default_referer="https://www.e-rara.ch",
        record_mode_policy="r_ok",
        policy_source_urls=(
            "https://www.e-rara.ch/wiki/termsOfUse?lang=en",
            "https://www.e-rara.ch/wiki/apiinfo",
        ),
    ),
    PortalInfo(
        key="e_codices",
        label="e-codices (Unifr)",
        group="\u2500\u2500 Svizzera \u2500\u2500",
        area="Svizzera",
        technical_family="iiif_direct",
        method="IIIF builder dedicato",
        maintenance_risk="Basso-Medio",
        roadmap_priority="consolidate",
        operational_note="Uso non commerciale con citazione salvo item Public Domain/CC.",
        default_referer="https://www.e-codices.unifr.ch",
        record_mode_policy="r_ok",
        policy_source_urls=(
            "https://www.e-codices.unifr.ch/en/about/terms",
            "https://www.e-codices.unifr.ch/en/about/webapplication",
        ),
    ),
    PortalInfo(
        key="e_manuscripta",
        label="e-manuscripta",
        group="\u2500\u2500 Svizzera \u2500\u2500",
        area="Svizzera",
        technical_family="iiif_direct",
        method="IIIF builder dedicato",
        maintenance_risk="Basso-Medio",
        roadmap_priority="consolidate",
        operational_note="Controllare licenza per documento; evitare copia sistematica.",
        default_referer="https://www.e-manuscripta.ch",
        record_mode_policy="r_ok",
        policy_source_urls=(
            "https://www.e-manuscripta.ch/wiki/termsOfUse?lang=en",
            "https://www.e-manuscripta.ch/wiki/apiinfo",
        ),
    ),
    PortalInfo(
        key="internet_archive",
        label="Internet Archive",
        group="\u2500\u2500 Internazionale \u2500\u2500",
        area="Internazionale",
        technical_family="synthetic_manifest",
        method="Manifest sintetico da metadata/files/BookReaderImages",
        maintenance_risk="Medio-Alto",
        roadmap_priority="maintain_with_warning",
        operational_note="Solo item pubblici scaricabili con diritti chiari.",
        default_referer="https://archive.org",
        record_mode_policy="r_limited",
        policy_source_urls=(
            "https://archive.org/about/terms",
            "https://archive.org/services/docs/api/",
            "https://archive.org/metadata/",
        ),
    ),
    PortalInfo(
        key="europeana",
        label="Europeana IIIF",
        group="\u2500\u2500 Internazionale \u2500\u2500",
        area="Internazionale",
        technical_family="iiif_direct",
        method="IIIF diretto da provider/record id",
        maintenance_risk="Basso-Medio",
        roadmap_priority="consolidate",
        operational_note="Verificare rights statement e attribuzione ai provider.",
        record_mode_policy="r_limited",
        policy_source_urls=(
            "https://www.europeana.eu/en/rights/terms-of-use",
            "https://api.europeana.eu/en",
        ),
    ),
    PortalInfo(
        key="manifest_diretto",
        label="Manifest diretto (URL gi\u00e0 noto)",
        group="\u2500\u2500 Avanzato \u2500\u2500",
        area="Avanzato",
        technical_family="user_supplied_manifest",
        method="URL manifest fornito dall'utente",
        maintenance_risk="Variabile",
        roadmap_priority="consolidate",
        operational_note="Termini e diritti dipendono dal sito di origine scelto dall'utente.",
        record_mode_policy="variable",
        policy_checked_at="",
        policy_source_urls=(),
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


def get_portal_technical_family(portale: str | None) -> str | None:
    portal = get_portal(portale)
    if not portal:
        return None
    return portal.technical_family


def get_portal_tile_download_policy(portale: str | None) -> tuple[int | None, float]:
    portal = get_portal(portale)
    if not portal:
        return None, 0.0
    return portal.tile_max_workers, portal.tile_inter_delay


def get_portal_policy_override_path() -> Path:
    try:
        from .config_utils import _config_file_path
    except ImportError:
        from config_utils import _config_file_path

    return Path(_config_file_path()).with_name("portal_policy_overrides.json")


def _parse_policy_date(value: str | None) -> date | None:
    if not value:
        return None
    try:
        return datetime.strptime(str(value), "%Y-%m-%d").date()
    except ValueError:
        return None


def _normalize_policy_override(raw: object) -> dict[str, object]:
    if not isinstance(raw, dict):
        return {}

    normalized: dict[str, object] = {}
    policy = raw.get("record_mode_policy")
    if isinstance(policy, str) and policy in RECORD_MODE_POLICIES:
        normalized["record_mode_policy"] = policy

    checked_at = raw.get("policy_checked_at")
    if isinstance(checked_at, str) and _parse_policy_date(checked_at):
        normalized["policy_checked_at"] = checked_at

    recheck_days = raw.get("policy_recheck_days")
    if isinstance(recheck_days, int) and recheck_days > 0:
        normalized["policy_recheck_days"] = recheck_days

    urls = raw.get("policy_source_urls")
    if isinstance(urls, list):
        clean_urls = tuple(str(url).strip() for url in urls if str(url).strip())
        normalized["policy_source_urls"] = clean_urls

    return normalized


def load_portal_policy_overrides(path: str | Path | None = None) -> dict[str, dict[str, object]]:
    override_path = Path(path) if path else get_portal_policy_override_path()
    if not override_path.exists():
        return {}

    try:
        data = json.loads(override_path.read_text(encoding="utf-8"))
    except Exception:
        return {}

    portal_data = data.get("portals") if isinstance(data, dict) else None
    if not isinstance(portal_data, dict):
        return {}

    overrides: dict[str, dict[str, object]] = {}
    for raw_key, raw_override in portal_data.items():
        key = normalize_portal_key(str(raw_key))
        if key not in PORTAL_REGISTRY:
            continue
        override = _normalize_policy_override(raw_override)
        if override:
            overrides[key] = override
    return overrides


def get_effective_portal_policy(
    portale: str | None,
    local_policy_path: str | Path | None = None,
    today: date | None = None,
) -> EffectivePortalPolicy | None:
    portal = get_portal(portale)
    if not portal:
        return None

    policy_data: dict[str, object] = {
        "record_mode_policy": portal.record_mode_policy,
        "policy_checked_at": portal.policy_checked_at,
        "policy_recheck_days": portal.policy_recheck_days,
        "policy_source_urls": portal.policy_source_urls,
    }
    overrides = load_portal_policy_overrides(local_policy_path)
    source = "registry"
    if portal.key in overrides:
        policy_data.update(overrides[portal.key])
        source = "local"

    record_mode_policy = str(policy_data["record_mode_policy"])
    checked_at = str(policy_data.get("policy_checked_at") or "")
    recheck_days = int(policy_data.get("policy_recheck_days") or portal.policy_recheck_days)
    source_urls = tuple(policy_data.get("policy_source_urls") or ())
    checked_date = _parse_policy_date(checked_at)
    today_date = today or date.today()
    recheck_due = checked_date is None or today_date >= checked_date + timedelta(days=recheck_days)
    if record_mode_policy == "variable" and checked_date is None:
        recheck_due = False

    return EffectivePortalPolicy(
        portal_key=portal.key,
        label=portal.label,
        record_mode_policy=record_mode_policy,
        policy_checked_at=checked_at,
        policy_recheck_days=recheck_days,
        policy_source_urls=source_urls,
        policy_source=source,
        recheck_due=recheck_due,
    )


def get_portal_record_mode_policy(
    portale: str | None,
    local_policy_path: str | Path | None = None,
    today: date | None = None,
) -> str | None:
    policy = get_effective_portal_policy(portale, local_policy_path=local_policy_path, today=today)
    return policy.record_mode_policy if policy else None


def write_portal_policy_override_template(path: str | Path | None = None) -> Path:
    output_path = Path(path) if path else get_portal_policy_override_path()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    template = {
        "version": 1,
        "updated_at": date.today().isoformat(),
        "note": "Aggiorna solo dopo aver ricontrollato le fonti ufficiali del portale.",
        "portals": {
            portal.key: {
                "record_mode_policy": portal.record_mode_policy,
                "policy_checked_at": portal.policy_checked_at,
                "policy_recheck_days": portal.policy_recheck_days,
                "policy_source_urls": list(portal.policy_source_urls),
            }
            for portal in _PORTALS
        },
    }
    output_path.write_text(json.dumps(template, ensure_ascii=False, indent=2), encoding="utf-8")
    return output_path


def portals_by_technical_family(technical_family: str) -> tuple[PortalInfo, ...]:
    return tuple(portal for portal in _PORTALS if portal.technical_family == technical_family)


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
