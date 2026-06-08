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

# property_detail取得
property_detail_sheet = spreadsheet.worksheet("property_detail")
property_detail_data = property_detail_sheet.get_all_records()
property_detail_df = pd.DataFrame(property_detail_data)

# 購入情報取得
purchase_sheet = spreadsheet.worksheet("purchase")
purchase_data = purchase_sheet.get_all_records()
purchase_df = pd.DataFrame(purchase_data)


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

# 物件詳細
detail = property_detail_df[
    property_detail_df["property_id"] == property_id
].iloc[0]
# 購入情報
purchase = purchase_df[
    purchase_df["property_id"] == property_id
].iloc[0]

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
    f"<div style='font-size:16px; font-weight:500; margin-top:2px;'>📍 {property_data['address']} ｜ 🏠 {property_data['units']}戸</div>",
    unsafe_allow_html=True
)

# タブ
tab1, tab2, tab3 = st.tabs([
    "部屋情報",
    "物件詳細",
    "購入情報"
])

with tab1:
    st.markdown(
        f"<div style='font-size:20px; font-weight:700;'>部屋情報</div>",
        unsafe_allow_html=True
    )

    for i, row in property_rooms.iterrows():
        with st.container(border=True):
            st.markdown(
            f"""
            <span style="font-size:18px;font-weight:700;">{row['room']}号室</span>
            <span style="font-size:16px;font-weight:500;">　　💰総賃料 {row['total_rent']}/月</span>
            """,
            unsafe_allow_html=True
            )

            status = row["status"]
            if status == "入居中":
                icon = "🟢"
            else:
                icon = "🔴"
            
            if st.button(
                f"{icon} {status}",
                key=f"status_btn_{row['room_id']}"
            ):

                # 変更があった時だけ更新
                new_status = "空室" if status == "入居中" else "入居中"
                cell = rooms_sheet.find(str(row["room_id"]))
                rooms_sheet.update_cell(
                    cell.row,
                    5, # status列（A=1 ... E=5）
                    new_status
                )
                st.rerun()
                


with tab2:

    st.markdown(
        f"<div style='font-size:18px; font-weight:600;'>入居率：{occupancy_rate:.0f}%</div>",
        unsafe_allow_html=True
    )

    st.markdown(
        f"<div style='font-size:18px; font-weight:600;'>"
        f"総戸数 {total_rooms}戸 ｜ 入居中 {occupied_count}戸 ｜ 空室 {vacant_count}戸"
        f"</div>",
        unsafe_allow_html=True
    )

    current_income = property_rooms[
    property_rooms["status"] == "入居中"
    ]["total_rent"].sum()

    full_income = property_rooms["total_rent"].sum()

    vacancy_loss = full_income - current_income

    st.markdown(
        f"""
        <div style='font-size:18px; font-weight:600;'>
            💰 現在収入：{current_income:,.0f}円/月<br>
            🏠 満室想定：{full_income:,.0f}円/月<br>
            ⚠️ 空室損失：{vacancy_loss:,.0f}円/月
        </div>
        """,
        unsafe_allow_html=True
    )

    st.divider()

    st.markdown(
        "<div style='font-size:20px; font-weight:700;'>基本情報</div>",
        unsafe_allow_html=True
    )
    st.markdown(f"📍 {detail['住所']}")
    st.markdown(f"📅 建築年月：{detail['建築年月']}")
    
    from datetime import datetime
    import pandas as pd
    build_date = pd.to_datetime(detail["建築年月"])
    age = datetime.now().year - build_date.year
    st.markdown(f"🏚️ 築年数：{age}年")

    st.markdown(f"📐 土地面積：{detail['土地面積']}㎡")
    st.markdown(f"🏠 延床面積：{detail['延床面積']}㎡")
    st.markdown(f"🏗️ 構造：{detail['構造']}")
    st.markdown(f"🏢 階数：{detail['階数']}階")

    st.divider()

with tab3:

    st.markdown(
        "<div style='font-size:20px; font-weight:700;'>購入情報</div>",
        unsafe_allow_html=True
    )

    st.divider()

    st.markdown(
        "<div style='font-size:18px; font-weight:600;'>購入情報</div>",
        unsafe_allow_html=True
    )

    st.write(f"売買価格：{purchase['売買価格']}")
    st.write(f"諸経費：{purchase['諸経費']}")
    st.write(f"総投資額：{purchase['総投資額']}")
    st.write(f"自己資金：{purchase['自己資金']}")
    st.write(f"購入日：{purchase['購入日']}")

    st.divider()

    st.markdown(
        "<div style='font-size:18px; font-weight:600;'>融資情報</div>",
        unsafe_allow_html=True
    )

    st.write(f"金融機関：{purchase['金融機関']}")
    st.write(f"借入額：{purchase['借入額']}")
    st.write(f"返済期間：{purchase['返済期間']}年")
    st.write(f"借入金利：{purchase['借入金利']}%")

    st.divider()

    st.markdown(
        "<div style='font-size:18px; font-weight:600;'>返済状況</div>",
        unsafe_allow_html=True
    )

    st.write(f"月返済額：{purchase['月返済額']}")
    st.write(f"残債：{purchase['残債']}")
    st.write(f"返済額：{purchase['返済額']}")

    

if st.button("← 所有物件へ戻る"):
    st.switch_page("app.py")