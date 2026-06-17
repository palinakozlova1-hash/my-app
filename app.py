import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

st.set_page_config(
    page_title="Predikcia TV komunikácie — Retail segment 2025",
    page_icon="📡",
    layout="wide",
)

# ============================================================================
# DENTSU BRAND THEME
# ============================================================================

DENTSU_BLACK = "#000000"
DENTSU_BG = "#AFC1CE"          # signature gray-blue background
DENTSU_RED = "#E8453C"
DENTSU_TEAL = "#1ABC9C"
DENTSU_PURPLE = "#7B6FD6"
DENTSU_BEIGE = "#E8D9C5"
DENTSU_GRAY = "#5C6670"

st.markdown(f"""
<style>
.stApp {{
    background-color: #FAFAFA;
}}
.dentsu-header {{
    background-color: {DENTSU_BG};
    padding: 2.4rem 2.6rem 2.1rem 2.6rem;
    border-radius: 4px;
    margin-bottom: 1.8rem;
    position: relative;
    overflow: hidden;
}}
.dentsu-header svg {{
    position: absolute;
    top: 0;
    right: 0;
    height: 100%;
    width: 55%;
    z-index: 0;
}}
.dentsu-eyebrow {{
    font-size: 0.78rem;
    font-weight: 700;
    letter-spacing: 2px;
    color: {DENTSU_BLACK};
    text-transform: uppercase;
    margin-bottom: 0.6rem;
    position: relative;
    z-index: 1;
}}
.dentsu-title-block {{
    display: inline-block;
    background-color: {DENTSU_BLACK};
    padding: 0.55rem 1.1rem;
    position: relative;
    z-index: 1;
}}
.dentsu-title {{
    font-size: 1.9rem;
    font-weight: 800;
    color: #FFFFFF;
    letter-spacing: -0.3px;
    margin: 0;
    line-height: 1.15;
}}
.dentsu-subtitle {{
    color: {DENTSU_GRAY};
    font-size: 0.95rem;
    margin-top: 0.9rem;
    font-weight: 500;
    position: relative;
    z-index: 1;
}}
.dentsu-wordmark {{
    font-size: 1.05rem;
    font-weight: 800;
    color: {DENTSU_BLACK};
    margin-top: 1.6rem;
    position: relative;
    z-index: 1;
}}
[data-testid="stMetricValue"] {{
    font-weight: 700;
    color: {DENTSU_BLACK};
}}
[data-testid="stMetricLabel"] {{
    color: {DENTSU_GRAY};
    font-weight: 500;
}}
section[data-testid="stSidebar"] {{
    background-color: #F3F4F5;
    border-right: 2px solid {DENTSU_BLACK};
}}
section[data-testid="stSidebar"] h2 {{
    font-weight: 800;
    letter-spacing: -0.3px;
}}
hr {{
    border-top: 1.5px solid {DENTSU_BLACK} !important;
    opacity: 0.15;
}}
</style>
""", unsafe_allow_html=True)

# ============================================================================
# NAČÍTAJ DÁTA
# ============================================================================

@st.cache_data
def load_data():
    df = pd.read_csv("retail_segment_2025.csv")
    df["date"] = pd.to_datetime(df["date"])
    df["forecast"] = pd.to_numeric(df["forecast"], errors="coerce")
    df["real"] = pd.to_numeric(df["real"], errors="coerce")
    df = df.sort_values("date")

    iso = df["date"].dt.isocalendar()
    df["iso_year"] = iso.year.astype(int)
    df["iso_week"] = iso.week.astype(int)
    df["week_key"] = df["iso_year"].astype(str) + "-W" + df["iso_week"].astype(str).str.zfill(2)
    df["month_key"] = df["date"].dt.strftime("%Y-%m")
    return df

df = load_data()

RETAILERS_WITH_REAL = sorted(df.loc[df["real"].notna(), "Značka"].unique().tolist())
ALL_RETAILERS = sorted(df["Značka"].unique().tolist())
if "KAUFLAND" in ALL_RETAILERS:
    ALL_RETAILERS.remove("KAUFLAND")
    ALL_RETAILERS = ["KAUFLAND"] + ALL_RETAILERS

