# Dashboard Público da Cotação do Dólar Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Entregar e publicar um dashboard Streamlit responsivo que consulta a série SGS nº 1, calcula indicadores confiáveis, permite exportação e identifica claramente qualquer dado demonstrativo.

**Architecture:** A camada `src/` concentra aquisição, normalização, métricas e exportação sem dependência de Streamlit. `app.py` compõe a interface e aplica cache, enquanto os scripts existentes passam a reutilizar o mesmo núcleo para evitar regras duplicadas.

**Tech Stack:** Python 3.10+, Streamlit, pandas, requests, Plotly, pytest, GitHub Actions e Streamlit Community Cloud.

**Spec:** `docs/superpowers/specs/2026-10-20-streamlit-dashboard-design.md`

## Global Constraints

- A fonte real é exclusivamente a API pública do Banco Central, série SGS nº 1.
- O DataFrame canônico contém somente `data: datetime64[ns]` e `cotacao_dolar: float64`.
- Dados demonstrativos nunca podem ser apresentados como atuais ou carregados silenciosamente.
- Períodos disponíveis: 30, 90, 180 e 365 registros.
- Cache da interface: uma hora.
- A aplicação não coleta dados pessoais, não usa credenciais e executa somente leituras públicas.
- Testes automatizados não dependem de rede.
- Os scripts `coleta.py` e `analise.py` devem manter as saídas documentadas.
- A interface e as mensagens são em português do Brasil.
- Nenhuma previsão ou recomendação financeira faz parte do escopo.

## Review Focus

- Payload com valor decimal usando vírgula deve produzir o mesmo `float` do formato com ponto; coberto na Task 1.
- Datas duplicadas e fora de ordem devem resultar em uma série ordenada com o último valor recebido por data; coberto na Task 1.
- `NaN`, infinito, zero e valores negativos devem ser rejeitados antes de qualquer indicador; coberto na Task 1.
- Série com um único registro deve apresentar indicadores válidos e variação indisponível; coberto na Task 2.
- Falha da API nunca deve ativar o fallback automaticamente; coberto na Task 3.

---

### Task 1: Cliente BCB e normalização canônica

**Files:**
- Create: `src/__init__.py`
- Create: `src/bcb.py`
- Create: `tests/test_bcb.py`
- Modify: `.gitignore`

**Interfaces:**
- Consumes: resposta JSON da série SGS nº 1 e `exemplo_cotacao_dolar.csv`.
- Produces: `normalize_records(records: list[dict[str, str]]) -> pd.DataFrame`, `fetch_quotes(limit: int, http_get: Callable = requests.get) -> pd.DataFrame`, `load_demo(path: str | Path = "exemplo_cotacao_dolar.csv") -> pd.DataFrame` e `BCBDataError`.

- [ ] **Step 1: Escrever testes RED do contrato válido**

Criar testes `test_normalize_records_returns_canonical_frame`, `test_normalize_records_accepts_comma_decimal` e `test_normalize_records_sorts_and_keeps_last_duplicate`, verificando colunas exatas, dtypes, índice sequencial e valores conhecidos.

- [ ] **Step 2: Executar os testes válidos e confirmar RED**

Run: `python -m pytest tests/test_bcb.py -k "canonical or comma or duplicate" -v`
Expected: FAIL por ausência de `src.bcb`.

- [ ] **Step 3: Implementar a normalização mínima**

Em `src/bcb.py`, criar `BCBDataError(ValueError)` e `normalize_records(records)` com conversão `DD/MM/AAAA`, vírgula decimal, ordenação e deduplicação que mantém o último registro recebido.

- [ ] **Step 4: Executar os testes válidos e confirmar GREEN**

Run: `python -m pytest tests/test_bcb.py -k "canonical or comma or duplicate" -v`
Expected: 3 passed.

- [ ] **Step 5: Escrever testes RED de dados inválidos**

Adicionar casos parametrizados para lista vazia, campos ausentes, data inválida, texto não numérico, `NaN`, infinito, zero e valor negativo. Todos devem gerar `BCBDataError`.

- [ ] **Step 6: Executar os testes inválidos e confirmar RED**

Run: `python -m pytest tests/test_bcb.py -k "rejects" -v`
Expected: FAIL nos casos ainda aceitos.

- [ ] **Step 7: Completar a validação mínima**

Validar existência dos campos, conversões, finitude e positividade sem corrigir silenciosamente registros inválidos.

- [ ] **Step 8: Executar a suíte de normalização**

Run: `python -m pytest tests/test_bcb.py -v`
Expected: todos os testes existentes de normalização passam.

