import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd

st.set_page_config(page_title="物件管理", layout="wide")

st.markdown(
    """
    <p style="font-size:22px; font-weight:bold; margin-bottom:20;">
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
st.markdown("###資産概要")
st.markdown(
    f"""
    **物件数** {total_properties}件　｜　
    **総戸数** {total_units}戸　｜　
    **入居率** {occupancy_rate:.1f}%
    """
)

# ======================
# 所有物件
# ======================
st.markdown("###所有物件")

for _, row in properties_df.iterrows():

    # この物件の部屋取得
    rooms = rooms_df[rooms_df["property_id"] == row["property_id"]]

    total = len(rooms)

    occupied = len(
        rooms[rooms["status"] == "入居中"]
    )

    rate = (occupied / total * 100) if total > 0 else 0

    col1, col2, col3 = st.columns([4, 1, 1])

    with col1:
        st.markdown(f"**🏠 {row['name']}**")

    with col2:
        st.write(f"入居率 {rate:.0f}%")

    with col3:
        if st.button("詳細を見る", key=row["property_id"]):

            st.session_state["property_id"] = row["property_id"]
            st.switch_page("pages/property_detail.py")