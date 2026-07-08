from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import numpy as np

app = FastAPI(
    title="Sistem Inventarisasi Buku Perpustakaan Badan Bahasa 2026",
    description="Backend API dan Frontend Terintegrasi untuk Pencarian BMN Buku",
    version="2026.2"
)

# Konfigurasi CORS agar API aman dan bisa diakses secara fleksibel
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
    """Fungsi helper untuk menarik data terbaru secara real-time dari Google Sheets"""
    try:
        df = pd.read_csv(SHEET_CSV_URL, dtype=str, on_bad_lines='skip', encoding='utf-8')
        df.columns = df.columns.str.strip()
        df = df.loc[:, ~df.columns.str.contains('^Unnamed:|^\s*$', case=False, na=True)]
        df = df.fillna("")
        return df
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal memuat data dari Google Sheets: {str(e)}")

# ==========================================
# 1. ENDPOINT FRONTEND (HALAMAN UTAMA WEB)
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
                        <label for="query" class="block text-sm font-medium text-gray-700 mb-2">Masukkan kata kunci pencarian:</label>
                        <input type="text" id="query" name="query" autocomplete="off" required
                            placeholder="NUP, Judul, Kode, ISBN, Barcode, dll..."
                            class="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition">
                    </div>
                    <div class="flex items-end">
                        <button type="submit" id="searchBtn"
                            class="w-full md:w-auto px-6 py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg shadow transition flex items-center justify-center gap-2">
                            <span>🔍</span> Cari Data
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
                                <th class="px-6 py-4">Judul Buku</th>
                                <th class="px-6 py-4">Kodefikasi</th>
                                <th class="px-6 py-4">Tahun Terbit</th>
                                <th class="px-6 py-4">Kata yang Dicari</th>
                            </tr>
                        </thead>
                        <tbody id="resultTableBody" class="divide-y divide-gray-200 text-sm text-gray-600">
                            </tbody>
                    </table>
                </div>
            </div>
        </div>

        <script>
            document.getElementById('searchForm').addEventListener('submit', async function(e) {
                e.preventDefault();
                
                const queryInput = document.getElementById('query').value.trim();
                const searchBtn = document.getElementById('searchBtn');
                const statusMessage = document.getElementById('statusMessage');
                const resultContainer = document.getElementById('resultContainer');
                const tableBody = document.getElementById('resultTableBody');

                if (!queryInput) return;

                // Set keadaan loading
                searchBtn.disabled = true;
                searchBtn.innerText = "Mencari...";
                statusMessage.className = "mb-6 p-4 rounded-lg font-medium text-sm bg-blue-50 text-blue-700 block";
                statusMessage.innerText = `Sedang mencari data untuk kata kunci "${queryInput}"...`;
                resultContainer.classList.add('hidden');
                tableBody.innerHTML = "";

                try {
                    // Panggil API backend relatif /search
                    const response = await fetch(`/search?q=${encodeURIComponent(queryInput)}`);
                    const result = await response.json();

                    searchBtn.disabled = false;
                    searchBtn.innerText = "🔍 Cari Data";

                    if (result.status === "success" && result.total_results > 0) {
                        statusMessage.className = "mb-6 p-4 rounded-lg font-medium text-sm bg-green-50 text-green-700 block";
                        statusMessage.innerText = `🎉 Berhasil! Ditemukan ${result.total_results} baris data.`;

                        // Render data ke dalam tabel HTML
                        result.data.forEach(item => {
                            const row = document.createElement('tr');
                            row.className = "hover:bg-gray-50 transition";
                            row.innerHTML = `
                                <td class="px-6 py-4 font-medium text-gray-900">${item.Judul || '-'}</td>
                                <td class="px-6 py-4">${item.Kodefikasi || '-'}</td>
                                <td class="px-6 py-4">${item['Tahun Terbit'] || '-'}</td>
                                <td class="px-6 py-4 bg-yellow-50 font-mono text-xs text-amber-800">${item['Kata yang Dicari'] || '-'}</td>
                            `;
                            tableBody.appendChild(row);
                        });

                        resultContainer.classList.remove('hidden');
                    } else {
                        statusMessage.className = "mb-6 p-4 rounded-lg font-medium text-sm bg-red-50 text-red-700 block";
                        statusMessage.innerText = "❌ Data tidak ditemukan di kolom manapun pada sheet 'slims'.";
                    }

                } catch (error) {
                    searchBtn.disabled = false;
                    searchBtn.innerText = "🔍 Cari Data";
                    statusMessage.className = "mb-6 p-4 rounded-lg font-medium text-sm bg-red-50 text-red-700 block";
                    statusMessage.innerText = `🚨 Terjadi kesalahan koneksi sistem: ${error.message}`;
                }
            });
        </script>
    </body>
    </html>
    """
    return html_content

# ==========================================
# 2. ENDPOINT BACKEND (PROSES PENCARIAN VEKTOR)
# ==========================================
@app.get("/search")
def search_books(q: str = Query(..., description="Kata kunci pencarian")):
    df = fetch_data_from_sheets()
    
    query_clean = q.replace(" ", "").replace(".", "").lower()
    if not query_clean:
        raise HTTPException(status_code=400, detail="Kata kunci tidak boleh kosong.")
    
    # Proses Operasi Vektor Matriks Pandas (Sangat Cepat)
    df_cleaned = df.astype(str).apply(lambda s: s.str.replace(" ", "", regex=False).str.replace(".", "", regex=False).str.lower())
    mask_match = df_cleaned.apply(lambda s: s.str.contains(query_clean, na=False))
    rows_matched = mask_match.any(axis=1)
    
    if rows_matched.any():
        hasil_filter = df[rows_matched].copy()
        mask_match_filtered = mask_match[rows_matched]
        
        # Ekstraksi nilai sel asli tempat ditemukannya kata kunci menggunakan NumPy secara instan
        col_indices = mask_match_filtered.values.argmax(axis=1)
        matched_values = hasil_filter.values[np.arange(len(hasil_filter)), col_indices]
        hasil_filter['Kata yang Dicari'] = matched_values
        
        # --- PROSES STANDARISASI KOLOM JUDUL ---
        kolom_judul_asli = next((c for c in hasil_filter.columns if c.lower() in ['merk', 'judul'] or 'judul' in c.lower() or 'nama' in c.lower()), None)
        hasil_filter['Judul'] = hasil_filter[kolom_judul_asli] if kolom_judul_asli else "Kolom Judul Tidak Terdeteksi"

        # --- PROSES STANDARISASI KOLOM KODEFIKASI ---
        kolom_kode_asli = next((c for c in hasil_filter.columns if c.lower() in ['klasifikasi', 'kode', 'kodefikasi'] or 'klasifikasi' in c.lower() or 'kode' in c.lower()), None)
        hasil_filter['Kodefikasi'] = hasil_filter[kolom_kode_asli] if kolom_kode_asli else "-"

        # --- PROSES STANDARISASI KOLOM TAHUN TERBIT ---
        kolom_tahun_asli = next((c for c in hasil_filter.columns if 'tahun' in c.lower() or 'terbit' in c.lower() or 'thn' in c.lower()), None)
        hasil_filter['Tahun Terbit'] = hasil_filter[kolom_tahun_asli] if kolom_tahun_asli else "-"

        # Pembatasan struktur akhir agar hanya memuat 4 kolom pesanan Anda
        df_final = hasil_filter[['Judul', 'Kodefikasi', 'Tahun Terbit', 'Kata yang Dicari']].copy()
        
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
