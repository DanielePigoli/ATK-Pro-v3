from src.elaborazione import _canvas_max_workers_for_portal


def test_canvas_workers_are_sequential_for_prudent_portals():
    assert _canvas_max_workers_for_portal("bub_digitale", cpu_count=16) == 1
    assert _canvas_max_workers_for_portal("dl_ficlit", cpu_count=16) == 1
    assert _canvas_max_workers_for_portal("biblioteca_digitale_siena", cpu_count=16) == 1
    assert _canvas_max_workers_for_portal("rovereto_digital_library", cpu_count=16) == 1


def test_canvas_workers_remain_parallel_for_unlimited_portals():
    assert _canvas_max_workers_for_portal("gallica", cpu_count=16) == 8
    assert _canvas_max_workers_for_portal("non_esiste", cpu_count=16) == 8
