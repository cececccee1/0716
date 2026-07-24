# -*- coding: utf-8 -*-
"""M4 · 推薦引擎 ★ 核心展示"""
import sys
import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(page_title="M4 推薦引擎", page_icon="🎯", layout="wide")

# 載入 lib/recommend
sys.path.insert(0, str(Path(__file__).parent.parent))
from lib.recommend import recommend, cluster_action_text
from lib.theme import apply_theme
apply_theme()

st.title("🎯 M4 · 推薦引擎(★ 核心展示)")
st.caption("D13 Apriori 規則 × D14 K-means 群 → 給對的人推對的品")
st.caption("＊此頁串接的客群分類，呼應BOSS_I簡報「避開AI盲區：K-means分群除錯實錄」的核心精神——模型看起來在跑，不代表邏輯沒洞。")

DATA = Path(__file__).parent.parent / "data"

try:
    df_customers = pd.read_csv(DATA / "customer_clustered.csv", encoding="utf-8-sig")
    rules = pd.read_csv(DATA / "apriori_top5_rules.csv", encoding="utf-8-sig")
except FileNotFoundError as e:
    st.error(f"找不到資料檔: {e}")
    st.stop()

# 交易明細(prepare_data.py 已把 D13 的籃子接上主檔的 customer_id)
try:
    df_tx = pd.read_csv(DATA / "transactions.csv", encoding="utf-8-sig")
except FileNotFoundError:
    df_tx = None

# ============================================================
# 客戶 ID 輸入
# ============================================================
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("輸入客戶 ID")

    # 提供常見預設選項
    sample_ids = {
        "VIP 範例(C0001 outlier)": "C0001",
        "VIP 範例(隨機抽 1)": df_customers[df_customers["cluster_name"] == "VIP 高頻高額"].iloc[0]["customer_id"]
                            if (df_customers["cluster_name"] == "VIP 高頻高額").any() else "C0001",
        "沉睡客戶(隨機抽 1)": df_customers[df_customers["cluster_name"] == "沉睡客戶"].iloc[0]["customer_id"]
                            if (df_customers["cluster_name"] == "沉睡客戶").any() else "C9999",
        "流失高風險(隨機抽 1)": df_customers[df_customers["cluster_name"] == "流失高風險"].iloc[0]["customer_id"]
                            if (df_customers["cluster_name"] == "流失高風險").any() else "C9999",
    }

    preset = st.selectbox("快速選擇範例", list(sample_ids.keys()))
    default_id = sample_ids[preset]

    cid = st.text_input("或自行輸入 customer_id", value=default_id)
    top_n = st.slider("推薦商品數", 1, 5, 3)

with col2:
    if cid in df_customers["customer_id"].values:
        result = recommend(cid, df_customers, rules, top_n=top_n)

        st.subheader(f"客戶 {cid}")

        # 客戶基本資料
        c_row = df_customers[df_customers["customer_id"] == cid].iloc[0]
        st.markdown(f"**所屬群:** {result['cluster']}")

        info_cols = st.columns(4)
        info_cols[0].metric("Recency", f"{c_row['Recency']} 天")
        info_cols[1].metric("Frequency", c_row["Frequency"])
        info_cols[2].metric("Monetary", f"{c_row['Monetary']:,.0f}")
        if "ComplaintCnt" in c_row:
            info_cols[3].metric("投訴次數", c_row["ComplaintCnt"])

        # 這位客戶買過什麼(客戶主檔 × 交易明細 join)
        if df_tx is not None:
            bought = df_tx[df_tx["customer_id"] == cid]
            if len(bought):
                items = bought["sku_id"].value_counts()
                st.caption(
                    f"🧾 歷史購買:{len(bought['order_id'].unique())} 張訂單 / "
                    f"{len(bought)} 個品項 — "
                    + "、".join(f"{k}×{v}" for k, v in items.head(5).items())
                )
            else:
                st.caption("🧾 歷史購買:此客戶在交易明細中沒有紀錄(沉睡客常見)")

        st.divider()

        # ============================================================
        # Top N 推薦商品
        # ============================================================
        st.subheader(f"🎁 推薦 Top {top_n}")

        for i, r in enumerate(result["recommendations"], 1):
            badge_col, info_col = st.columns([1, 5])
            badge_col.metric(f"Top {i}", r["sku"])
            info_col.caption(
                f"**Lift {r['lift']:.2f}** · Confidence {r['confidence']:.0%} · "
                f"來源規則:{r['from_rule']}"
            )

        st.caption(f"💡 {result['explain']}")

        # ============================================================
        # Line OA 文案範本(根據群差異化)
        # ============================================================
        st.divider()
        st.subheader("📱 Line OA 文案範本")

        prefix = cluster_action_text(result["cluster"])
        skus_str = "、".join([r["sku"] for r in result["recommendations"]])

        if "VIP" in result["cluster"]:
            template = (
                f"{prefix}本月 VIP 限定 → **{skus_str}** 套組 88 折!"
                f"出示券碼即享尊榮配送。#物流好夥伴"
            )
        elif "沉睡" in result["cluster"]:
            template = (
                f"{prefix}{skus_str} 任選 2 件 88 折,"
                f"限本週回娘家補貨,免運門檻打 5 折!#物流好夥伴"
            )
        elif "流失" in result["cluster"]:
            template = (
                f"{prefix}最近沒看到您下單?{skus_str} 任一件折 200,"
                f"客服可協助補貨評估。#物流好夥伴"
            )
        else:
            template = (
                f"{prefix}{skus_str} 配套販售,本週 9 折!"
                f"加入 Line OA 即享。#物流好夥伴"
            )

        st.code(template, language=None)
        st.caption("📌 真實上線可串 Claude / GPT API 把 prompt 自動生成 5 段不同文案 ── 留 BOSS III 加分項")

        # ============================================================
        # GenAI prompt 預覽(教學用)
        # ============================================================
        with st.expander("🤖 給 GenAI 寫文案的 prompt(可複製)"):
            prompt = f"""你是 Line OA 行銷文案寫手。客戶屬「{result['cluster']}」群。

推薦商品:{skus_str}
規則來源:{[r['from_rule'] for r in result['recommendations']]}

文案要求:
- 80 字以內
- 第一句鉤子(根據群名:VIP=尊榮、沉睡=喚醒、流失=挽留、穩定=新品)
- 最後一句行動(出示券碼/點選連結/限期)
- 結尾加 #物流好夥伴

請輸出 1 段。
"""
            st.code(prompt, language=None)

    else:
        st.error(f"找不到客戶 {cid}")

# ============================================================
# 全 Apriori 規則表(底部 expand)
# ============================================================
with st.expander("📜 全 Apriori 規則庫(D13 輸出)"):
    st.dataframe(rules, use_container_width=True)
