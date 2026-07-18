from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import numpy as np
import os

app = FastAPI(
    title="KarsaPustaka — Sistem Inventarisasi Buku Perpustakaan Badan Bahasa 2026",
    version="2026.12"
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

@app.get("/", response_class=HTMLResponse)
def home():
    html_content = """
    <!DOCTYPE html>
    <html lang="id" class="light">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Inventarisasi Buku Perpustakaan Badan Bahasa 2026</title>
        <link rel="icon" type="image/x-icon" href="/favicon.ico">
        <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap">
        <script src="https://cdn.tailwindcss.com"></script>
        <script>
            tailwind.config = {
                darkMode: 'class',
                theme: {
                    extend: {
                        colors: {
                            primary: {
                                400: '#67e8f9',
                                500: '#06b6d4',
                            }
                        }
                    }
                }
            }
        </script>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
                line-height: 1.6;
                min-height: 100vh;
                display: flex;
                flex-direction: column;
                -webkit-font-smoothing: antialiased;
                transition: background-color 0.2s, color 0.2s;
            }
            ::-webkit-scrollbar { width: 5px; height: 5px; }
            ::-webkit-scrollbar-track { background: transparent; }
            ::-webkit-scrollbar-thumb { background: #e2e8f0; border-radius: 99px; }
            .dark ::-webkit-scrollbar-thumb { background: #2d3748; }
            .custom-nav-container { max-width: 1100px; margin: 0 auto; width: 100%; padding: 0 2rem; }
            main { flex: 1; width: 100%; max-width: 1100px; margin: 0 auto; padding: 2.5rem 2rem; }
            .hidden { display: none; }
            @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
            .animate-fade { animation: fadeIn 0.3s ease; }
            @media (max-width: 768px) {
                .custom-nav-container { padding: 0 1rem; }
                main { padding: 2rem 1rem; }
                .input-wrapper { flex-direction: column; }
            }
        </style>
    </head>
    <body class="bg-white text-gray-900 dark:bg-gray-950 dark:text-gray-100">
        
        <!-- STICKY HEADER -->
        <div class="sticky top-0 z-50 border-b border-gray-100 bg-white/90 dark:border-gray-900 dark:bg-gray-950/90 backdrop-blur-md w-full transition-colors">
            <div class="custom-nav-container">
                <header class="flex items-center w-full justify-between py-10">
                    <a class="break-words" aria-label="KarsaPustaka" href="/">
                        <div class="flex items-center justify-between">
                            <div class="mr-3">
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
                            <div class="hidden h-6 text-2xl font-semibold sm:block text-gray-900 dark:text-gray-100">karsaPustaka</div>
                        </div>
                    </a>
                    <div class="flex items-center space-x-4 leading-5 sm:-mr-6 sm:space-x-6">
                        <div class="no-scrollbar hidden max-w-40 items-center gap-x-4 overflow-x-auto sm:flex md:max-w-72 lg:max-w-96">
                            <a class="hover:text-primary-500 dark:hover:text-primary-400 m-1 font-medium text-gray-900 dark:text-gray-100" href="https://blog.dedesaputra.com">Blog</a>
                            <a class="hover:text-primary-500 dark:hover:text-primary-400 m-1 font-medium text-gray-900 dark:text-gray-100" href="https://blog.dedesaputra.com/about">About</a>
                            <a class="hover:text-primary-500 dark:hover:text-primary-400 m-1 font-medium text-gray-900 dark:text-gray-100" href="https://docs.google.com/spreadsheets/d/1CtWwWaMNW8lhkAHsCUhSNHBZxGAWlTrqDABzRM4_wkk/edit?gid=0#gid=0" target="_blank">Cek Buku</a>
                        </div>
                        <div class="flex items-center">
                            <div class="relative inline-block text-left">
                                <div class="hover:text-primary-500 dark:hover:text-primary-400 flex items-center justify-center">
                                    <button aria-label="Theme switcher" id="themeToggleBtn" type="button" class="text-gray-900 dark:text-gray-100 hover:text-primary-500 dark:hover:text-primary-400 transition-colors">
                                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="h-6 w-6">
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
            <div class="mb-12 border-b border-gray-100 dark:border-gray-900 pb-6">
                <h1 class="text-4xl font-extrabold tracking-tight text-gray-900 dark:text-gray-100 sm:text-5xl">Sistem Tata Kelola Pustaka</h1>
                <p class="text-base text-gray-500 dark:text-gray-400 mt-2">Sekretariat Badan Pengembangan dan Pembinaan Bahasa</p>
            </div>

            <div class="mb-8">
                <form id="searchForm">
                    <div class="flex flex-col gap-3">
                        <label for="query" class="text-xs font-bold tracking-wider uppercase text-gray-900 dark:text-gray-100">PENCARIAN DATA</label>
                        <div class="input-wrapper flex gap-3">
                            <input type="text" id="query" name="query" autocomplete="off" required 
                                placeholder="Ketik kata kunci untuk mencari buku..." 
                                class="flex-1 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-md px-4 py-2.5 text-gray-900 dark:text-gray-100 focus:outline-none focus:border-gray-900 dark:focus:border-gray-100 transition-colors">
                            <button type="submit" id="searchBtn" class="bg-gray-900 text-white dark:bg-gray-100 dark:text-gray-900 px-6 py-2.5 font-semibold text-sm rounded-md hover:opacity-80 transition-opacity">Cari</button>
                        </div>
                    </div>
                </form>
            </div>

            <div id="statusBadge" class="hidden text-xs text-gray-500 dark:text-gray-400 items-center gap-2 mb-6 animate-fade">
                <div id="statusDot" class="w-1.5 h-1.5 bg-emerald-500 rounded-full"></div>
                <span id="statusText">Siap</span>
            </div>

            <div class="table-container hidden w-full overflow-x-auto mt-4 animate-fade" id="resultContainer">
                <table class="w-full text-left border-collapse">
                    <thead>
                        <tr class="border-b border-gray-900 dark:border-gray-100">
                            <th class="text-xs font-bold uppercase text-gray-900 dark:text-gray-100 py-3 px-4 w-[15%]">NUP</th>
                            <th class="text-xs font-bold uppercase text-gray-900 dark:text-gray-100 py-3 px-4 w-[55%]">Judul Buku</th>
                            <th class="text-xs font-bold uppercase text-gray-900 dark:text-gray-100 py-3 px-4 w-[15%]">Kodefikasi</th>
                            <th class="text-xs font-bold uppercase text-gray-900 dark:text-gray-100 py-3 px-4 w-[15%] text-center">Aksi</th>
                        </tr>
                    </thead>
                    <tbody id="resultTableBody" class="divide-y divide-gray-100 dark:divide-gray-900"></tbody>
                </table>
            </div>
        </main>

        <!-- FOOTER -->
        <footer class="border-t border-gray-100 dark:border-gray-900 bg-white dark:bg-gray-950 transition-colors">
            <div class="mt-16 flex flex-col items-center">
                <div class="mb-3 flex space-x-4">
                    <a class="text-sm text-gray-500 transition hover:text-gray-600 dark:hover:text-gray-400" target="_blank" rel="noopener noreferrer" href="mailto:address@yoursite.com">
                        <span class="sr-only">mail</span>
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" class="hover:text-primary-500 dark:hover:text-primary-400 fill-current text-gray-700 dark:text-gray-200 h-6 w-6">
                            <title>Mail</title>
                            <path d="M2.003 5.884L10 9.882l7.997-3.998A2 2 0 0016 4H4a2 2 0 00-1.997 1.884z"></path>
                            <path d="M18 8.118l-8 4-8-4V14a2 2 0 002 2h12a2 2 0 002-2V8.118z"></path>
                        </svg>
                    </a>
                    <a class="text-sm text-gray-500 transition hover:text-gray-600 dark:hover:text-gray-400" target="_blank" rel="noopener noreferrer" href="https://github.com">
                        <span class="sr-only">github</span>
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" class="hover:text-primary-500 dark:hover:text-primary-400 fill-current text-gray-700 dark:text-gray-200 h-6 w-6">
                            <title>GitHub</title>
                            <path d="M12 .297c-6.63 0-12 5.373-12 12 0 5.303 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61C4.422 18.07 3.633 17.7 3.633 17.7c-1.087-.744.084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305.76-1.605-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 1.02.006 2.04.138 3 .405 2.28-1.552 3.285-1.23 3.285-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 1.096.81 2.22 0 1.606-.015 2.896-.015 3.286 0 .315.21.69.825.57C20.565 22.092 24 17.592 24 12.297c0-6.627-5.373-12-12-12"></path>
                        </svg>
                    </a>
                </div>
                <div class="mb-2 flex space-x-2 text-sm text-gray-500 dark:text-gray-400">
                    <div>Dede Saputra</div>
                    <div> • </div>
                    <div>© 2026</div>
                    <div> • </div>
                    <a class="break-words" href="https://blog.dedesaputra.com">Dede Saputra Blog</a>
                </div>
            </div>
        </footer>
        
        <script>
            // PASTIKAN WEB_APP_URL SUDAH VERSI DEPLOY TERBARU ANDA
            const WEB_APP_URL = "https://script.google.com/macros/s/AKfycbxczAQx-0AVR0IZr6x8F4eXveeNVw0dz6FoUsKpppA63A1OFIVLQD4uHoTmXLbetDNx/exec";
            let debounceTimer;

            const htmlElement = document.documentElement;
            const themeToggleBtn = document.getElementById('themeToggleBtn');

            if (localStorage.getItem('theme') === 'dark') {
                htmlElement.className = 'dark';
            } else {
                htmlElement.className = 'light';
            }

            themeToggleBtn.addEventListener('click', () => {
                if (htmlElement.classList.contains('dark')) {
                    htmlElement.className = 'light';
                    localStorage.setItem('theme', 'light');
                } else {
                    htmlElement.className = 'dark';
                    localStorage.setItem('theme', 'dark');
                }
            });

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
                    buttonElement.className = "text-emerald-500 dark:text-emerald-400 font-bold text-xs pointer-events-none";
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

                statusBadge.style.display = 'flex';
                statusDot.className = "w-1.5 h-1.5 bg-amber-500 rounded-full loading";
                statusText.innerText = "Mencari data...";

                try {
                    const response = await fetch(`/search?q=${encodeURIComponent(queryInput)}`);
                    const result = await response.json();

                    if (result.status === "success" && result.total_results > 0) {
                        statusDot.className = "w-1.5 h-1.5 bg-emerald-500 rounded-full";
                        statusText.innerText = `Menampilkan ${result.total_results} data buku.`;
                        
                        tableBody.innerHTML = "";
                        
                        // Kumpulkan NUP untuk dicek via GET (Sangat Aman dari Blokir CORS)
                        const nupList = result.data.map(item => (item.NUP || '-').trim());
                        let registeredNUPs = [];
                        
                        try {
                            // Menggunakan GET dengan parameter URL agar tembus CORS Google Script
                            const checkUrl = `${WEB_APP_URL}?nups=${encodeURIComponent(nupList.join(','))}`;
                            const checkResponse = await fetch(checkUrl, { method: 'GET' });
                            const checkResult = await checkResponse.json();
                            
                            if (checkResult && checkResult.status === "success" && checkResult.exists) {
                                registeredNUPs = checkResult.exists.map(n => String(n).trim());
                            }
                        } catch (e) {
                            console.error("Gagal melakukan verifikasi NUP duplikat:", e);
                        }

                        result.data.forEach(item => {
                            const row = document.createElement('tr');
                            const safeNUP = (item.NUP || '-').replace(/'/g, "\\'").replace(/"/g, '&quot;');
                            const safeJudul = (item['Judul Buku'] || '-').replace(/'/g, "\\'").replace(/"/g, '&quot;');
                            
                            let buttonHtml = `<button onclick="eksekusiKirim(this, '${safeNUP}', '${safeJudul}')" class="underline text-xs font-semibold text-gray-900 dark:text-gray-100 hover:opacity-60 transition-opacity">Kirim Data</button>`;
                            
                            // Jika NUP terdeteksi ada di database Google Sheet
                            if (registeredNUPs.includes(String(item.NUP).trim())) {
                                buttonHtml = `<button disabled class="text-red-500 dark:text-red-400 font-bold text-xs cursor-not-allowed">Sudah pernah kirim</button>`;
                            }

                            row.innerHTML = `
                                <td class="font-mono-style py-4 px-4">${item.NUP || '-'}</td>
                                <td class="py-4 px-4 font-medium text-gray-950 dark:text-gray-50">${item['Judul Buku'] || '-'}</td>
                                <td class="py-4 px-4"><span class="text-xs text-gray-500 dark:text-gray-400">${item.Kodefikasi || '-'}</span></td>
                                <td class="py-4 px-4 text-center">${buttonHtml}</td>
                            `;
                            tableBody.appendChild(row);
                        });
                        resultContainer.classList.remove('hidden');
                    } else {
                        statusDot.className = "w-1.5 h-1.5 bg-red-500 rounded-full error";
                        statusText.innerText = "Data tidak ditemukan.";
                        resultContainer.classList.add('hidden');
                    }
                } catch (error) {
                    statusDot.className = "w-1.5 h-1.5 bg-red-500 rounded-full error";
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
# BACKEND ENGINE
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
