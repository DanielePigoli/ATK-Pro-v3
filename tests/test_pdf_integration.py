import os
from src.elaborazione import Elaborazione
import src.pdf_generator as pdf_gen


def test_pdf_integration_selects_single_variant_per_page(tmp_path, monkeypatch):
    """Verifica che `_generate_register_pdf` scelga una sola variante per pagina
    con priorità TIFF > PNG > JPEG e passi la lista selezionata a `create_pdf_from_images`.
    """
    outdir = tmp_path
    elab = Elaborazione('R', 'ark:/dummy/123', str(outdir))
    elab.nome_file = 'testname'
    elab.output_dir = str(outdir)

    # Creiamo file di esempio nel formato che la funzione si aspetta
    files = [
        'testname_canvas_1.tif', 'testname_canvas_1.png', 'testname_canvas_1.jpg',
        'testname_canvas_2.png', 'testname_canvas_2.jpg',
        'testname_canvas_3.jpg'
    ]
    for f in files:
        p = outdir / f
        p.write_bytes(b'0')

    captured = {}

    def fake_create_pdf_from_images(
        paths, outpath, resolution_dpi=400, resource_profile=None
    ):
        # Salviamo le paths passate per asserzioni
        captured['paths'] = list(paths)
        # Creiamo un PDF fittizio
        with open(outpath, 'wb') as fh:
            fh.write(b'%PDF-1.4\n%%EOF')
        return outpath

    # Le funzioni sono state importate direttamente in `src.elaborazione`, quindi
    # dobbiamo patchare i nomi lì per influenzare `_generate_register_pdf`.
    monkeypatch.setattr('src.elaborazione.create_pdf_from_images', fake_create_pdf_from_images)
    monkeypatch.setattr('src.elaborazione.enrich_pdf_metadata', lambda *a, **k: None)

    pdf_path = elab._generate_register_pdf(files)
    assert pdf_path is not None
    assert os.path.exists(pdf_path)

    # Controlliamo che sia stata selezionata una sola immagine per base
    assert 'paths' in captured
    paths = captured['paths']
    assert len(paths) == 3

    exts = [os.path.splitext(p)[1].lower() for p in paths]
    # Ordine previsto per i nostri nomi: canvas_1, canvas_2, canvas_3
    assert exts == ['.tif', '.png', '.jpg']
