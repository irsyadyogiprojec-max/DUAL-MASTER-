import streamlit as st
import pandas as pd
from datetime import datetime
from supabase import create_client

# Konfigurasi Halaman
st.set_page_config(
    page_title="Executive Dashboard & OEE System",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Styling Tema Gelap Profesional
st.markdown("""
<style>
    [data-testid="stSidebar"] {
        display: none !important;
    }
    .stApp {
        background: linear-gradient(135deg, #0B0F19 0%, #111827 50%, #0F172A 100%);
        color: #F3F4F6;
    }
    .card {
        background: rgba(30, 41, 59, 0.7);
        padding: 25px;
        border-radius: 14px;
        border: 1px solid rgba(56, 189, 248, 0.2);
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        margin-bottom: 20px;
    }
    .main-title {
        color: #38BDF8;
        font-weight: 800;
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

st.markdown("<h1 class='main-title'>⚡ EXECUTIVE DASHBOARD & OEE SYSTEM</h1>", unsafe_allow_html=True)
st.caption(f"📅 {datetime.now().strftime('%B %d, %Y')} | Real-time Monitoring Pabrik & Maintenance Log")
st.markdown("---")

# Tarik Data dari Database Supabase
@st.cache_data(ttl=10)
def fetch_data():
    if not supabase:
        return pd.DataFrame()
    try:
        response = supabase.table("maintenance_log").select("*").execute()
        return pd.DataFrame(response.data)
    except Exception:
        return pd.DataFrame()

df_logs = fetch_data()

# Metrik Utama Ringkasan
col1, col2, col3 = st.columns(3)

total_ng = len(df_logs) if not df_logs.empty else 0
total_lines = 5  # Sesuai data master Anda

with col1:
    st.markdown("""
    <div class="card">
        <h4>Total Part NG Tercatat</h4>
        <h2 style="color: #EF4444;">{} Part</h2>
    </div>
    """.format(total_ng), unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="card">
        <h4>Status Sistem</h4>
        <h2 style="color: #10B981;">Online / Normal</h2>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="card">
        <h4>Line Pabrik Terhubung</h4>
        <h2 style="color: #38BDF8;">{} Line</h2>
    </div>
    """.format(total_lines), unsafe_allow_html=True)

st.markdown("### 📋 Log Data Kerusakan & Perbaikan Terkini")

if not df_logs.empty:
    # Tampilkan tabel data secara rapi
    display_cols = [c for c in ["tanggal", "shift", "line", "mesin", "nama_part", "type_part", "no_seri", "qty", "teknisi", "status_part"] if c in df_logs.columns]
    st.dataframe(df_logs[display_cols], use_container_width=True)
else:
    st.info("Belum ada data log yang masuk ke database. Silakan lakukan input dari halaman Input Part NG.")
