"""Exportação reproduzível da série exibida."""

from __future__ import annotations

import pandas as pd


def to_csv_bytes(frame: pd.DataFrame) -> bytes:
    """Serializa a série por data em CSV UTF-8 sem coluna de índice."""
    ordered = frame.sort_values("data")[["data", "cotacao_dolar"]]
    content = ordered.to_csv(
        index=False,
        date_format="%Y-%m-%d",
        float_format="%.4f",
        lineterminator="\n",
    )
    return content.encode("utf-8")
