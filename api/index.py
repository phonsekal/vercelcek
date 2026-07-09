from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import numpy as np
import os

app = FastAPI(
    title="Sistem Inventarisasi Buku Perpustakaan Badan Bahasa 2026",
    version="2026.4"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# GLOBAL DATABASE CACHE (Membuat pembacaan file CSV menjadi instan setelah cold start)
DB_CACHE = None

def load_initial_data():
    global DB_CACHE
    if DB_CACHE is not None:
        return DB_CACHE
        
    csv_path = "databmnbuku.csv"
    if not os.path.exists(csv_path):
        csv_path = os.path.join(os.path.dirname(__file__), "..", "databmnbuku.csv")
        
    try:
        if not os.path.exists(csv_path):
            return None
        # Membaca file dengan separator ';'
        df = pd.read_csv(csv_path, sep=';', dtype=str, on_bad_lines='skip', encoding='utf-8')
        df.columns = df.columns.str.strip()
        df = df.loc[:, ~df.columns.str.contains('^Unnamed:|^\s*$', case=False, na=True)]
        df = df.fillna("")
        DB_CACHE = df
        return DB_CACHE
    except:
        return None

# Panggil fungsi saat aplikasi pertama kali diinisialisasi
load_initial_data()

# ==========================================
# 1. FRONTEND ANTARMUKA WEB
# ==========================================
@app.get("/", response_class=HTMLResponse)
def home():
    html_content = """
    <!DOCTYPE html>
    <html lang="id">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Inventarisasi Buku Perpustakaan Badan Bahasa 2026</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-gray-50 font-sans text-gray-800 min-h-screen">

        <div class="container mx-auto px-4 py-8 max-w-6xl">
            <div class="mb-8 text-center md:text-left">
                <h1 class="text-3xl font-bold text-blue-900">Sistem Inventarisasi Buku Perpustakaan</h1>
                <p class="text-gray-600 mt-2">Sekretariat Badan Pengembangan dan Pembinaan Bahasa</p>
            </div>

            <div class="bg-white p-6 rounded-xl shadow-sm border border-gray-100 mb-6">
                <form id="searchForm" class="flex flex-col md:flex-row gap-4">
                    <div class="flex-1">
                        <label for="query" class="block text-sm font-medium text-gray-700 mb-2">Cari berdasarkan Merk, Kode1, Kode2, atau Kode3:</label>
                        <input type="text" id="query" name="query" autocomplete="off" required
                            placeholder="Ketik kata kunci pencarian..."
                            class="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition">
                    </div>
                    <div class="flex items-end">
                        <button type="submit" id="searchBtn"
                            class="w-full md:w-auto px-6 py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg shadow transition">
                            🔍 Cari Data
                        </button>
                    </div>
                </form>
            </div>

            <div id="statusMessage" class="hidden mb-6 p-4 rounded-lg font-medium text-sm"></div>

            <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden hidden" id="resultContainer">
                <div class="overflow-x-auto">
                    <table class="w-full text-left border-collapse">
                        <thead>
                            <tr class="bg-gray-100 border-b border-gray-200 text-gray-700 text-sm font-semibold uppercase tracking-wider">
                                <th class="px-6 py-4">NUP</th>
                                <th class="px-6 py-4">Judul Buku</th>
                                <th class="px-6 py-4">Kodefikasi</th>
                                <th class="px-6 py-4">Aksi</th>
                            </tr>
                        </thead>
                        <tbody id="resultTableBody" class="divide-y divide-gray-200 text-sm text-gray-600">
                            </tbody>
                    </table>
                </div>
            </div>
        </div>

        <script>
            // Catatan Integrasiotomatisasi Google Sheets:
            // Karena Google Sheets API membutuhkan OAuth, cara termudah & aman langsung dari Frontend adalah 
            // menembakkannya menggunakan Google Form Link pre-filled yang terhubung ke Sheet tersebut, atau memicu tautan pendaftaran.
            function kirimKeGoogleSheets(nup, judul) {
                // Konfigurasi target URL Google Sheets Anda
                const targetSheetUrl = "https://docs.google.com/spreadsheets/d/1CtWwWaMNW8lhkAHsCUhSNHBZxGAWlTrqDABzRM4_wkk/edit?gid=0#gid=0";
                
                alert(`Mengirim data Buku:\\nNUP: ${nup}\\nJudul: ${judul}\\n\\nAnda akan diarahkan ke Google Sheets untuk mencatat.`);
                
                // Membuka Google Sheet secara langsung
                window.open(targetSheetUrl, '_blank');
            }

            document.getElementById('searchForm').addEventListener('submit', async function(e) {
                e.preventDefault();
                
                const queryInput = document.getElementById('query').value.trim();
                const searchBtn = document.getElementById('searchBtn');
                const statusMessage = document.getElementById('statusMessage');
                const resultContainer = document.getElementById('resultContainer');
                const tableBody = document.getElementById('resultTableBody');

                if (!queryInput) return;

                searchBtn.disabled = true;
                searchBtn.innerText = "Mencari...";
                statusMessage.className = "mb-6 p-4 rounded-lg font-medium text-sm bg-blue-50 text-blue-700 block";
                statusMessage.innerText = `Sedang memproses pencarian "${queryInput}"...`;
                resultContainer.classList.add('hidden');
                tableBody.innerHTML = "";

                try {
                    const response = await fetch(`/search?q=${encodeURIComponent(queryInput)}`);
                    const result = await response.json();

                    searchBtn.disabled = false;
                    searchBtn.innerText = "🔍 Cari Data";

                    if (result.status === "success" && result.total_results > 0) {
                        statusMessage.className = "mb-6 p-4 rounded-lg font-medium text-sm bg-green-50 text-green-700 block";
                        statusMessage.innerText = `🎉 Ditemukan ${result.total_results} data buku.`;

                        result.data.forEach(item => {
                            const row = document.createElement('tr');
                            row.className = "hover:bg-gray-50 transition";
                            
                            // Ambil parameter data yang aman untuk fungsi javascript string
                            const safeNUP = (item.NUP || '-').replace(/'/g, "\\'");
                            const safeJudul = (item['Judul Buku'] || '-').replace(/'/g, "\\'");

                            row.innerHTML = `
                                <td class="px-6 py-4 font-mono font-medium text-gray-900">${item.NUP || '-'}</td>
                                <td class="px-6 py-4">${item['Judul Buku'] || '-'}</td>
                                <td class="px-6 py-4"><span class="px-2 py-1 bg-gray-100 text-gray-700 rounded text-xs">${item.Kodefikasi || '-'}</span></td>
                                <td class="px-6 py-4">
                                    <button onclick="kirimKeGoogleSheets('${safeNUP}', '${safeJudul}')" 
                                        class="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white font-medium text-xs rounded shadow transition">
                                        🚀 Kirim Data
                                    </button>
                                </td>
                            `;
                            tableBody.appendChild(row);
                        });

                        resultContainer.classList.remove('hidden');
                    } else {
                        statusMessage.className = "mb-6 p-4 rounded-lg font-medium text-sm bg-red-50 text-red-700 block";
                        statusMessage.innerText = "❌ Data tidak ditemukan pada kolom Merk atau Kode1/2/3.";
                    }

                } catch (error) {
                    searchBtn.disabled = false;
                    searchBtn.innerText = "🔍 Cari Data";
                    statusMessage.className = "mb-6 p-4 rounded-lg font-medium text-sm bg-red-50 text-red-700 block";
                    statusMessage.innerText = `🚨 Terjadi gangguan koneksi: ${error.message}`;
                }
            });
        </script>
    </body>
    </html>
    """
    return html_content

# ==========================================
# 2. BACKEND ENGINE (PENCARIAN KHUSUS & CEPAT)
# ==========================================
@app.get("/search")
def search_books(q: str = Query(..., description="Kata kunci pencarian")):
    # Ambil data dari cache global RAM untuk mempercepat respons pencarian
    df = load_initial_data()
    if df is None:
        raise HTTPException(status_code=500, detail="Database file CSV gagal dimuat di server.")
    
    query_clean = q.replace(" ", "").replace(".", "").lower()
    if not query_clean:
        raise HTTPException(status_code=400, detail="Kata kunci tidak boleh kosong.")
    
    # 1. Batasi target kolom pencarian murni pada: Merk, Kode1, Kode2, Kode3
    target_search_cols = [c for c in ['Merk', 'Kode1', 'Kode2', 'Kode3'] if c in df.columns]
    if not target_search_cols:
        raise HTTPException(status_code=500, detail="Kolom target pencarian tidak ditemukan di struktur CSV.")
        
    # Jalankan pencarian vektor matriks super cepat khusus pada kolom target saja
    df_target = df[target_search_cols].astype(str).apply(lambda s: s.str.replace(" ", "", regex=False).str.replace(".", "", regex=False).str.lower())
    mask_match = df_target.apply(lambda s: s.str.contains(query_clean, na=False))
    rows_matched = mask_match.any(axis=1)
    
    if rows_matched.any():
        hasil_filter = df[rows_matched].copy()
        
        # 2. STANDARISASI KOLOM JUDUL BUKU (Dari Kolom 'Merk')
        hasil_filter['Judul Buku'] = hasil_filter['Merk'] if 'Merk' in hasil_filter.columns else "-"
        
        # 3. STANDARISASI KOLOM NUP
        if 'NUP' not in hasil_filter.columns:
            hasil_filter['NUP'] = "-"

        # 4. GABUNGKAN LOGIKA KODEFIKASI (Kode1, Kode2, Kode3 digabung dengan pemisah '/')
        def hitung_kodefikasi(row):
            parts = []
            for col in ['Kode1', 'Kode2', 'Kode3']:
                if col in row and str(row[col]).strip():
                    parts.append(str(row[col]).strip())
            return " / ".join(parts) if parts else "-"
            
        hasil_filter['Kodefikasi'] = hasil_filter.apply(hitung_kodefikasi, axis=1)

        # 5. PACKING STRUKTUR AKHIR (NUP, Judul Buku, Kodefikasi)
        df_final = hasil_filter[['NUP', 'Judul Buku', 'Kodefikasi']].copy()
        
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
