# -*- coding: utf-8 -*-
"""M3 · 銷量預測"""
import sys
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from lib.theme import apply_theme

st.set_page_config(page_title="M3 銷量預測", page_icon="📈", layout="wide")
apply_theme()
st.title("📈 M3 · 銷量預測")
st.caption("D12 Prophet · Top 5 SKU 下月區間預測")

DATA = Path(__file__).parent.parent / "data"

try:
    forecast = pd.read_csv(DATA / "sales_top5_forecast.csv", encoding="utf-8-sig")
    history = pd.read_csv(DATA / "sales_monthly.csv", parse_dates=["date"], encoding="utf-8-sig")
except FileNotFoundError:
    st.error("找不到 data/sales_top5_forecast.csv 或 sales_monthly.csv,請先跑 D12 並 prepare_data.py")
    st.stop()

# ============================================================
# SKU 篩選器
# ============================================================
# forecast / history 都有品號(sku_id,與 D12 共用)與品名(sku / sku_name)
sku_list = forecast["sku"].tolist()          # 品名
label = dict(zip(forecast["sku"], forecast["sku_id"]))   # 品名 → 品號
selected = st.selectbox("選擇商品", sku_list,
                        format_func=lambda n: f"{n}({label[n]})")

row = forecast[forecast["sku"] == selected].iloc[0]
st.caption(f"品號 `{row['sku_id']}`(D12 銷量預測)= 品名「{selected}」(D13 交易 / M4 推薦規則)")

# ============================================================
# 採購建議(主結論)
# ============================================================
st.success(
    f"📦 **建議備貨 {row['next_yhat']:.0f} 個 ± "
    f"{(row['next_upper']-row['next_lower'])/2:.0f}**  "
    f"(80% 信賴區間:{row['next_lower']:.0f} ~ {row['next_upper']:.0f})"
)

# ============================================================
# Decision badge
# ============================================================
col1, col2, col3 = st.columns(3)
col1.metric("Prophet MAPE", f"{row['prophet_mape']:.1f}%")
col2.metric("Best Baseline MAPE", f"{row['baseline_mape']:.1f}%",
             delta=f"{row['diff_pp']:+.1f}pp",
             delta_color="normal" if row['diff_pp'] > 0 else "inverse")
col3.metric("採用模型", "Prophet" if "Prophet" in row['decision'] else "Baseline")

st.caption(f"決策依據:{row['decision']}")

st.divider()

# ============================================================
# 歷史 + 區間預測線
# ============================================================
st.subheader(f"{selected} 月銷量趨勢 + 預測區間")

hist = history[history["sku_name"] == selected].sort_values("date")   # 依品名(品號在 sku_id 欄)

fig = go.Figure()

# 歷史實績
fig.add_trace(go.Scatter(
    x=hist["date"], y=hist["qty"],
    mode="lines+markers", name="歷史實績",
    line=dict(color="#3498DB", width=2),
))

# 預測點 + 區間
last_date = hist["date"].max()
next_date = last_date + pd.DateOffset(months=1)

fig.add_trace(go.Scatter(
    x=[last_date, next_date], y=[hist["qty"].iloc[-1], row["next_yhat"]],
    mode="lines+markers", name="預測點估",
    line=dict(color="#E74C3C", width=2, dash="dash"),
    marker=dict(size=12),
))

fig.add_trace(go.Scatter(
    x=[next_date, next_date], y=[row["next_lower"], row["next_upper"]],
    mode="lines", name="80% 信賴區間",
    line=dict(color="#F39C12", width=8),
    showlegend=True,
))

fig.update_layout(
    height=450,
    xaxis_title="月份",
    yaxis_title="銷量(qty)",
    hovermode="x unified",
)
st.plotly_chart(fig, use_container_width=True)

st.divider()

# ============================================================
# 全 5 SKU 總覽表
# ============================================================
st.subheader("Top 5 全部預測表")

show_df = forecast.copy()
show_df["建議備貨"] = show_df.apply(
    lambda r: f"{r['next_yhat']:.0f} ± {(r['next_upper']-r['next_lower'])/2:.0f}",
    axis=1
)
show_cols = ["sku", "prophet_mape", "baseline_mape", "decision",
             "next_lower", "next_yhat", "next_upper", "建議備貨"]
show_cols = [c for c in show_cols if c in show_df.columns]
st.dataframe(show_df[show_cols], use_container_width=True)

st.download_button(
    "📥 下載 Top 5 預測(CSV,給採購)",
    forecast.to_csv(index=False).encode("utf-8-sig"),
    "sales_top5_forecast.csv",
    "text/csv",
)
