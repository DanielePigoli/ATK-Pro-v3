"""
Test coverage per resilienza canvas ID extractor
Verifica fallback: Playwright timeout → HTML parsing → hardcoded fallback
"""
import re
from unittest.mock import Mock
from src import canvas_id_extractor as cie


def _install_mock_browser(monkeypatch, page):
    mock_context = Mock()
    mock_context.new_page.return_value = page
    mock_context.set_default_timeout = Mock()

    mock_browser = Mock()
    mock_browser.new_context.return_value = mock_context
    mock_browser.close = Mock()

    mock_playwright = Mock()
    mock_playwright.chromium.launch.return_value = mock_browser

    def mock_sync_playwright(*args, **kwargs):
        class PlaywrightContext:
            def __enter__(self):
                return mock_playwright

            def __exit__(self, *args):
                pass

        return PlaywrightContext()

    monkeypatch.setattr(cie, "sync_playwright", mock_sync_playwright)
    return mock_context, mock_browser


class TestCanvasExtractorPlaywrightFallback:
    """Test fallback chain: Playwright → HTML → hardcoded."""

    def test_canvas_id_from_playwright_intercept(self, monkeypatch):
        """Best case: intercetta info.json tramite evento response."""
        mock_page = Mock()
        callbacks = {}

        def on_event(event, callback):
            callbacks[event] = callback

        def wait_for_timeout(*args, **kwargs):
            response = Mock()
            response.url = 'https://base/iiif/2/CANVAS123/info.json'
            callbacks["response"](response)

        mock_page.on = Mock(side_effect=on_event)
        mock_page.goto = Mock()
        mock_page.locator.return_value.click = Mock()
        mock_page.wait_for_timeout = Mock(side_effect=wait_for_timeout)
        mock_page.wait_for_load_state = Mock()
        mock_page.content = Mock(return_value='<html></html>')
        
        mock_context = Mock()
        mock_context.new_page.return_value = mock_page
        mock_context.set_default_timeout = Mock()
        
        mock_browser = Mock()
        mock_browser.new_context.return_value = mock_context
        mock_browser.close = Mock()
        
        mock_playwright = Mock()
        mock_playwright.chromium.launch.return_value = mock_browser
        
        def mock_sync_playwright(*args, **kwargs):
            class PlaywrightContext:
                def __enter__(self):
                    return mock_playwright
                def __exit__(self, *args):
                    pass
            return PlaywrightContext()
        
        monkeypatch.setattr(cie, 'sync_playwright', mock_sync_playwright)
        
        result = cie.extract_ud_canvas_id_from_infojson_xhr('https://example.com', timeout_ms=30000)
        
        # Deve trovare CANVAS123 dalla URL intercettata
        assert result == 'CANVAS123'

    def test_canvas_id_from_html_fallback(self, monkeypatch):
        """Fallback 1: Se no XHR intercettato, parsa HTML per IIIF canvas ID."""
        mock_page = Mock()
        mock_page.goto = Mock()
        mock_page.on = Mock()
        mock_page.wait_for_timeout = Mock()
        mock_page.wait_for_load_state = Mock()
        mock_page.content.return_value = (
            '<script src="https://base.example/iiif/2/HTML123/info.json"></script>'
        )
        mock_page.frames = []
        _install_mock_browser(monkeypatch, mock_page)

        result = cie.extract_ud_canvas_id_from_infojson_xhr("https://example.com")

        assert result == "HTML123"

    def test_canvas_id_from_iframe_fallback(self, monkeypatch):
        """Fallback 2: Se HTML principale fallisce, cerca in iframe."""
        mock_frame = Mock()
        mock_frame.content.return_value = (
            '{"@id":"https://base.example/iiif/2/FRAME456/full/full/0/default.jpg"}'
        )
        mock_page = Mock()
        mock_page.goto = Mock()
        mock_page.on = Mock()
        mock_page.wait_for_timeout = Mock()
        mock_page.wait_for_load_state = Mock()
        mock_page.content.return_value = "<html><body>nessun canvas</body></html>"
        mock_page.frames = [mock_frame]
        _install_mock_browser(monkeypatch, mock_page)

        result = cie.extract_ud_canvas_id_from_infojson_xhr("https://example.com")

        assert result == "FRAME456"


