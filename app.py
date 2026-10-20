"""Dashboard público da cotação de venda do dólar comercial."""

from __future__ import annotations

import plotly.graph_objects as go
import streamlit as st

from src import bcb
from src.export import to_csv_bytes
from src.metrics import QuoteMetrics, calculate_metrics


st.set_page_config(
    page_title="Dólar comercial | Banco Central",
    page_icon="💱",
    layout="wide",
)

st.markdown(
    """
    <style>
    .stApp { color: #14231C; }
    .block-container { max-width: 1120px; padding-top: 3rem; padding-bottom: 4rem; }
    h1 { letter-spacing: -0.04em; font-weight: 680; }
    .stApp p.quote {
        color: #174A6E;
        font-size: clamp(3rem, 5vw, 4.5rem) !important;
        font-weight: 720;
        letter-spacing: -0.07em;
        line-height: .95;
        margin: 2rem 0 .25rem;
        font-variant-numeric: tabular-nums;
    }
    [data-testid="stMetric"] {
        border-top: 2px solid #D7DED9;
        padding-top: .9rem;
        font-variant-numeric: tabular-nums;
    }
    [data-testid="stMetricLabel"] { color: #40534A; }
    [data-testid="stMetricValue"] {
        font-size: clamp(1.2rem, 2vw, 1.55rem);
        line-height: 1.15;
    }
    button:focus-visible, [role="button"]:focus-visible, select:focus-visible {
        outline: 3px solid #174A6E !important;
        outline-offset: 3px;
    }
    @media (max-width: 640px) {
        .block-container { padding-top: 1.5rem; }
        .quote { margin-top: 1.4rem; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data(ttl=3600, show_spinner=False)
def load_live_data(limit: int):
    """Consulta dados reais com cache de uma hora."""
    return bcb.fetch_quotes(limit)


def format_brl(value: float) -> str:
    return f"R$ {value:.4f}".replace(".", ",")


def format_percent(value: float | None) -> str:
    if value is None:
        return "Indisponível"
    return f"{value:+.2f}%".replace(".", ",")


def build_chart(frame) -> go.Figure:
    figure = go.Figure(
        go.Scatter(
            x=frame["data"],
            y=frame["cotacao_dolar"],
            mode="lines",
            line={"color": "#174A6E", "width": 3},
            fill="tozeroy",
            fillcolor="rgba(23, 74, 110, 0.08)",
            hovertemplate="%{x|%d/%m/%Y}<br>R$ %{y:.4f}<extra></extra>",
        )
    )
    figure.update_layout(
        margin={"l": 8, "r": 8, "t": 20, "b": 8},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        hovermode="x unified",
        xaxis={"title": None, "showgrid": False},
        yaxis={"title": "R$ por US$", "gridcolor": "#D7DED9"},
        showlegend=False,
    )
    return figure


def render_metrics(metrics: QuoteMetrics) -> None:
    columns = st.columns(5)
    values = [
        ("Variação", format_percent(metrics.change_percent)),
        ("Mínima", format_brl(metrics.minimum)),
        ("Máxima", format_brl(metrics.maximum)),
        ("Média", format_brl(metrics.average)),
        ("Amplitude", format_brl(metrics.spread)),
    ]
    for column, (label, value) in zip(columns, values, strict=True):
        column.metric(label, value)


st.title("Dólar comercial")
st.caption("Dados oficiais da série SGS nº 1 — Banco Central do Brasil")

control_col, refresh_col = st.columns([4, 1])
period = control_col.selectbox(
    "Período analisado",
    options=[30, 90, 180, 365],
    index=1,
    format_func=lambda value: f"Últimos {value} registros",
)
if refresh_col.button("Atualizar dados", width="stretch"):
    load_live_data.clear()
    st.session_state["use_demo"] = False
    st.rerun()

demo_mode = bool(st.session_state.get("use_demo", False))
if demo_mode:
    data = bcb.load_demo()
    st.warning(
        "Dados demonstrativos — este conjunto é ilustrativo e não representa "
        "a cotação atual."
    )
else:
    try:
        with st.spinner("Consultando o Banco Central..."):
            data = load_live_data(period)
    except bcb.BCBDataError:
        st.error(
            "Não foi possível consultar o Banco Central agora. "
            "Atualize os dados ou tente novamente mais tarde."
        )
        if st.button("Visualizar dados demonstrativos"):
            st.session_state["use_demo"] = True
            st.rerun()
        st.stop()

metrics = calculate_metrics(data)
st.markdown(
    f"<p class='quote'>{format_brl(metrics.latest)}</p>",
    unsafe_allow_html=True,
)
st.caption(f"Cotação de venda em {metrics.latest_date:%d/%m/%Y}")
render_metrics(metrics)
st.plotly_chart(
    build_chart(data),
    width="stretch",
    config={"displayModeBar": False},
)

with st.expander("Ver dados do período"):
    st.dataframe(data, width="stretch", hide_index=True)
    st.download_button(
        "Baixar CSV",
        data=to_csv_bytes(data),
        file_name=f"cotacao_dolar_{period}_registros.csv",
        mime="text/csv",
    )

st.caption("Uso informativo. Estes dados não constituem recomendação financeira.")
