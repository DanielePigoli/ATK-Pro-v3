from src.elaborazione import _ficlit_direct_image_url_from_canvas


def test_ficlit_direct_image_url_is_extracted_from_canvas():
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

    assert (
        _ficlit_direct_image_url_from_canvas(canvas)
        == "https://dl.ficlit.unibo.it/iiif/2/45498/full/699,800/0/default.jpg"
    )


def test_ficlit_direct_image_url_rejects_external_canvas():
    canvas = {
        "images": [
            {
                "resource": {
                    "@id": "https://example.test/iiif/2/45498/full/699,800/0/default.jpg",
                    "service": {
                        "@id": "https://dl.ficlit.unibo.it/iiif/2/45498",
                    },
                }
            }
        ]
    }

    assert _ficlit_direct_image_url_from_canvas(canvas) is None
