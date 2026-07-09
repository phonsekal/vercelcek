from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import numpy as np
import os

app = FastAPI(
    title="Sistem Inventarisasi Buku Perpustakaan Badan Bahasa 2026",
    version="2026.5"
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

# Inisialisasi data di awal
load_initial_data()

# ==========================================
# 1. ROUTE KHUSUS UNTUK FAVICON
# ==========================================
@app.get('/favicon.ico', include_in_schema=False)
async def favicon():
    favicon_path = "favicon.ico"
    if not os.path.exists(favicon_path):
        favicon_path = os.path.join(os.path.dirname(__file__), "..", "favicon.ico")
    
    if os.path.exists(favicon_path):
        return FileResponse(favicon_path)
    return HTTPException(status_code=404, detail="Favicon tidak ditemukan")

# ==========================================
# 2. FRONTEND DENGAN DESAIN VERCEL DARK MODE
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
        <link rel="icon" type="image/x-icon" href="/favicon.ico">
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', sans-serif;
                background-color: #000000;
                color: #ffffff;
                line-height: 1.6;
                min-height: 100vh;
                display: flex;
                flex-direction: column;
            }
            header {
                border-bottom: 1px solid #333333;
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
                color: #ffffff;
                text-decoration: none;
                letter-spacing: -0.02em;
            }
            .nav-links {
                display: flex;
                gap: 1.5rem;
                margin-left: auto;
            }
            .nav-links a {
                text-decoration: none;
                color: #888888;
                padding: 0.5rem 1rem;
                border-radius: 6px;
                transition: all 0.2s ease;
                font-size: 0.875rem;
                font-weight: 500;
            }
            .nav-links a:hover {
                color: #ffffff;
                background-color: #111111;
            }
            main {
                flex: 1;
                width: 100%;
                max-width: 1200px;
                margin: 0 auto;
                padding: 3rem 2rem;
            }
            .hero h1 {
                font-size: 2.5rem;
                font-weight: 700;
                margin-bottom: 0.5rem;
                letter-spacing: -0.03em;
                background: linear-gradient(to right, #ffffff, #888888);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }
            .subtitle {
                font-size: 1.05rem;
                color: #888888;
                margin-bottom: 2.5rem;
            }
            .search-box {
                background-color: #0a0a0a;
                border: 1px solid #333333;
                border-radius: 8px;
                padding: 1.5rem;
                margin-bottom: 2rem;
            }
            .form-group {
                display: flex;
                flex-direction: column;
                gap: 0.5rem;
                width: 100%;
            }
            .form-group label {
                font-size: 0.875rem;
                color: #888888;
                font-weight: 500;
            }
            .input-wrapper {
                display: flex;
                gap: 1rem;
            }
            .search-box input {
                flex: 1;
                background-color: #000000;
                border: 1px solid #333333;
                border-radius: 6px;
                padding: 0.75rem 1rem;
                color: #ffffff;
                font-size: 0.95rem;
                outline: none;
                transition: border-color 0.2s;
            }
            .search-box input:focus {
                border-color: #0070f3;
            }
            .btn-search {
                background-color: #ffffff;
                color: #000000;
                border: none;
                padding: 0.75rem 1.5rem;
                font-size: 0.925rem;
                font-weight: 600;
                border-radius: 6px;
                cursor: pointer;
                transition: background-color 0.2s;
                white-space: nowrap;
            }
            .btn-search:hover {
                background-color: #cccccc;
            }
            .status-badge {
                display: inline-flex;
                align-items: center;
                gap: 0.5rem;
                background-color: #111111;
                border: 1px solid #333333;
                color: #888888;
                padding: 0.5rem 1rem;
                border-radius: 6px;
                font-size: 0.875rem;
                margin-bottom: 2rem;
                width: 100%;
            }
            .status-dot {
                width: 8px;
                height: 8px;
                background-color: #00ff88;
                border-radius: 50%;
            }
            .status-dot.loading { background-color: #ffaa00; }
            .status-dot.error { background-color: #ff3333; }
            
            .table-container {
                background-color: #0a0a0a;
                border: 1px solid #333333;
                border-radius: 8px;
                overflow: hidden;
                width: 100%;
            }
            table {
                width: 100%;
                border-collapse: collapse;
                text-align: left;
                font-size: 0.9rem;
            }
            th {
                background-color: #111111;
                border-bottom: 1px solid #333333;
                color: #888888;
                font-weight: 600;
                padding: 1rem 1.5rem;
                text-transform: uppercase;
                font-size: 0.75rem;
                letter-spacing: 0.05em;
            }
            td {
                padding: 1rem 1.5rem;
                border-bottom: 1px solid #222222;
                color: #cccccc;
            }
            tr:hover td {
                background-color: #141414;
            }
            .font-mono-style {
                font-family: 'SF Mono', Monaco, monospace;
                font-size: 0.8rem;
                color: #888888;
            }
            .badge-kode {
                background-color: #222222;
                color: #ffffff;
                padding: 0.25rem 0.5rem;
                border-radius: 4px;
                font-size: 0.8rem;
                border: 1px solid #333333;
            }
            .btn-action {
                display: inline-flex;
                align-items: center;
                color: #ffffff;
                text-decoration: none;
                font-size: 0.8rem;
                font-weight: 500;
                padding: 0.4rem 0.8rem;
                background-color: #222222;
                border-radius: 6px;
                border: 1px solid #333333;
                cursor: pointer;
                transition: all 0.2s ease;
            }
            .btn-action:hover {
                background-color: #333333;
                border-color: #555555;
            }
            .btn-success-style {
                background-color: #0070f3 !important;
                border-color: #0070f3 !important;
                color: #ffffff !important;
                cursor: default;
            }
            .hidden { display: none; }

            @media (max-width: 768px) {
                nav { padding: 1rem; flex-direction: column; gap: 1rem; }
                .nav-links { margin-left: 0; }
                main { padding: 2rem 1rem; }
                .input-wrapper { flex-direction: column; }
                .btn-search { width: 100%; }
                th, td { padding: 0.75rem 1rem; }
            }
        </style>
    </head>
    <body>
        <header>
            <nav>
                <a href="/" class="logo">Badan Bahasa + BMN</a>
                <div class="nav-links">
                    <a href="/docs">API Docs</a>
                </div>
            </nav>
        </header>
        
        <main>
            <div class="hero">
                <h1>Inventarisasi Buku Perpustakaan</h1>
                <p class="subtitle">Sekretariat Badan Pengembangan dan Pembinaan Bahasa</p>
            </div>

            <div class="search-box">
                <form id="searchForm">
                    <div class="form-group">
                        <label for="query">PENCARIAN DATA (MERK, KODE1, KODE2, KODE3)</label>
                        <div class="input-wrapper">
                            <input type="text" id="query" name="query" autocomplete="off" required placeholder="Masukkan kata kunci di sini...">
                            <button type="submit" id="searchBtn" class="btn-search">Cari Data</button>
                        </div>
                    </div>
                </form>
            </div>

            <div id="statusBadge" class="hidden status-badge">
                <div id="statusDot" class="status-dot"></div>
                <span id="statusText">Sistem Siap</span>
            </div>

            <div class="table-container hidden" id="resultContainer">
                <table>
                    <thead>
                        <tr>
                            <th>NUP</th>
                            <th>Judul Buku</th>
                            <th>Kodefikasi</th>
                            <th style="text-align: center;">Aksi</th>
                        </tr>
                    </thead>
                    <tbody id="resultTableBody">
                        </tbody>
                </table>
            </div>
        </main>

        <script>
            const WEB_APP_URL = "https://script.google.com/macros/s/AKfycbyVCt37xvsX_oiNsw-AX99RW2SC4gU0K0qOMJvcY0909zqGMC1J1eaUbZOMrRI1oOXh/exec";

            async function eksekusiKirim(buttonElement, nup, judul) {
                buttonElement.disabled = true;
                buttonElement.innerText = "Mengirim...";
                buttonElement.style.opacity = "0.6";

                const payload = { nup: nup, merk: judul };

                try {
                    await fetch(WEB_APP_URL, {
                        method: 'POST',
                        mode: 'no-cors', 
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(payload)
                    });
                    
                    buttonElement.innerText = "✓ Berhasil";
                    buttonElement.className = "btn-action btn-success-style";
                    buttonElement.style.opacity = "1";
                } catch (error) {
                    buttonElement.disabled = false;
                    buttonElement.innerText = "❌ Gagal";
                    buttonElement.style.opacity = "1";
                }
            }

            document.getElementById('searchForm').addEventListener('submit', async function(e) {
                e.preventDefault();
                
                const queryInput = document.getElementById('query').value.trim();
                const searchBtn = document.getElementById('searchBtn');
                const statusBadge = document.getElementById('statusBadge');
                const statusDot = document.getElementById('statusDot');
                const statusText = document.getElementById('statusText');
                const resultContainer = document.getElementById('resultContainer');
                const tableBody = document.getElementById('resultTableBody');

                if (!queryInput) return;

                searchBtn.disabled = true;
                searchBtn.innerText = "Memproses...";
                
                statusBadge.classList.remove('hidden');
                statusDot.className = "status-dot loading";
                statusText.innerText = `Sedang mencari "${queryInput}"...`;
                
                resultContainer.classList.add('hidden');
                tableBody.innerHTML = "";

                try {
                    const response = await fetch(`/search?q=${encodeURIComponent(queryInput)}`);
                    const result = await response.json();

                    searchBtn.disabled = false;
                    searchBtn.innerText = "Cari Data";

                    if (result.status === "success" && result.total_results > 0) {
                        statusDot.className = "status-dot";
                        statusText.innerText = `Berhasil memuat ${result.total_results} data buku.`;

                        result.data.forEach(item => {
                            const row = document.createElement('tr');
                            const safeNUP = (item.NUP || '-').replace(/'/g, "\\'").replace(/"/g, '&quot;');
                            const safeJudul = (item['Judul Buku'] || '-').replace(/'/g, "\\'").replace(/"/g, '&quot;');

                            row.innerHTML = `
                                <td class="font-mono-style">${item.NUP || '-'}</td>
                                <td style="color: #ffffff; font-weight: 500;">${item['Judul Buku'] || '-'}</td>
                                <td><span class="badge-kode">${item.Kodefikasi || '-'}</span></td>
                                <td style="text-align: center;">
                                    <button onclick="eksekusiKirim(this, '${safeNUP}', '${safeJudul}')" class="btn-action">
                                        Kirim Data →
                                    </button>
                                </td>
                            `;
                            tableBody.appendChild(row);
                        });

                        resultContainer.classList.remove('hidden');
                    } else {
                        statusDot.className = "status-dot error";
                        statusText.innerText = "Data tidak ditemukan pada kolom Merk atau Kode1/2/3.";
                    }
                } catch (error) {
                    searchBtn.disabled = false;
                    searchBtn.innerText = "Cari Data";
                    statusDot.className = "status-dot error";
                    statusText.innerText = `Terjadi kesalahan: ${error.message}`;
                }
            });
        </script>
    </body>
    </html>
    """
    return html_content

# ==========================================
# 3. BACKEND ENGINE (PENCARIAN KHUSUS & CEPAT)
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
