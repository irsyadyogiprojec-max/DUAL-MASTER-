import streamlit as st
import pandas as pd
from datetime import datetime
from PIL import Image
import io
import base64
import numpy as np
import requests
from supabase import create_client

try:
    import easyocr
    @st.cache_resource
    def load_ocr_reader():
        return easyocr.Reader(['en'], gpu=False)
    reader = load_ocr_reader()
    HAS_OCR = True
except ImportError:
    HAS_OCR = False

st.set_page_config(page_title="Input Part NG", page_icon="🔴", layout="wide")

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
    "M. Safiq": "General", "Eko P": "White", "Arif B": "Red", "Jaenal": "White",
    "Agus T": "Red", "Mas'ud": "Red", "Agus P": "Red", "Rendi K": "Red",
    "Eko M": "Staff", "Muhtarom": "Red", "Surya AS": "White", "Sigit R": "Green",
    "Tri M": "Red", "Mahdi R": "Green", "Agus Sonny": "White", "Annas G": "White",
    "Heru P": "White", "Jefry T": "Red", "M Wahyu": "White", "Ibrahim Hasan": "White",
    "M Derajat": "White", "Deni P": "Staff", "Mamun": "Staff", "Wahyu R": "Staff",
    "Rizky": "Staff", "Rain B": "White", "Irsyad": "White", "Ryan F": "Staff", "Asep": "Red"
}

MACHINE_DATA = {
    "IDR 052": "Cylinder Block", "Gondola": "Cylinder Block", "GRAFIR CR.SIZE": "Cylinder Block",
    "IAM 008": "Cylinder Block", "IAT 033": "Cylinder Block", "IAT 034": "Cylinder Block",
    "IBR 018": "Cylinder Block", "IBR 019": "Cylinder Block", "IBR 022": "Cylinder Block"
} # (Tambahkan data mesin lengkap Anda di sini jika perlu)
mp_list = list(MP_DATA.keys())
machine_list = list(MACHINE_DATA.keys())

st.markdown("# 🔴 Input Data Part NG (Dual Master)")
st.markdown("---")

if "extracted_type" not in st.session_state: st.session_state["extracted_type"] = ""
if "extracted_sn" not in st.session_state: st.session_state["extracted_sn"] = ""

uploaded_file = st.file_uploader("📷 Upload Foto Name Plate Dual Master", type=["png", "jpg", "jpeg"])
encoded_img = ""
if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, width=250)
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    encoded_img = base64.b64encode(buffered.getvalue()).decode("utf-8")

with st.form("form_input_ng", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        tanggal_input = st.date_input("Tanggal", value=datetime.now().date())
        nama_mp = st.selectbox("Nama MP / Pelapor", ["-- Pilih Nama MP --"] + mp_list)
        mesin_pilih = st.selectbox("Pilih Mesin Bermasalah", ["-- Pilih Mesin --"] + machine_list)
    with col2:
        type_part = st.text_input("TYPE", value=st.session_state["extracted_type"])
        nomor_seri = st.text_input("SERIAL No.", value=st.session_state["extracted_sn"])
        qty_part = st.number_input("Jumlah Part (Qty)", min_value=1, value=1)

    submitted = st.form_submit_button("🚨 Simpan & Kirim Data NG")
    if submitted:
        if nama_mp == "-- Pilih Nama MP --" or mesin_pilih == "-- Pilih Mesin --":
            st.error("Nama MP dan Mesin wajib dipilih!")
        else:
            payload_db = {
                "tanggal": str(tanggal_input), "shift": MP_DATA.get(nama_mp, "General"),
                "line": MACHINE_DATA.get(mesin_pilih, "General Line"), "mesin": mesin_pilih,
                "nama_part": "Dual Master Expander Device", "type_part": type_part,
                "no_seri": nomor_seri, "qty": int(qty_part), "teknisi": nama_mp,
                "status_part": "Part NG", "foto_base64": encoded_img
            }
            payload_sheets = {
                "tanggal": str(tanggal_input), "nama": nama_mp, "shift": MP_DATA.get(nama_mp, "General"),
                "line": MACHINE_DATA.get(mesin_pilih, "General Line"), "mesin": mesin_pilih,
                "nama_part": "Dual Master Expander Device", "type_part": type_part,
                "no_seri": nomor_seri, "qty": int(qty_part), "status": "Part NG"
            }
            if supabase:
                supabase.table("maintenance_log").insert(payload_db).execute()
            requests.post(GOOGLE_SHEETS_URL, json=payload_sheets)
            st.success("🎉 Data Part NG berhasil disimpan!")
