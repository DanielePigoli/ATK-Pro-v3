import time
from src.qt_worker import ElaborazioneWorker
import src.user_prompts as up


def test_worker_emits_need_pdf_and_main_handles(monkeypatch, tmp_path):
    called = {'ask': 0}

    def fake_ask(glossario_data=None, lingua='IT', parent=None):
        called['ask'] += 1
        return True

    monkeypatch.setattr(up, 'ask_generate_pdf', fake_ask)

    # Patch Elaborazione used inside the worker to a lightweight fake
    class FakeElab:
        def __init__(self, mode, url, out_dir, glossario_data=None, lingua='IT', **kwargs):
            self.mode = mode
            self.url = url
            self.out_dir = out_dir
        def set_nome_file(self, name):
            self.name = name
        def run(self, formats=None):
            self.ask_pdf_cb(self.name)
            return True

    import src.qt_worker as qw
    monkeypatch.setattr(qw, 'Elaborazione', FakeElab)

    # Prepare a record that requires PDF confirmation
    rec = {'modalita': 'R', 'url': 'http://fake', 'nome_file': 'r1', 'output': str(tmp_path), 'gen_pdf': None}
    worker = ElaborazioneWorker([rec], formats=['PNG'], glossario_data=None, lingua='IT')

    # Connect a main-thread-like handler to the signal
    def handler(idx, nome_file):
        # emulate main thread showing dialog
        resp = fake_ask()
        worker.records[idx]['gen_pdf'] = bool(resp)

    worker.signals.need_pdf_confirmation.connect(handler)

    # Run synchronously in test thread so signal handlers execute immediately
    worker.run()

    assert called['ask'] == 1
    assert rec['gen_pdf'] is True
