import streamlit as st
import pandas as pd
from datetime import datetime

# --- 外部CSSを読み込む関数 ---
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ページ設定
st.set_page_config(page_title="JANKEN LOG PRO", layout="wide")

# CSSの適用
try:
    local_css("style.css")
except FileNotFoundError:
    st.error("style.css が見つかりません。")

# --- 以降、ロジック部分はそのまま ---
st.title("JANKEN LOG PRO")
# ... (以下省略)