import src.elaborazione as elaborazione


def test_ficlit_resolves_manifest_before_browser(monkeypatch):
    def fail_selenium():
        raise AssertionError("Selenium should not be used for direct FICLIT URLs")

    def fail_playwright(_url):
        raise AssertionError("Playwright should not be used for direct FICLIT URLs")

    monkeypatch.setattr(elaborazione, "setup_selenium", fail_selenium)
    monkeypatch.setattr(elaborazione, "setup_playwright", fail_playwright)

    elab = object.__new__(elaborazione.Elaborazione)
    elab.ark_url = "https://dl.ficlit.unibo.it/s/lib/item/28429"
    elab.portale = "dl_ficlit"

    assert (
        elab._get_manifest_url()
        == "https://dl.ficlit.unibo.it/iiif/2/28429/manifest"
    )


def test_antenati_resolves_public_page_manifest_before_browser(monkeypatch):
    page_url = "https://antenati.cultura.gov.it/ark:/12657/an_ua21449/wQNNjzL"
    manifest_url = (
        "https://dam-antenati.cultura.gov.it/antenati/containers/abc123/manifest"
    )

    monkeypatch.setattr(
        elaborazione,
        "robust_find_manifest",
        lambda url, html=None: manifest_url if url == page_url else None,
    )
    monkeypatch.setattr(
        elaborazione,
        "setup_selenium",
        lambda: (_ for _ in ()).throw(
            AssertionError("Selenium should not run when Antenati HTML exposes a manifest")
        ),
    )
    monkeypatch.setattr(
        elaborazione,
        "setup_playwright",
        lambda _url: (_ for _ in ()).throw(
            AssertionError("Playwright should not run when Antenati HTML exposes a manifest")
        ),
    )

    elab = object.__new__(elaborazione.Elaborazione)
    elab.ark_url = page_url
    elab.portale = "antenati"

    assert elab._get_manifest_url() == manifest_url


def test_public_portal_html_manifest_is_resolved_before_browser(monkeypatch):
    page_url = (
        "https://bub.unibo.it/it/bub-digitale/bollettini-parrocchiali/"
        "l-angelo-della-famiglia-bollettino-parrocchiale-di-bondanello-castelmaggiore-bologna"
    )
    manifest_url = (
        "https://bub.unibo.it/iiif/2/manifest/bub/bollettiniparrocchiali/"
        "_castelmaggiore_-_s_bartolomeo_di_bondanello/jpg/1934.json"
    )

    monkeypatch.setattr(elaborazione, "robust_find_manifest", lambda url, html=None: manifest_url if url == page_url else None)
    monkeypatch.setattr(
        elaborazione,
        "setup_selenium",
        lambda: (_ for _ in ()).throw(
            AssertionError("Selenium should not run when the public page already exposes a manifest")
        ),
    )
    monkeypatch.setattr(
        elaborazione,
        "setup_playwright",
        lambda _url: (_ for _ in ()).throw(
            AssertionError("Playwright should not run when the public page already exposes a manifest")
        ),
    )

    elab = object.__new__(elaborazione.Elaborazione)
    elab.ark_url = page_url
    elab.portale = "bub_digitale"

    assert elab._get_manifest_url() == manifest_url
