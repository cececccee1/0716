# -*- coding: utf-8 -*-
"""
lib/recommend.py
================
推薦引擎函式 ── 從 D14 答案版移植,給 BOSS III App 的 M4 模組用。

簡化版:K-means 群 + Apriori 規則。真實系統需要客戶歷史交易資料 join。
"""
import pandas as pd


def recommend(customer_id, df_customers, rules, top_n=3):
    """
    Parameters
    ----------
    customer_id : str (例 "C0042")
    df_customers : DataFrame  含 cluster_name 欄(來自 D14 customer_clustered.csv)
    rules : DataFrame  Apriori 規則(來自 D13 apriori_top5_rules.csv,需含 antecedent / consequent / lift)
    top_n : int  推薦商品數

    Returns
    -------
    dict 或 None
    """
    if customer_id not in df_customers["customer_id"].values:
        return None

    row = df_customers[df_customers["customer_id"] == customer_id].iloc[0]
    cluster_name = row.get("cluster_name", "未分群")

    # 從規則庫挑 Top N(以「商品對」去重 → 避免雙向規則 A→B / B→A 同時出現)
    top_rules = rules.sort_values("lift", ascending=False)
    seen_pairs = set()
    recommendations = []
    for _, r in top_rules.iterrows():
        pair = frozenset([r["antecedent"], r["consequent"]])
        if pair in seen_pairs:
            continue
        seen_pairs.add(pair)
        recommendations.append({
            "sku":        r["consequent"],
            "lift":       float(r["lift"]),
            "confidence": float(r["confidence"]),
            "from_rule":  f"{r['antecedent']} → {r['consequent']}",
        })
        if len(recommendations) >= top_n:
            break

    return {
        "customer_id":     customer_id,
        "cluster":         cluster_name,
        "recommendations": recommendations,
        "explain":         f"基於「{cluster_name}」群 + Apriori Top {top_n} 規則(Lift 排序)",
    }


def cluster_action_text(cluster_name):
    """根據群名給推薦 Line OA 文案的開頭語氣"""
    if "VIP" in cluster_name:
        return "VIP 限定!"
    elif "沉睡" in cluster_name:
        return "好久不見!"
    elif "流失" in cluster_name:
        return "搶救!別走!"
    elif "穩定" in cluster_name:
        return "新品到貨!"
    else:
        return "嗨!"
