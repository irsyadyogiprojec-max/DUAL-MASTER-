import streamlit as st
import pandas as pd
from datetime import datetime
from PIL import Image
import io
import base64
from supabase import create_client

# Coba import EasyOCR untuk scan foto
try:
    import easyocr
    @st.cache_resource
    def load_ocr_reader():
        return easyocr.Reader(['en'], gpu=False)
    reader = load_ocr_reader()
    HAS_OCR = True
except ImportError:
    HAS_OCR = False

# Konfigurasi Halaman & Sembunyikan Sidebar Bawaan
st.set_page_config(
    page_title="Input Part NG",
    page_icon="🔴",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS Styling Tampilan Bersih & Terisolasi
st.markdown("""
<style>
    [data-testid="stSidebar"] {
        display: none !important;
    }
    .stApp {
        background: linear-gradient(135deg, #0B0F19 0%, #111827 50%, #0F172A 100%);
        color: #F3F4F6;
    }
    .main-title {
        color: #EF4444;
        font-weight: 800;
    }
    div[data-testid="stForm"] {
        background: rgba(30, 41, 59, 0.6) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 16px !important;
        padding: 25px !important;
    }
    .stButton>button {
        background: linear-gradient(90deg, #DC2626 0%, #991B1B 100%) !important;
        color: #FFFFFF !important;
        border-radius: 10px !important;
        width: 100% !important;
        font-weight: bold;
        padding: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Inisialisasi Supabase
@st.cache_resource
def init_supabase():
    url = st.secrets.get("SUPABASE_URL", "")
    key = st.secrets.get("SUPABASE_KEY", "")
    if not url or not key:
        return None
    return create_client(url, key)

supabase = init_supabase()

# --- LOAD SEMUA MASTER DATA DARI EXCEL SECARA LENGKAP ---
@st.cache_data
def load_master_data():
    try:
        df = pd.read_excel("Data Terbaru Dual Master.xlsx", sheet_name="Sheet1")
        
        # Ambil semua data PIC dan Shift secara utuh
        df_mp = df[['Shift', 'PIC']].dropna(subset=['PIC']).copy()
        mp_list = df_mp['PIC'].astype(str).tolist()
        mp_shift_map = dict(zip(df_mp['PIC'].astype(str), df_mp['Shift'].fillna('General').astype(str)))
        
        # Ambil semua data Machine dan Line secara utuh
        df_machine = df[['Line', 'Machine']].dropna(subset=['Machine']).copy()
        machine_list = df_machine['Machine'].astype(str).tolist()
        machine_line_map = dict(zip(df_machine['Machine'].astype(str), df_machine['Line'].astype(str)))
        
        return mp_list, mp_shift_map, machine_list, machine_line_map
    except Exception as e:
        return ["Ammar", "Agus M"], {}, ["IDR 052"], {"IDR 052": "Cylinder Block"}

mp_list, mp_shift_map, machine_list, machine_line_map = load_master_data()

st.markdown("<h1 class='main-title'>🔴 Input Part NG dari Mesin</h1>", unsafe_allow_html=True)
st.caption("Pilih Nama MP, ketik/pilih mesin, scan foto part, lalu klik Input.")
st.markdown("---")

# State OCR
if "extracted_nama" not in st.session_state: st.session_state["extracted_nama"] = ""
if "extracted_type" not in st.session_state: st.session_state["extracted_type"] = ""
if "extracted_sn" not in st.session_state: st.session_state["extracted_sn"] = ""

# Upload Foto
uploaded_file = st.file_uploader("📷 Upload Foto Part / Label Seri (Auto-Scan OCR)", type=["png", "jpg", "jpeg"])
encoded_img = ""

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, width=250, caption="Foto Part NG")
    
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    encoded_img = base64.b64encode(buffered.getvalue()).decode("utf-8")
    
    if HAS_OCR:
        with st.spinner("🔍 Memindai teks pada foto..."):
            image_np = io.BytesIO(buffered.getvalue())
            result = reader.readtext(image_np, detail=0)
            scanned_text = " ".join(result)
            
            st.session_state["extracted_nama"] = scanned_text[:30].upper()
            st.session_state["extracted_type"] = "TYPE-" + "".join(filter(str.isalnum, scanned_text[:6])).upper()
            st.session_state["extracted_sn"] = "SN-" + "".join(filter(str.isdigit, scanned_text))[:8]
            st.success("✅ Berhasil memindai teks dari foto!")

# Form Input
with st.form("form_input_ng_clean", clear_on_submit=True):
    col1, col2 = st.columns(2)
    
    with col1:
        tanggal_input = st.date_input("Tanggal", value=datetime.now().date())
        
        # Nama MP (Semua nama muncul lengkap)
        nama_mp = st.selectbox("Nama MP / Pelapor", ["-- Pilih Nama MP --"] + mp_list)
        
        # Pilihan Mesin (Bisa diketik untuk mencari dengan cepat, line terdeteksi otomatis di backend)
        mesin_pilih = st.selectbox("Pilih Mesin Bermasalah (Ketik untuk mencari...)", ["-- Pilih Mesin --"] + machine_list)

    with col2:
        nama_sparepart = st.text_input("Nama Sparepart", value=st.session_state["extracted_nama"])
        type_part = st.text_input("Type Part / Model", value=st.session_state["extracted_type"])
        nomor_seri = st.text_input("Nomor Seri (Serial No.)", value=st.session_state["extracted_sn"])
        qty_part = st.number_input("Jumlah Part (Qty)", min_value=1, value=1)

    # Tombol submit dengan tulisan "Input"
    submitted = st.form_submit_button("🚨 Input")
    
    if submitted:
        if nama_mp == "-- Pilih Nama MP --" or mesin_pilih == "-- Pilih Mesin --":
            st.error("Nama MP dan Mesin wajib dipilih!")
        else:
            # Shift dan Line otomatis terambil di backend tanpa ditampilkan di layar
            detected_shift = mp_shift_map.get(nama_mp, "General")
            detected_line = machine_line_map.get(mesin_pilih, "General Line")
            
            payload = {
                "tanggal": str(tanggal_input),
                "shift": detected_shift,
                "line": detected_line,
                "mesin": mesin_pilih,
                "nama_part": nama_sparepart if nama_sparepart else "Part NG Umum",
                "type_part": type_part if type_part else "Standard",
                "no_seri": nomor_seri if nomor_seri else "-",
                "qty": int(qty_part),
                "teknisi": nama_mp,
                "status_part": "Part NG",
                "foto_base64": encoded_img
            }
            
            if supabase:
                try:
                    supabase.table("maintenance_log").insert(payload).execute()
                    st.success("🎉 Data Part NG berhasil di-input!")
                    st.session_state["extracted_nama"] = ""
                    st.session_state["extracted_type"] = ""
                    st.session_state["extracted_sn"] = ""
                except Exception as e:
                    st.error(f"Gagal menyimpan ke database: {e}")
            else:
                st.error("Koneksi Supabase belum diatur!")
