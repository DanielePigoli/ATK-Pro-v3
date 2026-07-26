from src.portal_adapters import (
    DIRECT_IMAGE_ADAPTERS_BY_HOST_FRAGMENT,
    PortalRequestAdapter,
    resolve_direct_image_download,
    resolve_direct_pdf_download,
    resolve_synthetic_manifest_download,
)


def test_resolve_direct_image_download_for_bdt_context():
    canvas = {
        "images": [
            {
                "resource": {
                    "service": {
                        "@context": "bdt_direct",
                        "@id": "https://bdt.example.test/page-1.jpg",
                    }
                }
            }
        ]
    }

    adapter, image_url = resolve_direct_image_download(None, canvas, None)

    assert adapter is not None
    assert adapter.portal_label == "BDT"
    assert image_url == "https://bdt.example.test/page-1.jpg"


def test_resolve_direct_image_download_for_bnc_context():
    canvas = {
        "images": [
            {
                "resource": {
                    "service": {
                        "@context": "bnc_direct",
                        "@id": "https://digitale.bnc.roma.sbn.it/image.jpg",
                    }
                }
            }
        ]
    }

    adapter, image_url = resolve_direct_image_download(None, canvas, None)

    assert adapter is not None
    assert adapter.portal_label == "BNC"
    assert image_url == "https://digitale.bnc.roma.sbn.it/image.jpg"


def test_resolve_direct_image_download_for_internetculturale_context():
    canvas = {
        "images": [
            {
                "resource": {
                    "service": {
                        "@context": "internetculturale_cacheman_direct",
                        "@id": "https://www.internetculturale.it/jpg.jpg",
                    }
                }
            }
        ]
    }

    adapter, image_url = resolve_direct_image_download(None, canvas, None)

    assert adapter is not None
    assert adapter.portal_label == "InternetCulturale"
    assert image_url == "https://www.internetculturale.it/jpg.jpg"


def test_resolve_direct_image_download_for_archive_org_host():
    canvas = {"images": [{"resource": {"service": {}}}]}

    adapter, image_url = resolve_direct_image_download(
        None,
        canvas,
        "https://archive.org/download/example/BookReaderImages.php?zip=/foo.zip&file=page_0001.jp2",
    )

    assert adapter is not None
    assert adapter.portal_label == "IA"
    assert image_url.startswith("https://archive.org/download/example/BookReaderImages.php")


def test_resolve_direct_image_download_for_matricula_host():
    canvas = {"images": [{"resource": {"service": {}}}]}

    adapter, image_url = resolve_direct_image_download(
        None,
        canvas,
        "https://hosted-images.matricula-online.eu/foo/bar.jpg",
    )

    assert adapter is not None
    assert adapter.portal_label == "Matricula"
    assert image_url == "https://hosted-images.matricula-online.eu/foo/bar.jpg"


def test_direct_image_host_adapter_matches_service_id():
    adapter = DIRECT_IMAGE_ADAPTERS_BY_HOST_FRAGMENT["BookReaderImages.php"]

    assert adapter.matches_service_id(
        "https://archive.org/download/example/BookReaderImages.php?zip=/foo.zip&file=page_0001.jp2"
    )
    assert not adapter.matches_service_id("https://example.test/page.jpg")


def test_resolve_direct_image_download_for_rovereto_context():
    canvas = {
        "images": [
            {
                "resource": {
                    "service": {
                        "@context": "rovereto_direct",
                        "@id": "https://rovereto.example.test/page-2.png",
                    }
                }
            }
        ]
    }

    adapter, image_url = resolve_direct_image_download(None, canvas, None)

    assert adapter is not None
    assert adapter.portal_label == "Rovereto"
    assert image_url == "https://rovereto.example.test/page-2.png"


def test_direct_image_adapter_extracts_image_from_canvas_service():
    canvas = {
        "images": [
            {
                "resource": {
                    "service": {
                        "@context": "bdt_direct",
                        "@id": "https://bdt.example.test/page-9.jpg",
                    }
                }
            }
        ]
    }

    adapter, image_url = resolve_direct_image_download(None, canvas, None)

    assert adapter is not None
    assert image_url == "https://bdt.example.test/page-9.jpg"


def test_resolve_direct_image_download_for_ficlit_portal():
    canvas = {
        "images": [
            {
                "resource": {
                    "@id": "https://dl.ficlit.unibo.it/iiif/2/45498/full/699,800/0/default.jpg",
                    "service": {
                        "@id": "https://dl.ficlit.unibo.it/iiif/2/45498",
                    },
                }
            }
        ]
    }

    adapter, image_url = resolve_direct_image_download("dl_ficlit", canvas, None)

    assert adapter is not None
    assert adapter.portal_label == "FICLIT"
    assert image_url == "https://dl.ficlit.unibo.it/iiif/2/45498/full/699,800/0/default.jpg"


