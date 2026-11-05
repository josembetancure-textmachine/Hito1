# Pruebas unitarias del pipeline de Hito 1 (H-05).
# Se ejecutan desde la raíz del proyecto con: pytest -q

import pandas as pd

from main import (
    build_accent_dic,
    city_territories,
    classify_status,
    extract_contact,
    load_progress,
    normalized_dates,
    save_progress,
)


def test_classify_status_urgent_wins_over_normal():
    # H-01: una observación urgente que además dice "normal" y "sin novedad" debe quedar en Rojo, no en Verde.
    observations = pd.Series(["Urgente: revisar. Todo normal, sin novedad."])

    result = classify_status(observations)

    assert result.tolist() == ["Rojo"]


def test_normalized_dates_mixed_formats():
    # H-02: fechas en formatos distintos quedan en dd/mm/aaaa; una fecha imposible y un nulo quedan como "Sin dato".
    dates = pd.Series(["8/2/26", "Abr 05, 2026", "2026-02-11", "31/02/26", None])

    result = normalized_dates(dates)

    assert result.tolist() == ["08/02/2026", "05/04/2026", "11/02/2026", "Sin dato", "Sin dato"]


def test_city_territories_fixes_accent_from_input(monkeypatch):
    # H-04 y H-09: el input() se simula con monkeypatch para que la prueba no espere el teclado.
    # El operador escribe "uraba" sin tilde y la región debe guardarse como "Urabá".
    monkeypatch.setattr("builtins.input", lambda prompt: "uraba")
    accent_dic = build_accent_dic(pd.Series(["Urabá", "Norte"]))

    result = city_territories(["Turbo"], accent_dic)

    assert result == {"Turbo": "Urabá"}


def test_extract_contact_email_with_hyphen():
    # H-03: un correo con guion no se parte; el teléfono y el correo quedan cada uno en su lugar.
    result = extract_contact("3001234567 puerto-claver@dominio.com")

    assert result == ("3001234567", "puerto-claver@dominio.com")


def test_progress_missing_file_and_round_trip(tmp_path):
    # H-09: sin archivo de progreso se devuelve un diccionario vacío;
    # lo que se guarda con save_progress se recupera igual con load_progress.
    progress_file = tmp_path / "progress_territories.json"
    region_map = {"Medellín": "Valle de Aburrá"}

    assert load_progress(progress_file) == {}

    save_progress(region_map, progress_file)

    assert load_progress(progress_file) == region_map