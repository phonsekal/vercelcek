from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import numpy as np
import os

app = FastAPI(
    title="Sistem Inventarisasi Buku Perpustakaan Badan Bahasa 2026",
    version="2026.6"
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
# FRONTEND INTERAKTIF & ULTRA MODERN (VERCEL DESIGN v2)
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
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
                background-color: #050505;
                color: #fafafa;
                line-height: 1.6;
                min-height: 100vh;
                display: flex;
                flex-direction: column;
            }
            
            /* Custom Thin Scrollbar */
            ::-webkit-scrollbar { width: 6px; height: 6px; }
            ::-webkit-scrollbar-track { background: #0a0a0a; }
            ::-webkit-scrollbar-thumb { background: #222222; border-radius: 3px; }
            ::-webkit-scrollbar-thumb:hover { background: #333333; }

            header {
                border-bottom: 1px solid #1f1f1f;
                background: rgba(5, 5, 5, 0.8);
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
                font-size: 1.1rem;
                font-weight: 600;
                color: #ffffff;
                text-decoration: none;
                display: flex;
                align-items: center;
                gap: 0.5rem;
            }
            .nav-links a {
                text-decoration: none;
                color: #888888;
                padding: 0.5rem 1rem;
                border-radius: 6px;
                transition: all 0.2s;
                font-size: 0.875rem;
                font-weight: 500;
                margin-left: auto;
            }
            .nav-links a:hover { color: #ffffff; background-color: #111111; }
            
            main {
                flex: 1;
                width: 100%;
                max-width: 1200px;
                margin: 0 auto;
                padding: 4rem 2rem;
            }
            
            .hero { text-align: center; margin-bottom: 3rem; }
            .hero h1 {
                font-size: 3rem;
                font-weight: 800;
                margin-bottom: 0.75rem;
                letter-spacing: -0.04em;
                background: linear-gradient(180deg, #ffffff 0%, #a1a1a1 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }
            .subtitle { font-size: 1.1rem; color: #888888; font-weight: 400; }

            /* Search Panel Premium Glow */
            .search-box {
                background: #0a0a0a;
                border: 1px solid #1f1f1f;
                border-radius: 12px;
                padding: 2rem;
                margin-bottom: 2rem;
                box-shadow: 0 4px 30px rgba(0, 0, 0, 0.5);
                transition: border-color 0.3s, box-shadow 0.3s;
            }
            .search-box:focus-within {
                border-color: #333333;
                box-shadow: 0 0 25px rgba(0, 112, 243, 0.1);
            }
            .form-group label {
                font-size: 0.75rem;
                color: #666666;
                font-weight: 700;
                letter-spacing: 0.1em;
                display: block;
                margin-bottom: 0.75rem;
            }
            .input-wrapper { display: flex; gap: 1rem; }
            .search-box input {
                flex: 1;
                background-color: #000000;
                border: 1px solid #1f1f1f;
                border-radius: 8px;
                padding: 0.85rem 1.25rem;
                color: #ffffff;
                font-size: 1rem;
                outline: none;
                transition: all 0.2s;
            }
            .search-box input:focus {
                border-color: #0070f3;
                background-color: #030303;
            }
            .btn-search {
                background-color: #fafafa;
                color: #000000;
                border: none;
                padding: 0.85rem 2rem;
                font-size: 0.95rem;
                font-weight: 600;
                border-radius: 8px;
                cursor: pointer;
                transition: all 0.2s;
            }
            .btn-search:hover { background-color: #e1e1e1; transform: translateY(-1px); }
            .btn-search:active { transform: translateY(0); }

            /* Status Badge */
            .status-badge {
                display: inline-flex;
                align-items: center;
                gap: 0.6rem;
                background-color: #0a0a0a;
                border: 1px solid #1f1f1f;
                color: #a1a1a1;
                padding: 0.6rem 1.2rem;
                border-radius: 8px;
                font-size: 0.875rem;
                margin-bottom: 1.5rem;
                width: 100%;
                animation: fadeIn 0.3s ease;
            }
            .status-dot { width: 8px; height: 8px; background-color: #00ff88; border-radius: 50%; box-shadow: 0 0 8px #00ff88; }
            .status-dot.loading { background-color: #ffaa00; box-shadow: 0 0 8px #ffaa00; animation: pulse 1s infinite; }
            .status-dot.error { background-color: #ff3333; box-shadow: 0 0 8px #ff3333; }

            /* Table Container Smooth Fade-In */
            .table-container {
                background-color: #0a0a0a;
                border: 1px solid #1f1f1f;
                border-radius: 12px;
                overflow: hidden;
                width: 100%;
                box-shadow: 0 10px 30px rgba(0,0,0,0.4);
                animation: fadeIn 0.4s cubic-bezier(0.16, 1, 0.3, 1);
            }
            table { width: 100%; border-collapse: collapse; text-align: left; }
            th {
                background-color: #0f0f0f;
                border-bottom: 1px solid #1f1f1f;
                color: #666666;
                font-weight: 600;
                padding: 1.1rem 1.5rem;
                text-transform: uppercase;
                font-size: 0.725rem;
                letter-spacing: 0.08em;
            }
            td { padding: 1.1rem 1.5rem; border-bottom: 1px solid #141414; color: #a1a1a1; font-size: 0.925rem; transition: background-color 0.2s; }
            tr:last-child td { border-bottom: none; }
            tr:hover td { background-color: #121212; color: #ffffff; }
            
            .font-mono-style { font-family: monospace; font-size: 0.85rem; color: #666666; }
            .badge-kode {
                background-color: #141414;
                color: #eaeaea;
                padding: 0.25rem 0.5rem;
                border-radius: 6px;
                font-size: 0.775rem;
                border: 1px solid #1f1f1f;
            }
            
            /* Interactive Button Style */
            .btn-action {
                display: inline-flex;
                align-items: center;
                color: #ffffff;
                text-decoration: none;
                font-size: 0.8rem;
                font-weight: 500;
                padding: 0.5rem 1rem;
                background-color: #161616;
                border-radius: 6px;
                border: 1px solid #222222;
                cursor: pointer;
                transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
            }
            .btn-action:hover {
                background-color: #ffffff;
                color: #000000;
                border-color: #ffffff;
                transform: scale(1.03);
            }
            .btn-success-style {
                background-color: #0070f3 !important;
                border-color: #0070f3 !important;
                color: #ffffff !important;
                transform: scale(1) !important;
                cursor: default;
                box-shadow: 0 0 15px rgba(0, 112, 243, 0.3);
            }
            
            .hidden { display: none; }

            @keyframes fadeIn { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }
            @keyframes pulse { 0% { opacity: 0.5; } 50% { opacity: 1; } 100% { opacity: 0.5; } }

            @media (max-width: 768px) {
                main { padding: 2rem 1rem; }
                .hero h1 { font-size: 2rem; }
                .input-wrapper { flex-direction: column; }
                .btn-search { width: 100%; }
                th, td { padding: 0.85rem 1rem; }
            }
        </style>
    </head>
    <body>
        <header>
            <nav>
                <a href="/" class="logo">
                    <svg width="18" height="18" viewBox="0 0 76 65" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M37.5274 0L75.0548 65H0L37.5274 0Z" fill="#ffffff"/></svg>
                    <span>Badan Pengembangan dan Pembinaan Bahasa</span>
                </a>
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
                        <label for="query">PENCARIAN DATA INSTAN (MERK / KODE KELOMPOK)</label>
                        <div class="input-wrapper">
                            <input type="text" id="query" name="query" autocomplete="off" required placeholder="Mulai mengetik untuk mencari...">
                            <button type="submit" id="searchBtn" class="btn-search">Cari Data</button>
                        </div>
                    </div>
                </form>
            </div>

            <div id="statusBadge" class="hidden status-badge">
                <div id="statusDot" class="status-dot"></div>
                <span id="statusText">Sistem Bersiap</span>
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
                    
                    buttonElement.innerText = "✓ Berhasil";
                    buttonElement.className = "btn-action btn-success-style";
                    buttonElement.style.opacity = "1";
                } catch (error) {
                    buttonElement.disabled = false;
                    buttonElement.innerText = "❌ Gagal";
                    buttonElement.style.opacity = "1";
                }
            }

            // Fungsi Engine Inti untuk Menembak API Tanpa Reload Halaman
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
                statusText.innerText = "Sedang mencocokkan matriks data...";

                try {
                    const response = await fetch(`/search?q=${encodeURIComponent(queryInput)}`);
                    const result = await response.json();

                    if (result.status === "success" && result.total_results > 0) {
                        statusDot.className = "status-dot";
                        statusText.innerText = `Menampilkan ${result.total_results} buku yang cocok.`;
                        
                        tableBody.innerHTML = "";
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
                                        Kirim Data
                                    </button>
                                </td>
                            `;
                            tableBody.appendChild(row);
                        });
                        resultContainer.classList.remove('hidden');
                    } else {
                        statusDot.className = "status-dot error";
                        statusText.innerText = "Tidak ada kecocokan data.";
                        resultContainer.classList.add('hidden');
                    }
                } catch (error) {
                    statusDot.className = "status-dot error";
                    statusText.innerText = "Koneksi terputus.";
                }
            }

            // FITUR INTERAKTIF 1: Pencarian Otomatis Saat Mengetik (Debounce)
            document.getElementById('query').addEventListener('input', function() {
                clearTimeout(debounceTimer);
                // Menunggu 350ms setelah pengguna berhenti mengetik untuk mencegah overload request API
                debounceTimer = setTimeout(jalankanPencarian, 350);
            });

            // FITUR INTERAKTIF 2: Tombol Manual Enter tetap dipertahankan
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
        
        # Ambil maksimal 50 baris pertama untuk optimasi kecepatan render browser
        if len(hasil_filter) > 50:
            hasil_filter = hasil_filter.head(50)
            
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