def test_resolve_direct_pdf_download_for_bdt_manifest():
    manifest = {
        "seeAlso": [
            {
                "@id": "https://bdt.bibcom.trento.it/content/download/78214/1625910/file/BDT-113-TIf37.pdf",
                "format": "application/pdf",
            }
        ]
    }

    adapter, pdf_url = resolve_direct_pdf_download(
        "biblioteca_digitale_trentina",
        tiles_info=[],
        manifest=manifest,
    )

    assert adapter is not None
    assert adapter.portal_label == "BDT"
    assert pdf_url == "https://bdt.bibcom.trento.it/content/download/78214/1625910/file/BDT-113-TIf37.pdf"


def test_resolve_direct_pdf_download_for_bdt_manifest_see_also_alias():
    manifest = {
        "see_also": {
            "@id": "https://bdt.bibcom.trento.it/content/download/78214/1625910/file/BDT-113-TIf37.pdf",
            "format": "application/pdf",
        }
    }

    adapter, pdf_url = resolve_direct_pdf_download(
        "biblioteca_digitale_trentina",
        tiles_info=[],
        manifest=manifest,
    )

    assert adapter is not None
    assert adapter.portal_label == "BDT"
    assert pdf_url == "https://bdt.bibcom.trento.it/content/download/78214/1625910/file/BDT-113-TIf37.pdf"


def test_resolve_direct_pdf_download_for_bdl_context():
    tiles_info = [
        {
            "images": [
                {
                    "resource": {
                        "service": {
                            "@context": "bdl_direct_pdf",
                            "@id": "https://www.bdl.servizirl.it/bdl/public/rest/srv/item/12404/pdf",
                            "pdf_url": "https://www.bdl.servizirl.it/bdl/public/rest/srv/item/12404/pdf",
                        }
                    }
                }
            ]
        }
    ]

    adapter, pdf_url = resolve_direct_pdf_download(
        "biblioteca_digitale_lombarda",
        tiles_info=tiles_info,
        manifest=None,
    )

    assert adapter is not None
    assert adapter.portal_label == "BDL"
    assert pdf_url == "https://www.bdl.servizirl.it/bdl/public/rest/srv/item/12404/pdf"


def test_resolve_direct_pdf_download_prefers_portal_adapter_for_service_entries():
    tiles_info = [
        {
            "images": [
                {
                    "resource": {
                        "service": {
                            "@context": "bdl_direct_pdf",
                            "@id": "https://bdt.bibcom.trento.it/content/download/78214/1625910/file/BDT-113-TIf37.pdf",
                            "format": "application/pdf",
                        }
                    }
                }
            ]
        }
    ]

    adapter, pdf_url = resolve_direct_pdf_download(
        "biblioteca_digitale_trentina",
        tiles_info=tiles_info,
        manifest=None,
    )

    assert adapter is not None
    assert adapter.portal_label == "BDT"
    assert pdf_url == "https://bdt.bibcom.trento.it/content/download/78214/1625910/file/BDT-113-TIf37.pdf"


def test_portal_request_adapter_uses_registry_referer_and_policy():
    adapter = PortalRequestAdapter.for_portal("bub_digitale")

    assert adapter.portal_key == "bub_digitale"
    assert adapter.referer == "https://bub.unibo.it"
    assert adapter.tile_max_workers == 1
    assert adapter.tile_inter_delay == 0.3


def test_portal_request_adapter_handles_unknown_portal():
    adapter = PortalRequestAdapter.for_portal("non_esiste")

    assert adapter.referer is None
    assert adapter.tile_max_workers is None
    assert adapter.tile_inter_delay == 0.0


def test_resolve_synthetic_manifest_download_for_bdt(monkeypatch):
    monkeypatch.setattr(
        "src.portal_adapters._build_bdt_synthetic_manifest",
        lambda page_url, scraped_html=None: {"sequences": [{"canvases": [{"label": "1"}]}]},
    )

    adapter, manifest, filename = resolve_synthetic_manifest_download(
        "biblioteca_digitale_trentina",
        "https://bdt.bibcom.trento.it/Testi-a-stampa/113",
        container_id="smoke",
        title_slug="titolo",
        scraped_html="<html></html>",
    )

    assert adapter is not None
    assert adapter.portal_label == "BDT"
    assert manifest == {"sequences": [{"canvases": [{"label": "1"}]}]}
    assert filename == "manifest_bdt_113_titolo.json"