# ============================================================================
# HLAVIČKA — Dentsu brand style
# ============================================================================

DIAGONAL_LINES_SVG = f"""
<svg viewBox="0 0 400 220" preserveAspectRatio="none">
  <line x1="80" y1="220" x2="280" y2="0" stroke="{DENTSU_RED}" stroke-width="2" opacity="0.85"/>
  <circle cx="80" cy="220" r="4" fill="{DENTSU_BLACK}"/>
  <circle cx="280" cy="0" r="4" fill="{DENTSU_BLACK}"/>

  <line x1="140" y1="220" x2="340" y2="0" stroke="{DENTSU_BEIGE}" stroke-width="2" opacity="0.9"/>
  <circle cx="140" cy="220" r="4" fill="{DENTSU_BLACK}"/>

  <line x1="200" y1="220" x2="400" y2="10" stroke="{DENTSU_TEAL}" stroke-width="2" opacity="0.85"/>
  <circle cx="200" cy="220" r="4" fill="{DENTSU_BLACK}"/>

  <line x1="260" y1="220" x2="400" y2="70" stroke="{DENTSU_PURPLE}" stroke-width="2" opacity="0.85"/>
  <circle cx="260" cy="220" r="4" fill="{DENTSU_BLACK}"/>

  <line x1="320" y1="220" x2="400" y2="140" stroke="{DENTSU_GRAY}" stroke-width="2" opacity="0.7"/>
</svg>
"""

