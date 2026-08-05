import streamlit as st
import datetime
import requests
from supabase import create_client

st.set_page_config(page_title="Input Part NG", page_icon="🔴", layout="wide")

supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
SHEETS_URL = "URL_WEB_APP_SPREADSHEET_ANDA"

MP_DATA = {"Ammar": "Red", "Agus M": "Red", "Irul K": "White"}
MACHINE_DATA = {"IDR 052": "Cylinder Block", "Gondola": "Cylinder Block"}

st.markdown("# 🔴 Input Data Part NG")
st.markdown("---")

with st.form("form_ng", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        tanggal = st.date_input("Tanggal", value=datetime.date.today())
        nama = st.selectbox("Nama MP", ["-- Pilih --"] + list(MP_DATA.keys()))
        mesin = st.selectbox("Mesin Bermasalah", ["-- Pilih --"] + list(MACHINE_DATA.keys()))
    with col2:
        nama_part = st.text_input("Nama Part", value="Dual Master Expander Device", disabled=True)
        type_part = st.text_input("TYPE", value="DME-010")
        no_seri = st.text_input("SERIAL No.")
        qty = st.number_input("QTY", min_value=1, value=1)

    submitted = st.form_submit_button("🚨 Simpan Part NG")
    if submitted:
        if nama == "-- Pilih --" or mesin == "-- Pilih --":
            st.error("Nama MP dan Mesin wajib dipilih!")
        else:
            shift = MP_DATA.get(nama, "General")
            line = MACHINE_DATA.get(mesin, "General Line")
            
            payload = {
                "action": "NG", "tanggal": str(tanggal), "nama": nama, "shift": shift,
                "line": line, "mesin": mesin, "nama_part": nama_part, "type_part": type_part,
                "no_seri": no_seri, "qty": qty, "status": "Part NG"
            }
            supabase.table("maintenance_log").insert(payload).execute()
            requests.post(SHEETS_URL, json=payload)
            st.success("✅ Data Part NG berhasil disimpan!")