- [ ] **Step 9: Escrever testes RED do cliente HTTP**

Criar `test_fetch_quotes_calls_series_endpoint_with_timeout`, `test_fetch_quotes_wraps_http_error` e `test_fetch_quotes_wraps_timeout`. Usar função HTTP injetada; não chamar a rede.

- [ ] **Step 10: Implementar o cliente HTTP**

Definir `BCB_URL = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.1/dados"`; `fetch_quotes` aceita apenas 30, 90, 180 ou 365, chama `{BCB_URL}/ultimos/{limit}` com `params={"formato": "json"}` e `timeout=15`, e converte falhas de requests em `BCBDataError` preservando a causa.

- [ ] **Step 11: Escrever e atender o teste do fallback explícito**

`test_load_demo_returns_canonical_frame` deve ler o CSV ilustrativo, remover horário da data e produzir o contrato canônico. Implementar `load_demo` sem conectá-lo automaticamente a `fetch_quotes`.

- [ ] **Step 12: Executar a Task 1**

Run: `python -m pytest tests/test_bcb.py -v`
Expected: 0 failed.

- [ ] **Step 13: Commit**

```bash
git add .gitignore src/__init__.py src/bcb.py tests/test_bcb.py
git commit -m "feat: add validated BCB data client"
```

### Task 2: Indicadores e exportação

**Files:**
- Create: `src/metrics.py`
- Create: `src/export.py`
- Create: `tests/test_metrics.py`
- Create: `tests/test_export.py`

**Interfaces:**
- Consumes: DataFrame canônico da Task 1.
- Produces: `QuoteMetrics`, `calculate_metrics(df: pd.DataFrame) -> QuoteMetrics` e `to_csv_bytes(df: pd.DataFrame) -> bytes`.

- [ ] **Step 1: Escrever testes RED dos indicadores**

Criar `test_calculate_metrics_for_known_series` com cotações `[5.0, 5.5, 6.0]` e afirmar último `6.0`, variação `20.0`, mínima `5.0`, máxima `6.0`, média `5.5` e amplitude `1.0`. Adicionar `test_calculate_metrics_sorts_by_date`.

- [ ] **Step 2: Confirmar RED**

Run: `python -m pytest tests/test_metrics.py -v`
Expected: FAIL por ausência de `src.metrics`.

- [ ] **Step 3: Implementar indicadores**

Criar `@dataclass(frozen=True) QuoteMetrics` com `latest`, `latest_date`, `change_percent: float | None`, `minimum`, `maximum`, `average` e `spread`. `calculate_metrics` ordena uma cópia e não muta a entrada.

- [ ] **Step 4: Testar casos-limite**

Adicionar `test_calculate_metrics_single_record_has_no_change` e `test_calculate_metrics_rejects_empty_frame`; implementar o mínimo para passar.

- [ ] **Step 5: Confirmar GREEN de métricas**

Run: `python -m pytest tests/test_metrics.py -v`
Expected: 0 failed.

- [ ] **Step 6: Escrever teste RED da exportação**

`test_to_csv_bytes_exports_iso_dates_without_index` deve verificar cabeçalho `data,cotacao_dolar`, data `2026-10-20`, decimal com ponto, ausência de coluna de índice e bytes UTF-8.

- [ ] **Step 7: Implementar exportação determinística**

Criar `to_csv_bytes` que ordena por data, formata datas como `%Y-%m-%d`, preserva quatro casas decimais e usa `index=False`.

- [ ] **Step 8: Confirmar GREEN da Task 2**

Run: `python -m pytest tests/test_metrics.py tests/test_export.py -v`
Expected: 0 failed.

- [ ] **Step 9: Commit**

```bash
git add src/metrics.py src/export.py tests/test_metrics.py tests/test_export.py
git commit -m "feat: add quote metrics and CSV export"
```

### Task 3: Dashboard Streamlit e estados explícitos

**Files:**
- Create: `app.py`
- Create: `.streamlit/config.toml`
- Create: `tests/test_app.py`
- Modify: `requirements.txt`
- Create: `requirements-dev.txt`

**Interfaces:**
- Consumes: `fetch_quotes`, `load_demo`, `calculate_metrics` e `to_csv_bytes`.
- Produces: aplicação Streamlit pública com filtros, indicadores, gráfico, tabela, download e fallback acionado somente pelo usuário.

- [ ] **Step 1: Escrever teste RED da aplicação real**

Com `streamlit.testing.v1.AppTest`, criar `test_app_renders_real_data_without_demo_banner`: substituir `fetch_quotes` por dados conhecidos, executar o app, verificar título, fonte BCB, indicadores e ausência de “Dados demonstrativos”.

