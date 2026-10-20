# Dashboard Público da Cotação do Dólar — Design

**Data:** 2026-10-20
**Status:** aprovado para implementação
**Repositório:** `rhoneycruz-ui/cotacao-dolar-bcb`
**Branch:** `codex/streamlit-dashboard`

## 1. Objetivo

Transformar o pipeline Python existente em uma aplicação web pública que demonstre competências de integração com API, tratamento de dados, análise e apresentação visual.

O público principal são recrutadores, avaliadores técnicos e visitantes do portfólio. A aplicação deve abrir sem configuração local, explicar a origem dos dados e continuar compreensível quando a API do Banco Central estiver indisponível.

## 2. Escopo

A primeira versão inclui:

- consulta da série SGS nº 1, dólar comercial de venda;
- seleção de 30, 90, 180 ou 365 registros;
- cotação mais recente e data de referência;
- variação entre o primeiro e o último registro do período;
- mínima, máxima e média;
- gráfico temporal interativo;
- tabela dos registros;
- download em CSV;
- cache temporário da consulta;
- fallback explícito para o arquivo demonstrativo versionado;
- mensagens de erro orientadas à recuperação;
- layout responsivo;
- testes automatizados das regras independentes da interface;
- configuração compatível com Streamlit Community Cloud.

Ficam fora desta versão:

- autenticação;
- banco de dados;
- moedas além do dólar comercial;
- previsão de cotação;
- alertas;
- recomendações financeiras;
- tarefas agendadas e armazenamento histórico externo.

## 3. Alternativas consideradas

### 3.1 Streamlit modular de página única — selecionada

Oferece um link público, implantação simples e bom equilíbrio entre código de dados e experiência visual. A lógica ficará separada da camada Streamlit para permitir testes diretos.

### 3.2 Streamlit com múltiplas páginas

Permitiria seções adicionais, mas fragmentaria uma experiência pequena e adicionaria navegação sem ganho real nesta versão.

### 3.3 React com API FastAPI

Demonstraria uma arquitetura mais ampla, porém exigiria dois serviços, CORS, duas implantações e maior manutenção. Não é necessário para cumprir o objetivo de portfólio atual.

## 4. Arquitetura

```text
Banco Central (SGS série 1)
          |
          v
src/bcb.py — requisição, validação e normalização
          |
          v
DataFrame canônico: data + cotacao_dolar
          |
          +---------------------+
          |                     |
          v                     v
src/metrics.py             src/export.py
indicadores                CSV em memória
          |                     |
          +----------+----------+
                     |
                     v
                  app.py
       interface, filtros e estados
```

Arquivos planejados:

- `app.py`: composição da página e interação do usuário;
- `src/bcb.py`: cliente da API, validação do payload e carregamento demonstrativo;
- `src/metrics.py`: cálculo dos indicadores;
- `src/export.py`: serialização determinística para CSV;
- `src/__init__.py`: pacote da aplicação;
- `tests/test_bcb.py`: normalização, validação e falhas da API;
- `tests/test_metrics.py`: indicadores e casos-limite;
- `tests/test_export.py`: CSV e formatação;
- `.streamlit/config.toml`: tema e configuração;
- `requirements.txt`: dependências de execução com restrições de versão;
- `requirements-dev.txt`: pytest e ferramentas exclusivas de desenvolvimento;
- `README.md`: uso local, testes, arquitetura, demonstração e link publicado.

Os scripts `coleta.py` e `analise.py` permanecem disponíveis e passam a reutilizar as funções do pacote quando isso puder ser feito sem mudar suas saídas documentadas.

## 5. Contrato de dados

O DataFrame interno sempre terá:

| Coluna | Tipo | Regra |
|---|---|---|
| `data` | `datetime64[ns]` | válida, sem horário relevante |
| `cotacao_dolar` | `float64` | finita e positiva |

A normalização deve:

1. rejeitar resposta vazia;
2. exigir os campos `data` e `valor`;
3. converter datas no formato `DD/MM/AAAA`;
4. aceitar vírgula ou ponto como separador decimal;
5. rejeitar valores ausentes, não numéricos, infinitos ou não positivos;
6. ordenar por data;
7. eliminar datas duplicadas mantendo o último valor recebido;
8. devolver índice sequencial.

O dashboard nunca apresentará dados demonstrativos como se fossem atuais.

## 6. Aquisição e cache

A URL continuará sendo a API oficial do Banco Central para a série 1. O número de registros será limitado às opções disponíveis na interface.

A camada HTTP terá:

- timeout explícito;
- `raise_for_status()`;
- mensagem de domínio sem expor detalhes internos ao visitante;
- injeção da função HTTP nos testes;
- nenhuma credencial ou segredo.

A interface aplicará cache de dados por uma hora. Um botão de atualização permitirá limpar o cache e solicitar nova leitura.

Se a API falhar, a aplicação mostrará:

1. aviso de indisponibilidade da fonte;
2. orientação para tentar novamente;
3. botão para abrir o conjunto demonstrativo;
4. identificação persistente “Dados demonstrativos” enquanto o fallback estiver ativo.

O fallback nunca será automático ou silencioso.

