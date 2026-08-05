import streamlit as st
import pandas as pd
from supabase import create_client

st.set_page_config(page_title="Data Part Repair", page_icon="🛠️", layout="wide")

@st.cache_resource
def init_supabase():
    url = st.secrets.get("SUPABASE_URL", "")
    key = st.secrets.get("SUPABASE_KEY", "")
    if not url or not key: return None
    return create_client(url, key)

supabase = init_supabase()

st.markdown("# 🛠️ Halaman Data Part Repair")
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
        st.error(f"Gagal mengambil data: {e}")
else:
    st.warning("Database belum terhubung. Periksa secrets Supabase Anda.")
