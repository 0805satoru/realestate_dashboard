import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd

st.markdown(
    """
    <p style="font-size:28px; font-weight:bold; margin-bottom:20;">
    🏢 不動産管理 - 物件詳細
    </p>
    """,
    unsafe_allow_html=True
)

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
st.markdown(
    f"<div style='font-size:22px; font-weight:700;'>🏠 {property_data['name']}</div>",
    unsafe_allow_html=True
)
st.markdown(
    f"<div font-size:18px; margin-top:4px;'>📍 {property_data['address']} ｜ 🏠 {property_data['units']}戸</div>",
    unsafe_allow_html=True
)

# タブ
tab1, tab2 = st.tabs([
    "部屋情報",
    "物件詳細"
])

with tab1:

    st.subheader("部屋情報")

    for i, row in property_rooms.iterrows():

        col1, col2 = st.columns([2, 1])

        with col1:
            st.write(f"{row['room']}号室")

        with col2:

            col_icon, col_select = st.columns([1, 3])
            status = row["status"]


            
            icon = "🟢" if row["status"] == "入居中" else "🔴"
            with col_icon:
                st.markdown(icon)
            with col_select:
                st.selectbox(
                    "",
                    ["入居中", "空室"],
                    label_visibility="collapsed",
                    key=f"status_{row['room_id']}"
            )

            #st.markdown(
            #    f"<span style='color:{color}; font-weight:700;'>{icon}</span>",
            #    unsafe_allow_html=True
            #)

           

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