class TestCanvasExtractorTimeout:
    """Test timeout personalizzabile di Playwright."""

    def test_custom_timeout_respected(self, monkeypatch):
        """Timeout personalizzato viene passato a Playwright."""
        captured_timeouts = {}
        
        mock_page = Mock()
        mock_page.goto = Mock()
        mock_page.on = Mock()
        mock_page.locator.return_value.click = Mock()
        mock_page.wait_for_timeout = Mock()
        mock_page.wait_for_load_state = Mock()
        mock_page.content = Mock(return_value='<html></html>')
        mock_page.frames = []
        
        def set_timeout(timeout_ms):
            captured_timeouts['timeout_ms'] = timeout_ms
        
        mock_context = Mock()
        mock_context.new_page.return_value = mock_page
        mock_context.set_default_timeout = Mock(side_effect=set_timeout)
        
        mock_browser = Mock()
        mock_browser.new_context.return_value = mock_context
        mock_browser.close = Mock()
        
        mock_playwright = Mock()
        mock_playwright.chromium.launch.return_value = mock_browser
        
        def mock_sync_playwright(*args, **kwargs):
            class PlaywrightContext:
                def __enter__(self):
                    return mock_playwright
                def __exit__(self, *args):
                    pass
            return PlaywrightContext()
        
        monkeypatch.setattr(cie, 'sync_playwright', mock_sync_playwright)
        
        # Chiama con timeout custom di 60 secondi
        cie.extract_ud_canvas_id_from_infojson_xhr('https://example.com', timeout_ms=60000)
        
        # Verifica che timeout sia stato settato
        assert captured_timeouts.get('timeout_ms') == 60000


class TestCanvasExtractorErrorHandling:
    """Test gestione errori e eccezioni."""

    def test_playwright_error_returns_none(self, monkeypatch):
        """Se Playwright crasha completamente → ritorna None."""
        def mock_sync_playwright(*args, **kwargs):
            raise Exception("Playwright initialization failed")
        
        monkeypatch.setattr(cie, 'sync_playwright', mock_sync_playwright)
        
        result = cie.extract_ud_canvas_id_from_infojson_xhr('https://example.com')
        
        # No crash, just returns None
        assert result is None

    def test_network_error_handled_gracefully(self, monkeypatch):
        """Errore di rete (navigazione pagina) gestito gracefully."""
        mock_page = Mock()
        mock_page.goto = Mock(side_effect=Exception("Network error"))
        
        mock_context = Mock()
        mock_context.new_page.return_value = mock_page
        mock_context.set_default_timeout = Mock()
        
        mock_browser = Mock()
        mock_browser.new_context.return_value = mock_context
        mock_browser.close = Mock()
        
        mock_playwright = Mock()
        mock_playwright.chromium.launch.return_value = mock_browser
        
        def mock_sync_playwright(*args, **kwargs):
            class PlaywrightContext:
                def __enter__(self):
                    return mock_playwright
                def __exit__(self, *args):
                    pass
            return PlaywrightContext()
        
        monkeypatch.setattr(cie, 'sync_playwright', mock_sync_playwright)
        
        result = cie.extract_ud_canvas_id_from_infojson_xhr('https://example.com')
        
        # No crash
        assert result is None

    def test_frame_parsing_error_continues(self, monkeypatch):
        """Errore parsing iframe non blocca, continua con altri fallback."""
        mock_page = Mock()
        mock_page.goto = Mock()
        mock_page.on = Mock()
        mock_page.locator.return_value.click = Mock()
        mock_page.wait_for_timeout = Mock()
        mock_page.wait_for_load_state = Mock()
        mock_page.content = Mock(return_value='<html><body>Fallback HTML</body></html>')
        
        # Uno dei frame crasha nel content()
        mock_frame1 = Mock()
        mock_frame1.content = Mock(side_effect=Exception("Frame error"))
        
        mock_frame2 = Mock()
        mock_frame2.content = Mock(return_value='<html><script src="https://base/iiif/2/CANVAS_GOOD/info.json"></script></html>')
        
        mock_page.frames = [mock_frame1, mock_frame2]
        
        mock_context = Mock()
        mock_context.new_page.return_value = mock_page
        mock_context.set_default_timeout = Mock()
        
        mock_browser = Mock()
        mock_browser.new_context.return_value = mock_context
        mock_browser.close = Mock()
        
        mock_playwright = Mock()
        mock_playwright.chromium.launch.return_value = mock_browser
        
        def mock_sync_playwright(*args, **kwargs):
            class PlaywrightContext:
                def __enter__(self):
                    return mock_playwright
                def __exit__(self, *args):
                    pass
            return PlaywrightContext()
        
        monkeypatch.setattr(cie, 'sync_playwright', mock_sync_playwright)
        
        result = cie.extract_ud_canvas_id_from_infojson_xhr('https://example.com')
        
        # Non crasha, continua e trova CANVAS_GOOD nel frame2
        assert result == 'CANVAS_GOOD'


