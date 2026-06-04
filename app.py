import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd

st.set_page_config(page_title="不動産ダッシュボード", layout="wide")
st.title("🏠 不動産ダッシュボード")

# ======================
# Google認証 & データ取得（エラーハンドリング付き）
# ======================
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# 画面がぐるぐるで止まらないように全体をtryで囲む
try:
    # StreamlitのSecretsから辞書形式で取得
    secret_info = dict(st.secrets["gcp_service_account"])
    
    # 改行コード(\\n)が文字列として壊れるのを防ぐ対策
    if "private_key" in secret_info:
        secret_info["private_key"] = secret_info["private_key"].replace("\\n", "\n")

    creds = Credentials.from_service_account_info(secret_info, scopes=scope)
    client = gspread.authorize(creds)
    spreadsheet = client.open("不動産管理DB")

    properties_sheet = spreadsheet.worksheet("properties")
    rooms_sheet = spreadsheet.worksheet("rooms")

    properties_df = pd.DataFrame(properties_sheet.get_all_records())
    rooms_df = pd.DataFrame(rooms_sheet.get_all_records())

    # データが正しく取得できたかフラグを立てる
    data_loaded = True

except Exception as e:
    st.error("⚠️ Googleスプレッドシートへの接続に失敗しました。")
    st.exception(e)  # 画面に具体的なエラー内容を表示
    data_loaded = False


# ======================
# メイン処理（データが取得できた場合のみ実行）
# ======================
if data_loaded:
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
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("物件数", total_properties)

    with col2:
        st.metric("総戸数", total_units)

    with col3:
        st.metric("入居率", f"{occupancy_rate:.1f}%")

    st.divider()

    # ======================
    # 物件一覧
    # ======================
    st.subheader("🏢 物件一覧")

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
            st.write(f"🏠 {row['name']}")

        with col2:
            st.write(f"{rate:.0f}%")

        with col3:
            if st.button("開く", key=row["property_id"]):
                st.session_state["property_id"] = row["property_id"]
                st.switch_page("pages/property_detail.py")