- [ ] **Step 2: Confirmar RED**

Run: `python -m pytest tests/test_app.py::test_app_renders_real_data_without_demo_banner -v`
Expected: FAIL por ausência de `app.py`.

- [ ] **Step 3: Implementar o esqueleto funcional**

Em `app.py`, configurar a página, seletor de período, função `@st.cache_data(ttl=3600)` para consulta, indicadores e fonte. Usar `plotly.graph_objects.Figure` com uma linha principal e tooltip em pt-BR.

- [ ] **Step 4: Confirmar GREEN inicial**

Run: `python -m pytest tests/test_app.py::test_app_renders_real_data_without_demo_banner -v`
Expected: PASS.

- [ ] **Step 5: Escrever teste RED da falha sem fallback automático**

`test_api_error_offers_demo_without_loading_it` deve fazer `fetch_quotes` lançar `BCBDataError`, verificar mensagem de indisponibilidade e botão “Visualizar dados demonstrativos”, e confirmar ausência de métricas/gráfico demonstrativos antes do clique.

- [ ] **Step 6: Implementar o estado de erro**

Capturar somente `BCBDataError`, mostrar orientação para atualizar/tentar novamente e oferecer o botão de fallback. Não exibir stack trace nem payload bruto.

- [ ] **Step 7: Escrever teste RED do fallback acionado**

`test_demo_button_loads_demo_with_persistent_banner` deve clicar no botão, verificar a faixa “Dados demonstrativos” e confirmar que os indicadores usam o DataFrame demonstrativo.

- [ ] **Step 8: Implementar o fallback explícito**

Guardar a escolha em `st.session_state`, carregar `load_demo()` somente após o clique e manter a faixa visível em todas as reruns enquanto o fallback estiver ativo.

- [ ] **Step 9: Escrever e atender testes dos controles**

Adicionar testes para cada opção 30/90/180/365, botão “Atualizar dados” limpando o cache, tabela expansível e download com o mesmo período exibido.

- [ ] **Step 10: Aplicar a direção visual**

Configurar cores base em `.streamlit/config.toml` e CSS mínimo no app para largura, números tabulares, foco visível, indicadores responsivos e faixa demonstrativa. Respeitar a paleta e evitar animações e decoração sem função.

- [ ] **Step 11: Confirmar GREEN da Task 3**

Run: `python -m pytest tests/test_app.py -v`
Expected: 0 failed e nenhum acesso real à rede.

- [ ] **Step 12: Smoke test de importação**

Run: `python -c "import app"`
Expected: exit 0 sem traceback.

- [ ] **Step 13: Commit**

```bash
git add app.py .streamlit/config.toml requirements.txt requirements-dev.txt tests/test_app.py
git commit -m "feat: add interactive Streamlit dashboard"
```

### Task 4: Reutilizar o núcleo nos scripts existentes

**Files:**
- Modify: `coleta.py`
- Modify: `analise.py`
- Create: `tests/test_legacy_scripts.py`

**Interfaces:**
- Consumes: interfaces das Tasks 1 e 2.
- Produces: scripts legados com as mesmas saídas públicas, sem duplicar aquisição ou cálculo.

- [ ] **Step 1: Caracterizar o comportamento atual em testes RED**

Criar testes que fixam: `coleta.coletar_cotacao(dias=90)` retorna o contrato canônico; o CLI grava `data/cotacao_dolar_AAAA-MM-DD.csv`; `analise.carregar_ultimo_csv()` seleciona o nome mais recente; `gerar_grafico(df)` grava `images/cotacao_dolar.png`.

- [ ] **Step 2: Executar e registrar a linha de base**

Run: `python -m pytest tests/test_legacy_scripts.py -v`
Expected: os testes de caracterização compatíveis passam; qualquer lacuna de injeção necessária falha de forma identificada antes da refatoração.

- [ ] **Step 3: Refatorar `coleta.py` minimamente**

Delegar coleta a `fetch_quotes`, manter o nome `coletar_cotacao`, criar `data/` com `mkdir(parents=True, exist_ok=True)` no CLI e preservar textos e padrão de arquivo.

- [ ] **Step 4: Refatorar `analise.py` minimamente**

Usar `calculate_metrics` para o resumo, manter `carregar_ultimo_csv` e `gerar_grafico`, criar `images/` antes do save e preservar o PNG estático para compatibilidade.

- [ ] **Step 5: Confirmar compatibilidade**

Run: `python -m pytest tests/test_legacy_scripts.py -v`
Expected: 0 failed.

- [ ] **Step 6: Rodar toda a suíte**

