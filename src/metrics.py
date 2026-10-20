"""Indicadores derivados da série canônica de câmbio."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class QuoteMetrics:
    latest: float
    latest_date: pd.Timestamp
    change_percent: float | None
    minimum: float
    maximum: float
    average: float
    spread: float


def calculate_metrics(frame: pd.DataFrame) -> QuoteMetrics:
    """Calcula indicadores sem alterar o DataFrame recebido."""
    if frame.empty:
        raise ValueError("A série de cotações está vazia.")

    ordered = frame.sort_values("data").reset_index(drop=True)
    values = ordered["cotacao_dolar"]
    first = float(values.iloc[0])
    latest = float(values.iloc[-1])
    minimum = float(values.min())
    maximum = float(values.max())
    return QuoteMetrics(
        latest=latest,
        latest_date=pd.Timestamp(ordered["data"].iloc[-1]),
        change_percent=(latest / first - 1) * 100 if len(ordered) > 1 else None,
        minimum=minimum,
        maximum=maximum,
        average=float(values.mean()),
        spread=maximum - minimum,
    )
