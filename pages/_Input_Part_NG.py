import streamlit as st
import datetime
from PIL import Image
import requests
import json

# 1. Konfigurasi Halaman (Menggunakan 'centered' agar tidak merenggang terlalu lebar)
st.set_page_config(page_title="Input Part NG", page_icon="❌", layout="centered")

# 2. CSS Custom Theme Luxury Dark & Glassmorphism
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

    /* Font Global */
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    /* Background Utama Dark Luxury Gradient */
    .stApp {
        background: linear-gradient(135deg, #0F1015 0%, #171922 100%);
        color: #E2E8F0;
    }

    /* Membatasi lebar kontainer agar rapi di tengah */
    .block-container {
        max-width: 800px !important;
        padding-top: 2.5rem;
        padding-bottom: 3rem;
    }

    /* Judul Utama */
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

    /* Label Input */
    label {
        color: #CBD5E1 !important;
        font-weight: 500 !important;
        font-size: 14px !important;
        margin-bottom: 6px !important;
    }

    /* Styling Kotak Input & Dropdown */
    div[data-baseweb="input"], 
    div[data-baseweb="select"] > div {
        background-color: #1E2230 !important;
        border: 1px solid #333A4E !important;
        border-radius: 8px !important;
        color: #FFFFFF !important;
    }

    div[data-baseweb="input"]:focus-within, 
    div[data-baseweb="select"]:focus-within {
        border-color: #D4AF37 !important;
        box-shadow: 0 0 8px rgba(212, 175, 55, 0.3) !important;
    }

    /* Teks dalam Input & Dropdown */
    input {
        color: #FFFFFF !important;
    }
    
    div[data-baseweb="select"] * {
        color: #FFFFFF !important;
        background-color: #1E2230 !important;
    }

    /* File Uploader Styling */
    div[data-testid="stFileUploader"] {
        background-color: #1E2230;
        border: 1.5px dashed #D4AF37;
        border-radius: 10px;
        padding: 12px;
    }

    div[data-testid="stFileUploader"] section {
        background-color: transparent !important;
    }

    /* Tombol Simpan Mewah (Marun + Emas Glow) */
    div.stButton > button {
        background: linear-gradient(135deg, #8B1E37 0%, #5B1021 100%) !important;
        color: #FFF !important;
        border: 1px solid #D4AF37 !important;
        font-weight: 700 !important;
        font-size: 16px !important;
        padding: 14px 28px !important;
        border-radius: 8px !important;
        width: 100% !important;
        box-shadow: 0 4px 15px rgba(139, 30, 55, 0.5);
        transition: all 0.3s ease !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-top: 15px;
    }

    div.stButton > button:hover {
        background: linear-gradient(135deg, #A82544 0%, #75152B 100%) !important;
        color: #F3E5AB !important;
        box-shadow: 0 6px 20px rgba(212, 175, 55, 0.4);
        transform: translateY(-2px);
    }
    </style>
""", unsafe_allow_html=True)

# 3. Database Data
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
mp_list = ["-- Pilih MP --"] + sorted(list(MP_DATA.keys()))

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
mesin_list = ["-- Pilih Mesin --"] + sorted(list(MACHINE_LINE_MAPPING.keys()))

# 4. Header UI
st.markdown('<div class="title-text">❌ Input Part NG (Not Good)</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle-text">Formulir pelaporan part tidak sesuai standar</div>', unsafe_allow_html=True)

# 5. Area Upload Foto
st.markdown("**📸 Foto Name Plate Part NG**")
uploaded_file = st.file_uploader("", type=["jpg", "jpeg", "png"], help="Upload foto komponen yang bermasalah (Maks 200MB)")

st.write("")

# 6. Grid Form Input
col1, col2 = st.columns(2)

with col1:
    tanggal_temuan = st.date_input("Tanggal Temuan", datetime.date.today())
    nama_teknisi = st.selectbox("Nama Teknisi / MP", mp_list)
    serial_no = st.text_input("Serial No. Part", placeholder="Contoh: SN-12345")
    qty = st.number_input("Qty", min_value=1, value=1, step=1)

with col2:
    nama_part = st.text_input("Nama Part", placeholder="Masukkan nama part")
    tipe_part = st.text_input("Type", placeholder="Masukkan tipe part")
    nama_mesin = st.selectbox("Mesin", mesin_list)

st.write("")

# 7. Tombol Simpan
if st.button("SIMPAN DATA PART NG"):
    if nama_teknisi == "-- Pilih MP --":
        st.error("Silakan pilih Nama Teknisi / MP terlebih dahulu.")
    elif nama_mesin == "-- Pilih Mesin --":
        st.error("Silakan pilih Mesin terlebih dahulu.")
    elif not nama_part or not serial_no:
        st.error("Harap isi Nama Part dan Serial No.")
    else:
        line_mesin = MACHINE_LINE_MAPPING.get(nama_mesin, "Unknown Line")
        st.success(f"✅ Data berhasil disimpan untuk Line: {line_mesin}")
        st.balloons()