## 7. Indicadores

Para o período selecionado:

- **Última cotação:** último valor por data;
- **Variação:** `(último / primeiro - 1) × 100`;
- **Mínima:** menor cotação;
- **Máxima:** maior cotação;
- **Média:** média aritmética;
- **Amplitude:** máxima menos mínima.

Com um único registro, a variação será exibida como indisponível. Um conjunto vazio será rejeitado antes do cálculo.

## 8. Experiência e direção visual

A página terá uma única coluna estrutural com largura controlada e três zonas:

```text
┌──────────────────────────────────────────────┐
│ Cotação do dólar          Fonte e atualização│
│ R$ 0,0000                  DD/MM/AAAA         │
├──────────────────────────────────────────────┤
│ Período [30 | 90 | 180 | 365]  Atualizar     │
├──────────────────────────────────────────────┤
│ variação   mínima   máxima   média   amplitude│
├──────────────────────────────────────────────┤
│                                              │
│            gráfico temporal                  │
│                                              │
├──────────────────────────────────────────────┤
│ detalhes dos dados + download CSV            │
└──────────────────────────────────────────────┘
```

Direção visual:

- fundo “papel financeiro” `#F5F7F4`;
- texto principal `#14231C`;
- azul institucional `#174A6E`;
- verde positivo `#24734A`;
- vermelho negativo `#A33A3A`;
- linhas e áreas neutras `#D7DED9`;
- tipografia sans-serif legível, usando a pilha do sistema para evitar dependência externa;
- valores monetários com números tabulares;
- cor de variação usada apenas quando carrega significado;
- sem gradientes decorativos, excesso de cartões ou animações automáticas.

O elemento memorável será o traçado do câmbio ocupando a maior área útil, com a cotação atual alinhada visualmente ao último ponto.

A interface usará português do Brasil, foco visível por teclado e contraste suficiente. Em telas pequenas, indicadores quebram em duas colunas e o gráfico preserva rolagem/legibilidade.

## 9. Estados da interface

A aplicação terá estados explícitos:

- **carregando:** indicador durante a consulta;
- **dados reais:** fonte, data e link do BCB visíveis;
- **erro da fonte:** causa resumida e ações possíveis;
- **dados demonstrativos:** faixa persistente de identificação;
- **sem dados válidos:** bloqueio dos indicadores e explicação;
- **download pronto:** arquivo correspondente exatamente ao período exibido.

Mensagens não incluirão stack traces, tokens ou conteúdo bruto inesperado da API.

## 10. Testes

O desenvolvimento seguirá TDD.

Testes de `bcb.py`:

- payload válido;
- separador decimal com vírgula;
- ordenação;
- duplicidade de datas;
- payload vazio;
- campo ausente;
- data inválida;
- valor não numérico, infinito, zero ou negativo;
- erro HTTP e timeout;
- leitura do fallback.

Testes de `metrics.py`:

- valores conhecidos;
- série não ordenada;
- registro único;
- conjunto vazio.

Testes de `export.py`:

- cabeçalho e ordem;
- datas em formato ISO;
- decimal estável;
- ausência de índice acidental.

Verificação final:

1. suíte focada;
2. suíte completa;
3. importação do `app.py`;
4. execução local do Streamlit;
5. inspeção visual em desktop e viewport móvel;
6. validação da implantação pública;
7. leitura do link publicado em sessão anônima.

Chamadas reais ao BCB serão usadas somente em verificação manual controlada. Testes automatizados não dependerão da rede.

## 11. Dependências e implantação

O entrypoint `app.py` e o `requirements.txt` ficarão na raiz, formato reconhecido pelo Streamlit Community Cloud.

Dependências previstas:

- Streamlit;
- pandas;
- requests;
- Plotly;
- pytest apenas no arquivo de desenvolvimento.

As versões serão restringidas para evitar atualizações incompatíveis inesperadas. A implantação usará o repositório público e a branch principal depois da integração aprovada.

O primeiro vínculo com o Streamlit Community Cloud pode exigir autenticação e autorização do proprietário do GitHub. Essa etapa será feita com confirmação do usuário no momento da ação.

## 12. Segurança, privacidade e integridade

- nenhuma chave de API é necessária;
- nenhum dado pessoal é coletado;
- nenhum segredo será salvo no repositório;
- a aplicação fará somente leituras públicas;
- nenhum write será feito no Banco Central ou em sistemas externos;
- os dados demonstrativos permanecerão claramente separados dos dados reais;
- o README manterá o aviso de uso informativo.

## 13. Critérios de aceite

A versão estará pronta quando:

1. abrir por URL pública sem instalação local;
2. consultar e mostrar dados reais do BCB;
3. permitir os quatro períodos definidos;
4. calcular corretamente todos os indicadores;
5. permitir download do período mostrado;
6. identificar de forma inequívoca dados demonstrativos;
7. orientar o visitante quando a API falhar;
8. funcionar em desktop e celular;
9. não conter segredos;
10. passar por todos os testes automatizados;
11. ter README com instruções locais, testes e link público;
12. preservar os scripts existentes ou documentar qualquer mudança necessária.
