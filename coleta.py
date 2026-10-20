"""
Coleta automática da cotação do Dólar Comercial (venda)
Fonte: API oficial do Banco Central do Brasil (SGS - série 1)
Autor: Rhoney

Este script busca a série histórica de cotação do dólar direto na API
pública do BCB e salva em CSV, pronta para análise ou para alimentar
um dashboard.
"""

import requests
from datetime import datetime
from pathlib import Path

from src.bcb import fetch_quotes


def coletar_cotacao(dias=90):
    """
    Busca os últimos `dias` de cotação do dólar na API do BCB.
    Retorna um DataFrame com as colunas: data, valor.
    """
    return fetch_quotes(dias, http_get=requests.get)


def main():
    df = coletar_cotacao(dias=90)

    Path("data").mkdir(parents=True, exist_ok=True)
    nome_arquivo = f"data/cotacao_dolar_{datetime.now().strftime('%Y-%m-%d')}.csv"
    df.to_csv(nome_arquivo, index=False)

    print(f"Coletados {len(df)} registros.")
    print(f"Salvo em: {nome_arquivo}")
    print(f"\nÚltima cotação: R$ {df['cotacao_dolar'].iloc[-1]:.4f} em {df['data'].iloc[-1].strftime('%d/%m/%Y')}")


if __name__ == "__main__":
    main()
