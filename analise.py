"""
Análise da série de cotação do dólar coletada por coleta.py
Autor: Rhoney
"""

import glob
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style="whitegrid")


def carregar_ultimo_csv():
    arquivos = sorted(glob.glob("data/cotacao_dolar_*.csv"))
    if not arquivos:
        raise FileNotFoundError(
            "Nenhum CSV encontrado. Rode 'python coleta.py' primeiro."
        )
    return pd.read_csv(arquivos[-1], parse_dates=["data"])


def gerar_grafico(df):
    plt.figure(figsize=(10, 5))
    sns.lineplot(data=df, x="data", y="cotacao_dolar", color="#2E86AB", linewidth=2)
    plt.title("Cotação do Dólar Comercial (venda) — últimos dias")
    plt.xlabel("Data")
    plt.ylabel("R$ por US$")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("images/cotacao_dolar.png", dpi=150)
    plt.close()


if __name__ == "__main__":
    df = carregar_ultimo_csv()

    print(f"Período: {df['data'].min().strftime('%d/%m/%Y')} a {df['data'].max().strftime('%d/%m/%Y')}")
    print(f"Cotação mínima: R$ {df['cotacao_dolar'].min():.4f}")
    print(f"Cotação máxima: R$ {df['cotacao_dolar'].max():.4f}")
    print(f"Cotação média:  R$ {df['cotacao_dolar'].mean():.4f}")

    gerar_grafico(df)
    print("\nGráfico salvo em images/cotacao_dolar.png")
