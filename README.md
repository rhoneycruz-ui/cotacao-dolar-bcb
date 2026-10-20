# Cotação do Dólar — API do Banco Central

Pipeline em Python que coleta a cotação de venda do dólar comercial na API pública do Banco Central do Brasil, armazena os dados em CSV e gera estatísticas e visualizações.

## Fluxo

1. `coleta.py` consulta os últimos 90 registros da série SGS nº 1.
2. As datas e os valores são normalizados com pandas.
3. O resultado é salvo em `data/cotacao_dolar_AAAA-MM-DD.csv`.
4. `analise.py` seleciona o CSV mais recente, calcula mínima, máxima e média e gera um gráfico em `images/cotacao_dolar.png`.

## Exemplo visual

![Exemplo de gráfico da cotação do dólar](cotacao_dolar.png)

> O gráfico acima e o arquivo [`exemplo_cotacao_dolar.csv`](exemplo_cotacao_dolar.csv) contêm dados ilustrativos usados somente para demonstrar o formato de saída. Eles não devem ser tratados como cotações oficiais ou atuais.

## Como executar

Requer Python 3.10 ou mais recente e acesso à internet para a etapa de coleta.

```bash
python -m venv .venv
```

No Windows:

```powershell
.venv\Scripts\python -m pip install -r requirements.txt
New-Item -ItemType Directory -Force data, images
.venv\Scripts\python coleta.py
.venv\Scripts\python analise.py
```

No Linux ou macOS:

```bash
.venv/bin/python -m pip install -r requirements.txt
mkdir -p data images
.venv/bin/python coleta.py
.venv/bin/python analise.py
```

## Saídas

- `data/cotacao_dolar_AAAA-MM-DD.csv`: dados reais retornados pela API durante a execução.
- `images/cotacao_dolar.png`: gráfico produzido a partir do CSV mais recente.
- terminal: período analisado, cotação mínima, máxima, média e último valor coletado.

## Automação

O comando de coleta pode ser agendado no Agendador de Tarefas do Windows ou em um `cron job` no Linux e macOS. Em uma automação real, registre falhas de rede e só execute a análise depois de confirmar que o CSV foi gravado.

## Tecnologias

- Python
- requests
- pandas
- matplotlib
- seaborn
- API REST do Banco Central do Brasil

## Fonte e limitações

A fonte consultada é a [API de Dados Abertos do Banco Central do Brasil — série 1](https://dadosabertos.bcb.gov.br/dataset/1-taxa-de-cambio-livre-dolar-americano-venda-diario).

O projeto depende da disponibilidade da API e não implementa persistência em banco de dados, retentativas automáticas, monitoramento ou alertas. Os dados coletados devem ser validados antes de qualquer uso financeiro.
