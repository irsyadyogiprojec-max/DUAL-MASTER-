import streamlit as st
import datetime
import re
import requests
import numpy as np
from PIL import Image

# 1. Konfigurasi Halaman & Endpoint Google Sheets dari Kodingan Lama
st.set_page_config(page_title="Input Part NG", page_icon="❌", layout="centered")

SHEETS_URL = "https://script.google.com/macros/s/AKfycbxsUPF4TJ-IWd6N2vam8mBAwcuzqG0lOcSuVu5PCW2TkCZeKGqMhO5GixLCsw6oOmQX/exec"

# 2. Inisialisasi State OCR
if "ng_type" not in st.session_state: 
    st.session_state["ng_type"] = ""
if "ng_sn" not in st.session_state: 
    st.session_state["ng_sn"] = ""
if "ng_name" not in st.session_state:
    st.session_state["ng_name"] = ""

# 3. OCR Engine Setup (EasyOCR dengan fallback)
try:
    import easyocr
    @st.cache_resource
    def load_ocr_reader():
        return easyocr.Reader(['en'], gpu=False)
    reader = load_ocr_reader()
    HAS_OCR = True
except ImportError:
    HAS_OCR = False

# 4. Custom Dark CSS
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    .stApp {
        background: linear-gradient(135deg, #0F1015 0%, #171922 100%);
        color: #E2E8F0;
    }
    .block-container {
        max-width: 800px !important;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }
    .title-text {
        color: #F3E5AB;
        font-size: 26px;
        font-weight: 700;
        margin-bottom: 4px;
    }
    .subtitle-text {
        color: #94A3B8;
        font-size: 14px;
        margin-bottom: 20px;
    }
    label {
        color: #CBD5E1 !important;
        font-weight: 500 !important;
        font-size: 14px !important;
    }
    div[data-baseweb="input"], div[data-baseweb="select"] > div {
        background-color: #1E2230 !important;
        border: 1px solid #333A4E !important;
        border-radius: 8px !important;
        color: #FFFFFF !important;
    }
    div[data-testid="stFileUploader"] {
        background-color: #1E2230;
        border: 1.5px dashed #D4AF37;
        border-radius: 10px;
        padding: 10px;
    }
    div.stButton > button {
        background: linear-gradient(135deg, #8B1E37 0%, #5B1021 100%) !important;
        color: #FFF !important;
        border: 1px solid #D4AF37 !important;
        font-weight: 700 !important;
        font-size: 16px !important;
        padding: 12px 28px !important;
        border-radius: 8px !important;
        width: 100% !important;
        margin-top: 15px;
    }
    </style>
""", unsafe_allow_html=True)

# 5. Master Data (MP & Mesin Mapping)
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
mp_list = sorted(list(MP_DATA.keys()))

MACHINE_LINE_MAPPING = {
    "IDR 052": "Cylinder Block", "Gondola": "Cylinder Block", "GRAFIR CR.SIZE": "Cylinder Block",
    "IAM 008": "Cylinder Block", "IAT 033": "Cylinder Block", "IAT 034": "Cylinder Block",
    "IBR 018": "Cylinder Block", "IBR 019": "Cylinder Block", "IBR 022": "Cylinder Block",
    "IBR 024": "Cylinder Block", "IBR 025": "Cylinder Block", "IBR 026": "Cylinder Block",
    "IBR 027": "Cylinder Block", "IBR 028": "Cylinder Block", "IBR 029": "Cylinder Block",
    "IDR 044": "Cylinder Block", "IDR 045": "Cylinder Block", "IDR 046": "Cylinder Block",
    "IDR 047": "Cylinder Block", "IDR 048": "Cylinder Block", "IDR 049": "Cylinder Block",
    "IDR 050": "Cylinder Block", "IDR 051": "Cylinder Block", "IDR 053": "Cylinder Block",
    "IDR 054": "Cylinder Block", "IDR 055": "Cylinder Block", "IDR 056": "Cylinder Block",
    "IDR 057": "Cylinder Block", "IDR 058": "Cylinder Block", "IDR 059": "Cylinder Block",
    "IDR 060": "Cylinder Block", "IDR 061": "Cylinder Block", "IDR 062": "Cylinder Block",
    "IDR 065": "Cylinder Block", "IDR 066": "Cylinder Block", "IDR 067": "Cylinder Block",
    "IDR 068": "Cylinder Block", "IDR 069": "Cylinder Block", "IDR 071": "Cylinder Block",
    "IGR 023": "Cylinder Block", "IGR 045": "Cylinder Block", "IGR 046": "Cylinder Block",
    "IMI 033": "Cylinder Block", "IMI 034": "Cylinder Block", "IMI 035": "Cylinder Block",
    "IMI 036": "Cylinder Block", "IMI 037": "Cylinder Block", "IMI 039": "Cylinder Block",
    "IMI 045": "Cylinder Block", "IMI 046": "Cylinder Block", "IMM 014": "Cylinder Block",
    "IMM 015": "Cylinder Block", "ISP 074": "Cylinder Block", "ISP 075": "Cylinder Block",
    "ISP 076": "Cylinder Block", "ISP 077": "Cylinder Block", "ISP 078": "Cylinder Block",
    "ISP 079": "Cylinder Block", "ISP 080": "Cylinder Block", "ISP 081": "Cylinder Block",
    "ISP 082": "Cylinder Block", "ISP 083": "Cylinder Block", "ISP 084": "Cylinder Block",
    "ISP 085": "Cylinder Block", "ISP 086": "Cylinder Block", "ISP 087": "Cylinder Block",
    "ISP 088": "Cylinder Block", "ISP 089": "Cylinder Block", "ISP 095": "Cylinder Block",
    "ISP 096": "Cylinder Block", "ISP 097": "Cylinder Block", "ISP 098": "Cylinder Block",
    "ISPS 027": "Cylinder Block", "ISPS 028": "Cylinder Block", "ISPS 029": "Cylinder Block",
    "ISPS 030": "Cylinder Block", "ISPS 031": "Cylinder Block", "ISPS 032": "Cylinder Block",
    "ISPS 033": "Cylinder Block", "ISPS 036": "Cylinder Block", "ISPS 037": "Cylinder Block",
    "ITP 004": "Cylinder Block", "ITS 005": "Cylinder Block", "ITS 015": "Cylinder Block",
    "ITS 016": "Cylinder Block", "ITS 033": "Cylinder Block", "IWB 026": "Cylinder Block",
    "IWB 032": "Cylinder Block", "IWB 033": "Cylinder Block", "Junbiki": "Cylinder Block",
    "LASER MARKING CB": "Cylinder Block", "COBOT": "Cylinder Head", "DAISHA": "Cylinder Head",
    "IAT 001": "Cylinder Head", "IAT 002": "Cylinder Head", "IAT 003": "Cylinder Head",
    "IDR 040": "Cylinder Head", "IMI 040": "Cylinder Head", "ISP 005": "Cylinder Head",
    "ISP 009": "Cylinder Head", "ISP 016": "Cylinder Head", "ISP 018": "Cylinder Head",
    "ISP 019": "Cylinder Head", "ISP 022": "Cylinder Head", "ISP 023": "Cylinder Head",
    "ISP 026": "Cylinder Head", "ISP 027": "Cylinder Head", "ISP 028": "Cylinder Head",
    "ISP 029": "Cylinder Head", "ISP 030": "Cylinder Head", "ISP 031": "Cylinder Head",
    "ISP 032": "Cylinder Head", "ISP 033": "Cylinder Head", "ISP 034": "Cylinder Head",
    "ISP 035": "Cylinder Head", "ISP 036": "Cylinder Head", "ISP 037": "Cylinder Head",
    "ISP 038": "Cylinder Head", "ISP 039": "Cylinder Head", "ISP 040": "Cylinder Head",
    "ISP 041": "Cylinder Head", "ISP 042": "Cylinder Head", "ISP 043": "Cylinder Head",
    "ISP 045": "Cylinder Head", "ISP 046": "Cylinder Head", "ISP 047": "Cylinder Head",
    "ISP 048": "Cylinder Head", "ISP 049": "Cylinder Head", "ISP 050": "Cylinder Head",
    "ISP 051": "Cylinder Head", "ISP 052": "Cylinder Head", "ISP 053": "Cylinder Head",
    "ISP 090": "Cylinder Head", "ISP 091": "Cylinder Head", "ISP 093": "Cylinder Head",
    "ISP 094": "Cylinder Head", "ISP 099": "Cylinder Head", "ISPS 001": "Cylinder Head",
    "ISPS 002": "Cylinder Head", "ISPS 003": "Cylinder Head", "ISPS 004": "Cylinder Head",
    "ISPS 005": "Cylinder Head", "ISPS 006": "Cylinder Head", "ISPS 007": "Cylinder Head",
    "ISPS 008": "Cylinder Head", "ISPS 009": "Cylinder Head", "ISPS 010": "Cylinder Head",
    "ISPS 011": "Cylinder Head", "ISPS 012": "Cylinder Head", "ISPS 013": "Cylinder Head",
    "ISPS 014": "Cylinder Head", "ISPS 015": "Cylinder Head", "ISPS 016": "Cylinder Head",
    "ISPS 017": "Cylinder Head", "ISPS 018": "Cylinder Head", "ISPS 019": "Cylinder Head",
    "ISPS 020": "Cylinder Head", "ISPS 021": "Cylinder Head", "ISPS 022": "Cylinder Head",
    "ISPS 023": "Cylinder Head", "ISPS 024": "Cylinder Head", "ISPS 025": "Cylinder Head",
    "ISPS 026": "Cylinder Head", "ISPS 034": "Cylinder Head", "ISPS 035": "Cylinder Head",
    "ISPS 049": "Cylinder Head", "ITS 013": "Cylinder Head", "ITS 014": "Cylinder Head",
    "IWB 022": "Cylinder Head", "IWBS 001": "Cylinder Head", "IZK 044": "Cylinder Head",
    "IZK 046": "Cylinder Head", "IZK 047": "Cylinder Head", "IZK 048": "Cylinder Head",
    "IZK 049": "Cylinder Head", "KARAKURI PARALEL A": "Cylinder Head", "LASER MARKING": "Cylinder Head",
    "ITS 017": "Crank Shaft", "ILA 003": "Crank Shaft", "ILA 004": "Crank Shaft",
    "IMI 041": "Crank Shaft", "IZY 018": "Crank Shaft", "ILS 022": "Crank Shaft",
    "IMI 042": "Crank Shaft", "IMI 043": "Crank Shaft", "IZY 019": "Crank Shaft",
    "ISP 054": "Crank Shaft", "ISP 055": "Crank Shaft", "ISP 056": "Crank Shaft",
    "ISP 057": "Crank Shaft", "IWB 027": "Crank Shaft", "IMIH 014": "Crank Shaft",
    "ISP 063": "Crank Shaft", "ISP 064": "Crank Shaft", "ISP 065": "Crank Shaft",
    "ISP 066": "Crank Shaft", "ISP 067": "Crank Shaft", "ISP 060": "Crank Shaft",
    "ISP 068": "Crank Shaft", "ILS 023": "Crank Shaft", "ILA 005": "Crank Shaft"
}
mesin_list = sorted(list(MACHINE_LINE_MAPPING.keys()))

# 6. Header
st.markdown('<div class="title-text">❌ Input Part NG (Not Good)</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle-text">Formulir pelaporan part tidak sesuai standar</div>', unsafe_allow_html=True)

# 7. File Upload & Process OCR
uploaded_file = st.file_uploader("📷 Upload Foto Name Plate Part NG", type=["png", "jpg", "jpeg"])
if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, width=300)
    
    if HAS_OCR:
        with st.spinner("🔍 Memindai teks dari foto..."):
            try:
                image_np = np.array(image)
                results = reader.readtext(image_np, detail=0)
                detected_type, detected_sn, detected_name = "", "", ""
                
                for i, text in enumerate(results):
                    t_upper = text.upper()
                    if "TYPE" in t_upper or "MODEL" in t_upper:
                        if ":" in t_upper: detected_type = t_upper.split(":")[1].strip()
                        elif i + 1 < len(results): detected_type = results[i+1].strip()
                    if "SERIAL" in t_upper or "S/N" in t_upper or "SER" in t_upper:
                        if ":" in t_upper: detected_sn = t_upper.split(":")[1].strip()
                        elif i + 1 < len(results): detected_sn = results[i+1].strip()
                    if "NAME" in t_upper or "PART" in t_upper:
                        if ":" in t_upper: detected_name = t_upper.split(":")[1].strip()

                if detected_type: st.session_state["ng_type"] = detected_type
                if detected_sn: st.session_state["ng_sn"] = detected_sn
                if detected_name: st.session_state["ng_name"] = detected_name
            except Exception:
                pass

st.write("")

# 8. Form Utama
with st.form("form_ng", clear_on_submit=False):
    col1, col2 = st.columns(2)
    
    with col1:
        tanggal = st.date_input("Tanggal Temuan", value=datetime.date.today())
        teknisi = st.selectbox("Nama Teknisi / MP", ["-- Pilih MP --"] + mp_list)
        mesin = st.selectbox("Mesin", ["-- Pilih Mesin --"] + mesin_list)
        status_aksi = st.radio("Status NG:", ["Pending Analisa", "Scrap / Reject"])
        
    with col2:
        nama_part = st.text_input("Nama Part", value=st.session_state.get("ng_name", ""), placeholder="Masukkan nama part")
        type_part = st.text_input("TYPE", value=st.session_state.get("ng_type", ""), placeholder="Masukkan tipe part")
        no_seri = st.text_input("SERIAL No. Part", value=st.session_state.get("ng_sn", ""), placeholder="Contoh: SN-12345")
        qty = st.number_input("QTY", min_value=1, value=1, step=1)

    submitted = st.form_submit_button("💾 Simpan Data Part NG")

    if submitted:
        if teknisi == "-- Pilih MP --":
            st.error("Nama Teknisi wajib dipilih!")
        elif mesin == "-- Pilih Mesin --":
            st.error("Mesin wajib dipilih!")
        elif not nama_part or not no_seri:
            st.error("Nama Part dan Serial No. wajib diisi!")
        else:
            shift = MP_DATA.get(teknisi, "General")
            line = MACHINE_LINE_MAPPING.get(mesin, "Unknown Line")

            # Payload persis seperti skema Google Apps Script lama Anda
            payload = {
                "action": "NG", 
                "tanggal": str(tanggal), 
                "nama": teknisi, 
                "shift": shift,
                "line": line, 
                "mesin": mesin, 
                "nama_part": nama_part, 
                "type_part": type_part,
                "no_seri": no_seri, 
                "qty": int(qty), 
                "status": status_aksi
            }
            
            with st.spinner("⏳ Mengirim data ke Spreadsheet..."):
                try:
                    res = requests.post(SHEETS_URL, json=payload, timeout=10)
                    st.success(f"Input Berhasil! Data tersimpan di Line: {line}")
                    st.balloons()
                    
                    # Reset state setelah sukses
                    st.session_state["ng_type"] = ""
                    st.session_state["ng_sn"] = ""
                    st.session_state["ng_name"] = ""
                except Exception as err:
                    st.error(f"Gagal koneksi ke Sheets: {err}")
