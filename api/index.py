from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import numpy as np
import requests

app = FastAPI(
    title="API Inventarisasi Buku Perpustakaan Badan Bahasa",
    description="Backend API untuk pencarian cepat buku berdasarkan data Google Sheets",
    version="2026.1"
)

# Mengizinkan CORS agar API bisa dipanggil dari frontend mana saja (Streamlit, Web HTML, dll)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# URL Google Sheet Baru yang diarahkan khusus untuk mengekspor tab/sheet "slims"
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/17QsetCX0AX_u4w4fQbCxH6yOXXuinAfeVfe9acvkHiE/export?format=csv&sheet=slims"

def fetch_data_from_sheets():
    """Fungsi helper untuk menarik data terbaru dari Google Sheets"""
    try:
        df = pd.read_csv(SHEET_CSV_URL, dtype=str, on_bad_lines='skip', encoding='utf-8')
        df.columns = df.columns.str.strip()
        df = df.loc[:, ~df.columns.str.contains('^Unnamed:|^\s*$', case=False, na=True)]
        df = df.fillna("")
        return df
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal memuat data dari Google Sheets: {str(e)}")

@app.get("/")
def home():
    return {"message": "Sistem Inventarisasi Buku Perpustakaan Badan Bahasa API is running!"}

@app.get("/search")
def search_books(q: str = Query(..., description="Kata kunci pencarian (NUP, Judul, ISBN, Barcode, dll)")):
    # 1. Tarik data ter-update dari Google Sheets
    df = fetch_data_from_sheets()
    
    query_clean = q.replace(" ", "").replace(".", "").lower()
    if not query_clean:
        raise HTTPException(status_code=400, detail="Kata kunci pencarian tidak boleh kosong.")
    
    # 2. Proses Pencarian Vektor (Super Cepat)
    df_cleaned = df.astype(str).apply(lambda s: s.str.replace(" ", "", regex=False).str.replace(".", "", regex=False).str.lower())
    mask_match = df_cleaned.apply(lambda s: s.str.contains(query_clean, na=False))
    rows_matched = mask_match.any(axis=1)
    
    # 3. Jika data ditemukan, lakukan standarisasi format JSON output
    if rows_matched.any():
        hasil_filter = df[rows_matched].copy()
        mask_match_filtered = mask_match[rows_matched]
        
        # Ambil nilai sel asli pertama yang cocok pada tiap baris
        col_indices = mask_match_filtered.values.argmax(axis=1)
        matched_values = hasil_filter.values[np.arange(len(hasil_filter)), col_indices]
        hasil_filter['Kata yang Dicari'] = matched_values
        
        # --- STANDARISASI KOLOM JUDUL ---
        kolom_judul_asli = next((c for c in hasil_filter.columns if c.lower() in ['merk', 'judul'] or 'judul' in c.lower() or 'nama' in c.lower()), None)
        hasil_filter['Judul'] = hasil_filter[kolom_judul_asli] if kolom_judul_asli else "Kolom Judul Tidak Terdeteksi"

        # --- STANDARISASI KOLOM KODEFIKASI ---
        kolom_kode_asli = next((c for c in hasil_filter.columns if c.lower() in ['klasifikasi', 'kode', 'kodefikasi'] or 'klasifikasi' in c.lower() or 'kode' in c.lower()), None)
        hasil_filter['Kodefikasi'] = hasil_filter[kolom_kode_asli] if kolom_kode_asli else "-"

        # --- STANDARISASI KOLOM TAHUN TERBIT ---
        kolom_tahun_asli = next((c for c in hasil_filter.columns if 'tahun' in c.lower() or 'terbit' in c.lower() or 'thn' in c.lower()), None)
        hasil_filter['Tahun Terbit'] = hasil_filter[kolom_tahun_asli] if kolom_tahun_asli else "-"

        # --- FORMATTING KE JSON LIST ---
        df_final = hasil_filter[['Judul', 'Kodefikasi', 'Tahun Terbit', 'Kata yang Dicari']].copy()
        
        # Mengembalikan hasil dalam bentuk list of dict/JSON
        return {
            "status": "success",
            "total_results": len(df_final),
            "data": df_final.to_dict(orient="records")
        }
    
    return {
        "status": "success",
        "total_results": 0,
        "data": []
    }
