import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd

st.set_page_config(page_title="不動産ダッシュボード", layout="wide")

st.title("🏠 不動産ダッシュボード")

# ======================
# Google認証
# ======================
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=scope
)

client = gspread.authorize(creds)

spreadsheet = client.open("不動産管理DB")


#
st.write("認証開始")

creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=scope
)

st.write("認証成功")

client = gspread.authorize(creds)

st.write("gspread成功")

spreadsheet = client.open("不動産管理DB")

st.write("スプレッドシート接続成功")