def test_resolve_synthetic_manifest_download_for_bdl(monkeypatch):
    monkeypatch.setattr(
        "src.portal_adapters._build_bdl_pdf_manifest",
        lambda page_url: {"seeAlso": [{"@id": page_url, "format": "application/pdf"}]},
    )

    adapter, manifest, filename = resolve_synthetic_manifest_download(
        "biblioteca_digitale_lombarda",
        "https://www.bdl.servizirl.it/bdl/public/rest/srv/item/12404/pdf",
        container_id="smoke",
        title_slug="titolo",
    )

    assert adapter is not None
    assert adapter.portal_label == "BDL"
    assert manifest["seeAlso"][0]["@id"].endswith("/12404/pdf")
    assert filename == "manifest_bdl_12404_titolo.json"


def test_resolve_synthetic_manifest_download_for_rovereto(monkeypatch):
    monkeypatch.setattr(
        "src.portal_adapters._build_rovereto_synthetic_manifest",
        lambda page_url: {"sequences": [{"canvases": [{"label": "1"}, {"label": "2"}]}]},
    )

    adapter, manifest, filename = resolve_synthetic_manifest_download(
        "rovereto_digital_library",
        "https://digitallibrary.bibliotecacivica.rovereto.tn.it/entities/publication/e4199e9b-c79b-4c3d-b157-be2dcfc0407f",
        container_id="smoke",
        title_slug="titolo",
    )

    assert adapter is not None
    assert adapter.portal_label == "Rovereto"
    assert len(manifest["sequences"][0]["canvases"]) == 2
    assert filename == "manifest_rovereto_e4199e9b-c79b-4c3d-b157-be2dcfc0407f_titolo.json"


def test_resolve_synthetic_manifest_download_returns_none_for_unknown_portal():
    adapter, manifest, filename = resolve_synthetic_manifest_download(
        "non_esiste",
        "https://example.test/item/1",
        container_id="smoke",
        title_slug="titolo",
    )

    assert adapter is None
    assert manifest is None
    assert filename is None


def test_resolve_synthetic_manifest_download_for_matricula(monkeypatch):
    monkeypatch.setattr(
        "src.portal_adapters._build_matricula_synthetic_manifest",
        lambda page_url, scraped_html=None: {"sequences": [{"canvases": [{"label": "1"}]}]},
    )

    adapter, manifest, filename = resolve_synthetic_manifest_download(
        "matricula",
        "https://data.matricula-online.eu/en/oesterreich/graz-seckau/example/",
        container_id="smoke",
        title_slug="titolo",
        scraped_html="<html></html>",
    )

    assert adapter is not None
    assert adapter.portal_label == "Matricula"
    assert manifest == {"sequences": [{"canvases": [{"label": "1"}]}]}
    assert filename == "manifest_smoke_titolo.json"


def test_resolve_synthetic_manifest_download_for_internet_archive(monkeypatch):
    monkeypatch.setattr(
        "src.portal_adapters._build_internet_archive_synthetic_manifest",
        lambda page_url: {"sequences": [{"canvases": [{"label": "1"}, {"label": "2"}]}]},
    )

    adapter, manifest, filename = resolve_synthetic_manifest_download(
        "internet_archive",
        "https://archive.org/details/example",
        container_id="smoke",
        title_slug="titolo",
    )

    assert adapter is not None
    assert adapter.portal_label == "IA"
    assert len(manifest["sequences"][0]["canvases"]) == 2
    assert filename == "manifest_smoke_titolo.json"


def test_resolve_synthetic_manifest_download_for_bnc_roma(monkeypatch):
    monkeypatch.setattr(
        "src.portal_adapters._build_bnc_roma_synthetic_manifest",
        lambda page_url, scraped_html=None: {"sequences": [{"canvases": [{"label": "1"}]}]},
    )

    adapter, manifest, filename = resolve_synthetic_manifest_download(
        "bnc_roma",
        "http://digitale.bnc.roma.sbn.it/tecadigitale/libro/example",
        container_id="smoke",
        title_slug="titolo",
        scraped_html="<html></html>",
    )

    assert adapter is not None
    assert adapter.portal_label == "BNC"
    assert manifest == {"sequences": [{"canvases": [{"label": "1"}]}]}
    assert filename == "manifest_smoke_titolo.json"


def test_resolve_synthetic_manifest_download_for_internetculturale_estense(monkeypatch):
    monkeypatch.setattr(
        "src.portal_adapters._build_internetculturale_estense_synthetic_manifest",
        lambda page_url: {"sequences": [{"canvases": [{"label": "1"}, {"label": "2"}, {"label": "3"}]}]},
    )

    adapter, manifest, filename = resolve_synthetic_manifest_download(
        "internetculturale_estense",
        "https://www.internetculturale.it/jmms/iccuviewer/iccu.jsp?id=oai%3Aexample",
        container_id="smoke",
        title_slug="titolo",
    )

    assert adapter is not None
    assert adapter.portal_label == "InternetCulturale"
    assert len(manifest["sequences"][0]["canvases"]) == 3
    assert filename == "manifest_smoke_titolo.json"