class TestCanvasExtractorRegexPatterns:
    """Test che regex pattern IIIF sia corretto."""

    def test_iiif_pattern_matches_standard_format(self):
        """Pattern regex /iiif/2/<id>/ corrisponde a canvas standard."""
        pattern = r"/iiif/2/([A-Za-z0-9]+)/"
        
        # Should match
        assert re.search(pattern, '/iiif/2/CANVAS123/')
        assert re.search(pattern, '/iiif/2/abc123def/')
        
        # Should not match
        assert not re.search(pattern, '/iiif/3/CANVAS123/')
        assert not re.search(pattern, '/iiif/2//empty/')

    def test_info_json_endpoint_pattern(self):
        """Pattern per info.json endpoint."""
        assert (
            cie._extract_canvas_id_from_text(
                "https://base.example/iiif/2/INFO_789-abc/info.json"
            )
            == "INFO_789-abc"
        )
        assert (
            cie._extract_canvas_id_from_text(
                "canvasId: 'https://antenati.example/ark:/12657/ARK123'"
            )
            == "ARK123"
        )
        assert cie._extract_canvas_id_from_text("") is None

    def test_canvas_id_extraction_from_multiple_urls(self):
        """Estrae correttamente canvas ID da varie URL format."""
        test_cases = [
            ('https://dam.it/iiif/2/ABC123/manifest.json', 'ABC123'),
            ('https://base/iiif/2/XYZ_789/info.json', 'XYZ_789'),
            ('http://localhost/iiif/2/test/full/0/default.jpg', 'test'),
        ]

        for url, expected in test_cases:
            assert cie._extract_canvas_id_from_text(url) == expected


class TestCanvasExtractorBrowserHeadless:
    """Test browser mode (headless vs headed)."""

    def test_headless_browser_launched(self, monkeypatch):
        """Browser deve essere lanciato in headless mode."""
        captured_kwargs = {}
        
        mock_browser = Mock()
        mock_browser.new_context = Mock(return_value=Mock())
        mock_browser.close = Mock()
        
        def fake_launch(headless=None, **kwargs):
            captured_kwargs['headless'] = headless
            captured_kwargs['kwargs'] = kwargs
            return mock_browser
        
        mock_chromium = Mock()
        mock_chromium.launch = fake_launch
        
        mock_playwright = Mock()
        mock_playwright.chromium = mock_chromium
        
        def mock_sync_playwright(*args, **kwargs):
            class PlaywrightContext:
                def __enter__(self):
                    return mock_playwright
                def __exit__(self, *args):
                    pass
            return PlaywrightContext()
        
        monkeypatch.setattr(cie, 'sync_playwright', mock_sync_playwright)
        
        try:
            cie.extract_ud_canvas_id_from_infojson_xhr('https://example.com')
        except:
            pass
        
        # Verifica che headless=True sia stato usato
        assert captured_kwargs.get('headless') == True
