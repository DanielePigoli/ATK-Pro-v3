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
