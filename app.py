import streamlit as st

st.write("アプリ開始")

try:
    st.write("Secrets確認開始")

    gcp = st.secrets["gcp_service_account"]

    st.write("Secrets取得成功")

    st.write(gcp["project_id"])

except Exception as e:
    st.error(e)
    st.stop()