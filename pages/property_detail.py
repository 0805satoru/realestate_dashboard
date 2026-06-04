import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd

st.title("物件詳細")

# Google認証
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

# properties取得
properties_sheet = spreadsheet.worksheet("properties")
properties_data = properties_sheet.get_all_records()
properties_df = pd.DataFrame(properties_data)

# rooms取得
rooms_sheet = spreadsheet.worksheet("rooms")
rooms_data = rooms_sheet.get_all_records()
rooms_df = pd.DataFrame(rooms_data)

property_id = st.session_state.get("property_id")

if property_id is None:
    st.error("物件が選択されていません")
    st.stop()

# 選択物件
property_data = properties_df[
    properties_df["property_id"] == property_id
].iloc[0]

# 対象部屋
property_rooms = rooms_df[
    rooms_df["property_id"] == property_id
]

# 入居率計算
occupied_count = len(
    property_rooms[
        property_rooms["status"] == "入居中"
    ]
)

vacant_count = len(
    property_rooms[
        property_rooms["status"] == "空室"
    ]
)

total_rooms = len(property_rooms)

occupancy_rate = (
    occupied_count / total_rooms * 100
    if total_rooms > 0
    else 0
)

# ヘッダー
st.header(property_data["name"])
st.markdown(f"📍 **{property_data['address']}**  ｜  🏠 {property_data['units']}戸")

# タブ
tab1, tab2 = st.tabs([
    "部屋情報",
    "物件詳細"
])

with tab1:

    st.subheader("部屋情報")

    rooms_sheet = spreadsheet.worksheet("rooms")

    for i, row in property_rooms.iterrows():

        col1, col2 = st.columns([2, 1])

        with col1:
            st.write(f"{row['room']}")

        with col2:
            new_status = st.selectbox(
                "状態",
                ["入居中", "空室"],
                index=0 if row["status"] == "入居中" else 1,
                key=f"status_{row['room_id']}"
            )

        # 変更があった時だけ更新
        if new_status != row["status"]:

            cell = rooms_sheet.find(str(row["room_id"]))

            rooms_sheet.update_cell(
                cell.row,
                5,  # status列（A=1 ... E=5）
                new_status
            )

            st.rerun()
        
    

with tab2:

    st.write("戸数")
    st.write(property_data["units"])

    st.metric(
        "入居率",
        f"{occupancy_rate:.1f}%"
    )

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "入居中",
            occupied_count
        )

    with col2:
        st.metric(
            "空室",
            vacant_count
        )

st.divider()

if st.button("← 物件一覧へ戻る"):
    st.switch_page("app.py")