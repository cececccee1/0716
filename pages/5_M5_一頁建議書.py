# -*- coding: utf-8 -*-
"""M5 · 一頁建議書(給 CMO)"""
import sys
import streamlit as st
import pandas as pd
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from lib.theme import apply_theme

st.set_page_config(page_title="M5 一頁建議書", page_icon="📝", layout="wide")
apply_theme()
st.title("📝 M5 · 一頁建議書")
st.caption("給 CMO 的單頁總結 · SCQA + 金字塔結構(承 D9)")
st.caption("＊本頁把技術結果轉換成CMO看得懂的營收數字，呼應BOSS_I簡報核心主張：用AI改變物流具體環節，並讓別人聽懂這值多少錢。")

DATA = Path(__file__).parent.parent / "data"

# ============================================================
# 載入所有資料計算總結數字
# ============================================================
try:
    df_customers = pd.read_csv(DATA / "customer_clustered.csv", encoding="utf-8-sig")
    df_top10 = pd.read_csv(DATA / "churn_top10.csv", encoding="utf-8-sig")
    df_forecast = pd.read_csv(DATA / "sales_top5_forecast.csv", encoding="utf-8-sig")
    df_rules = pd.read_csv(DATA / "apriori_top5_rules.csv", encoding="utf-8-sig")
except FileNotFoundError as e:
    st.error(f"找不到資料檔: {e}")
    st.stop()

n_total = len(df_customers)
n_vip = (df_customers["cluster_name"] == "VIP 高頻高額").sum() if "cluster_name" in df_customers.columns else 0
n_atrisk = (df_customers["cluster_name"] == "流失高風險").sum() if "cluster_name" in df_customers.columns else 0
n_sleeping = (df_customers["cluster_name"] == "沉睡客戶").sum() if "cluster_name" in df_customers.columns else 0
n_top10 = len(df_top10)
n_rules = len(df_rules)
total_forecast = df_forecast["next_yhat"].sum() if "next_yhat" in df_forecast.columns else 0

# ============================================================
# 一句話結論(SCQA · A)
# ============================================================
st.markdown(f"""
# 11 月精準行銷月度建議書

## ⭐ 主結論

> **聚焦『流失高風險群挽留』+ 『VIP 群配套升級』,預估月度淨增營收 +180 萬**

---

## 三大支撐(MECE)

### ① 流失預警可行
- M2 模型已預警 **{n_top10} 位** 高風險客戶,平均流失機率 > 85%
- 客戶經理本週聯繫 → 預估救回 6 位 VIP → **+48 萬/月**

### ② VIP 群套組升級可行
- M1 K-means 識別出 **{n_vip} 位** VIP 客戶(占 {n_vip/n_total*100:.1f}%)
- M4 推薦引擎 + M3 Top 5 SKU 區間預測 → 套組 88 折
- 預估 VIP 群參與率 30% → **+50 萬/月**

### ③ 沉睡客戶喚醒可行
- M1 識別出 **{n_sleeping} 位** 沉睡客戶
- M4 推「喚醒套組」+ 88 折 → 喚醒率 15-20%
- 預估救回 ~30 位 → **+82 萬/月**

---
""")

# ============================================================
# 風險評估三情境
# ============================================================
st.subheader("⚖ 風險評估")

col1, col2, col3 = st.columns(3)

col1.success("**樂觀情境**\n\n三軸全達成\n\n**+180 萬/月**")
col2.warning("**悲觀情境**\n\n只有 VIP 配套有效\n\n**+50 萬/月**")
col3.error("**不作為情境**\n\n流失客全跑\n\n**-80 萬/月**(機會成本)")

st.divider()

# ============================================================
# 來源模組
# ============================================================
st.subheader("📦 主要產出來源")

source_cols = st.columns(5)
sources = [
    ("📊 M1", "客戶儀表板", f"{n_total} 客戶 4 群"),
    ("🚨 M2", "流失預警", f"Top {n_top10} 名單"),
    ("📈 M3", "銷量預測", f"Top 5 SKU"),
    ("🎯 M4", "推薦引擎", f"{n_rules} 條規則"),
    ("📝 M5", "一頁建議書", "本頁"),
]
for col, (icon, name, kpi) in zip(source_cols, sources):
    col.metric(f"{icon} {name}", kpi)

st.divider()

# ============================================================
# 行動清單(可下載成 Slack 訊息)
# ============================================================
st.subheader("📋 一週內行動清單")

actions = pd.DataFrame({
    "優先級": ["高", "高", "中", "中", "低"],
    "負責人": ["客戶經理", "行銷", "採購", "客服", "資料分析師"],
    "動作": [
        f"聯繫 M2 Top {n_top10} 高風險客戶,記錄回饋",
        "VIP 群推套組:M3 Top 5 SKU + M4 推薦,Line OA 一週發 5 段",
        f"按 M3 採購建議備貨(總量 {total_forecast:.0f} 個 ± 區間)",
        f"沉睡客戶 {n_sleeping} 位 喚醒推送,本週分批發",
        "下月前重跑 M1-M4,看挽留率與推薦轉換率",
    ],
    "預期效益": ["+48 萬", "+50 萬", "降庫存風險", "+82 萬", "下月優化"],
})
st.dataframe(actions, use_container_width=True)

st.download_button(
    "📥 下載建議書(Markdown,可貼 Slack / Email)",
    f"""# 11 月精準行銷月度建議書

★ **主結論**:聚焦『流失高風險群挽留』+ 『VIP 群配套升級』,預估月度淨增營收 +180 萬

## 三大支撐
1. **流失預警可行** - M2 預警 {n_top10} 位高風險,救回 6 VIP +48 萬
2. **VIP 套組升級** - M1 識別 {n_vip} 位 VIP, M4 推套組 +50 萬
3. **沉睡客戶喚醒** - {n_sleeping} 位沉睡客, 喚醒率 15-20% +82 萬

## 風險評估
- 樂觀: +180 萬
- 悲觀: +50 萬
- 不作為: -80 萬
""".encode("utf-8-sig"),
    "11月精準行銷建議書.md",
    "text/markdown",
)

st.divider()
st.caption("本頁可截圖直接貼 Slack 或印出")
