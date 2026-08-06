import streamlit as st
import datetime
from PIL import Image
import io
import base64
import numpy as np
import requests

try:
    import easyocr
    @st.cache_resource
    def load_ocr_reader():
        return easyocr.Reader(['en'], gpu=False)
    reader = load_ocr_reader()
    HAS_OCR = True
except ImportError:
    HAS_OCR = False

st.set_page_config(page_title="Input Part NG", page_icon="❌", layout="wide")

# Styling CSS Tema Mewah (Dominan Putih/Krim, Marun, dan Aksen Gold)
st.markdown("""
    <style>
    .stApp {
        background-color: #FDFBF7;
    }
    h1, h2, h3 {
        color: #5A1827 !important;
    }
    p, label, .stMarkdown {
        color: #2C2C2C !important;
    }
    .stButton>button {
        background-color: #6b1d2f;
        color: #D4AF37;
        border: 1px solid #D4AF37;
        border-radius: 6px;
        width: 100%;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #8c263d;
        color: #FFFFFF;
        border-color: #FFFFFF;
    }
    </style>
""", unsafe_allow_html=True)

SHEETS_URL = "https://script.google.com/macros/s/AKfycbxsUPF4TJ-IWd6N2vam8mBAwcuzqG0lOcSuVu5PCW2TkCZeKGqMhO5GixLCsw6oOmQX/exec"

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

