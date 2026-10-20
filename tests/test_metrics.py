import pandas as pd
import pytest


def quote_frame(values, dates=None):
    if dates is None:
        dates = pd.date_range("2026-10-18", periods=len(values), freq="D")
    return pd.DataFrame({"data": dates, "cotacao_dolar": values})


def test_calculate_metrics_for_known_series():
    from src.metrics import calculate_metrics

    result = calculate_metrics(quote_frame([5.0, 5.5, 6.0]))

    assert result.latest == 6.0
    assert result.latest_date == pd.Timestamp("2026-10-20")
    assert result.change_percent == pytest.approx(20.0)
    assert result.minimum == 5.0
    assert result.maximum == 6.0
    assert result.average == 5.5
    assert result.spread == 1.0


def test_calculate_metrics_sorts_by_date_without_mutating_input():
    from src.metrics import calculate_metrics

    frame = quote_frame(
        [6.0, 5.0, 5.5],
        pd.to_datetime(["2026-10-20", "2026-10-18", "2026-10-19"]),
    )
    original = frame.copy(deep=True)

    result = calculate_metrics(frame)

    assert result.latest == 6.0
    assert result.change_percent == pytest.approx(20.0)
    pd.testing.assert_frame_equal(frame, original)


def test_calculate_metrics_single_record_has_no_change():
    from src.metrics import calculate_metrics

    result = calculate_metrics(quote_frame([5.25]))

    assert result.latest == 5.25
    assert result.minimum == 5.25
    assert result.maximum == 5.25
    assert result.average == 5.25
    assert result.spread == 0.0
    assert result.change_percent is None


def test_calculate_metrics_rejects_empty_frame():
    from src.metrics import calculate_metrics

    with pytest.raises(ValueError, match="vazia"):
        calculate_metrics(quote_frame([]))