st.markdown(f"""
<div class="dentsu-header">
  {DIAGONAL_LINES_SVG}
  <div class="dentsu-eyebrow">Retail segment · Slovenský trh</div>
  <div class="dentsu-title-block">
    <p class="dentsu-title">Predikcia TV komunikačnej aktivity 2025</p>
  </div>
  <div class="dentsu-subtitle">GRP 30s</div>
  <div class="dentsu-wordmark">dentsu</div>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# SIDEBAR
# ============================================================================

st.sidebar.header("Nastavenia")

selected_brand = st.sidebar.selectbox("Vyber retailera", ALL_RETAILERS, index=0)

is_real_available = selected_brand in RETAILERS_WITH_REAL

view = st.sidebar.radio("Režim", ["Mesačne", "Týždenne"], index=0)

show_real = False
if is_real_available:
    show_real = st.sidebar.checkbox("Zobraziť reálne údaje", value=True)

st.sidebar.divider()
st.sidebar.caption("Sledovaní retaileri")
st.sidebar.caption(", ".join(ALL_RETAILERS))

# ============================================================================
# FILTER
# ============================================================================

df_brand = df[df["Značka"] == selected_brand].copy()

def fmt_num(x):
    try:
        return f"{x:,.0f}".replace(",", " ")
    except Exception:
        return "—"

# ============================================================================
# AGREGÁCIE
# ============================================================================

agg_dict = {"forecast": "sum"}
if "real" in df_brand.columns:
    agg_dict["real"] = "sum"

monthly = df_brand.groupby("month_key", as_index=False).agg(agg_dict)
weekly = df_brand.groupby("week_key", as_index=False).agg(agg_dict)

# ============================================================================
# TOP METRIKY
# ============================================================================

if is_real_available and show_real:
    col1, col2, col3, col4 = st.columns(4)
else:
    col1, col3, col4 = st.columns(3)
    col2 = None

with col1:
    st.metric("Predikcia za rok 2025", fmt_num(df_brand["forecast"].sum()))

if col2 is not None:
    with col2:
        real_total = df_brand["real"].sum()
        diff_pct = (df_brand["forecast"].sum() - real_total) / real_total * 100
        st.metric("Reálny súčet 2025", fmt_num(real_total), delta=f"{diff_pct:+.1f}%")

# SOV% — podiel značky na celkovom GRP segmentu za rok 2025
segment_forecast_total = df["forecast"].sum()
brand_forecast_sov = df_brand["forecast"].sum() / segment_forecast_total * 100

with col3:
    st.metric("Forecast SOV", f"{brand_forecast_sov:.1f}%")

with col4:
    if is_real_available and show_real:
        segment_real_total = df["real"].sum()
        brand_real_sov = df_brand["real"].sum() / segment_real_total * 100
        sov_diff = brand_forecast_sov - brand_real_sov
        st.metric("Real SOV", f"{brand_real_sov:.1f}%", delta=f"{sov_diff:+.1f} p.b.")
    else:
        st.metric("Real SOV", "—")

st.divider()

# ============================================================================
# MESAČNÝ POHĽAD
# ============================================================================

if view == "Mesačne":
    months = monthly["month_key"].tolist()
    default_m = "2025-01" if "2025-01" in months else months[0]
    sel_month = st.selectbox("Vyber mesiac", months, index=months.index(default_m))

    row = monthly[monthly["month_key"] == sel_month].iloc[0]
    fc = float(row["forecast"])
    rl = float(row["real"]) if (is_real_available and show_real and pd.notna(row.get("real"))) else None

    if rl is not None:
        c1, c2 = st.columns(2)
        with c1:
            st.metric(f"Predikcia za {sel_month}", fmt_num(fc))
        with c2:
            st.metric("Real", fmt_num(rl), delta=fmt_num(fc - rl))
    else:
        st.metric(f"Predikcia za {sel_month}", fmt_num(fc))

    st.subheader("Denný priebeh v mesiaci")
    sub = df_brand[df_brand["month_key"] == sel_month].copy()

    fig, ax = plt.subplots(figsize=(13, 4.3))
    ax.plot(sub["date"], sub["forecast"], marker="o", linewidth=2, markersize=4, color=DENTSU_BLACK, label="Predikcia")
    if show_real and is_real_available and sub["real"].notna().any():
        ax.plot(sub["date"], sub["real"], marker="o", linewidth=2, markersize=4, color=DENTSU_RED, label="Real")
        ax.fill_between(sub["date"], sub["forecast"], sub["real"], alpha=0.07, color=DENTSU_GRAY)
        ax.legend(frameon=False)
    ax.set_xlabel("Dátum")
    ax.set_ylabel("GRP 30s")
    ax.grid(True, alpha=0.2)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d.%m"))
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
    plt.tight_layout()
    st.pyplot(fig)

    st.subheader("Prehľad roka (mesačné sumy)")
    fig2, ax2 = plt.subplots(figsize=(13, 4.3))
    month_dates = pd.to_datetime(monthly["month_key"] + "-01")
    ax2.plot(month_dates, monthly["forecast"], marker="o", linewidth=2.5, color=DENTSU_BLACK, label="Predikcia")
    if show_real and is_real_available and monthly["real"].notna().any():
        ax2.plot(month_dates, monthly["real"], marker="o", linewidth=2.5, color=DENTSU_RED, label="Real")
        ax2.legend(frameon=False)
    ax2.set_xlabel("Mesiac")
    ax2.set_ylabel("Suma GRP 30s")
    ax2.grid(True, alpha=0.2)
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)
    ax2.xaxis.set_major_formatter(mdates.DateFormatter("%b"))
    plt.tight_layout()
    st.pyplot(fig2)

    with st.expander("Tabuľka: všetky mesiace 2025"):
        t = monthly.copy()
        t["forecast"] = t["forecast"].round(0).astype(int)
        if is_real_available and show_real:
            t["real"] = t["real"].round(0)
        else:
            t = t.drop(columns=["real"], errors="ignore")
        st.dataframe(t, use_container_width=True, hide_index=True)

# ============================================================================
# TÝŽDENNÝ POHĽAD
# ============================================================================

else:
    weeks = weekly["week_key"].tolist()
    default_w = "2025-W01" if "2025-W01" in weeks else weeks[0]
    sel_week = st.selectbox("Vyber týždeň (ISO)", weeks, index=weeks.index(default_w))

    row = weekly[weekly["week_key"] == sel_week].iloc[0]
    fc = float(row["forecast"])
    rl = float(row["real"]) if (is_real_available and show_real and pd.notna(row.get("real"))) else None

    if rl is not None:
        c1, c2 = st.columns(2)
        with c1:
            st.metric(f"Predikcia za {sel_week}", fmt_num(fc))
        with c2:
            st.metric("Real", fmt_num(rl), delta=fmt_num(fc - rl))
    else:
        st.metric(f"Predikcia za {sel_week}", fmt_num(fc))

    st.subheader("Denný priebeh v týždni")
    sub = df_brand[df_brand["week_key"] == sel_week].copy()

    fig, ax = plt.subplots(figsize=(13, 4.3))
    ax.plot(sub["date"], sub["forecast"], marker="o", linewidth=2, markersize=6, color=DENTSU_BLACK, label="Predikcia")
    if show_real and is_real_available and sub["real"].notna().any():
        ax.plot(sub["date"], sub["real"], marker="o", linewidth=2, markersize=6, color=DENTSU_RED, label="Real")
        ax.legend(frameon=False)
    ax.set_xlabel("Dátum")
    ax.set_ylabel("GRP 30s")
    ax.grid(True, alpha=0.2)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%a %d.%m"))
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
    plt.tight_layout()
    st.pyplot(fig)

    st.subheader("Prehľad roka (týždenné sumy)")
    week_dates = df_brand.groupby("week_key")["date"].min().reset_index().rename(columns={"date": "week_start"})
    w = weekly.merge(week_dates, on="week_key", how="left").sort_values("week_start")

    fig2, ax2 = plt.subplots(figsize=(13, 4.3))
    ax2.plot(w["week_start"], w["forecast"], marker="o", linewidth=1.8, color=DENTSU_BLACK, label="Predikcia")
    if show_real and is_real_available and w["real"].notna().any():
        ax2.plot(w["week_start"], w["real"], marker="o", linewidth=1.8, color=DENTSU_RED, label="Real")
        ax2.legend(frameon=False)
    ax2.set_xlabel("Týždeň")
    ax2.set_ylabel("Suma GRP 30s")
    ax2.grid(True, alpha=0.2)
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)
    ax2.xaxis.set_major_formatter(mdates.DateFormatter("%b"))
    plt.tight_layout()
    st.pyplot(fig2)

    with st.expander("Tabuľka: všetky týždne 2025"):
        cols = ["week_key", "forecast"]
        if is_real_available and show_real:
            cols.append("real")
        t = w[cols].copy()
        t["forecast"] = t["forecast"].round(0).astype(int)
        if "real" in t.columns:
            t["real"] = t["real"].round(0)
        st.dataframe(t, use_container_width=True, hide_index=True)

# ============================================================================
# POROVNANIE CELÉHO SEGMENTU
# ============================================================================

st.divider()
st.subheader("Porovnanie retail segmentu")

comparison = df.groupby(["Značka", "month_key"], as_index=False).agg(forecast=("forecast", "sum"))
comparison_pivot = comparison.pivot(index="month_key", columns="Značka", values="forecast")

fig3, ax3 = plt.subplots(figsize=(13, 5))
colors_map = {
    "KAUFLAND": DENTSU_RED,
    "BILLA": DENTSU_PURPLE,
    "LIDL": DENTSU_TEAL,
    "TESCO": "#C9A96E",
    "COOP JEDNOTA": DENTSU_GRAY,
}
for col in comparison_pivot.columns:
    dates = pd.to_datetime(comparison_pivot.index + "-01")
    lw = 3 if col == selected_brand else 1.3
    alpha = 1.0 if col == selected_brand else 0.4
    ax3.plot(dates, comparison_pivot[col], marker="o", linewidth=lw, alpha=alpha,
              color=colors_map.get(col, "gray"), label=col)

ax3.legend(loc="upper left", ncol=5, fontsize=9, frameon=False)
ax3.set_xlabel("Mesiac")
ax3.set_ylabel("Suma GRP 30s")
ax3.grid(True, alpha=0.2)
ax3.spines["top"].set_visible(False)
ax3.spines["right"].set_visible(False)
ax3.xaxis.set_major_formatter(mdates.DateFormatter("%b"))
plt.tight_layout()
st.pyplot(fig3)
