import streamlit as st
import datetime
from PIL import Image
import requests
import json
import numpy as np

# Konfigurasi Halaman
st.set_page_config(page_title="Input Part NG", page_icon="❌", layout="wide")

# --- CSS Styling untuk Tema Mewah Marun & Gold ---
st.markdown("""
    <style>
    /* Background Utama Putih */
    .stApp {
        background-color: #FFFFFF;
    }
    
    /* Judul Utama - Marun */
    h1, h2, h3 {
        color: #5A1827 !important;
        font-weight: 600;
    }
    
    /* Label Teks - Abu-abu Gelap */
    p, label, .stMarkdown {
        color: #333333 !important;
    }

    /* --- Styling Kotak Input (Dark Mode inside White) --- */
    /* Input Text, Date, Number */
    div.stTextInput > div > div > input, 
    div.stDateInput > div > div > input,
    div.stNumberInput > div > div > input {
        background-color: #262626 !important; /* Abu-abu Sangat Gelap */
        color: #FFFFFF !important; /* Teks Putih */
        border-radius: 4px;
        border: 1px solid #404040;
        font-family: monospace;
    }
    
    /* Dropdown Selectbox */
    div.stSelectbox > div > div > div {
        background-color: #262626 !important;
        color: #FFFFFF !important;
        border-radius: 4px;
        border: 1px solid #404040;
    }
    /* Warna ikon panah dropdown */
    div.stSelectbox svg {
        fill: #D4AF37 !important; /* Gold */
    }

    /* Placeholder text color */
    ::placeholder { color: #AAAAAA !important; }

    /* --- Styling Area Upload File --- */
    div.stFileUploader {
        background-color: #FDFDFD;
        border: 1px solid #E0E0E0;
        border-radius: 5px;
        padding: 10px;
    }
    /* Tombol upload di dalam box */
    div.stFileUploader > section > button {
        background-color: #5A1827 !important; /* Marun */
        color: #FFFFFF !important;
        border: none;
    }

    /* --- Styling Tombol Simpan Utama --- */
    .stButton>button {
        background-color: #5A1827 !important; /* Marun Solid */
        color: #F3E5AB !important; /* Gold Muda */
        border: 1px solid #D4AF37 !important; /* Gold Tua */
        border-radius: 4px;
        width: 100%;
        font-weight: bold;
        padding: 10px;
        font-size: 16px;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .stButton>button:hover {
        background-color: #751F33 !important; /* Marun Lebih Terang saat hover */
        color: #FFFFFF !important;
        border-color: #FFFFFF !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- Inisialisasi OCR (Opsional) ---
try:
    import easyocr
    @st.cache_resource
    def load_ocr_reader():
        return easyocr.Reader(['en'], gpu=False)
    reader = load_ocr_reader()
    HAS_OCR = True
except ImportError:
    HAS_OCR = False
    st.sidebar.warning("EasyOCR tidak terinstall. Fitur scan foto dimatikan.")

# --- Konfigurasi Google Sheets ---
SHEETS_URL = "https://script.google.com/macros/s/AKfycbxsUPF4TJ-IWd6N2vam8mBAwcuzqG0lOcSuVu5PCW2TkCZeKGqMhO5GixLCsw6oOmQX/exec"

# --- Database MP (Teknisi) ---
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
mp_list = ["-- Pilih --"] + list(MP_DATA.keys())

# --- Database Mesin & Line Lengkap (SUDAH DIPERBAIKI) ---
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
    "ISP 068": "Crank Shaft", "ILS 023": "Crank Shaft", "ILA 005
