"""Aquisição e normalização da série SGS nº 1 do Banco Central."""

from __future__ import annotations

import math
from collections.abc import Callable
from pathlib import Path

import pandas as pd
import requests


BCB_URL = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.1/dados"
VALID_LIMITS = frozenset({30, 90, 180, 365})


class BCBDataError(ValueError):
    """Indica que a fonte não pôde produzir uma série válida."""


def normalize_records(records: list[dict[str, str]]) -> pd.DataFrame:
    """Converte registros SGS para o contrato canônico do projeto."""
    if not records:
        raise BCBDataError("A fonte não retornou registros.")

    frame = pd.DataFrame(records)
    if not {"data", "valor"}.issubset(frame.columns):
        raise BCBDataError("A resposta não contém data e valor.")

    try:
        frame["data"] = pd.to_datetime(
            frame["data"], format="%d/%m/%Y"
        ).astype("datetime64[ns]")
        frame["cotacao_dolar"] = (
            frame["valor"].astype(str).str.replace(",", ".", regex=False).astype(float)
        )
    except (TypeError, ValueError) as exc:
        raise BCBDataError("A resposta contém data ou valor inválido.") from exc

    valid_values = frame["cotacao_dolar"].map(math.isfinite) & (
        frame["cotacao_dolar"] > 0
    )
    if not valid_values.all():
        raise BCBDataError("A resposta contém cotação inválida.")

    return (
        frame[["data", "cotacao_dolar"]]
        .drop_duplicates(subset="data", keep="last")
        .sort_values("data")
        .reset_index(drop=True)
    )


def fetch_quotes(
    limit: int,
    http_get: Callable[..., requests.Response] = requests.get,
) -> pd.DataFrame:
    """Busca e normaliza as últimas cotações publicadas pelo BCB."""
    if limit not in VALID_LIMITS:
        raise BCBDataError("Período de consulta não suportado.")

    try:
        response = http_get(
            f"{BCB_URL}/ultimos/{limit}",
            params={"formato": "json"},
            timeout=15,
        )
        response.raise_for_status()
        records = response.json()
    except requests.RequestException as exc:
        raise BCBDataError("Não foi possível consultar o Banco Central.") from exc

    return normalize_records(records)


def load_demo(
    path: str | Path = "exemplo_cotacao_dolar.csv",
) -> pd.DataFrame:
    """Carrega o conjunto demonstrativo sem tratá-lo como dado atual."""
    try:
        frame = pd.read_csv(path)
        if frame.empty or set(frame.columns) != {"data", "cotacao_dolar"}:
            raise BCBDataError("O arquivo demonstrativo não possui o formato esperado.")
        frame["data"] = (
            pd.to_datetime(frame["data"]).dt.normalize().astype("datetime64[ns]")
        )
        frame["cotacao_dolar"] = frame["cotacao_dolar"].astype(float)
    except BCBDataError:
        raise
    except (OSError, TypeError, ValueError) as exc:
        raise BCBDataError("Não foi possível carregar os dados demonstrativos.") from exc

    valid_values = frame["cotacao_dolar"].map(math.isfinite) & (
        frame["cotacao_dolar"] > 0
    )
    if not valid_values.all():
        raise BCBDataError("O arquivo demonstrativo contém cotação inválida.")

    return (
        frame[["data", "cotacao_dolar"]]
        .drop_duplicates(subset="data", keep="last")
        .sort_values("data")
        .reset_index(drop=True)
    )