# Mapping Mesin dan Line Lengkap berdasarkan data Anda
MACHINE_LINE_MAPPING = {
    "IDR 052": "Cylinder Block", "Gondola": "Cylinder Block", "GRAFIR CR.SIZE": "Cylinder Block",
    "IAM 008": "Cylinder Block", "IAT 033": "Cylinder Block", "IAT 034": "Cylinder Block",
    "IBR 018": "Cylinder Block", "IBR 019": "Cylinder Block", "IBR 022": "Cylinder Block",
    "IBR 024": "Cylinder Block", "IBR 025": "Cylinder Block", "IBR 026": "Cylinder Block",
    "IBR 027": "Cylinder Block", "IBR 028": "Cylinder Block", "IBR 029": "Cylinder Block",
    "IDR 044": "Cylinder Block", "IDR 045": "Cylinder Block", "IDR 046": "Cylinder Block",
    "IDR 047": "Cylinder Block", "IDR 048": "Cylinder Block", "IDR 049": "Cylinder Block",
    "IDR 050": "Cylinder Block", "IDR 051": "Cylinder Block", "IDR 052": "Cylinder Block",
    "IDR 053": "Cylinder Block", "IDR 054": "Cylinder Block", "IDR 055": "Cylinder Block",
    "IDR 056": "Cylinder Block", "IDR 057": "Cylinder Block", "IDR 058": "Cylinder Block",
    "IDR 059": "Cylinder Block", "IDR 060": "Cylinder Block", "IDR 061": "Cylinder Block",
    "IDR 062": "Cylinder Block", "IDR 065": "Cylinder Block", "IDR 066": "Cylinder Block",
    "IDR 067": "Cylinder Block", "IDR 068": "Cylinder Block", "IDR 069": "Cylinder Block",
    "IDR 071": "Cylinder Block", "IGR 023": "Cylinder Block", "IGR 045": "Cylinder Block",
    "IGR 046": "Cylinder Block", "IMI 033": "Cylinder Block", "IMI 034": "Cylinder Block",
    "IMI 035": "Cylinder Block", "IMI 036": "Cylinder Block", "IMI 037": "Cylinder Block",
    "IMI 039": "Cylinder Block", "IMI 045": "Cylinder Block", "IMI 046": "Cylinder Block",
    "IMM 014": "Cylinder Block", "IMM 015": "Cylinder Block", "ISP 074": "Cylinder Block",
    "ISP 075": "Cylinder Block", "ISP 076": "Cylinder Block", "ISP 077": "Cylinder Block",
    "ISP 078": "Cylinder Block", "ISP 079": "Cylinder Block", "ISP 080": "Cylinder Block",
    "ISP 081": "Cylinder Block", "ISP 082": "Cylinder Block", "ISP 083": "Cylinder Block",
    "ISP 084": "Cylinder Block", "ISP 085": "Cylinder Block", "ISP 086": "Cylinder Block",
    "ISP 087": "Cylinder Block", "ISP 088": "Cylinder Block", "ISP 089": "Cylinder Block",
    "ISP 095": "Cylinder Block", "ISP 096": "Cylinder Block", "ISP 097": "Cylinder Block",
    "ISP 098": "Cylinder Block", "ISPS 027": "Cylinder Block", "ISPS 028": "Cylinder Block",
    "ISPS 029": "Cylinder Block", "ISPS 030": "Cylinder Block", "ISPS 031": "Cylinder Block",
    "ISPS 032": "Cylinder Block", "ISPS 033": "Cylinder Block", "ISPS 036": "Cylinder Block",
    "ISPS 037": "Cylinder Block", "ITP 004": "Cylinder Block", "ITS 005": "Cylinder Block",
    "ITS 015": "Cylinder Block", "ITS 016": "Cylinder Block", "ITS 033": "Cylinder Block",
    "IWB 026": "Cylinder Block", "IWB 032": "Cylinder Block", "IWB 033": "Cylinder Block",
    "Junbiki": "Cylinder Block", "LASER MARKING CB": "Cylinder Block", "COBOT": "Cylinder Head",
    "DAISHA": "Cylinder Head", "IAT 001": "Cylinder Head", "IAT 002": "Cylinder Head",
    "IAT 003": "Cylinder Head", "IDR 040": "Cylinder Head", "IMI 040": "Cylinder Head",
    "ISP 005": "Cylinder Head", "ISP 009": "Cylinder Head", "ISP 016": "Cylinder Head",
    "ISP 018": "Cylinder Head", "ISP 019": "Cylinder Head", "ISP 022": "Cylinder Head",
    "ISP 023": "Cylinder Head", "ISP 026": "Cylinder Head", "ISP 027": "Cylinder Head",
    "ISP 028": "Cylinder Head", "ISP 029": "Cylinder Head", "ISP 030": "Cylinder Head",
    "ISP 031": "Cylinder Head", "ISP 032": "Cylinder Head", "ISP 033": "Cylinder Head",
    "ISP 034": "Cylinder Head", "ISP 035": "Cylinder Head", "ISP 036": "Cylinder Head",
    "ISP 037": "Cylinder Head", "ISP 038": "Cylinder Head", "ISP 039": "Cylinder Head",
    "ISP 040": "Cylinder Head", "ISP 041": "Cylinder Head", "ISP 042": "Cylinder Head",
    "ISP 043": "Cylinder Head", "ISP 045": "Cylinder Head", "ISP 046": "Cylinder Head",
    "ISP 047": "Cylinder Head", "ISP 048": "Cylinder Head", "ISP 049": "Cylinder Head",
    "ISP 050": "Cylinder Head", "ISP 051": "Cylinder Head", "ISP 052": "Cylinder Head",
    "ISP 053": "Cylinder Head", "ISP 090": "Cylinder Head", "ISP 091": "Cylinder Head",
    "ISP 093": "Cylinder Head", "ISP 094": "Cylinder Head", "ISP 099": "Cylinder Head",
    "ISPS 001": "Cylinder Head", "ISPS 002": "Cylinder Head", "ISPS 003": "Cylinder Head",
    "ISPS 004": "Cylinder Head", "ISPS 005": "Cylinder Head", "ISPS 006": "Cylinder Head",
    "ISPS 007": "Cylinder Head", "ISPS 008": "Cylinder Head", "ISPS 009": "Cylinder Head",
    "ISPS 010": "Cylinder Head", "ISPS 011": "Cylinder Head", "ISPS 012": "Cylinder Head",
    "ISPS 013": "Cylinder Head", "ISPS 014": "Cylinder Head", "ISPS 015": "Cylinder Head",
    "ISPS 016": "Cylinder Head", "ISPS 017": "Cylinder Head", "ISPS 018": "Cylinder Head",
    "ISPS 019": "Cylinder Head", "ISPS 020": "Cylinder Head", "ISPS 021": "Cylinder Head",
    "ISPS 022": "Cylinder Head", "ISPS 023": "Cylinder Head", "ISPS 024": "Cylinder Head",
    "ISPS 025": "Cylinder Head", "ISPS 026": "Cylinder Head", "ISPS 034": "Cylinder Head",
    "ISPS 035": "Cylinder Head", "ISPS 036": "Cylinder Head", "ISPS 049": "Cylinder Head",
    "ITS 013": "Cylinder Head", "ITS 014": "Cylinder Head", "ITS 015": "Cylinder Head",
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
    "ISP 068": "Crank Shaft", "ILS 023": "Crank Shaft", "ILA 005": "Crank Shaft",
    "IZK 033": "Crank Shaft", "IWB 028": "Crank Shaft", "IGR 037": "Crank Shaft",
    "IGR 024": "Crank Shaft", "IGR 025": "Crank Shaft", "IGR 026": "Crank Shaft",
    "IGR 038": "Crank Shaft", "IGR 028": "Crank Shaft", "IGR 029": "Crank Shaft",
    "IMI 044": "Crank Shaft", "ITS 019": "Crank Shaft", "ILP 003": "Crank Shaft",
    "IZY 029": "Crank Shaft", "IWB 020": "Crank Shaft", "IAT 004": "Crank Shaft",
    "LASER MARKING CS": "Crank Shaft", "GRAFIR FINISH": "Crank Shaft", "ICE 002": "Cam Shaft",
    "IGR 032": "Cam Shaft", "IGR 034": "Cam Shaft", "IGR 039": "Cam Shaft",
    "IGR 040": "Cam Shaft", "IGR 041": "Cam Shaft", "IGR 042": "Cam Shaft",
    "IGR 043": "Cam Shaft", "IGR 044": "Cam Shaft", "IMIH 003": "Cam Shaft",
    "ISP 069": "Cam Shaft", "ISP 070": "Cam Shaft", "ISP 071": "Cam Shaft",
    "ISP 072": "Cam Shaft", "ISP 073": "Cam Shaft", "ISP 095": "Cam Shaft",
    "ISP 096": "Cam Shaft", "ILA 006": "Cam Shaft", "ILA 007": "Cam Shaft",
    "ILP 004": "Cam Shaft", "IWB 030": "Cam Shaft", "ILA 008": "Cam Shaft",
    "Press Pin": "Cam Shaft", "IZK 050": "Cam Shaft", "IZK 051": "Cam Shaft",
    "LASER MARKING CAM": "Cam Shaft", "Airblow": "Cam Shaft", "Gantry": "Cam Shaft",
    "Hoist No.6": "Assy Line", "Hoist No.7": "Assy Line", "IAM 003": "Assy Line",
    "IAM 004": "Assy Line", "IAM 005": "Assy Line", "IAM 007": "Assy Line",
    "IAM 009": "Assy Line", "ICK 3 1 1": "Assy Line", "ICK 3 1 2": "Assy Line",
    "ITS 020": "Assy Line", "ITS 021": "Assy Line", "ITS 023": "Assy Line",
    "ITS 024": "Assy Line", "ITS 025": "Assy Line", "ITS 026": "Assy Line",
    "ITS 028": "Assy Line", "ITS 029": "Assy Line", "ITS 030": "Assy Line",
    "ITS 031": "Assy Line", "ITS 032": "Assy Line", "IZK 021": "Assy Line",
    "IZK 038": "Assy Line", "IZK 039": "Assy Line", "IZK 040": "Assy Line",
    "IZK 041": "Assy Line", "IZK 041A": "Assy Line", "IZK 042": "Assy Line",
    "IZK 043": "Assy Line", "IZK 045": "Assy Line", "IZK 046": "Assy Line",
    "IZK 047": "Assy Line", "IZY 023": "Assy Line", "IZY 024": "Assy Line",
    "IZY 027": "Assy Line", "IZY 028": "Assy Line", "IZY 029": "Assy Line",
    "IZY 030": "Assy Line", "IZY 031": "Assy Line", "IZYL 001": "Assy Line",
    "IZYL 003": "Assy Line", "IAM 011": "Assy Line", "IAM 012": "Assy Line",
    "IAM 013": "Assy Line", "IAM 014": "Assy Line", "IAM 015": "Assy Line",
    "AAM 105": "Assy Line", "IZK 048": "Assy Line", "ICK 3-1-2": "Assy Line",
    "ICK 3-1-1": "Assy Line", "IZYL 004": "Assy Line"
}

