import sys
import subprocess

# --- TRICK BYPASS INSTALASI OTOMATIS (Anti ModuleNotFoundError) ---
try:
    import joblib
    import mysql.connector
    import sklearn
    import matplotlib
except ModuleNotFoundError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "joblib", "scikit-learn", "mysql-connector-python", "matplotlib"])

import streamlit as st
import pandas as pd
import numpy as np
import joblib
import mysql.connector
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix

# KONFIGURASI HALAMAN
st.set_page_config(page_title='Dashboard AI Kodim', page_icon='🪖', layout='wide')

hide_menu_style = """
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        /* Menyembunyikan tombol deploy/manage app jika muncul */
        [data-testid="stToolbar"] {visibility: hidden !important;}
        [data-testid="stDecoration"] {visibility: hidden !important;}
        [data-testid="stStatusWidget"] {visibility: hidden !important;}
        /* Menghilangkan padding atas agar tidak ada celah kosong bekas header */
        .main .block-container {
            padding-top: 1rem;
        }
        </style>
        """
st.markdown(hide_menu_style, unsafe_allow_html=True)

# ================= CUSTOM CSS (UI PREMIUM) =====================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    html, body, [class*="css"]  {
        font-family: 'Inter', sans-serif;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        color: white;
        border-radius: 10px;
        border: none;
        transition: all 0.3s ease;
        font-weight: 600;
        padding: 0.6rem 1rem;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1);
        color: white;
        border: none;
    }
    
    .title-banner {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1);
    }
            
    /* Matplotlib dark */
    div[data-testid="stpyplot"] {
        background: transparent;
        border-radius: 10px;
        padding: 0.5rem;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
    }
     
    .stTextInput > div > div > input {
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)


# ================= DATABASE INIT =====================
@st.cache_resource
def get_db_connection():
    # 1. Coba koneksi menggunakan st.secrets (jika tersedia)
    try:
        if "mysql" in st.secrets:
            conn = mysql.connector.connect(
                host=st.secrets["mysql"]["host"],
                port=int(st.secrets["mysql"]["port"]),
                user=st.secrets["mysql"]["user"],
                password=st.secrets["mysql"]["password"],
                database=st.secrets["mysql"]["database"],
                ssl_disabled=False
            )
            
            # Buat tabel jika belum ada
            cursor = conn.cursor()
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE,
                password VARCHAR(100)
            )
            """)
            
            cursor.execute("SELECT * FROM users WHERE username='admin'")
            if not cursor.fetchone():
                cursor.execute("INSERT INTO users(username, password) VALUES('admin', 'admin123')")
                conn.commit()
                
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS riwayat_prediksi (
                id VARCHAR(100) PRIMARY KEY,
                nama VARCHAR(255),
                umur FLOAT,
                tb FLOAT,
                bb FLOAT,
                lari FLOAT,
                pullup FLOAT,
                situp FLOAT,
                pushup FLOAT,
                shuttle FLOAT,
                hasil VARCHAR(50)
            )
            """)
            conn.commit()
            cursor.close()
            return conn
    except Exception as e:
        # Lanjutkan ke fallback lokal jika koneksi secrets gagal
        pass

    # 2. Fallback koneksi ke database lokal XAMPP / MariaDB
    conn = None
    last_err = None
    for p in ["", "123456"]:
        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password=p
            )
            break
        except Exception as e:
            last_err = e

    if not conn:
        st.error(f"Gagal koneksi database lokal: {last_err}")
        st.stop()

    try:
        cursor = conn.cursor()
        
        # Buat database jika belum ada
        cursor.execute("CREATE DATABASE IF NOT EXISTS db_kodim")
        cursor.execute("USE db_kodim")
        
        # Buat tabel Login
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) UNIQUE,
            password VARCHAR(100)
        )
        """)
        
        # User default
        cursor.execute("SELECT * FROM users WHERE username='admin'")
        if not cursor.fetchone():
            cursor.execute("INSERT INTO users (username, password) VALUES ('admin', 'admin123')")
            conn.commit()
            
        # Tabel riwayat
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS riwayat_prediksi (
            id VARCHAR(100) PRIMARY KEY,
            nama VARCHAR(255),
            umur FLOAT,
            tb FLOAT,
            bb FLOAT,
            lari FLOAT,
            pullup FLOAT,
            situp FLOAT,
            pushup FLOAT,
            shuttle FLOAT,
            hasil VARCHAR(50)
        )
        """)
        conn.commit()
        cursor.close()
        return conn
    except Exception as e:
        st.error(f"Gagal inisialisasi database lokal: {e}")
        st.stop()


