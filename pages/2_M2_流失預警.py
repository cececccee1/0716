# -*- coding: utf-8 -*-
"""M2 · 流失預警"""
import sys
import streamlit as st
import pandas as pd
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from lib.theme import apply_theme

st.set_page_config(page_title="M2 流失預警", page_icon="🚨", layout="wide")
apply_theme()
st.title("🚨 M2 · 流失預警")
st.caption("D11 決策樹 · Top 10 高風險客戶名單")

DATA = Path(__file__).parent.parent / "data"

try:
    df = pd.read_csv(DATA / "churn_top10.csv", encoding="utf-8-sig")
except FileNotFoundError:
    st.error("找不到 data/churn_top10.csv,請先跑 D11_流失預測 答案版 + prepare_data.py")
    st.stop()

# ============================================================
# 主結論
# ============================================================
n_top = len(df)
avg_prob = df["churn_prob"].mean() * 100 if "churn_prob" in df.columns else 0

st.error(
    f"⚠️ **本月模型預警 {n_top} 位高風險客戶** · "
    f"平均流失機率 **{avg_prob:.0f}%** · "
    f"建議客戶經理本週內優先聯繫"
)

st.divider()

# ============================================================
# Top 10 表格(精簡版)
# ============================================================
st.subheader(f"Top {n_top} 名單")

# 加 Rank + 風險指數(combined score 才能看出 ranking 差異)
df_show = df.copy().reset_index(drop=True)

# 風險指數 = 模型機率 70% + Recency 久沒下單 20% + 投訴次數 10%
# 0-100 整數,讓 10 位客戶有真正的 ranking 差別
recency_norm = (df_show["Recency"].clip(0, 365) / 365)
complaint_norm = df_show["ComplaintCnt"].clip(0, 5) / 5
df_show["risk_index"] = (
    df_show["churn_prob"] * 70
    + recency_norm * 20
    + complaint_norm * 10
).round().astype(int)

# 按風險指數重新排序
df_show = df_show.sort_values("risk_index", ascending=False).reset_index(drop=True)
df_show.insert(0, "Rank", range(1, len(df_show) + 1))

show_cols = ["Rank", "customer_id", "risk_index", "churn_prob", "Recency",
             "Frequency", "Monetary", "ComplaintCnt", "main_reason", "suggested_action"]
show_cols = [c for c in show_cols if c in df_show.columns]

column_config = {
    "Rank": st.column_config.NumberColumn(
        "優先順序",
        help="本週客戶經理聯繫優先序(基於風險指數降序)",
        format="%d",
        width="small",
    ),
    "risk_index": st.column_config.ProgressColumn(
        "風險指數",
        help="模型機率 70% + Recency 20% + 投訴次數 10%(0-100)",
        format="%d",
        min_value=0,
        max_value=100,
    ),
    "churn_prob": st.column_config.NumberColumn(
        "模型機率",
        help="決策樹原始預測機率",
        format="%.3f",
    ),
    "Monetary": st.column_config.NumberColumn("Monetary", format="%d"),
    "main_reason": st.column_config.TextColumn("主因", width="medium"),
    "suggested_action": st.column_config.TextColumn("建議動作", width="medium"),
}
st.dataframe(df_show[show_cols], use_container_width=True,
             column_config=column_config, hide_index=True)

st.caption("📌 **風險指數**是業務調整版分數(0-100),結合模型機率 + 行為訊號。"
           "純看模型機率 10 位都是 0.936(同一個決策樹葉子),"
           "加上 Recency / 投訴次數加權後,Rank 1-10 才有真實業務差別。"
           "教學重點:**ML 機率 + 業務規則** = 真實上線決策依據。")

st.divider()

# ============================================================
# 風險原因分布
# ============================================================
if "main_reason" in df.columns:
    st.subheader("Top 10 流失主因分布")
    reason_counts = df["main_reason"].value_counts()
    st.bar_chart(reason_counts)

# ============================================================
# 一鍵下載 + 寄送(模擬)
# ============================================================
st.divider()
col1, col2 = st.columns(2)

col1.download_button(
    "📥 下載 Top 10 名單(CSV,給客戶經理)",
    df.to_csv(index=False).encode("utf-8-sig"),
    "churn_top10.csv",
    "text/csv",
)

if col2.button("📧 模擬寄送名單給客戶經理"):
    st.success("(模擬)已寄送至 sales@company.com 與 csm@company.com")

st.divider()

# ============================================================
# 模型可解釋性(D11 反直覺第三問銜接)
# ============================================================
with st.expander("🔍 模型如何判斷高風險?(可解釋性說明)"):
    st.markdown("""
    決策樹模型(承 D11)學了這條規則(範例):

    ```
    Recency > 60 天?
      ├─ Yes → Frequency < 3?
      │         ├─ Yes → 流失機率 92%
      │         └─ No  → 流失機率 65%
      └─ No  → 投訴 > 0 次?
                ├─ Yes → 流失機率 35%
                └─ No  → 流失機率 5%
    ```

    每個 Top 10 客戶的 `main_reason` 欄就是落到哪條決策路徑。
    """)
