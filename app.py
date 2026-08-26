from pathlib import Path

import pandas as pd
import streamlit as st
import yfinance as yf

from stock_ranker import load_companies, rank

BASE_DIR = Path(__file__).parent
DATA_FILE = BASE_DIR / "data" / "companies.csv"
ICON_FILE = BASE_DIR / "assets" / "pea_stock_analyser_fixed_small.ico"

st.set_page_config(
    page_title="PEA Stock Analyser",
    page_icon=str(ICON_FILE),
    layout="wide",
)


@st.cache_data(ttl=900)
def get_price_history(ticker: str, period: str) -> pd.DataFrame:
    """Fetch price history from Yahoo Finance with a short cache."""
    if not ticker:
        return pd.DataFrame()
    try:
        data = yf.download(
            ticker,
            period=period,
            auto_adjust=True,
            progress=False,
            threads=False,
        )
        if data.empty:
            return pd.DataFrame()
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)
        return data
    except Exception:
        return pd.DataFrame()


def pct(value):
    if value is None or pd.isna(value):
        return "—"
    return f"{value * 100:.1f}%"


def multiple(value):
    if value is None or pd.isna(value):
        return "—"
    return f"{value:.2f}x"


def eur_m(value):
    if value is None or pd.isna(value):
        return "—"
    return f"€{value:.2f}m"


def score_colour(score: float) -> str:
    if score >= 70:
        return "#15803d"
    if score >= 55:
        return "#a16207"
    return "#b91c1c"


companies = load_companies(DATA_FILE)
results = rank(companies)
result_by_name = {row["name"]: row for row in results}

st.title("PEA Stock Analyser")
st.caption(
    "Microcap research dashboard. Higher scores are better. "
    "Financial inputs remain manually sourced until automated data validation is added."
)

with st.sidebar:
    st.header("Company")
    selected_name = st.selectbox(
        "Select a company",
        [row["name"] for row in results],
        index=0,
    )
    period = st.selectbox(
        "Price history",
        ["1mo", "3mo", "6mo", "ytd", "1y", "2y", "5y"],
        index=3,
    )
    st.divider()
    st.caption("Current ranking")
    for idx, row in enumerate(results, start=1):
        st.write(f"**{idx}. {row['name']}** — {row['final_score']:.1f}/100")

row = result_by_name[selected_name]

title_col, score_col = st.columns([4, 1])
with title_col:
    st.subheader(row["name"])
    st.caption(f"{row['ticker']} · {row['theme']}")
    if row.get("description"):
        st.write(row["description"])
    elif row.get("note"):
        st.write(row["note"])

with score_col:
    score = row["final_score"]
    colour = score_colour(score)
    st.markdown(
        f"""
        <div style="text-align:center;padding:12px;border:1px solid #d1d5db;border-radius:10px;">
          <div style="font-size:0.8rem;color:#6b7280;">OVERALL SCORE</div>
          <div style="font-size:2.2rem;font-weight:700;color:{colour};">{score:.1f}</div>
          <div style="font-size:0.8rem;color:#6b7280;">/ 100</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.divider()

# Price action
price_ticker = row.get("yahoo_ticker") or ""
history = get_price_history(price_ticker, period)

left, right = st.columns([2, 1])
with left:
    st.markdown("### Price action")
    if not history.empty and "Close" in history.columns:
        closes = history["Close"].dropna()
        if not closes.empty:
            start_price = float(closes.iloc[0])
            current_price = float(closes.iloc[-1])
            change = current_price / start_price - 1 if start_price else None

            c1, c2 = st.columns(2)
            c1.metric("Latest adjusted price", f"{current_price:.3f}")
            c2.metric(
                f"Change ({period})",
                pct(change),
                delta=pct(change) if change is not None else None,
            )
            st.line_chart(closes, height=330)
        else:
            st.info("No usable closing-price history returned for this ticker.")
    else:
        st.info(
            "Live price history is unavailable for this company right now. "
            "The financial ranking still works from the stored research data."
        )

with right:
    st.markdown("### Investment snapshot")
    st.metric("Market cap", eur_m(row["market_cap_m"]))
    st.metric("Revenue", eur_m(row["revenue_m"]))
    st.metric("Forward revenue growth", pct(row["revenue_growth_forward"]))
    st.metric("Gross margin", pct(row["gross_margin"]))
    st.caption(f"PEA: {row.get('pea_eligible', '—')}")
    st.caption(f"Broker access: {row.get('broker_access', '—')}")

st.divider()

st.markdown("### Key metrics")
m1, m2, m3, m4, m5, m6 = st.columns(6)
m1.metric("P/S", multiple(row["ps"]))
m2.metric("EV / Sales", multiple(row["ev_sales"]))
m3.metric("Net cash / debt", eur_m(row["net_cash_m"]))
m4.metric("Forward EBITDA", eur_m(row["ebitda_forward_m"]))
m5.metric("Forward EBITDA margin", pct(row["ebitda_margin_forward"]))
m6.metric("Quant score", f"{row['quant_score']:.1f}")

st.markdown("### Score breakdown")
score_rows = pd.DataFrame(
    {
        "Factor": [
            "Revenue growth",
            "Gross margin",
            "Balance sheet",
            "P/S valuation",
            "EV/Sales valuation",
            "EBITDA margin",
            "Autonomy exposure",
            "Dilution / liquidity",
        ],
        "Score": [
            row["growth_score"],
            row["gross_margin_score"],
            row["balance_sheet_score"],
            row["ps_score"],
            row["ev_sales_score"],
            row["ebitda_margin_score"],
            row["autonomy_exposure"],
            row["dilution_liquidity_quality"],
        ],
    }
)
st.bar_chart(score_rows.set_index("Factor"), horizontal=True, height=370)

with st.expander("Company thesis / caveats"):
    st.write(row.get("note") or "No thesis note stored yet.")

st.divider()
st.markdown("### Compare all reviewed companies")
comparison = pd.DataFrame(results)[
    [
        "name",
        "market_cap_m",
        "revenue_growth_forward",
        "gross_margin",
        "ps",
        "ev_sales",
        "quant_score",
        "final_score",
    ]
].copy()
comparison.columns = [
    "Company",
    "Market cap (€m)",
    "Forward revenue growth",
    "Gross margin",
    "P/S",
    "EV/Sales",
    "Quant score",
    "Final score",
]
st.dataframe(
    comparison.style.format(
        {
            "Market cap (€m)": "{:.2f}",
            "Forward revenue growth": "{:.1%}",
            "Gross margin": "{:.1%}",
            "P/S": "{:.2f}x",
            "EV/Sales": "{:.2f}x",
            "Quant score": "{:.1f}",
            "Final score": "{:.1f}",
        }
    ),
    hide_index=True,
    width="stretch",
)

st.caption(
    "Price data is retrieved from Yahoo Finance when available. "
    "Fundamental estimates are research inputs and should be refreshed from primary filings before investing."
)
