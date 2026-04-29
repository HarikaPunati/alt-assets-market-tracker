import pandas as pd
import plotly.express as px
import streamlit as st

PROCESSED = "data/processed"

st.set_page_config(
    page_title="Alt Assets Market Tracker",
    page_icon="📊",
    layout="wide",
)

# ── Dark theme overrides ───────────────────────────────────────────────────────
PLOTLY_THEME = "plotly_dark"
CHART_BG = "#0e1117"
PAPER_BG = "#0e1117"

def apply_theme(fig):
    fig.update_layout(
        title_text="",
        plot_bgcolor=CHART_BG,
        paper_bgcolor=PAPER_BG,
        font_color="#e0e0e0",
        margin=dict(t=30, b=40, l=40, r=20),
    )
    return fig


# ── Data loading ───────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    firms        = pd.read_csv(f"{PROCESSED}/dim_firm.csv")
    dim_sector   = pd.read_csv(f"{PROCESSED}/dim_sector.csv")
    transactions = pd.read_csv(f"{PROCESSED}/fact_transaction.csv", parse_dates=["date"])
    outreach     = pd.read_csv(f"{PROCESSED}/fact_outreach.csv")
    transactions = transactions.merge(dim_sector[["sector_id", "sector"]], on="sector_id", how="left")
    return firms, transactions, outreach


firms, transactions, outreach = load_data()


# ── Header ─────────────────────────────────────────────────────────────────────
st.title("Alternative Assets Market Tracker")
st.markdown(
    "An overview of firm AUM, deal activity, transaction volume, and investor outreach "
    "across the alternative assets universe. Data is sourced from the ETL pipeline output."
)
st.divider()


# ── Row 1: AUM + Deal count ────────────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.subheader("Top 10 Firms by AUM")
    top_firms = (
        firms.nlargest(10, "aum_estimate_usd")
             .sort_values("aum_estimate_usd")
    )
    fig_aum = px.bar(
        top_firms,
        x="aum_estimate_usd",
        y="name",
        orientation="h",
        labels={"aum_estimate_usd": "AUM (USD)", "name": ""},
        color="aum_estimate_usd",
        color_continuous_scale="Blues",
        template=PLOTLY_THEME,
    )
    fig_aum.update_coloraxes(showscale=False)
    fig_aum.update_xaxes(tickprefix="$", tickformat=".2s")
    st.plotly_chart(apply_theme(fig_aum), width="stretch")

with col2:
    st.subheader("Deal Count by Sector")
    deal_by_sector = (
        transactions.groupby("sector", dropna=False)
                    .size()
                    .reset_index(name="deal_count")
                    .sort_values("deal_count", ascending=False)
    )
    fig_sector = px.bar(
        deal_by_sector,
        x="sector",
        y="deal_count",
        labels={"sector": "Sector", "deal_count": "Number of Deals"},
        color="deal_count",
        color_continuous_scale="Teal",
        template=PLOTLY_THEME,
    )
    fig_sector.update_coloraxes(showscale=False)
    st.plotly_chart(apply_theme(fig_sector), width="stretch")


# ── Row 2: Transaction volume + Outreach outcomes ──────────────────────────────
col3, col4 = st.columns(2)

with col3:
    st.subheader("Transaction Volume Over Time")
    tx_monthly = (
        transactions.dropna(subset=["date"])
                    .set_index("date")
                    .resample("ME")["amount_usd"]
                    .sum()
                    .reset_index()
    )
    tx_monthly.columns = ["month", "total_usd"]
    fig_volume = px.line(
        tx_monthly,
        x="month",
        y="total_usd",
        labels={"month": "Month", "total_usd": "Total Volume (USD)"},
        markers=True,
        template=PLOTLY_THEME,
        color_discrete_sequence=["#00b4d8"],
    )
    fig_volume.update_yaxes(tickprefix="$", tickformat=".2s")
    st.plotly_chart(apply_theme(fig_volume), width="stretch")

with col4:
    st.subheader("Outreach Outcomes")
    outcome_counts = (
        outreach["outcome"]
        .value_counts()
        .reset_index()
    )
    outcome_counts.columns = ["outcome", "count"]
    fig_outreach = px.bar(
        outcome_counts,
        x="outcome",
        y="count",
        labels={"outcome": "Outcome", "count": "Number of Outreaches"},
        color="outcome",
        color_discrete_sequence=px.colors.qualitative.Pastel,
        template=PLOTLY_THEME,
    )
    fig_outreach.update_layout(showlegend=False)
    st.plotly_chart(apply_theme(fig_outreach), width="stretch")
