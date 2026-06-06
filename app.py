import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd

st.set_page_config(page_title="物件管理", layout="wide")

st.markdown(
    """
    <p style="font-size:28px; font-weight:bold; margin-bottom:20;">
    🏢 不動産管理
    </p>
    """,
    unsafe_allow_html=True
)

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


# ======================
# データ取得
# ======================
properties_sheet = spreadsheet.worksheet("properties")
rooms_sheet = spreadsheet.worksheet("rooms")

properties_df = pd.DataFrame(properties_sheet.get_all_records())
rooms_df = pd.DataFrame(rooms_sheet.get_all_records())

# ======================
# KPI計算
# ======================
total_properties = len(properties_df)
total_units = len(rooms_df)

occupied_units = len(
    rooms_df[rooms_df["status"] == "入居中"]
)

occupancy_rate = (
    occupied_units / total_units * 100
    if total_units > 0 else 0
)

# ======================
# KPI表示（カード）
# ======================
st.markdown(
    """
    <p style="font-size:24px; font-weight:bold;">
    物件概要
    </p>
    """,
    unsafe_allow_html=True
)

with st.container(border=True):

    st.markdown(
        f"**物件数:** {total_properties}件 ｜ "
        f"**総戸数:** {total_units}戸 ｜ "
        f"**入居率:** {occupancy_rate:.0f}%"
    )


# ======================
# 所有物件
# ======================
st.markdown(
    """
    <p style="font-size:24px; font-weight:bold;">
    所有物件
    </p>
    """,
    unsafe_allow_html=True
)

for _, row in properties_df.iterrows():

    # この物件の部屋取得
    rooms = rooms_df[rooms_df["property_id"] == row["property_id"]]

    total = len(rooms)

    occupied = len(
        rooms[rooms["status"] == "入居中"]
    )

    vacant = total - occupied

    rate = (occupied / total * 100) if total > 0 else 0

    # 入居率の色判定
    if rate >= 95:
        color = "#22c55e"  # 緑（満室）
    elif rate >= 80:
        color = "#f59e0b"  # 黄（注意）
    else:
        color = "#ef4444"  # 赤（空室多い）


    with st.container(border=True):

        st.markdown(
            f"<span style='color:{color}; font-weight:900; margin-right:6px;'>●</span>"
            f"**🏠 {row['name']}**",
            unsafe_allow_html=True
        )
        st.markdown(
            f"<div style='font-size:20px; font-weight:700;'>"
            f"<span style='color:{color}; margin-right:6px;'>●</span>"
            f"🏠 {row['name']}"
            f"</div>",
            unsafe_allow_html=True
        )

        st.markdown(
            f"<div style='font-size:18px; margin-top:4px;'>"
            f"総戸数 {total}戸 ｜ 空室 {vacant}戸"
            f"</div>",
            unsafe_allow_html=True
        )
        st.write(f"入居率 {rate:.0f}%")
        st.progress(rate / 100)

        if st.button("詳細を見る", key=row["property_id"]):

            st.session_state["property_id"] = row["property_id"]
            st.switch_page("pages/property_detail.py")