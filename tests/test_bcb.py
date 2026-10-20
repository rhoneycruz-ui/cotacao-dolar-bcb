import pandas as pd
import pytest
import requests


def test_normalize_records_returns_canonical_frame():
    from src.bcb import normalize_records

    result = normalize_records(
        [
            {"data": "19/10/2026", "valor": "5.2500"},
            {"data": "20/10/2026", "valor": "5.3000"},
        ]
    )

    assert result.columns.tolist() == ["data", "cotacao_dolar"]
    assert str(result["data"].dtype) == "datetime64[ns]"
    assert str(result["cotacao_dolar"].dtype) == "float64"
    assert result.index.tolist() == [0, 1]
    assert result["cotacao_dolar"].tolist() == [5.25, 5.3]


def test_normalize_records_accepts_comma_decimal():
    from src.bcb import normalize_records

    result = normalize_records([{"data": "20/10/2026", "valor": "5,4321"}])

    assert result.loc[0, "cotacao_dolar"] == 5.4321


def test_normalize_records_sorts_and_keeps_last_duplicate():
    from src.bcb import normalize_records

    result = normalize_records(
        [
            {"data": "20/10/2026", "valor": "5.1000"},
            {"data": "19/10/2026", "valor": "5.0000"},
            {"data": "20/10/2026", "valor": "5.2000"},
        ]
    )

    assert result["data"].dt.strftime("%Y-%m-%d").tolist() == [
        "2026-10-19",
        "2026-10-20",
    ]
    assert result["cotacao_dolar"].tolist() == [5.0, 5.2]


@pytest.mark.parametrize(
    "records",
    [
        [],
        [{"valor": "5.1000"}],
        [{"data": "20/10/2026"}],
        [{"data": "2026-10-20", "valor": "5.1000"}],
        [{"data": "20/10/2026", "valor": "texto"}],
        [{"data": "20/10/2026", "valor": "NaN"}],
        [{"data": "20/10/2026", "valor": "inf"}],
        [{"data": "20/10/2026", "valor": "0"}],
        [{"data": "20/10/2026", "valor": "-1.0"}],
    ],
)
def test_normalize_records_rejects_invalid_payload(records):
    from src.bcb import BCBDataError, normalize_records

    with pytest.raises(BCBDataError):
        normalize_records(records)


class FakeResponse:
    def __init__(self, payload=None, error=None):
        self.payload = payload
        self.error = error

    def raise_for_status(self):
        if self.error:
            raise self.error

    def json(self):
        return self.payload


def test_fetch_quotes_calls_series_endpoint_with_timeout():
    from src.bcb import BCB_URL, fetch_quotes

    calls = []

    def fake_get(url, *, params, timeout):
        calls.append((url, params, timeout))
        return FakeResponse([{"data": "20/10/2026", "valor": "5.4321"}])

    result = fetch_quotes(30, http_get=fake_get)

    assert calls == [
        (f"{BCB_URL}/ultimos/30", {"formato": "json"}, 15),
    ]
    assert result.loc[0, "cotacao_dolar"] == 5.4321


def test_fetch_quotes_wraps_http_error():
    from src.bcb import BCBDataError, fetch_quotes

    def fake_get(url, *, params, timeout):
        return FakeResponse(error=requests.HTTPError("503"))

    with pytest.raises(BCBDataError) as exc_info:
        fetch_quotes(90, http_get=fake_get)

    assert isinstance(exc_info.value.__cause__, requests.HTTPError)


def test_fetch_quotes_wraps_timeout():
    from src.bcb import BCBDataError, fetch_quotes

    def fake_get(url, *, params, timeout):
        raise requests.Timeout("tempo esgotado")

    with pytest.raises(BCBDataError) as exc_info:
        fetch_quotes(180, http_get=fake_get)

    assert isinstance(exc_info.value.__cause__, requests.Timeout)


def test_fetch_quotes_rejects_unsupported_limit_without_network():
    from src.bcb import BCBDataError, fetch_quotes

    def unexpected_get(url, *, params, timeout):
        raise AssertionError("a rede não deve ser chamada")

    with pytest.raises(BCBDataError):
        fetch_quotes(60, http_get=unexpected_get)


def test_load_demo_returns_canonical_frame(tmp_path):
    from src.bcb import load_demo

    csv_path = tmp_path / "demo.csv"
    csv_path.write_text(
        "data,cotacao_dolar\n"
        "2026-10-19 10:21:31.360703,5.2500\n"
        "2026-10-20 10:21:31.360703,5.3000\n",
        encoding="utf-8",
    )

    result = load_demo(csv_path)

    assert result.columns.tolist() == ["data", "cotacao_dolar"]
    assert str(result["data"].dtype) == "datetime64[ns]"
    assert result["data"].dt.hour.tolist() == [0, 0]
    assert result["cotacao_dolar"].tolist() == [5.25, 5.3]
