from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import numpy as np
import os

app = FastAPI(
    title="Sistem Inventarisasi Buku Perpustakaan Badan Bahasa 2026",
    version="2026.7"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# GLOBAL DATABASE CACHE (RAM)
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
        df = pd.read_csv(csv_path, sep=';', dtype=str, on_bad_lines='skip', encoding='utf-8')
        df.columns = df.columns.str.strip()
        df = df.loc[:, ~df.columns.str.contains('^Unnamed:|^\s*$', case=False, na=True)]
        df = df.fillna("")
        DB_CACHE = df
        return DB_CACHE
    except:
        return None

load_initial_data()

@app.get('/favicon.ico', include_in_schema=False)
async def favicon():
    favicon_path = "favicon.ico"
    if not os.path.exists(favicon_path):
        favicon_path = os.path.join(os.path.dirname(__file__), "..", "favicon.ico")
    if os.path.exists(favicon_path):
        return FileResponse(favicon_path)
    return HTTPException(status_code=404, detail="Favicon tidak ditemukan")

# ========================================================
# FRONTEND INTERAKTIF & MODERN (CLEAN LIGHT THEME)
# ========================================================
@app.get("/", response_class=HTMLResponse)
def home():
    html_content = """
    <!DOCTYPE html>
    <html lang="id">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Inventarisasi Buku Perpustakaan Badan Bahasa 2026</title>
        <link rel="icon" type="image/x-icon" href="/favicon.ico">
        <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap">
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            body {
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
                background-color: #f4f7fa;
                color: #2d3748;
                line-height: 1.6;
                min-height: 100vh;
                display: flex;
                flex-direction: column;
            }
            
            /* Custom Scrollbar yang Halus */
            ::-webkit-scrollbar { width: 6px; height: 6px; }
            ::-webkit-scrollbar-track { background: #f1f1f1; }
            ::-webkit-scrollbar-thumb { background: #cbd5e0; border-radius: 3px; }
            ::-webkit-scrollbar-thumb:hover { background: #a0aec0; }

            header {
                border-bottom: 1px solid #e2e8f0;
                background: rgba(255, 255, 255, 0.9);
                backdrop-filter: blur(8px);
                position: sticky;
                top: 0;
                z-index: 50;
            }
            nav {
                max-width: 1200px;
                margin: 0 auto;
                display: flex;
                align-items: center;
                padding: 1rem 2rem;
                width: 100%;
            }
            .logo {
                font-size: 1.15rem;
                font-weight: 600;
                color: #1a365d;
                text-decoration: none;
                display: flex;
                align-items: center;
                gap: 0.6rem;
            }
            .nav-links a {
                text-decoration: none;
                color: #4a5568;
                padding: 0.5rem 1rem;
                border-radius: 6px;
                transition: all 0.2s;
                font-size: 0.875rem;
                font-weight: 500;
                margin-left: auto;
            }
            .nav-links a:hover { color: #1a365d; background-color: #edf2f7; }
            
            main {
                flex: 1;
                width: 100%;
                max-width: 1200px;
                margin: 0 auto;
                padding: 3rem 2rem;
            }
            
            .hero { text-align: center; margin-bottom: 2.5rem; }
            .hero h1 {
                font-size: 2.5rem;
                font-weight: 700;
                margin-bottom: 0.5rem;
                letter-spacing: -0.03em;
                color: #1a365d;
            }
            .subtitle { font-size: 1.05rem; color: #718096; font-weight: 400; }

            /* Panel Pencarian Cerah & Berbayangan Lembut */
            .search-box {
                background: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                padding: 1.75rem;
                margin-bottom: 1.5rem;
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
                transition: box-shadow 0.2s;
            }
            .search-box:focus-within {
                box-shadow: 0 10px 15px -3px rgba(66, 153, 225, 0.14), 0 4px 6px -2px rgba(66, 153, 225, 0.05);
            }
            .form-group label {
                font-size: 0.75rem;
                color: #4a5568;
                font-weight: 700;
                letter-spacing: 0.05em;
                display: block;
                margin-bottom: 0.5rem;
            }
            .input-wrapper { display: flex; gap: 0.75rem; }
            .search-box input {
                flex: 1;
                background-color: #f8fafc;
                border: 1px solid #cbd5e0;
                border-radius: 8px;
                padding: 0.8rem 1.25rem;
                color: #2d3748;
                font-size: 0.95rem;
                outline: none;
                transition: all 0.2s;
            }
            .search-box input:focus {
                border-color: #3182ce;
                background-color: #ffffff;
                box-shadow: 0 0 0 3px rgba(66, 153, 225, 0.15);
            }
            .btn-search {
                background-color: #3182ce;
                color: #ffffff;
                border: none;
                padding: 0.8rem 1.75rem;
                font-size: 0.95rem;
                font-weight: 600;
                border-radius: 8px;
                cursor: pointer;
                transition: all 0.2s;
                box-shadow: 0 2px 4px rgba(49, 130, 206, 0.2);
            }
            .btn-search:hover { background-color: #2b6cb0; }

            /* Status Badge */
            .status-badge {
                display: inline-flex;
                align-items: center;
                gap: 0.6rem;
                background-color: #ffffff;
                border: 1px solid #e2e8f0;
                color: #4a5568;
                padding: 0.6rem 1.2rem;
                border-radius: 8px;
                font-size: 0.875rem;
                margin-bottom: 1.5rem;
                width: 100%;
                box-shadow: 0 1px 3px rgba(0,0,0,0.02);
            }
            .status-dot { width: 8px; height: 8px; background-color: #48bb78; border-radius: 50%; box-shadow: 0 0 6px #48bb78; }
            .status-dot.loading { background-color: #ed8936; box-shadow: 0 0 6px #ed8936; animation: pulse 1s infinite; }
            .status-dot.error { background-color: #f56565; box-shadow: 0 0 6px #f56565; }

            /* Kontainer Tabel Cerah Modern */
            .table-container {
                background-color: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                overflow: hidden;
                width: 100%;
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
                animation: fadeIn 0.3s cubic-bezier(0.16, 1, 0.3, 1);
            }
            table { width: 100%; border-collapse: collapse; text-align: left; }
            th {
                background-color: #f8fafc;
                border-bottom: 2px solid #edf2f7;
                color: #4a5568;
                font-weight: 600;
                padding: 1rem 1.5rem;
                text-transform: uppercase;
                font-size: 0.725rem;
                letter-spacing: 0.05em;
            }
            td { padding: 1rem 1.5rem; border-bottom: 1px solid #edf2f7; color: #4a5568; font-size: 0.925rem; }
            tr:last-child td { border-bottom: none; }
            tr:hover td { background-color: #f7fafc; }
            
            .font-mono-style { font-family: monospace; font-size: 0.85rem; color: #718096; font-weight: 500; }
            .badge-kode {
                background-color: #ebf8ff;
                color: #2b6cb0;
                padding: 0.25rem 0.5rem;
                border-radius: 6px;
                font-size: 0.775rem;
                font-weight: 500;
                border: 1px solid #bee3f8;
            }
            
            /* Tombol Aksi Cerah Modern */
            .btn-action {
                display: inline-flex;
                align-items: center;
                color: #3182ce;
                text-decoration: none;
                font-size: 0.8rem;
                font-weight: 600;
                padding: 0.45rem 1rem;
                background-color: #edf2f7;
                border-radius: 6px;
                border: 1px solid #e2e8f0;
                cursor: pointer;
                transition: all 0.2s;
            }
            .btn-action:hover {
                background-color: #3182ce;
                color: #ffffff;
                border-color: #3182ce;
            }
            .btn-success-style {
                background-color: #38a169 !important;
                border-color: #38a169 !important;
                color: #ffffff !important;
                cursor: default;
                box-shadow: 0 2px 4px rgba(56, 161, 105, 0.2);
            }
            
            .hidden { display: none; }
            @keyframes fadeIn { from { opacity: 0; transform: translateY(6px); } to { opacity: 1; transform: translateY(0); } }
            @keyframes pulse { 0% { opacity: 0.6; } 50% { opacity: 1; } 100% { opacity: 0.6; } }

            @media (max-width: 768px) {
                main { padding: 1.5rem 1rem; }
                .hero h1 { font-size: 1.85rem; }
                .input-wrapper { flex-direction: column; }
                .btn-search { width: 100%; }
                th, td { padding: 0.75rem 1rem; }
            }
        </style>
    </head>
    <body>
        <header>
            <nav>
                <a href="/" class="logo">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#3182ce" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path></svg>
                    <span>Badan Bahasa + BMN</span>
                </a>
                <div class="nav-links"><a href="/docs">API Docs</a></div>
            </nav>
        </header>
        
        <main>
            <div class="hero">
                <h1>Inventarisasi Buku</h1>
                <p class="subtitle">Sekretariat Badan Pengembangan dan Pembinaan Bahasa</p>
            </div>

            <div class="search-box">
                <form id="searchForm">
                    <div class="form-group">
                        <label for="query">KATA KUNCI PENCARIAN (MERK / KODE KELOMPOK)</label>
                        <div class="input-wrapper">
                            <input type="text" id="query" name="query" autocomplete="off" required placeholder="Ketik minimal 2 karakter untuk memicu pencarian otomatis...">
                            <button type="submit" id="searchBtn" class="btn-search">Cari Data</button>
                        </div>
                    </div>
                </form>
            </div>

            <div id="statusBadge" class="hidden status-badge">
                <div id="statusDot" class="status-dot"></div>
                <span id="statusText">Menunggu Input</span>
            </div>

            <div class="table-container hidden" id="resultContainer">
                <table>
                    <thead>
                        <tr>
                            <th style="width: 15%;">NUP</th>
                            <th style="width: 55%;">Judul Buku</th>
                            <th style="width: 15%;">Kodefikasi</th>
                            <th style="width: 15%; text-align: center;">Aksi</th>
                        </tr>
                    </thead>
                    <tbody id="resultTableBody"></tbody>
                </table>
            </div>
        </main>

        <script>
            const WEB_APP_URL = "https://script.google.com/macros/s/AKfycbyVCt37xvsX_oiNsw-AX99RW2SC4gU0K0qOMJvcY0909zqGMC1J1eaUbZOMrRI1oOXh/exec";
            let debounceTimer;

            async function eksekusiKirim(buttonElement, nup, judul) {
                buttonElement.disabled = true;
                buttonElement.innerText = "Mengirim...";
                buttonElement.style.opacity = "0.7";

                try {
                    await fetch(WEB_APP_URL, {
                        method: 'POST',
                        mode: 'no-cors', 
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ nup: nup, merk: judul })
                    });
                    
                    buttonElement.innerText = "✓ Tersimpan";
                    buttonElement.className = "btn-action btn-success-style";
                    buttonElement.style.opacity = "1";
                } catch (error) {
                    buttonElement.disabled = false;
                    buttonElement.innerText = "❌ Gagal";
                    buttonElement.style.opacity = "1";
                }
            }

            async function jalankanPencarian() {
                const queryInput = document.getElementById('query').value.trim();
                const statusBadge = document.getElementById('statusBadge');
                const statusDot = document.getElementById('statusDot');
                const statusText = document.getElementById('statusText');
                const resultContainer = document.getElementById('resultContainer');
                const tableBody = document.getElementById('resultTableBody');

                if (!queryInput || queryInput.length < 2) {
                    resultContainer.classList.add('hidden');
                    statusBadge.classList.add('hidden');
                    return;
                }

                statusBadge.classList.remove('hidden');
                statusDot.className = "status-dot loading";
                statusText.innerText = "Memproses pencarian data...";

                try {
                    const response = await fetch(`/search?q=${encodeURIComponent(queryInput)}`);
                    const result = await response.json();

                    if (result.status === "success" && result.total_results > 0) {
                        statusDot.className = "status-dot";
                        statusText.innerText = `Menampilkan seluruh ${result.total_results} data buku yang cocok secara utuh.`;
                        
                        tableBody.innerHTML = "";
                        result.data.forEach(item => {
                            const row = document.createElement('tr');
                            const safeNUP = (item.NUP || '-').replace(/'/g, "\\'").replace(/"/g, '&quot;');
                            const safeJudul = (item['Judul Buku'] || '-').replace(/'/g, "\\'").replace(/"/g, '&quot;');

                            row.innerHTML = `
                                <td class="font-mono-style">${item.NUP || '-'}</td>
                                <td style="color: #1a202c; font-weight: 600;">${item['Judul Buku'] || '-'}</td>
                                <td><span class="badge-kode">${item.Kodefikasi || '-'}</span></td>
                                <td style="text-align: center;">
                                    <button onclick="eksekusiKirim(this, '${safeNUP}', '${safeJudul}')" class="btn-action">
                                        Kirim Data
                                    </button>
                                </td>
                            `;
                            tableBody.appendChild(row);
                        });
                        resultContainer.classList.remove('hidden');
                    } else {
                        statusDot.className = "status-dot error";
                        statusText.innerText = "Tidak ditemukan data yang cocok.";
                        resultContainer.classList.add('hidden');
                    }
                } catch (error) {
                    statusDot.className = "status-dot error";
                    statusText.innerText = "Gangguan mengambil data ke server.";
                }
            }

            document.getElementById('query').addEventListener('input', function() {
                clearTimeout(debounceTimer);
                debounceTimer = setTimeout(jalankanPencarian, 350);
            });

            document.getElementById('searchForm').addEventListener('submit', function(e) {
                e.preventDefault();
                clearTimeout(debounceTimer);
                jalankanPencarian();
            });
        </script>
    </body>
    </html>
    """
    return html_content

# ==========================================
# 3. BACKEND ENGINE (PENCARIAN FULL TANPA BATAS)
# ==========================================
@app.get("/search")
def search_books(q: str = Query(..., description="Kata kunci pencarian")):
    df = load_initial_data()
    if df is None:
        raise HTTPException(status_code=500, detail="Database file CSV gagal dimuat di server.")
    
    query_clean = q.replace(" ", "").replace(".", "").lower()
    if not query_clean:
        raise HTTPException(status_code=400, detail="Kata kunci tidak boleh kosong.")
    
    target_search_cols = [c for c in ['Merk', 'Kode1', 'Kode2', 'Kode3'] if c in df.columns]
    if not target_search_cols:
        raise HTTPException(status_code=500, detail="Kolom target pencarian tidak ditemukan di struktur CSV.")
        
    df_target = df[target_search_cols].astype(str).apply(lambda s: s.str.replace(" ", "", regex=False).str.replace(".", "", regex=False).str.lower())
    mask_match = df_target.apply(lambda s: s.str.contains(query_clean, na=False))
    rows_matched = mask_match.any(axis=1)
    
    if rows_matched.any():
        hasil_filter = df[rows_matched].copy()
        
        # NOTE: Batasan head(50) telah dihapus sepenuhnya agar menampilkan semua baris data
        
        hasil_filter['Judul Buku'] = hasil_filter['Merk'] if 'Merk' in hasil_filter.columns else "-"
        if 'NUP' not in hasil_filter.columns:
            hasil_filter['NUP'] = "-"

        def hitung_kodefikasi(row):
            parts = []
            for col in ['Kode1', 'Kode2', 'Kode3']:
                if col in row and str(row[col]).strip():
                    parts.append(str(row[col]).strip())
            return " / ".join(parts) if parts else "-"
            
        hasil_filter['Kodefikasi'] = hasil_filter.apply(hitung_kodefikasi, axis=1)
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
