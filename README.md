# Coleta Automática de Cotação do Dólar (API do Banco Central)

Automação em Python que coleta a série histórica de cotação do dólar comercial direto na **API pública e oficial do Banco Central do Brasil (SGS)**, salva os dados em CSV e gera um gráfico de evolução.

> **Nota:** o gráfico e o CSV de exemplo neste repositório (`data/exemplo_cotacao_dolar.csv`) usam **dados ilustrativos**, gerados só para demonstrar o resultado — não são cotações reais. Ao rodar `coleta.py` na sua máquina, os dados reais são baixados da API do BCB.

## O que o projeto faz

1. `coleta.py` — conecta na API do BCB (série 1 do SGS = dólar comercial venda), baixa os últimos N dias de cotação e salva em `data/cotacao_dolar_AAAA-MM-DD.csv`
2. `analise.py` — lê o CSV mais recente, calcula estatísticas básicas (mínima, máxima, média) e gera um gráfico de evolução em `images/cotacao_dolar.png`

## Exemplo do resultado

![cotação exemplo](images/cotacao_dolar.png)

## Como rodar

```bash
pip install requests pandas matplotlib seaborn

python coleta.py    # baixa os dados reais mais recentes
python analise.py   # gera as estatísticas e o gráfico
```

## Automatizando a coleta (rodar sozinho todo dia)

Para não precisar rodar manualmente, dá pra agendar o `coleta.py`:

- **Windows:** use o Agendador de Tarefas (Task Scheduler) para rodar `python coleta.py` no horário desejado
- **Linux/Mac:** use um `cron job`

## Tecnologias usadas

- Python
- `requests` (consumo de API)
- pandas (tratamento dos dados)
- matplotlib / seaborn (visualização)

## Fonte dos dados

[API de Dados Abertos do Banco Central do Brasil — SGS](https://dadosabertos.bcb.gov.br/dataset/1-taxa-de-cambio-livre-dolar-americano-venda-diario) (série 1, dólar comercial venda)
