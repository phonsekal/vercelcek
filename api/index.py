from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import numpy as np
import os

app = FastAPI(
    title="Sistem Inventarisasi Buku Perpustakaan Badan Bahasa 2026",
    version="2026.9"
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
# FRONTEND WITH REQUESTED CUSTOM HEADER
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
        <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap">
        <script src="https://cdn.tailwindcss.com"></script>
        <script>
            // Menambahkan warna tema khusus untuk mendefinisikan utilitas kelas text-primary/hover:text-primary
            tailwind.config = {
                theme: {
                    extend: {
                        colors: {
                            primary: {
                                400: '#22d3ee',
                                500: '#06b6d4',
                            }
                        }
                    }
                }
            }
        </script>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            body {
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
                background-color: #ffffff;
                color: #111111;
                line-height: 1.6;
                min-height: 100vh;
                display: flex;
                flex-direction: column;
                -webkit-font-smoothing: antialiased;
            }
            
            ::-webkit-scrollbar { width: 5px; height: 5px; }
            ::-webkit-scrollbar-track { background: #ffffff; }
            ::-webkit-scrollbar-thumb { background: #e2e8f0; border-radius: 99px; }
            ::-webkit-scrollbar-thumb:hover { background: #cbd5e0; }

            .custom-nav-container {
                max-width: 1100px;
                margin: 0 auto;
                width: 100%;
                padding: 0 2rem;
            }
            
            main {
                flex: 1;
                width: 100%;
                max-width: 1100px;
                margin: 0 auto;
                padding: 2.5rem 2rem;
            }
            
            .hero { margin-bottom: 3rem; border-bottom: 1px solid #efefef; padding-bottom: 1.5rem; }
            .hero h1 {
                font-size: 2.5rem;
                font-weight: 800;
                color: #111111;
                letter-spacing: -0.04em;
                margin-bottom: 0.25rem;
            }
            .subtitle { font-size: 1.05rem; color: #666666; font-weight: 400; }

            .form-group label {
                font-size: 0.75rem;
                color: #111111;
                font-weight: 700;
                letter-spacing: 0.05em;
                display: block;
                margin-bottom: 0.75rem;
            }
            .input-wrapper { display: flex; gap: 0.75rem; }
            .search-box input {
                flex: 1;
                background-color: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                padding: 0.75rem 1rem;
                color: #111111;
                font-size: 0.95rem;
                outline: none;
                transition: border-color 0.2s;
            }
            .search-box input:focus {
                border-color: #111111;
            }
            .btn-search {
                background-color: #111111;
                color: #ffffff;
                border: none;
                padding: 0.75rem 1.5rem;
                font-size: 0.9rem;
                font-weight: 600;
                border-radius: 6px;
                cursor: pointer;
                transition: opacity 0.2s;
            }
            .btn-search:hover { opacity: 0.9; }

            .status-badge {
                display: flex;
                align-items: center;
                gap: 0.5rem;
                color: #666666;
                font-size: 0.85rem;
                margin-bottom: 1.5rem;
                padding-bottom: 0.5rem;
            }
            .status-dot { width: 6px; height: 6px; background-color: #10b981; border-radius: 50%; }
            .status-dot.loading { background-color: #f59e0b; animation: pulse 1s infinite; }
            .status-dot.error { background-color: #ef4444; }

            .table-container {
                width: 100%;
                margin-top: 1rem;
                animation: fadeIn 0.3s ease;
            }
            table { width: 100%; border-collapse: collapse; text-align: left; }
            th {
                border-bottom: 1px solid #111111;
                color: #111111;
                font-weight: 700;
                padding: 0.75rem 1rem;
                font-size: 0.8rem;
                text-transform: uppercase;
                letter-spacing: 0.05em;
            }
            td { padding: 1rem; border-bottom: 1px solid #f0f0f0; color: #444444; font-size: 0.9rem; }
            tr:hover td { color: #111111; }
            
            .font-mono-style { font-family: monospace; font-size: 0.8rem; color: #888888; }
            .badge-kode { color: #666666; font-size: 0.8rem; }
            
            .btn-action {
                background: none;
                border: none;
                color: #111111;
                font-size: 0.85rem;
                font-weight: 600;
                cursor: pointer;
                text-decoration: underline;
                padding: 0.25rem 0.5rem;
                transition: opacity 0.2s;
            }
            .btn-action:hover { opacity: 0.6; }
            .btn-success-style {
                color: #10b981 !important;
                text-decoration: none !important;
                cursor: default;
                font-weight: 700;
            }
            
            .hidden { display: none; }
            @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
            @keyframes pulse { 0% { opacity: 0.5; } 50% { opacity: 1; } 100% { opacity: 0.5; } }

            @media (max-width: 768px) {
                .custom-nav-container { padding: 0 1rem; }
                main { padding: 2rem 1rem; }
                .hero h1 { font-size: 2rem; }
                .input-wrapper { flex-direction: column; }
                .btn-search { width: 100%; }
                th, td { padding: 0.75rem 0.5rem; }
            }
        </style>
    </head>
    <body>
        <div class="border-b border-gray-100 bg-white dark:bg-gray-950 w-full">
            <div class="custom-nav-container">
                <header class="flex items-center w-full justify-between py-10">
                    <a class="break-words" aria-label="dedesaputra Blog" href="/">
                        <div class="flex items-center justify-between" bis_skin_checked="1">
                            <div class="mr-3" bis_skin_checked="1">
                                <svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="53.87" height="43.61" viewBox="344.564 330.278 111.737 91.218">
                                    <defs>
                                        <linearGradient id="logo_svg__b" x1="420.97" x2="420.97" y1="331.28" y2="418.5" gradientUnits="userSpaceOnUse">
                                            <stop offset="0%" style="stop-color:#06b6d4;stop-opacity:1"></stop>
                                            <stop offset="100%" style="stop-color:#67e8f9;stop-opacity:1"></stop>
                                        </linearGradient>
                                        <linearGradient id="logo_svg__d" x1="377.89" x2="377.89" y1="331.28" y2="418.5" gradientUnits="userSpaceOnUse">
                                            <stop offset="0%" style="stop-color:#06b6d4;stop-opacity:1"></stop>
                                            <stop offset="100%" style="stop-color:#67e8f9;stop-opacity:1"></stop>
                                        </linearGradient>
                                        <path id="logo_svg__a" d="M453.3 331.28v28.57l-64.66 58.65v-30.08z"></path>
                                        <path id="logo_svg__c" d="M410.23 331.28v28.57l-64.67 58.65v-30.08z"></path>
                                    </defs>
                                    <use xlink:href="#logo_svg__a" fill="url(#logo_svg__b)"></use>
                                    <use xlink:href="#logo_svg__c" fill="url(#logo_svg__d)"></use>
                                </svg>
                            </div>
                            <div class="hidden h-6 text-2xl font-semibold sm:block" bis_skin_checked="1">dedesaputra Blog</div>
                        </div>
                    </a>
                    <div class="flex items-center space-x-4 leading-5 sm:-mr-6 sm:space-x-6" bis_skin_checked="1">
                        <div class="no-scrollbar hidden max-w-40 items-center gap-x-4 overflow-x-auto sm:flex md:max-w-72 lg:max-w-96" bis_skin_checked="1">
                            <a class="hover:text-primary-500 dark:hover:text-primary-400 m-1 font-medium text-gray-900 dark:text-gray-100" href="/blog">Blog</a>
                            <a class="hover:text-primary-500 dark:hover:text-primary-400 m-1 font-medium text-gray-900 dark:text-gray-100" href="/projects">Projects</a>
                            <a class="hover:text-primary-500 dark:hover:text-primary-400 m-1 font-medium text-gray-900 dark:text-gray-100" href="/about">About</a>
                        </div>
                        <button aria-label="Search">
                            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="hover:text-primary-500 dark:hover:text-primary-400 h-6 w-6 text-gray-900 dark:text-gray-100">
                                <path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.607 10.607z"></path>
                            </svg>
                        </button>
                        <div class="flex items-center" bis_skin_checked="1">
                            <div class="relative inline-block text-left" data-headlessui-state="" bis_skin_checked="1">
                                <div class="hover:text-primary-500 dark:hover:text-primary-400 flex items-center justify-center" bis_skin_checked="1">
                                    <button aria-label="Theme switcher" id="headlessui-menu-button-«Rtpkqlb»" type="button" aria-haspopup="menu" aria-expanded="false" data-headlessui-state="">
                                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="group:hover:text-gray-100 h-6 w-6">
                                            <path fill-rule="evenodd" d="M10 2a1 1 0 011 1v1a1 1 0 11-2 0V3a1 1 0 011-1zm4 8a4 4 0 11-8 0 4 4 0 018 0zm-.464 4.95l.707.707a1 1 0 001.414-1.414l-.707-.707a1 1 0 00-1.414 1.414zm2.12-10.607a1 1 0 010 1.414l-.706.707a1 1 0 11-1.414-1.414l.707-.707a1 1 0 011.414 0zM17 11a1 1 0 100-2h-1a1 1 0 100 2h1zm-7 4a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1zM5.05 6.464A1 1 0 106.465 5.05l-.708-.707a1 1 0 00-1.414 1.414l.707.707zm1.414 8.486l-.707.707a1 1 0 01-1.414-1.414l.707-.707a1 1 0 011.414 1.414zM4 11a1 1 0 100-2H3a1 1 0 000 2h1z" clip-rule="evenodd"></path>
                                        </svg>
                                    </button>
                                </div>
                            </div>
                        </div>
                        <button aria-label="Toggle Menu" class="sm:hidden">
                            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="hover:text-primary-500 dark:hover:text-primary-400 h-8 w-8 text-gray-900 dark:text-gray-100">
                                <path fill-rule="evenodd" d="M3 5a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zM3 10a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zM3 15a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clip-rule="evenodd"></path>
                            </svg>
                        </button>
                    </div>
                </header>
            </div>
        </div>
        
        <main>
            <div class="hero">
                <h1>Inventarisasi Buku</h1>
                <p class="subtitle">Sekretariat Badan Pengembangan dan Pembinaan Bahasa</p>
            </div>

            <div class="search-box">
                <form id="searchForm">
                    <div class="form-group">
                        <label for="query">PENCARIAN DATA</label>
                        <div class="input-wrapper">
                            <input type="text" id="query" name="query" autocomplete="off" required placeholder="Ketik kata kunci untuk mencari buku...">
                            <button type="submit" id="searchBtn" class="btn-search">Cari</button>
                        </div>
                    </div>
                </form>
            </div>

            <div id="statusBadge" class="hidden status-badge">
                <div id="statusDot" class="status-dot"></div>
                <span id="statusText">Siap</span>
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

                try {
                    await fetch(WEB_APP_URL, {
                        method: 'POST',
                        mode: 'no-cors', 
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ nup: nup, merk: judul })
                    });
                    
                    buttonElement.innerText = "✓ Tersimpan";
                    buttonElement.className = "btn-action btn-success-style";
                } catch (error) {
                    buttonElement.disabled = false;
                    buttonElement.innerText = "Gagal";
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
                statusText.innerText = "Mencari data...";

                try {
                    const response = await fetch(`/search?q=${encodeURIComponent(queryInput)}`);
                    const result = await response.json();

                    if (result.status === "success" && result.total_results > 0) {
                        statusDot.className = "status-dot";
                        statusText.innerText = `Menampilkan ${result.total_results} data buku.`;
                        
                        tableBody.innerHTML = "";
                        result.data.forEach(item => {
                            const row = document.createElement('tr');
                            const safeNUP = (item.NUP || '-').replace(/'/g, "\\'").replace(/"/g, '&quot;');
                            const safeJudul = (item['Judul Buku'] || '-').replace(/'/g, "\\'").replace(/"/g, '&quot;');

                            row.innerHTML = `
                                <td class="font-mono-style">${item.NUP || '-'}</td>
                                <td style="color: #111111; font-weight: 500;">${item['Judul Buku'] || '-'}</td>
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
                        statusText.innerText = "Data tidak ditemukan.";
                        resultContainer.classList.add('hidden');
                    }
                } catch (error) {
                    statusDot.className = "status-dot error";
                    statusText.innerText = "Gagal mengambil data.";
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
# 3. BACKEND ENGINE (PENCARIAN UTUH)
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
