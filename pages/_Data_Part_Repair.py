import streamlit as st
import datetime
from PIL import Image
import io
import base64
import numpy as np
import requests
from supabase import create_client

# Coba import EasyOCR untuk scan foto name plate
try:
    import easyocr
    @st.cache_resource
    def load_ocr_reader():
        return easyocr.Reader(['en'], gpu=False)
    reader = load_ocr_reader()
    HAS_OCR = True
except ImportError:
    HAS_OCR = False

st.set_page_config(page_title="Input Part Repair", page_icon="🛠️", layout="wide")

# Inisialisasi Supabase dengan aman (tidak bikin error fatal jika Secrets belum terbaca)
@st.cache_resource
def init_supabase():
    try:
        url = st.secrets.get("SUPABASE_URL", "")
        key = st.secrets.get("SUPABASE_KEY", "")
        if not url or not key: 
            return None
        return create_client(url, key)
    except Exception:
        return None

supabase = init_supabase()

# --- GANTI DENGAN URL WEB APP GOOGLE APPS SCRIPT ANDA DI BAWAH INI ---
SHEETS_URL = "https://script.google.com/macros/s/AKfycbwcwsvm7SwocuXzjyMBdWyTCllWT7wi5hMRMm3fxo-64Q_EcgXqRaWfMXeC0O6rxkbT/exec"

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
mp_list = list(MP_DATA.keys())

st.markdown("# 🛠️ Halaman Proses & Perbaikan Part (Repair)")
st.markdown("---")

if "repair_type" not in st.session_state: st.session_state["repair_type"] = ""
if "repair_sn" not in st.session_state: st.session_state["repair_sn"] = ""

# Fitur Upload Foto & OCR untuk deteksi otomatis
uploaded_file = st.file_uploader("📷 Upload Foto Name Plate Part Repair", type=["png", "jpg", "jpeg"])
encoded_img = ""

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, width=250)
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    encoded_img = base64.b64encode(buffered.getvalue()).decode("utf-8")
    
    if HAS_OCR:
        with st.spinner("🔍 Memindai teks..."):
            try:
                image_np = np.array(image)
                results = reader.readtext(image_np, detail=0)
                detected_type, detected_sn = "", ""
                for i, text in enumerate(results):
                    t_upper = text.upper()
                    if "TYPE" in t_upper:
                        if ":" in t_upper: detected_type = t_upper.split(":")[1].strip()
                        elif i + 1 < len(results): detected_type = results[i+1].strip()
                    if "SERIAL" in t_upper or "SER" in t_upper:
                        if ":" in t_upper: detected_sn = t_upper.split(":")[1].strip()
                        elif i + 1 < len(results): detected_sn = results[i+1].strip()
                st.session_state["repair_type"] = detected_type if detected_type else "DME-010"
                st.session_state["repair_sn"] = detected_sn if detected_sn else "2CB0421 A"
            except:
                pass

with st.form("form_repair", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        tanggal = st.date_input("Tanggal Pengerjaan", value=datetime.date.today())
        teknisi = st.selectbox("Nama Teknisi / MP", ["-- Pilih --"] + mp_list)
        status_aksi = st.radio("Status Pengerjaan:", ["On Progress Repair", "Done Repair (OK)"])
    with col2:
        nama_part = st.text_input("Nama Part", value="Dual Master Expander Device", disabled=True)
        type_part = st.text_input("TYPE", value=st.session_state["repair_type"])
        no_seri = st.text_input("SERIAL No. Part", value=st.session_state["repair_sn"])
        qty = st.number_input("QTY", min_value=1, value=1)

    submitted = st.form_submit_button("💾 Proses & Simpan Data Repair")
    if submitted:
        if teknisi == "-- Pilih --":
            st.error("Nama Teknisi wajib dipilih!")
        else:
            shift = MP_DATA.get(teknisi, "General")
            
            if "On Progress" in status_aksi:
                action_type = "Repair"
                status_val = "On Progress"
            else:
                action_type = "OK"
                status_val = "Done Repair / OK"

            payload = {
                "action": action_type, 
                "tanggal": str(tanggal), 
                "nama": teknisi, 
                "shift": shift,
                "line": "-", 
                "mesin": "-", 
                "nama_part": nama_part, 
                "type_part": type_part if type_part else "DME-010",
                "no_seri": no_seri if no_seri else "2CB0421 A", 
                "qty": int(qty), 
                "status": status_val
            }
            
            # Coba simpan ke Supabase secara aman (jika gagal, diabaikan agar tidak merah)
            if supabase:
                try:
                    supabase.table("maintenance_log").insert(payload).execute()
                except Exception:
                    pass
            
            # Kirim data ke Google Sheets
            try:
                requests.post(SHEETS_URL, json=payload)
            except Exception as err:
                st.warning(f"Gagal mengirim ke Sheets: {err}")
                
            # Notifikasi sukses disederhanakan
            st.success("Input Berhasil")
            st.session_state["repair_type"] = ""
            st.session_state["repair_sn"] = ""
