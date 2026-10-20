import pandas as pd


def test_to_csv_bytes_exports_iso_dates_without_index():
    from src.export import to_csv_bytes

    frame = pd.DataFrame(
        {
            "data": pd.to_datetime(["2026-10-20", "2026-10-19"]),
            "cotacao_dolar": [5.3, 5.25],
        }
    )

    result = to_csv_bytes(frame)

    assert isinstance(result, bytes)
    assert result.decode("utf-8") == (
        "data,cotacao_dolar\n"
        "2026-10-19,5.2500\n"
        "2026-10-20,5.3000\n"
    )
