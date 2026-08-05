import streamlit as st
import pandas as pd
from datetime import datetime
from PIL import Image
import io
import base64
import numpy as np
import requests
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

# Konfigurasi Halaman & Layout
st.set_page_config(
    page_title="Sistem Rekap Part Maintenance",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS Styling Tampilan Bersih & Terisolasi
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #0B0F19 0%, #111827 50%, #0F172A 100%);
        color: #F3F4F6;
    }
    .main-title {
        color: #38BDF8;
        font-weight: 800;
    }
    div[data-testid="stForm"] {
        background: rgba(30, 41, 59, 0.6) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 16px !important;
        padding: 25px !important;
    }
    .stButton>button {
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
GOOGLE_SHEETS_URL = "https://script.google.com/macros/s/AKfycbwcwsvm7SwocuXzjyMBdWyTCllWT7wi5hMRMm3fxo-64Q_EcgXqRaWfMXeC0O6rxkbT/exec"

# --- DATA MASTER LENGKAP ---
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
    "ITP 004": "Cylinder Block", "ITP 005": "Cylinder Block", "ITS 015": "Cylinder Block",
    "ITS 016": "Cylinder Block", "ITS 033": "Cylinder Block", "IWB 026": "Cylinder Block",
    "IWB 032": "Cylinder Block", "IWB 033": "Cylinder Block", "Junbiki": "Cylinder Block",
    "LASER MARKING CB": "Cylinder Block",
    "COBOT": "Cylinder Head", "DAISHA": "Cylinder Head", "IAT 001": "Cylinder Head",
    "IAT 002": "Cylinder Head", "IAT 003": "Cylinder Head", "IDR 040": "Cylinder Head",
    "IMI 040": "Cylinder Head", "ISP 005": "Cylinder Head", "ISP 009": "Cylinder Head",
    "ISP 016": "Cylinder Head", "ISP 018": "Cylinder Head", "ISP 019": "Cylinder Head",
    "ISP 022": "Cylinder Head", "ISP 023": "Cylinder Head", "ISP 026": "Cylinder Head",
    "ISP 027": "Cylinder Head", "ISP 028": "Cylinder Head", "ISP 029": "Cylinder Head",
    "ISP 030": "Cylinder Head", "ISP 031": "Cylinder Head", "ISP 032": "Cylinder Head",
    "ISP 033": "Cylinder Head", "ISP 034": "Cylinder Head", "ISP 035": "Cylinder Head",
    "ISP 036": "Cylinder Head", "ISP 037": "Cylinder Head", "ISP 038": "Cylinder Head",
    "ISP 039": "Cylinder Head", "ISP 040": "Cylinder Head", "ISP 041": "Cylinder Head",
    "ISP 042": "Cylinder Head", "ISP 043": "Cylinder Head", "ISP 045": "Cylinder Head",
    "ISP 046": "Cylinder Head", "ISP 047": "Cylinder Head", "ISP 048": "Cylinder Head",
    "ISP 049": "Cylinder Head", "ISP 050": "Cylinder Head", "ISP 051": "Cylinder Head",
    "ISP 052": "Cylinder Head", "ISP 053": "Cylinder Head", "ISP 090": "Cylinder Head",
    "ISP 091": "Cylinder Head", "ISP 093": "Cylinder Head", "ISP 094": "Cylinder Head",
    "ISP 099": "Cylinder Head", "ISPS 001": "Cylinder Head", "ISPS 002": "Cylinder Head",
    "ISPS 003": "Cylinder Head", "ISPS 004": "Cylinder Head", "ISPS 005": "Cylinder Head",
    "ISPS 006": "Cylinder Head", "ISPS 007": "Cylinder Head", "ISPS 008": "Cylinder Head",
    "ISPS 009": "Cylinder Head", "ISPS 010": "Cylinder Head", "ISPS 011": "Cylinder Head",
    "ISPS 012": "Cylinder Head", "ISPS 013": "Cylinder Head", "ISPS 014": "Cylinder Head",
    "ISPS 015": "Cylinder Head", "ISPS 016": "Cylinder Head", "ISPS 017": "Cylinder Head",
    "ISPS 018": "Cylinder Head", "ISPS 019": "Cylinder Head", "ISPS 020": "Cylinder Head",
    "ISPS 021": "Cylinder Head", "ISPS 022": "Cylinder Head", "ISPS 023": "Cylinder Head",
    "ISPS 024": "Cylinder Head", "ISPS 025": "Cylinder Head", "ISPS 026": "Cylinder Head",
    "ISPS 034": "Cylinder Head", "ISPS 035": "Cylinder Head", "ISPS 036": "Cylinder Head",
    "ISPS 049": "Cylinder Head", "ITS 013": "Cylinder Head", "ITS 014": "Cylinder Head",
    "ITS 015": "Cylinder Head", "IWB 022": "Cylinder Head", "IWBS 001": "Cylinder Head",
    "IZK 044": "Cylinder Head", "IZK 046": "Cylinder Head", "IZK 047": "Cylinder Head",
    "IZK 048": "Cylinder Head", "IZK 049": "Cylinder Head", "KARAKURI PARALEL A": "Cylinder Head",
    "LASER MARKING": "Cylinder Head",
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
    "IZY 020": "Crank Shaft", "IWB 029": "Crank Shaft", "IAT 004": "Crank Shaft",
    "LASER MARKING CS": "Crank Shaft", "GRAFIR FINISH": "Crank Shaft",
    "ICE 002": "Cam Shaft", "IGR 032": "Cam Shaft", "IGR 034": "Cam Shaft",
    "IGR 039": "Cam Shaft", "IGR 040": "Cam Shaft", "IGR 041": "Cam Shaft",
    "IGR 042": "Cam Shaft", "IGR 043": "Cam Shaft", "IGR 044": "Cam Shaft",
    "IMIH 003": "Cam Shaft", "ISP 069": "Cam Shaft", "ISP 070": "Cam Shaft",
    "ISP 071": "Cam Shaft", "ISP 072": "Cam Shaft", "ISP 073": "Cam Shaft",
    "ISP 095": "Cam Shaft", "ISP 096": "Cam Shaft", "ILA 006": "Cam Shaft",
    "ILA 007": "Cam Shaft", "ILP 004": "Cam Shaft", "IWB 030": "Cam Shaft",
    "ILA 008": "Cam Shaft", "Press Pin": "Cam Shaft", "IZK 050": "Cam Shaft",
    "IZK 051": "Cam Shaft", "LASER MARKING CAM": "Cam Shaft", "Airblow": "Cam Shaft", "Gantry": "Cam Shaft",
    "Hoist No.6": "Assy Line", "Hoist No.7": "Assy Line", "IAM 003": "Assy Line",
    "IAM 004": "Assy Line", "IAM 005": "Assy Line", "IAM 007": "Assy Line",
    "IAM 009": "Assy Line", "ICK 3 1 1": "Assy Line", "ICK 3 1 2": "Assy Line",
    "ITS 020": "Assy Line", "ITS 021": "Assy Line", "ITS 023": "Assy Line",
    "ITS 024": "Assy Line", "ITS 025": "Assy Line", "ITS 026": "Assy Line",
    "ITS 028": "Assy Line", "ITS 029": "Assy Line", "ITS 030": "Assy Line",
    "ITS 031": "Assy Line", "ITS 032": "Assy Line", "IZK 021": "Assy Line",
    "IZK 038": "Assy Line", "IZK 039": "Assy Line", "IZK 040": "Assy Line",
    "IZK 041": "Assy Line", "IZK 041A": "Assy Line", "IZK 042": "Assy Line",
    "IZK 043": "Assy Line", "IZK 044": "Assy Line", "IZK 045": "Assy Line",
    "IZK 046": "Assy Line", "IZK 047": "Assy Line", "IZY 023": "Assy Line",
    "IZY 024": "Assy Line", "IZY 027": "Assy Line", "IZY 028": "Assy Line",
    "IZY 029": "Assy Line", "IZY 030": "Assy Line", "IZY 031": "Assy Line",
    "IZYL 001": "Assy Line", "IZYL 003": "Assy Line", "IAM 011": "Assy Line",
    "IAM 012": "Assy Line", "IAM 013": "Assy Line", "IAM 014": "Assy Line",
    "IAM 015": "Assy Line", "AAM 105": "Assy Line", "IZK 048": "Assy Line",
    "ICK 3-1-2": "Assy Line", "ICK 3-1-1": "Assy Line", "IZYL 004": "Assy Line"
}