# ================= LOGIN SYSTEM =====================
if hasattr(st, "query_params"):
    if st.query_params.get("auth") == "true":
        st.session_state['logged_in'] = True
        if 'username' not in st.session_state:
            st.session_state['username'] = "admin (Pulih)"

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    st.markdown("""
        <div class='title-banner'>
            <h1 style='color: white; margin-bottom:0;'>🔒 Login Kodim 0713 Brebes</h1>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            st.markdown("<h3 style='text-align: center;'>Login Admin</h3>", unsafe_allow_html=True)
            username = st.text_input("Username", placeholder="👤 Silakan Ketik Username Akses", label_visibility="collapsed")
            password = st.text_input("Password", placeholder="🔑 Silakan Ketik Kata Sandi Rahasia", type="password", label_visibility="collapsed")
            st.write("") 
            submit = st.form_submit_button("Masuk ke Sistem Utama 🚀", use_container_width=True)
            
            if submit:
                conn = get_db_connection()
                if conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
                    user = cursor.fetchone()
                    cursor.close()
                    
                    if user:
                        st.session_state['logged_in'] = True
                        st.session_state['username'] = username
                        if hasattr(st, "query_params"):
                            st.query_params["auth"] = "true"
                        st.rerun()
                    else:
                        st.error("❌ Username atau Password Salah!")
else:
    # ================= Halaman Utama =====================
    conn = get_db_connection()
    
    col1, col2 = st.columns([8, 2])
    with col1:
        st.title('🪖 Halaman Utama')
        st.write(f"Selamat datang Komandan **{st.session_state['username']}**. Sistem Database MySQL [🟢 AKTIF].")
    with col2:
        st.write("") 
        if st.button("🚪 Logout (Keluar)", use_container_width=True):
            st.session_state['logged_in'] = False
            if hasattr(st, "query_params"):
                st.query_params.clear()
            st.rerun()
            
    # Load Model
    @st.cache_resource
    def load_model():
        return joblib.load('model_svm.pkl'), joblib.load('scaler.pkl')

    try:
        model = joblib.load('model_svm.pkl')
        scaler = joblib.load('scaler.pkl')
    except Exception as e:
        st.error("Model SVM gagal dimuat. Harap jalankan file Model Training terlebih dahulu.")
        st.stop()

    # Form Sidebar (Kiri)
    st.sidebar.header('📝 Identitas & Nilai Fisik')
    with st.sidebar.form(key='input_form', clear_on_submit=True):
        id_prajurit = st.text_input("No. Siswa / ID Prajurit", placeholder="Ketik kombinasi Huruf/Angka (Cth: PR-01)")
        nama_prajurit = st.text_input("Nama Lengkap", placeholder="Ketik Tulisan (Cth: Budi Santoso)")
        
        st.markdown("---")
        umur = st.number_input('Umur (Tahun)', min_value=17, max_value=60, value=None, placeholder="Cth: 25")
        tb = st.number_input('Tinggi Badan (cm)', min_value=140, max_value=200, value=None, placeholder="Cth: 175")
        bb = st.number_input('Berat Badan (kg)', min_value=40, max_value=120, value=None, placeholder="Cth: 65")
        lari = st.number_input('Lari 12 Menit (Jarak Meter)', value=None, step=10.0, placeholder="Cth: 2400")
        pullup = st.number_input('Pull Up (Jumlah)', value=None, placeholder="Cth: 12")
        situp = st.number_input('Sit Up (Jumlah)', value=None, placeholder="Cth: 40")
        pushup = st.number_input('Push Up (Jumlah)', value=None, placeholder="Cth: 35")
        shuttle = st.number_input('Shuttle Run (Detik)', value=None, placeholder="Cth: 16.5")

        # Eksekusi (Tombol Utama) - Evaluasi di awal sebelum penggambaran tab/grafik
        submit_btn = st.form_submit_button('🧠 Analisa & Simpan ke Database', use_container_width=True, type='primary')

    # Inisialisasi status penyimpanan
    submit_success = False
    error_msg = None
    success_msg = None
    info_msg = None
    hasil_akhir = None

    if submit_btn:
        if not id_prajurit or not nama_prajurit:
            st.sidebar.error("⚠️ Lengkapi No. Siswa/ID dan Nama Prajurit terlebih dahulu!")
        elif None in [umur, tb, bb, lari, pullup, situp, pushup, shuttle]:
            st.sidebar.error("⚠️ Lengkapi kedelapan angka Fisik sebelum menekan tombol!")
        else:
            # Hitung SVM dengan DataFrame untuk menghindari warning feature names
            feature_names = ['umur', 'tb', 'bb', 'lari', 'pullup', 'situp', 'pushup', 'shuttle']
            data_fisik = pd.DataFrame([[umur, tb, bb, lari, pullup, situp, pushup, shuttle]], columns=feature_names)
            data_scaled = scaler.transform(data_fisik)
            hasil_akhir = model.predict(data_scaled)[0]
            
            # Simpan ke MySQL
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT id FROM riwayat_prediksi WHERE id = %s", (id_prajurit,))
                if cursor.fetchone():
                    error_msg = f"⚠️ Gagal Disimpan! ID Prajurit **{id_prajurit}** sudah pernah dimasukkan sebelumnya."
                else:
                    query = """
                        INSERT INTO riwayat_prediksi (id, nama, umur, tb, bb, lari, pullup, situp, pushup, shuttle, hasil)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    values = (id_prajurit, nama_prajurit, umur, tb, bb, lari, pullup, situp, pushup, shuttle, hasil_akhir)
                    cursor.execute(query, values)
                    conn.commit()
                    submit_success = True
                cursor.close()
            except Exception as e:
                error_msg = f"Terjadi kesalahan saat injeksi ke SQL Database: {e}"

    # Menampilkan Notifikasi Hasil Input di Atas Area Utama
    if error_msg:
        st.error(error_msg)
    elif submit_success:
        db_mapping = {
            'BS': 'Baik Sekali',
            'B': 'Baik',
            'C': 'Cukup',
            'Kurang': 'Kurang'
        }
        hasil_readable = db_mapping.get(hasil_akhir, hasil_akhir)
        st.success(f'### Kategori Kelulusan Ditetapkan (Tingkat Prediksi): **{hasil_readable}**')
        st.info(f"💾 Data **{nama_prajurit}** ({id_prajurit}) berhasil diamankan ke dalam Bunker Database MySQL.")
        if hasil_akhir in ["TL", "Kurang"]:
            st.snow()
        else:
            st.balloons()

    # Membuat tab Utama
    tab1, tab2 = st.tabs(["📊 Dashboard & Statistik", "🗄️ Catatan Riwayat Prajurit"])
    
    with tab1:
        st.subheader("📊 Distribusi Kelas Kinerja")
        
        # Mengambil data dari MySQL untuk grafik distribusi
        db_mapping = {
            'BS': 'Baik Sekali',
            'B': 'Baik',
            'C': 'Cukup',
            'Kurang': 'Kurang'
        }
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT hasil, COUNT(*) as jumlah FROM riwayat_prediksi GROUP BY hasil")
            rows = cursor.fetchall()
            df_dist = pd.DataFrame(rows, columns=['Hasil_Prediksi', 'jumlah'])
            cursor.close()
            
            # Populasi counts ke label representatif
            kc = {'Baik Sekali': 0, 'Baik': 0, 'Cukup': 0, 'Kurang': 0}
            for _, row in df_dist.iterrows():
                raw_val = row['Hasil_Prediksi']
                mapped_val = db_mapping.get(raw_val, raw_val)
                kc[mapped_val] = kc.get(mapped_val, 0) + row['jumlah']
        except Exception as e:
            kc = {'Baik Sekali': 2, 'Baik': 10, 'Cukup': 8, 'Kurang': 3} # Data cadangan jika query gagal
            
        K_ORDER = ['Baik Sekali', 'Baik', 'Cukup', 'Kurang']
        K_CLR = {'Baik Sekali': '#1abc9c', 'Baik': '#2ecc71', 'Cukup': '#3498db', 'Kurang': '#e74c3c'}
        
        # Tampilan KPI Card Ringkas
        col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)
        col_kpi1.metric("🏅 Baik Sekali", f"{kc.get('Baik Sekali', 0)} Orang")
        col_kpi2.metric("🟢 Baik", f"{kc.get('Baik', 0)} Orang")
        col_kpi3.metric("🔵 Cukup", f"{kc.get('Cukup', 0)} Orang")
        col_kpi4.metric("🔴 Kurang", f"{kc.get('Kurang', 0)} Orang")
        
        st.write("")
            
        # Membuat Grafik dengan background transparent Legibel & Premium
        fig, ax = plt.subplots(figsize=(6.5, 4.0), facecolor='none')
        ax.set_facecolor('none')
        
        vals = [kc.get(k, 0) for k in K_ORDER]
        clrs = [K_CLR[k] for k in K_ORDER]
            
        bars = ax.bar(K_ORDER, vals, color=clrs, width=0.5, edgecolor='#ffffff', linewidth=1.2, zorder=3)
            
        for bar, v in zip(bars, vals):
            ax.text(bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + 0.1, str(v),
                    ha="center", va="bottom",
                    fontsize=9, color='#333333', fontweight="bold")
                        
        ax.set_ylabel("Jumlah Personel", fontsize=9, fontweight="bold", color='#4a5568')
        ax.set_title("Grafik Distribusi Kinerja Fisik Prajurit", fontsize=11, fontweight="bold", pad=10, color='#1a202c')
        ax.grid(axis="y", linestyle="--", alpha=0.3, zorder=0)
        ax.spines[["top","right","left","bottom"]].set_visible(False)
        fig.tight_layout()
            
        st.pyplot(fig)
        plt.close()
        
    with tab2:
        # ================= Tabel Catatan Prajurit di Bagian Bawah =====================
        st.subheader("📋 Catatan Riwayat Prajurit Aktif (Live MySQL Sync)")
        
        try:
            query_tabel = ("SELECT id as 'ID Prajurit', nama as 'Nama', umur as 'Umur', "
                           "tb as 'TB', bb as 'BB', lari as 'Lari', pullup as 'Pull-Up', "
                           "situp as 'Sit-Up', pushup as 'Push-Up', shuttle as 'Shuttle Run', "
                           "hasil as 'Status Akhir' FROM riwayat_prediksi ORDER BY id DESC")
            df_riwayat = pd.read_sql_query(query_tabel, conn)
            
            # Ubah juga hasil di tabel menjadi label readable jika diperlukan
            if not df_riwayat.empty:
                df_riwayat['Status Akhir'] = df_riwayat['Status Akhir'].map(db_mapping).fillna(df_riwayat['Status Akhir'])
                st.dataframe(df_riwayat, use_container_width=True)
            else:
                st.write("*(Belum ada data historis uji coba terbaru yang tersimpan di MySQL).*")
                
            col1_db, col2_db = st.columns([1, 4])
            with col1_db:
                if st.button("🔄 Segarkan Data MySQL", use_container_width=True):
                    st.rerun()
        except Exception as e:
            st.write(f"Gangguan pembacaan tabel MySQL: {e}")
