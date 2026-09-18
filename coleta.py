"""
Coleta automática da cotação do Dólar Comercial (venda)
Fonte: API oficial do Banco Central do Brasil (SGS - série 1)
Autor: Rhoney

Este script busca a série histórica de cotação do dólar direto na API
pública do BCB e salva em CSV, pronta para análise ou para alimentar
um dashboard.
"""

import requests
import pandas as pd
from datetime import datetime

# Série 1 do SGS/BCB = Dólar comercial venda (diário)
URL = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.1/dados"


def coletar_cotacao(dias=90):
    """
    Busca os últimos `dias` de cotação do dólar na API do BCB.
    Retorna um DataFrame com as colunas: data, valor.
    """
    params = {"formato": "json"}
    resposta = requests.get(f"{URL}/ultimos/{dias}", params=params, timeout=15)
    resposta.raise_for_status()

    dados = resposta.json()
    df = pd.DataFrame(dados)
    df["data"] = pd.to_datetime(df["data"], format="%d/%m/%Y")
    df["valor"] = df["valor"].astype(float)
    df = df.rename(columns={"valor": "cotacao_dolar"})

    return df.sort_values("data").reset_index(drop=True)


if __name__ == "__main__":
    df = coletar_cotacao(dias=90)

    nome_arquivo = f"data/cotacao_dolar_{datetime.now().strftime('%Y-%m-%d')}.csv"
    df.to_csv(nome_arquivo, index=False)

    print(f"Coletados {len(df)} registros.")
    print(f"Salvo em: {nome_arquivo}")
    print(f"\nÚltima cotação: R$ {df['cotacao_dolar'].iloc[-1]:.4f} em {df['data'].iloc[-1].strftime('%d/%m/%Y')}")
