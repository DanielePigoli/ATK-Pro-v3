from src.portal_adapters import resolve_direct_image_download


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
