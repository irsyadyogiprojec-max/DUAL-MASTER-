import streamlit as st
import datetime
import requests
from supabase import create_client

st.set_page_config(page_title="Input Part Repair", page_icon="🛠️", layout="wide")

supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
SHEETS_URL = "URL_WEB_APP_SPREADSHEET_ANDA"

MP_DATA = {"Ammar": "Red", "Agus M": "Red", "Irul K": "White"}

st.markdown("# 🛠️ Halaman Proses & Perbaikan Part (Repair)")
st.markdown("---")

with st.form("form_repair", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        tanggal = st.date_input("Tanggal", value=datetime.date.today())
        teknisi = st.selectbox("Teknisi", ["-- Pilih --"] + list(MP_DATA.keys()))
        no_seri = st.text_input("Scan/Ketik SERIAL No. Part")
    with col2:
        nama_part = st.text_input("Nama Part", value="Dual Master Expander Device", disabled=True)
        type_part = st.text_input("TYPE", value="DME-010")
        qty = st.number_input("QTY", min_value=1, value=1)
        
        # Pilihan status aksi repair
        status_aksi = st.radio("Status Pengerjaan:", ["On Progress Repair", "Done Repair (OK)"])

    submitted = st.form_submit_button("💾 Proses Data Repair")
    if submitted:
        if teknisi == "-- Pilih --" or not no_seri:
            st.error("Teknisi dan Serial No wajib diisi!")
        else:
            shift = MP_DATA.get(teknisi, "General")
            
            if "On Progress" in status_aksi:
                action_type = "Repair"
                status_val = "On Progress"
            else:
                action_type = "OK"
                status_val = "Done Repair / OK"

            payload = {
                "action": action_type, "tanggal": str(tanggal), "nama": teknisi, "shift": shift,
                "line": "-", "mesin": "-", "nama_part": nama_part, "type_part": type_part,
                "no_seri": no_seri, "qty": qty, "status": status_val
            }
            supabase.table("maintenance_log").insert(payload).execute()
            requests.post(SHEETS_URL, json=payload)
            st.success(f"✅ Data berhasil dicatat dengan status: {status_val}!")
