# Worker Qt per eseguire l'elaborazione in background e inviare segnali di progresso
from PySide6.QtCore import QObject, Signal, QThread
import logging
import time
import os
from logging.handlers import RotatingFileHandler
ATKPRO_ENV = os.environ.get("ATKPRO_ENV", "development").lower()
logger = logging.getLogger(__name__)


if not logger.hasHandlers():
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG if ATKPRO_ENV != "production" else logging.WARNING)
    logger.addHandler(handler)
    if ATKPRO_ENV != "production":
        file_handler = RotatingFileHandler('atkpro_output.log', maxBytes=5*1024*1024, backupCount=3, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        logger.addHandler(file_handler)
logger.setLevel(logging.DEBUG if ATKPRO_ENV != "production" else logging.WARNING)

from elaborazione import Elaborazione
try:
    from portal_registry import detect_portal_from_url
except ImportError:
    from src.portal_registry import detect_portal_from_url

logger = logging.getLogger(__name__)


class WorkerSignals(QObject):
    progress = Signal(int, int, str, int, int)  # current, total, name, page, page_total
    finished = Signal(list)  # risultati
    error = Signal(str)
    need_pdf_confirmation = Signal(int, str)  # idx, name -- richiesta al main thread


class ElaborazioneWorker(QThread):
    def __init__(
        self,
        records,
        formats=None,
        glossario_data=None,
        lingua='IT',
        portale='antenati',
        resource_profile: str | None = None,
    ):
        super().__init__()
        self.records = records or []
        self.formats = formats
        self.glossario = glossario_data
        self.lingua = lingua
        self.portale = portale
        self.resource_profile = resource_profile
        self._is_cancelled = False
        self.results = []
        self.signals = WorkerSignals()

    def cancel(self):
        self._is_cancelled = True

    def run(self):
        total = len(self.records)
        results = []
        for idx, record in enumerate(self.records):
            if self._is_cancelled:
                logger.info("[Worker] Cancellazione richiesta, interrompo")
                break

            try:
                modalita = str(record.get('modalita', '')).strip().upper()
                url = record.get('url')
                nome_file = record.get('nome_file', 'documento')
                dettaglio = record.get('descrizione') or record.get('tipo') or ''
                # Rimuovi eventuale 'pag. x' da dettaglio
                import re
                dettaglio_clean = re.sub(r'—?\s*pag\.\s*\d+\s*$', '', dettaglio).strip()
                if dettaglio_clean:
                    progress_descr = f"{nome_file} — {dettaglio_clean}"
                else:
                    progress_descr = nome_file

                out_dir = record.get('output') or record.get('output_dir') or os.getcwd()

                # Simulazione
                if record.get('simulate'):
                    steps = record.get('simulate_steps', 3)
                    for s in range(steps):
                        if self._is_cancelled:
                            break
                        time.sleep(0.5)
                        self.signals.progress.emit(idx+1, total, progress_descr, s+1, steps)
                    results.append({
                        'file': nome_file,
                        'modalita': modalita,
                        'output': out_dir,
                        'status': 'SIMULATED'
                    })
                    self.signals.progress.emit(idx+1, total, progress_descr, steps, steps)
                    continue

                # Segnala l'inizio dell'elaborazione del record (aggiorna UI)
                try:
                    page = getattr(record, 'page', None)
                    page_total = getattr(record, 'page_total', None)
                    if page is not None and page_total is not None:
                        self.signals.progress.emit(idx+1, total, progress_descr, page, page_total)
                    else:
                        self.signals.progress.emit(idx+1, total, progress_descr, 0, 0)
                except Exception:
                    pass

                # Esegue l'elaborazione reale (sincrona)

                detected_portal = detect_portal_from_url(url)
                record_portal = detected_portal or self.portale
                if record_portal != self.portale:
                    logger.warning(
                        f"[Worker] URL incompatibile con il portale selezionato: "
                        f"correzione da {self.portale} a {record_portal} "
                        f"in base all'URL del record"
                    )
                elab = Elaborazione(
                    modalita.lower(),
                    url,
                    out_dir,
                    self.glossario,
                    self.lingua,
                    portale=record_portal,
                    resource_profile=self.resource_profile,
                )
                elab.set_nome_file(nome_file)
                # Range canvas opzionale (es. canvas 1-5)
                elab.canvas_da = record.get('canvas_da') or None
                elab.canvas_a = record.get('canvas_a') or None
                # Callback per progresso canvas
                try:
                    def _canvas_progress(c_idx, c_tot, c_name=None):
                        try:
                            label = f"{progress_descr}"
                            if c_name:
                                label = f"{progress_descr} — {c_name}"
                            else:
                                label = f"{progress_descr} — canvas {c_idx}/{c_tot}"
                            self.signals.progress.emit(idx+1, total, label, c_idx, c_tot)
                        except Exception:
                            pass
                    setattr(elab, 'progress_cb', _canvas_progress)
                except Exception:
                    pass
                # Callback per richiesta PDF: emette segnale e attende risposta
                def _ask_pdf_cb(nome_file):
                    self.signals.need_pdf_confirmation.emit(idx, nome_file)
                    wait_start = time.time()
                    wait_timeout = 120.0
                    while not self._is_cancelled and record.get('gen_pdf') is None and (time.time() - wait_start) < wait_timeout:
                        time.sleep(0.1)
                    if record.get('gen_pdf') is None:
                        record['gen_pdf'] = False
                    return record.get('gen_pdf', False)
                setattr(elab, 'ask_pdf_cb', _ask_pdf_cb)
                # Se è stata predecisa la generazione del PDF dal main thread, passala
                try:
                    if record.get('gen_pdf') is not None:
                        elab.force_gen_pdf = bool(record.get('gen_pdf'))
                except Exception:
                    pass
                success = elab.run(formats=self.formats)

                if success:
                    results.append({
                        'file': nome_file,
                        'modalita': modalita,
                        'output': out_dir,
                        'formati': self.formats,
                        'status': 'SUCCESS'
                    })
                else:
                    results.append({
                        'file': nome_file,
                        'modalita': modalita,
                        'output': out_dir,
                        'status': 'FAILED'
                    })

                # Emissione progresso
                self.signals.progress.emit(idx+1, total, progress_descr, 0, 0)

            except Exception as e:
                logger.error(f"[Worker] Errore record {record}: {e}")
                try:
                    self.signals.error.emit(str(e))
                except Exception:
                    pass
                results.append({
                    'file': record.get('nome_file', 'sconosciuto'),
                    'modalita': modalita,
                    'errore': str(e),
                    'status': 'ERROR'
                })

        # Fine
        self.results = results
        try:
            self.signals.finished.emit(results)
        except Exception:
            pass
