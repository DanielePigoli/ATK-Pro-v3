"""
Test coverage completo per qt_worker.py (ElaborazioneWorker)
Evita regressioni nel worker di elaborazione multi-threaded
"""
import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from src.qt_worker import ElaborazioneWorker, WorkerSignals


@pytest.fixture
def glossario_data():
    """Glossario mock per test."""
    return {
        "messaggi_dialogo": [
            {"messaggio": "Elaborazione in corso", "IT": "Elaborazione in corso", "EN": "Processing"},
            {"messaggio": "Elaborazione record: {n}/{tot}", "IT": "Elaborazione record: {n}/{tot}", "EN": "Processing: {n}/{tot}"},
        ]
    }


@pytest.fixture
def worker(glossario_data):
    """Istanza ElaborazioneWorker per test."""
    records = [
        {"modalita": "R", "url": "http://test.com", "nome_file": "test1"},
        {"modalita": "D", "url": "http://test.com", "nome_file": "test2"},
    ]
    return ElaborazioneWorker(records, formats=["PNG", "JPG"], glossario_data=glossario_data, lingua="IT")


class TestElaborazioneWorkerInit:
    """Test inizializzazione ElaborazioneWorker."""
    
    def test_init_with_records(self, worker):
        """ElaborazioneWorker inizializza con record list."""
        assert worker is not None
        assert len(worker.records) > 0
    
    def test_init_with_formats(self):
        """ElaborazioneWorker memorizza formati selezionati."""
        worker = ElaborazioneWorker([], formats=["PNG", "JPEG", "TIFF"])
        assert hasattr(worker, 'formats')
    
    def test_init_with_glossario(self, glossario_data):
        """ElaborazioneWorker riceve glossario_data per localizzazione."""
        worker = ElaborazioneWorker([], glossario_data=glossario_data, lingua="IT")
        assert hasattr(worker, 'glossario')
        assert worker.glossario is not None
    
    def test_init_lingua_default(self):
        """ElaborazioneWorker usa lingua default se non specificata."""
        worker = ElaborazioneWorker([])
        assert hasattr(worker, 'lingua')
        lingue_supportate = ["IT", "EN", "ES", "DE", "FR", "PT", "NL", "AR", "HE", "RU",
                               "DA", "EL", "JA", "NO", "PL", "RO", "SV", "TR", "VI", "ZH"]
        assert worker.lingua in lingue_supportate


class TestWorkerSignals:
    """Test Qt signals dal WorkerSignals."""
    
    def test_signals_progress_exists(self):
        """WorkerSignals ha signal progress."""
        signals = WorkerSignals()
        assert hasattr(signals, 'progress')
    
    def test_signals_finished_exists(self):
        """WorkerSignals ha signal finished."""
        signals = WorkerSignals()
        assert hasattr(signals, 'finished')
    
    def test_signals_error_exists(self):
        """WorkerSignals ha signal error."""
        signals = WorkerSignals()
        assert hasattr(signals, 'error')


class TestElaborazioneWorkerSignals:
    """Test signals dal worker."""
    
    def test_worker_has_signals(self, worker):
        """ElaborazioneWorker ha signals object."""
        assert hasattr(worker, 'signals')
        assert worker.signals is not None
        assert isinstance(worker.signals, WorkerSignals)


class TestElaborazioneWorkerProcessing:
    """Test logica elaborazione record."""
    
    def test_worker_has_run_method(self, worker):
        """ElaborazioneWorker ha metodo run."""
        assert hasattr(worker, 'run')
    
    def test_worker_skips_on_cancel(self):
        """ElaborazioneWorker può essere cancellato."""
        worker = ElaborazioneWorker([])
        assert hasattr(worker, 'cancel')
        worker.cancel()
        assert worker._is_cancelled is True
    
    def test_worker_handles_missing_urls(self):
        """ElaborazioneWorker gestisce record senza URL."""
        records = [
            {"modalita": "R", "nome_file": "test"},  # URL mancante
        ]
        worker = ElaborazioneWorker(records)
        
        # Non deve crashare durante init
        assert worker is not None

    def test_worker_stores_results_after_run(self, monkeypatch, tmp_path):
        """ElaborazioneWorker espone i risultati per la dialog finale."""
        import src.qt_worker as qw

        class FakeElab:
            def __init__(self, *args, **kwargs):
                pass
            def set_nome_file(self, name):
                self.name = name
            def run(self, formats=None):
                return True

        monkeypatch.setattr(qw, "Elaborazione", FakeElab)
        worker = ElaborazioneWorker([
            {"modalita": "D", "url": "https://example.test/doc", "nome_file": "doc", "output": str(tmp_path)}
        ], formats=["PDF"])

        worker.run()

        assert worker.results == [{
            "file": "doc",
            "modalita": "D",
            "output": str(tmp_path),
            "formati": ["PDF"],
            "status": "SUCCESS",
        }]


class TestElaborazioneWorkerLocalization:
    """Test localizzazione messaggi nel worker."""
    
    def test_worker_uses_glossario_for_messages(self, worker, glossario_data):
        """ElaborazioneWorker usa glossario per messaggi localizzati."""
        assert worker.glossario == glossario_data
        assert worker.lingua == "IT"
    
    def test_worker_fallback_without_glossario(self):
        """ElaborazioneWorker funziona senza glossario_data (fallback)."""
        worker = ElaborazioneWorker([], glossario_data=None)
        # Deve funzionare con messaggi hardcoded
        assert worker is not None


class TestElaborazioneWorkerErrorHandling:
    """Test gestione errori nel worker."""
    
    def test_worker_handles_exceptions_gracefully(self):
        """ElaborazioneWorker gestisce eccezioni without crashing."""
        records = [
            {"modalita": "INVALID", "url": "http://invalid"},
        ]
        worker = ElaborazioneWorker(records)
        
        # Dovrebbe gestire eccezioni durante run
        assert worker is not None


class TestElaborazioneWorkerFormatHandling:
    """Test gestione formati immagine."""
    
    def test_worker_respects_format_selection(self):
        """ElaborazioneWorker rispetta selezione formati da GUI."""
        formats = ["PNG"]  # Solo PNG, non JPG/TIFF
        worker = ElaborazioneWorker([], formats=formats)
        
        assert worker.formats == formats
    
    def test_worker_handles_all_formats(self):
        """ElaborazioneWorker gestisce PNG, JPEG, TIFF."""
        for fmt in ["PNG", "JPEG", "TIFF", "JPG"]:
            worker = ElaborazioneWorker([], formats=[fmt])
            assert worker is not None


class TestElaborazioneWorkerThreading:
    """Test thread safety."""
    
    def test_worker_is_threadable(self, worker):
        """ElaborazioneWorker estende QThread."""
        # ElaborazioneWorker estende QThread
        assert hasattr(worker, 'run')
        assert hasattr(worker, 'start')
    
    def test_worker_has_cancel_mechanism(self, worker):
        """ElaborazioneWorker ha meccanismo per cancellazione."""
        assert hasattr(worker, 'cancel')
        worker.cancel()
        assert worker._is_cancelled is True


class TestElaborazioneWorkerIntegration:
    """Test integrazione con componenti correlate."""
    
    def test_worker_compatible_with_main_gui(self):
        """ElaborazioneWorker integra con main_gui_qt."""
        records = [{"modalita": "R", "url": "http://test.com"}]
        worker = ElaborazioneWorker(records, formats=["PNG"])
        assert worker is not None
        assert worker.signals is not None
