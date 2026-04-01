import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="Predikcia 2025 — Kaufland",
    page_icon="📈",
    layout="wide",
)

st.title("📈 Predikcia 2025")
st.caption("")

@st.cache_data
def load_daily():
    df = pd.read_csv("forecast_daily_2025.csv")
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date")
    return df

df = load_daily()

# priprava kalendára
iso = df["date"].dt.isocalendar()
df["iso_year"] = iso.year.astype(int)
df["iso_week"] = iso.week.astype(int)
df["week_key"] = df["iso_year"].astype(str) + "-W" + df["iso_week"].astype(str).str.zfill(2)
df["month_key"] = df["date"].dt.strftime("%Y-%m")

# len 2025 (ak by sa tam dostalo viac)
df_2025 = df[df["date"].dt.year == 2025].copy()

# sidebar
st.sidebar.header("Nastavenia")
view = st.sidebar.radio("Režim", ["Mesačne", "Týždenne"], index=0)

show_real = False
if "real" in df_2025.columns:
    show_real = st.sidebar.checkbox("Zobraziť reálne údaje (ak sú dostupné)", value=True)

st.sidebar.divider()
st.sidebar.caption("")

# agregácie
monthly = df_2025.groupby("month_key", as_index=False).agg(
    forecast=("forecast", "sum"),
    real=("real", "sum") if "real" in df_2025.columns else ("forecast", "sum"),
)

weekly = df_2025.groupby("week_key", as_index=False).agg(
    forecast=("forecast", "sum"),
    real=("real", "sum") if "real" in df_2025.columns else ("forecast", "sum"),
)

# helper na formát
def fmt_num(x: float) -> str:
    try:
        return f"{x:,.0f}".replace(",", " ")
    except Exception:
        return str(x)

# -------------------------
# MESAČNÝ POHĽAD
# -------------------------
if view == "Mesačne":
    months = monthly["month_key"].tolist()
    default_m = "2025-01" if "2025-01" in months else months[0]

    sel_month = st.selectbox("Vyber mesiac", months, index=months.index(default_m))

    row = monthly[monthly["month_key"] == sel_month].iloc[0]
    fc = float(row["forecast"])
    rl = float(row["real"]) if ("real" in monthly.columns and show_real) else None

    c1, c2, c3 = st.columns([1.2, 1.2, 2.0])
    with c1:
        st.metric(f"Predikcia za {sel_month}", fmt_num(fc))
    with c2:
        if rl is not None:
            st.metric("Real", fmt_num(rl), delta=fmt_num(fc - rl))
        else:
            st.metric("Real", "—")
    with c3:
        st.write("")

    st.subheader("Denný priebeh v mesiaci")
    sub = df_2025[df_2025["month_key"] == sel_month].copy()

    fig = plt.figure(figsize=(12, 4))
    plt.plot(sub["date"], sub["forecast"], marker="o", linewidth=1)
    if show_real and "real" in sub.columns:
        plt.plot(sub["date"], sub["real"], marker="o", linewidth=1)
        plt.legend(["Predikcia", "Real"])
    else:
        plt.legend(["Predikcia"])
    plt.xlabel("Dátum")
    plt.ylabel("Hodnota")
    plt.tight_layout()
    st.pyplot(fig)

    st.subheader("Prehľad roka (mesačné sumy)")
    fig2 = plt.figure(figsize=(12, 4))
    plt.plot(pd.to_datetime(monthly["month_key"] + "-01"), monthly["forecast"], marker="o", linewidth=2)
    if show_real and "real" in monthly.columns:
        plt.plot(pd.to_datetime(monthly["month_key"] + "-01"), monthly["real"], marker="o", linewidth=2)
        plt.legend(["Predikcia", "Real"])
    else:
        plt.legend(["Predikcia"])
    plt.xlabel("Mesiac")
    plt.ylabel("Suma")
    plt.tight_layout()
    st.pyplot(fig2)

    with st.expander("Tabuľka: všetky mesiace 2025"):
        t = monthly.copy()
        t["forecast"] = t["forecast"].round(0).astype(int)
        if "real" in t.columns:
            t["real"] = t["real"].round(0)
        st.dataframe(t, use_container_width=True, hide_index=True)

# -------------------------
# TÝŽDENNÝ POHĽAD
# -------------------------
else:
    weeks = weekly["week_key"].tolist()
    default_w = "2025-W01" if "2025-W01" in weeks else weeks[0]

    sel_week = st.selectbox("Vyber týždeň (ISO)", weeks, index=weeks.index(default_w))

    row = weekly[weekly["week_key"] == sel_week].iloc[0]
    fc = float(row["forecast"])
    rl = float(row["real"]) if ("real" in weekly.columns and show_real) else None

    c1, c2, c3 = st.columns([1.2, 1.2, 2.0])
    with c1:
        st.metric(f"Predikcia za {sel_week}", fmt_num(fc))
    with c2:
        if rl is not None:
            st.metric("Real", fmt_num(rl), delta=fmt_num(fc - rl))
        else:
            st.metric("Real", "—")
    with c3:
        st.write("")

    st.subheader("Denný priebeh v týždni")
    sub = df_2025[df_2025["week_key"] == sel_week].copy()

    fig = plt.figure(figsize=(12, 4))
    plt.plot(sub["date"], sub["forecast"], marker="o", linewidth=1)
    if show_real and "real" in sub.columns:
        plt.plot(sub["date"], sub["real"], marker="o", linewidth=1)
        plt.legend(["Predikcia", "Real"])
    else:
        plt.legend(["Predikcia"])
    plt.xlabel("Dátum")
    plt.ylabel("Hodnota")
    plt.tight_layout()
    st.pyplot(fig)

    st.subheader("Prehľad roka (týždenné sumy)")
    # pre x-os použijeme prvý deň týždňa
    week_dates = df_2025.groupby("week_key")["date"].min().reset_index().rename(columns={"date": "week_start"})
    w = weekly.merge(week_dates, on="week_key", how="left").sort_values("week_start")

    fig2 = plt.figure(figsize=(12, 4))
    plt.plot(w["week_start"], w["forecast"], marker="o", linewidth=2)
    if show_real and "real" in w.columns:
        plt.plot(w["week_start"], w["real"], marker="o", linewidth=2)
        plt.legend(["Predikcia", "Real"])
    else:
        plt.legend(["Predikcia"])
    plt.xlabel("Týždeň (začiatok)")
    plt.ylabel("Suma")
    plt.tight_layout()
    st.pyplot(fig2)

    with st.expander("Tabuľka: všetky týždne 2025"):
        t = weekly.copy()
        t["forecast"] = t["forecast"].round(0).astype(int)
        if "real" in t.columns:
            t["real"] = t["real"].round(0)
        st.dataframe(t, use_container_width=True, hide_index=True)

st.divider()
st.caption("")
