import streamlit as st
import pandas as pd
from datetime import datetime
import requests
from supabase import create_client

st.set_page_config(page_title="Input Part OK", page_icon="🟢", layout="wide")

@st.cache_resource
def init_supabase():
    url = st.secrets.get("SUPABASE_URL", "")
    key = st.secrets.get("SUPABASE_KEY", "")
    if not url or not key: return None
    return create_client(url, key)

supabase = init_supabase()
GOOGLE_SHEETS_URL = "https://script.google.com/macros/s/AKfycbwcwsvm7SwocuXzjyMBdWyTCllWT7wi5hMRMm3fxo-64Q_EcgXqRaWfMXeC0O6rxkbT/exec"

MP_DATA = {
    "Ammar": "Red", "Agus M": "Red", "Irul K": "White", "Apriansyah": "Red",
    "M. Safiq": "General", "Eko P": "White", "Arif B": "Red", "Jaenal": "White"
}
MACHINE_DATA = {"IDR 052": "Cylinder Block", "Gondola": "Cylinder Block"}
mp_list = list(MP_DATA.keys())
machine_list = list(MACHINE_DATA.keys())

st.markdown("# 🟢 Input Data Part OK (Selesai Repair)")
st.markdown("---")

with st.form("form_input_ok", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        tgl_ok = st.date_input("Tanggal Selesai", value=datetime.now().date())
        teknisi_ok = st.selectbox("Teknisi / Pelapor", ["-- Pilih Nama MP --"] + mp_list)
        mesin_ok = st.selectbox("Pilih Mesin Terpasang", ["-- Pilih Mesin --"] + machine_list)
    with col2:
        type_ok = st.text_input("TYPE", value="DME-010")
        seri_ok = st.text_input("SERIAL No.", value="2CB0421 A")
        qty_ok = st.number_input("Jumlah Qty OK", min_value=1, value=1)

    submitted_ok = st.form_submit_button("✅ Simpan Status Part OK")
    if submitted_ok:
        if teknisi_ok == "-- Pilih Nama MP --" or mesin_ok == "-- Pilih Mesin --":
            st.error("Teknisi dan Mesin wajib dipilih!")
        else:
            payload_ok_db = {
                "tanggal": str(tgl_ok), "shift": MP_DATA.get(teknisi_ok, "General"),
                "line": MACHINE_DATA.get(mesin_ok, "General Line"), "mesin": mesin_ok,
                "nama_part": "Dual Master Expander Device", "type_part": type_ok,
                "no_seri": seri_ok, "qty": int(qty_ok), "teknisi": teknisi_ok,
                "status_part": "Part OK", "foto_base64": ""
            }
            payload_ok_sheets = {
                "tanggal": str(tgl_ok), "nama": teknisi_ok, "shift": MP_DATA.get(teknisi_ok, "General"),
                "line": MACHINE_DATA.get(mesin_ok, "General Line"), "mesin": mesin_ok,
                "nama_part": "Dual Master Expander Device", "type_part": type_ok,
                "no_seri": seri_ok, "qty": int(qty_ok), "status": "Part OK"
            }
            if supabase:
                supabase.table("maintenance_log").insert(payload_ok_db).execute()
            requests.post(GOOGLE_SHEETS_URL, json=payload_ok_sheets)
            st.success("🎉 Data Part OK berhasil disimpan!")
