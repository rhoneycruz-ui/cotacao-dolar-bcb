from unittest.mock import patch
from pathlib import Path

import pandas as pd
import pytest
import streamlit as st
from streamlit.testing.v1 import AppTest

from src.bcb import BCBDataError


APP_PATH = Path(__file__).parents[1] / "app.py"


@pytest.fixture(autouse=True)
def clear_streamlit_cache():
    st.cache_data.clear()
    yield
    st.cache_data.clear()


def sample_quotes():
    return pd.DataFrame(
        {
            "data": pd.to_datetime(["2026-10-19", "2026-10-20"]),
            "cotacao_dolar": [5.25, 5.3],
        }
    )


def test_app_renders_real_data_without_demo_banner():
    with patch("src.bcb.fetch_quotes", return_value=sample_quotes()):
        app = AppTest.from_file(APP_PATH, default_timeout=10).run()

    assert not app.exception
    assert app.title[0].value == "Dólar comercial"
    labels = [metric.label for metric in app.metric]
    assert labels == ["Variação", "Mínima", "Máxima", "Média", "Amplitude"]
    assert app.metric[0].value == "+0,95%"
    assert not any("Dados demonstrativos" in item.value for item in app.warning)
    assert any("Banco Central do Brasil" in item.value for item in app.caption)


def test_api_error_offers_demo_without_loading_it():
    with patch(
        "src.bcb.fetch_quotes",
        side_effect=BCBDataError("fonte indisponível"),
    ):
        app = AppTest.from_file(APP_PATH, default_timeout=10).run()

    assert not app.exception
    assert any("Banco Central" in item.value for item in app.error)
    assert [button.label for button in app.button] == [
        "Atualizar dados",
        "Visualizar dados demonstrativos",
    ]
    assert not app.metric


def test_demo_button_loads_demo_with_persistent_banner():
    with (
        patch(
            "src.bcb.fetch_quotes",
            side_effect=BCBDataError("fonte indisponível"),
        ),
        patch("src.bcb.load_demo", return_value=sample_quotes()),
    ):
        app = AppTest.from_file(APP_PATH, default_timeout=10).run()
        app.button[1].click().run()

    assert not app.exception
    assert any("Dados demonstrativos" in item.value for item in app.warning)
    assert len(app.metric) == 5
    assert app.metric[0].value == "+0,95%"


def test_period_selector_requests_every_supported_limit():
    calls = []

    def fake_fetch(limit):
        calls.append(limit)
        return sample_quotes()

    with patch("src.bcb.fetch_quotes", side_effect=fake_fetch):
        app = AppTest.from_file(APP_PATH, default_timeout=10).run()
        for limit in (30, 180, 365):
            app.selectbox[0].select(limit).run()

    assert app.selectbox[0].options == [
        "Últimos 30 registros",
        "Últimos 90 registros",
        "Últimos 180 registros",
        "Últimos 365 registros",
    ]
    assert {30, 90, 180, 365}.issubset(calls)


def test_refresh_button_requests_live_data_again():
    calls = []

    def fake_fetch(limit):
        calls.append(limit)
        return sample_quotes()

    with patch("src.bcb.fetch_quotes", side_effect=fake_fetch):
        app = AppTest.from_file(APP_PATH, default_timeout=10).run()
        first_count = len(calls)
        app.button[0].click().run()

    assert first_count == 1
    assert len(calls) >= 2


def test_details_show_table_and_download_for_displayed_period():
    with patch("src.bcb.fetch_quotes", return_value=sample_quotes()):
        app = AppTest.from_file(APP_PATH, default_timeout=10).run()

    assert app.expander[0].label == "Ver dados do período"
    assert len(app.dataframe) == 1
    assert len(app.get("download_button")) == 1
