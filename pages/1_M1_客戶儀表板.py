# -*- coding: utf-8 -*-
"""M1 · 客戶儀表板"""
import sys
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from lib.theme import apply_theme

st.set_page_config(page_title="M1 客戶儀表板", page_icon="📊", layout="wide")
apply_theme()
st.title("📊 M1 · 客戶儀表板")
st.caption("K-means 4 群 · 看誰是誰")
st.caption("＊本頁的分群方法論，呼應BOSS_I簡報「避開AI盲區：K-means分群除錯實錄」——用標準化與log轉換，避免消費金額(M)量級壓垮頻率(F)維度。")

DATA = Path(__file__).parent.parent / "data"

try:
    df = pd.read_csv(DATA / "customer_clustered.csv", encoding="utf-8-sig")
except FileNotFoundError:
    st.error("找不到 data/customer_clustered.csv,請先跑 prepare_data.py")
    st.stop()

# ============================================================
# 4 KPI
# ============================================================
st.subheader("各群人數")
col1, col2, col3, col4 = st.columns(4)

cluster_counts = df["cluster_name"].value_counts()
for i, (col, name) in enumerate(zip(
    [col1, col2, col3, col4],
    ["VIP 高頻高額", "穩定中段", "流失高風險", "沉睡客戶"]
)):
    n = cluster_counts.get(name, 0)
    pct = n / len(df) * 100 if len(df) > 0 else 0
    col.metric(name, f"{n}", delta=f"{pct:.1f}%", delta_color="off")

st.divider()

# ============================================================
# R × M 散點圖
# ============================================================
st.subheader("客戶散點圖(Recency × log Monetary)")

df_plot = df.copy()
df_plot["log_Monetary"] = np.log1p(df_plot["Monetary"])

fig = px.scatter(
    df_plot,
    x="Recency",
    y="log_Monetary",
    color="cluster_name",
    hover_data=["customer_id", "Frequency", "Monetary", "ComplaintCnt"],
    title="客戶 RFM 分布(顏色 = K-means 群)",
    height=500,
    color_discrete_map={
        "VIP 高頻高額": "#E74C3C",
        "穩定中段":     "#3498DB",
        "流失高風險":   "#F39C12",
        "沉睡客戶":     "#95A5A6",
    },
)
st.plotly_chart(fig, use_container_width=True)

st.divider()

# ============================================================
# 群描述表
# ============================================================
st.subheader("各群業務動作建議")

action_map = {
    "VIP 高頻高額": "升級服務 / 套組推薦 / 專屬客服",
    "穩定中段":     "持續經營 / 新品推薦",
    "流失高風險":   "電話挽留 / 折扣券 / 客服主動聯繫",
    "沉睡客戶":     "喚醒推送 / 重大優惠 / 重新破冰",
}

summary = df.groupby("cluster_name").agg(
    客數=("customer_id", "count"),
    Recency=("Recency", "median"),
    Frequency=("Frequency", "median"),
    Monetary=("Monetary", "median"),
).round(0).astype(int)
summary["建議動作"] = summary.index.map(action_map)
st.dataframe(summary, use_container_width=True)

# ============================================================
# 一鍵下載
# ============================================================
st.divider()
st.download_button(
    "📥 下載完整客戶分群表(CSV)",
    df.to_csv(index=False).encode("utf-8-sig"),
    "customer_clustered.csv",
    "text/csv",
)
