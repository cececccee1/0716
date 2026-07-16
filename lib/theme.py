# -*- coding: utf-8 -*-
"""
lib/theme.py
============
藍黑主題共用樣式。.streamlit/config.toml 已經處理好底色/主色，
這裡只補強卡片邊框、標題漸層等細節，讓五個頁面看起來一致。

用法（每個頁面 st.set_page_config() 之後呼叫一次）：
    from lib.theme import apply_theme
    apply_theme()
"""
import streamlit as st

_CSS = """
<style>
/* 卡片化 st.metric */
div[data-testid="stMetric"]{
    background: #0d1424;
    border: 1px solid rgba(122,162,255,0.18);
    border-radius: 12px;
    padding: 14px 16px 10px;
}
div[data-testid="stMetric"] label{
    color:#9aa4c4 !important;
}

/* 標題加一點藍色光暈 */
h1, h2, h3{
    letter-spacing: .3px;
}

/* dataframe / table 圓角 */
div[data-testid="stDataFrame"], div[data-testid="stTable"]{
    border-radius: 10px;
    overflow: hidden;
    border: 1px solid rgba(122,162,255,0.15);
}

/* expander 卡片化 */
details{
    background: #0d1424;
    border: 1px solid rgba(122,162,255,0.15);
    border-radius: 10px;
}

/* 分隔線淡化 */
hr{ border-color: rgba(122,162,255,0.15) !important; }

/* 側邊欄 */
section[data-testid="stSidebar"]{
    background: #080b16;
    border-right: 1px solid rgba(122,162,255,0.12);
}

/* 主要按鈕加藍色漸層 */
button[kind="primary"]{
    background: linear-gradient(135deg,#4f8cff,#7fd4ff) !important;
    border: none !important;
    color: #04070f !important;
    font-weight: 700 !important;
}

/* alert 區塊圓角統一 */
div[data-testid="stAlert"]{
    border-radius: 10px;
}
</style>
"""


def apply_theme():
    st.markdown(_CSS, unsafe_allow_html=True)