Run: `python -m pytest -v`
Expected: 0 failed.

- [ ] **Step 7: Commit**

```bash
git add coleta.py analise.py tests/test_legacy_scripts.py
git commit -m "refactor: share dashboard data core with scripts"
```

### Task 5: CI e documentação de portfólio

**Files:**
- Create: `.github/workflows/tests.yml`
- Modify: `README.md`

**Interfaces:**
- Consumes: comandos e artefatos das Tasks 1–4.
- Produces: verificação automática em push/PR e documentação reproduzível.

- [ ] **Step 1: Criar workflow de testes**

Configurar GitHub Actions para Python 3.10 e 3.12, instalar `requirements.txt` e `requirements-dev.txt`, e executar `python -m pytest -v`. Usar apenas ações oficiais com versões principais fixadas.

- [ ] **Step 2: Validar estruturalmente o workflow**

Run: `python -c "import yaml; yaml.safe_load(open('.github/workflows/tests.yml', encoding='utf-8'))"`
Expected: exit 0. Adicionar `PyYAML` somente às dependências de desenvolvimento se o validador for mantido como teste do projeto.

- [ ] **Step 3: Atualizar o README**

Documentar link reservado para a aplicação, screenshot a ser capturado após o deploy, arquitetura, indicadores, fallback, execução `streamlit run app.py`, testes, scripts legados, fonte oficial e limitações. Não preencher uma URL pública antes de ela existir.

- [ ] **Step 4: Verificar comandos documentados**

Run: `python -m pytest -v`
Expected: 0 failed.

Run: `python -m streamlit run app.py --server.headless true --server.port 8501`
Expected: servidor inicia sem traceback; encerrar após o health check local.

- [ ] **Step 5: Commit**

```bash
git add .github/workflows/tests.yml README.md
git commit -m "ci: test dashboard and document usage"
```

### Task 6: Revisão, integração e publicação

**Files:**
- Modify: `README.md` após a URL existir.
- Create: screenshot original do dashboard em `docs/assets/dashboard.png`.

**Interfaces:**
- Consumes: branch integral testada e conta Streamlit do proprietário.
- Produces: PR revisado, aplicação pública validada e link no README/perfil.

- [ ] **Step 1: Verificação local final**

Run: `python -m pytest -v`
Expected: 0 failed.

Run: `python -c "from src.bcb import fetch_quotes; df=fetch_quotes(30); print(len(df), df.columns.tolist())"`
Expected: `30 ['data', 'cotacao_dolar']` com uma única chamada real controlada ao BCB.

- [ ] **Step 2: Revisão visual local**

Abrir o Streamlit e verificar desktop e viewport móvel: legibilidade, quebra dos indicadores, foco por teclado, gráfico, tabela, download, erro da API e fallback. Salvar screenshot original em `docs/assets/dashboard.png`.

- [ ] **Step 3: Revisão do diff e segurança**

Confirmar que não há segredos, tokens, dados pessoais, writes externos, payloads brutos em mensagens ou alterações fora do escopo.

- [ ] **Step 4: Abrir pull request**

Criar PR de `codex/streamlit-dashboard` para `main` com resumo, evidências dos testes, screenshot e checklist dos critérios de aceite. Aguardar GitHub Actions verde antes da integração.

- [ ] **Step 5: Integrar após revisão**

Mesclar somente com testes verdes e revisão aprovada. Não forçar merge sobre falhas.

- [ ] **Step 6: Publicar no Streamlit Community Cloud**

Com confirmação de ação externa, autenticar o proprietário, selecionar `rhoneycruz-ui/cotacao-dolar-bcb`, branch `main`, arquivo `app.py` e escolher subdomínio relacionado a `cotacao-dolar-bcb`.

- [ ] **Step 7: Verificar a aplicação pública**

Abrir a URL em sessão anônima, confirmar dados reais, os quatro períodos, indicadores, gráfico, tabela, download, layout móvel e ausência de erros nos logs.

- [ ] **Step 8: Registrar URL e screenshot**

Atualizar o README com a URL real e o screenshot, executar novamente a suíte completa e criar commit `docs: add live dashboard link and screenshot`.

- [ ] **Step 9: Atualizar o portfólio**

Adicionar o link da demonstração ao README do perfil `rhoneycruz-ui/rhoneycruz-ui` e, com confirmação separada, usar a URL como Website do repositório.

- [ ] **Step 10: Relatório final**

Registrar arquivos alterados, testes focados/completos, chamada real ao BCB, writes externos de publicação, riscos e ausência de alterações no Production Core do Projeto Ville.