mp_list = list(MP_DATA.keys())
machine_list = list(MACHINE_DATA.keys())

# --- SIDEBAR NAVIGASI UTAMA ---
st.sidebar.title("📌 Menu Navigasi")
menu = st.sidebar.radio("Pilih Halaman:", ["🔴 Input Part NG", "🛠️ Data Part Repair", "🟢 Input Part OK"])

# ==========================================
# HALAMAN 1: INPUT PART NG
# ==========================================
if menu == "🔴 Input Part NG":
    st.markdown("<h1 class='main-title'>🔴 Input Data Part NG (Dual Master)</h1>", unsafe_allow_html=True)
    st.caption("Scan OCR name plate, lengkapi data, lalu simpan ke Database & Google Spreadsheet.")
    st.markdown("---")

    if "extracted_type" not in st.session_state: st.session_state["extracted_type"] = ""
    if "extracted_sn" not in st.session_state: st.session_state["extracted_sn"] = ""

    uploaded_file = st.file_uploader("📷 Upload Foto Name Plate Dual Master", type=["png", "jpg", "jpeg"])
    encoded_img = ""

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, width=250, caption="Foto Dual Master NG")
        
        buffered = io.BytesIO()
        image.save(buffered, format="JPEG")
        encoded_img = base64.b64encode(buffered.getvalue()).decode("utf-8")
        
        if HAS_OCR:
            with st.spinner("🔍 Memindai teks pada name plate..."):
                try:
                    image_np = np.array(image)
                    results = reader.readtext(image_np, detail=0)
                    
                    detected_type = ""
                    detected_sn = ""
                    
                    for i, text in enumerate(results):
                        t_upper = text.upper()
                        if "REPAIR" in t_upper or "MAR" in t_upper or "OK" in t_upper:
                            continue
                        if "TYPE" in t_upper:
                            if ":" in t_upper:
                                parts = t_upper.split(":")
                                if len(parts) > 1 and parts[1].strip():
                                    detected_type = parts[1].strip()
                            elif i + 1 < len(results):
                                detected_type = results[i+1].strip()
                        
                        if "SERIAL" in t_upper or "SER" in t_upper:
                            if ":" in t_upper:
                                parts = t_upper.split(":")
                                if len(parts) > 1 and len(parts[1].strip()) > 3:
                                    detected_sn = parts[1].strip()
                            elif i + 1 < len(results):
                                candidate = results[i+1].strip()
                                if len(candidate) >= 4 and "REPAIR" not in candidate.upper():
                                    detected_sn = candidate

                    if not detected_type:
                        for text in results:
                            if "DME" in text.upper():
                                detected_type = text.strip()
                                break
                                
                    if not detected_sn:
                        for text in results:
                            t_clean = text.strip()
                            t_up = t_clean.upper()
                            if "2CB" in t_up or ("2" in t_up and len(t_clean) >= 7 and "2026" not in t_up):
                                detected_sn = t_clean
                                break

                    st.session_state["extracted_type"] = detected_type if detected_type else "DME-010"
                    st.session_state["extracted_sn"] = detected_sn if detected_sn else "2CB0421 A"
                    st.success("✅ Berhasil memindai Name Plate!")
                except Exception as ocr_err:
                    st.warning(f"Catatan OCR: Gagal membaca otomatis ({ocr_err}), silakan ketik manual.")

    with st.form("form_input_ng", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            tanggal_input = st.date_input("Tanggal", value=datetime.now().date())
            nama_mp = st.selectbox("Nama MP / Pelapor", ["-- Pilih Nama MP --"] + mp_list)
            mesin_pilih = st.selectbox("Pilih Mesin Bermasalah", ["-- Pilih Mesin --"] + machine_list)

        with col2:
            nama_sparepart = st.text_input("Dual Master", value="Dual Master Expander Device", disabled=True)
            type_part = st.text_input("TYPE", value=st.session_state["extracted_type"])
            nomor_seri = st.text_input("SERIAL No.", value=st.session_state["extracted_sn"])
            qty_part = st.number_input("Jumlah Part (Qty)", min_value=1, value=1)

        submitted = st.form_submit_button("🚨 Simpan & Kirim Data NG")
        
        if submitted:
            if nama_mp == "-- Pilih Nama MP --" or mesin_pilih == "-- Pilih Mesin --":
                st.error("Nama MP dan Mesin wajib dipilih!")
            else:
                detected_shift = MP_DATA.get(nama_mp, "General")
                detected_line = MACHINE_DATA.get(mesin_pilih, "General Line")
                
                # Payload untuk Supabase (lengkap dengan foto)
                payload_db = {
                    "tanggal": str(tanggal_input),
                    "shift": detected_shift,
                    "line": detected_line,
                    "mesin": mesin_pilih,
                    "nama_part": "Dual Master Expander Device",
                    "type_part": type_part if type_part else "DME-010",
                    "no_seri": nomor_seri if nomor_seri else "2CB0421 A",
                    "qty": int(qty_part),
                    "teknisi": nama_mp,
                    "status_part": "Part NG",
                    "foto_base64": encoded_img
                }
                
                # Payload untuk Google Sheets (sesuai urutan kolom bersih Anda)
                payload_sheets = {
                    "tanggal": str(tanggal_input),
                    "nama": nama_mp,
                    "shift": detected_shift,
                    "line": detected_line,
                    "mesin": mesin_pilih,
                    "nama_part": "Dual Master Expander Device",
                    "type_part": type_part if type_part else "DME-010",
                    "no_seri": nomor_seri if nomor_seri else "2CB0421 A",
                    "qty": int(qty_part),
                    "status": "Part NG"
                }
                
                success_all = True
                if supabase:
                    try:
                        supabase.table("maintenance_log").insert(payload_db).execute()
                    except Exception as e:
                        st.error(f"Gagal simpan ke Supabase: {e}")
                        success_all = False
                
                try:
                    requests.post(GOOGLE_SHEETS_URL, json=payload_sheets)
                except Exception as err:
                    st.warning(f"Gagal kirim ke Google Sheets: {err}")
                
                if success_all:
                    st.success("🎉 Data Part NG berhasil disimpan dan dikirim ke Spreadsheet!")
                    st.session_state["extracted_type"] = ""
                    st.session_state["extracted_sn"] = ""

# ==========================================
# HALAMAN 2: DATA PART REPAIR
# ==========================================
elif menu == "🛠️ Data Part Repair":
    st.markdown("<h1 class='main-title'>🛠️ Halaman Data Part Repair</h1>", unsafe_allow_html=True)
    st.caption("Kelola dan pantau part yang sedang dalam status perbaikan.")
    st.markdown("---")
    
    if supabase:
        try:
            response = supabase.table("maintenance_log").select("*").eq("status_part", "Part NG").execute()
            data_repair = response.data
            
            if data_repair:
                df_repair = pd.DataFrame(data_repair)
                st.dataframe(df_repair, use_container_width=True)
            else:
                st.info("Belum ada data part yang masuk dalam daftar perbaikan.")
        except Exception as e:
            st.error(f"Gagal mengambil data dari database: {e}")
    else:
        st.warning("Database belum terhubung.")

# ==========================================
# HALAMAN 3: INPUT PART OK
# ==========================================
elif menu == "🟢 Input Part OK":
    st.markdown("<h1 class='main-title'>🟢 Input Data Part OK (Selesai Repair)</h1>", unsafe_allow_html=True)
    st.caption("Catat part yang telah selesai diperbaiki dan kembali normal.")
    st.markdown("---")

    with st.form("form_input_ok", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            tgl_ok = st.date_input("Tanggal Selesai", value=datetime.now().date())
            teknisi_ok = st.selectbox("Teknisi / Pelapor", ["-- Pilih Nama MP --"] + mp_list)
            mesin_ok = st.selectbox("Pilih Mesin Terpasang", ["-- Pilih Mesin --"] + machine_list)

        with col2:
            nama_part_ok = st.text_input("Nama Part", value="Dual Master Expander Device", disabled=True)
            type_ok = st.text_input("TYPE", value="DME-010")
            seri_ok = st.text_input("SERIAL No.", value="2CB0421 A")
            qty_ok = st.number_input("Jumlah Qty OK", min_value=1, value=1)

        submitted_ok = st.form_submit_button("✅ Simpan Status Part OK")
        
        if submitted_ok:
            if teknisi_ok == "-- Pilih Nama MP --" or mesin_ok == "-- Pilih Mesin --":
                st.error("Teknisi dan Mesin wajib dipilih!")
            else:
                detected_shift_ok = MP_DATA.get(teknisi_ok, "General")
                detected_line_ok = MACHINE_DATA.get(mesin_ok, "General Line")

                payload_ok_db = {
                    "tanggal": str(tgl_ok),
                    "shift": detected_shift_ok,
                    "line": detected_line_ok,
                    "mesin": mesin_ok,
                    "nama_part": "Dual Master Expander Device",
                    "type_part": type_ok,
                    "no_seri": seri_ok,
                    "qty": int(qty_ok),
                    "teknisi": teknisi_ok,
                    "status_part": "Part OK",
                    "foto_base64": ""
                }

                payload_ok_sheets = {
                    "tanggal": str(tgl_ok),
                    "nama": teknisi_ok,
                    "shift": detected_shift_ok,
                    "line": detected_line_ok,
                    "mesin": mesin_ok,
                    "nama_part": "Dual Master Expander Device",
                    "type_part": type_ok,
                    "no_seri": seri_ok,
                    "qty": int(qty_ok),
                    "status": "Part OK"
                }
                
                success_ok = True
                if supabase:
                    try:
                        supabase.table("maintenance_log").insert(payload_ok_db).execute()
                    except Exception as e:
                        st.error(f"Gagal menyimpan data OK ke Supabase: {e}")
                        success_ok = False
                
                try:
                    requests.post(GOOGLE_SHEETS_URL, json=payload_ok_sheets)
                except Exception as err:
                    st.warning(f"Gagal kirim ke Google Sheets: {err}")

                if success_ok:
                    st.success("🎉 Data Part OK berhasil disimpan ke sistem dan Spreadsheet!")
