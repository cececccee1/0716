# -*- coding: utf-8 -*-
"""
Home.py · BOSS III 主頁
==========================
跑法:
  streamlit run Home.py
"""
import sys
import streamlit as st
import pandas as pd
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from lib.theme import apply_theme

st.set_page_config(
    page_title="BOSS III · 精準行銷引擎",
    page_icon="🎯",
    layout="wide",
)
apply_theme()

# ============================================================
# 主標題
# ============================================================
st.title("🎯 BOSS III · 精準行銷引擎")
st.caption("Week 3 AI 價值師 · 週驗收 · 預知 · 推薦 · 創價")
st.caption("＊這套引擎的分群邏輯，正是BOSS_I簡報「避開AI盲區：K-means分群除錯實錄」那頁的最終成果落地應用。")

# ============================================================
# 一句話結論(SCQA + 金字塔結構)
# ============================================================
st.success(
    "📌 **本月聚焦『流失高風險群挽留』+ 『VIP 群配套升級』,"
    "預估月度淨增營收 +180 萬**(M2 救 60 流失 + M4 推 5 套組)"
)

# ============================================================
# 三大支撐(三欄 KPI)
# ============================================================
data_dir = Path(__file__).parent / "data"

col1, col2, col3 = st.columns(3)

# 嘗試載入主要資料計算 KPI
try:
    df_customers = pd.read_csv(data_dir / "customer_clustered.csv", encoding="utf-8-sig")
    n_total = len(df_customers)
    n_vip = (df_customers["cluster_name"] == "VIP 高頻高額").sum() if "cluster_name" in df_customers.columns else 0
    n_atrisk = (df_customers["cluster_name"] == "流失高風險").sum() if "cluster_name" in df_customers.columns else 0
except FileNotFoundError:
    n_total = n_vip = n_atrisk = "?"

try:
    df_top10 = pd.read_csv(data_dir / "churn_top10.csv", encoding="utf-8-sig")
    n_top10 = len(df_top10)
except FileNotFoundError:
    n_top10 = "?"

try:
    df_rules = pd.read_csv(data_dir / "apriori_top5_rules.csv", encoding="utf-8-sig")
    n_rules = len(df_rules)
except FileNotFoundError:
    n_rules = "?"

col1.metric("客戶總數", f"{n_total:,}" if isinstance(n_total, int) else n_total)
col2.metric("VIP 群人數", n_vip, delta=f"流失高風險 {n_atrisk}",
             delta_color="inverse")
col3.metric("Apriori 強規則", n_rules, delta=f"Top 10 高風險名單 {n_top10}")

st.divider()

# ============================================================
# 5 模組導航
# ============================================================
st.subheader("📦 5 個模組")

modules = [
    ("📊", "M1 客戶儀表板", "K-means 4 群分布 + R/M 散點 + 群描述",
     "pages/1_M1_客戶儀表板.py"),
    ("🚨", "M2 流失預警", "Top 10 高風險名單 + 風險原因 + 一鍵下載",
     "pages/2_M2_流失預警.py"),
    ("📈", "M3 銷量預測", "Top 5 SKU 下月區間 + 採購建議",
     "pages/3_M3_銷量預測.py"),
    ("🎯", "M4 推薦引擎(★ 核心)", "輸入客戶 ID → 群 + Top 3 推薦 + Line OA 文案",
     "pages/4_M4_推薦引擎.py"),
    ("📝", "M5 一頁建議書", "給 CMO 的單頁總結",
     "pages/5_M5_一頁建議書.py"),
]

for icon, title, desc, path in modules:
    st.markdown(f"**{icon} {title}** ── {desc}")

st.divider()

# ============================================================
# W3 主軸回收
# ============================================================
st.subheader("W3 主軸:預知 · 推薦 · 創價")

col_a, col_b, col_c = st.columns(3)
col_a.info("🔮 **預知**(D11 D12)\n\n分類:誰會走\n回歸:多少銷量")
col_b.warning("🎁 **推薦**(D13 D14)\n\nApriori:誰跟誰一起\nK-means:誰是誰")
col_c.success("💎 **創價**(D15)\n\n5 模組合一 = 1 個產品\n= 給 CMO 的決策工具")

st.divider()

# ============================================================
# 5 分鐘 Demo 節奏(教師備課用 expand)
# ============================================================
with st.expander("🎬 5 分鐘 Demo 節奏(教師展示用)"):
    st.markdown("""
    | 時段 | 頁面 | 重點 |
    |---|---|---|
    | 0:00 - 0:30 | Home | 一句話結論 |
    | 0:30 - 1:00 | M1 | 4 群分布 |
    | 1:00 - 1:30 | M2 | Top 10 名單 |
    | 1:30 - 2:00 | M3 | Top 5 區間 |
    | 2:00 - 3:30 | **M4 ★** | 核心 demo:輸入 ID → 推薦 |
    | 3:30 - 4:00 | M5 | 一頁建議書 |
    | 4:00 - 4:30 | (回 Home) | W3 主軸回收 |
    | 4:30 - 5:00 | Q&A | |
    """)
