from src.portal_adapters import (
    PortalRequestAdapter,
    resolve_direct_image_download,
    resolve_direct_pdf_download,
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