machine_list = list(MACHINE_LINE_MAPPING.keys())

st.markdown("### ❌ Input part NG (not good)")
st.markdown("<p style='color: #666666; margin-top: -15px;'>Formulir pelaporan part tidak sesuai standar</p>", unsafe_allow_html=True)
st.markdown("---")

if "ng_type" not in st.session_state: st.session_state["ng_type"] = ""
if "ng_sn" not in st.session_state: st.session_state["ng_sn"] = ""

uploaded_file = st.file_uploader("📷 Foto name plate part NG (PNG atau JPG, maks 200MB)", type=["png", "jpg", "jpeg"])
if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, width=250)
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
                st.session_state["ng_type"] = detected_type if detected_type else ""
                st.session_state["ng_sn"] = detected_sn if detected_sn else ""
            except:
                pass

with st.form("form_ng", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        tanggal = st.date_input("Tanggal temuan", value=datetime.date.today())
        teknisi = st.selectbox("Nama teknisi / MP", ["-- Pilih --"] + mp_list)
        no_seri = st.text_input("Serial No. part", value=st.session_state["ng_sn"], placeholder="SN-000000")
    with col2:
        nama_part = st.text_input("Nama part", value="Dual Master Expander Device", disabled=True)
        type_part = st.text_input("Type", value=st.session_state["ng_type"], placeholder="Masukkan tipe part")
        mesin = st.selectbox("Mesin", ["-- Pilih Mesin --"] + machine_list)

    qty = st.number_input("Qty", min_value=1, value=1)

    submitted = st.form_submit_button("💾 Simpan data part NG")
    if submitted:
        if teknisi == "-- Pilih --":
            st.error("Nama Teknisi wajib dipilih!")
        elif mesin == "-- Pilih Mesin --":
            st.error("Mesin wajib dipilih!")
        else:
            shift = MP_DATA.get(teknisi, "General")
            # Otomatis tentukan Line berdasarkan Mesin yang dipilih dari database
            line_terdeteksi = MACHINE_LINE_MAPPING.get(mesin, "-")

            payload = {
                "action": "NG", 
                "tanggal": str(tanggal), 
                "nama": teknisi, 
                "shift": shift,
                "line": line_terdeteksi,  # Otomatis masuk ke Spreadsheet
                "mesin": mesin, 
                "nama_part": nama_part, 
                "type_part": type_part if type_part else "-",
                "no_seri": no_seri if no_seri else "-", 
                "qty": int(qty), 
                "status": "NG"  # Status otomatis NG
            }
            
            try:
                requests.post(SHEETS_URL, json=payload)
                st.success("Data Part NG Berhasil Disimpan!")
            except Exception as err:
                st.warning(f"Gagal koneksi ke Sheets: {err}")
                
            st.session_state["ng_type"] = ""
            st.session_state["ng_sn"] = ""
