from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import numpy as np
import os

app = FastAPI(
    title="Sistem Inventarisasi Buku Perpustakaan Badan Bahasa 2026",
    version="2026.10"
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
# FRONTEND WITH STICKY HEADER & CUSTOM FOOTER
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
            // Konfigurasi Tailwind Utility untuk text-primary & hover:text-primary-500
            tailwind.config = {
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
        
        <div class="sticky top-0 z-50 border-b border-gray-100 bg-white/90 backdrop-blur-md w-full">
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

        <footer>
            <div class="mt-16 flex flex-col items-center" bis_skin_checked="1">
                <div class="mb-3 flex space-x-4" bis_skin_checked="1">
                    <a class="text-sm text-gray-500 transition hover:text-gray-600" target="_blank" rel="noopener noreferrer" href="mailto:address@yoursite.com">
                        <span class="sr-only">mail</span>
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" class="hover:text-primary-500 fill-current text-gray-700 h-6 w-6">
                            <title>Mail</title>
                            <path d="M2.003 5.884L10 9.882l7.997-3.998A2 2 0 0016 4H4a2 2 0 00-1.997 1.884z"></path>
                            <path d="M18 8.118l-8 4-8-4V14a2 2 0 002 2h12a2 2 0 002-2V8.118z"></path>
                        </svg>
                    </a>
                    <a class="text-sm text-gray-500 transition hover:text-gray-600" target="_blank" rel="noopener noreferrer" href="https://github.com">
                        <span class="sr-only">github</span>
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" class="hover:text-primary-500 fill-current text-gray-700 h-6 w-6">
                            <title>GitHub</title>
                            <path d="M12 .297c-6.63 0-12 5.373-12 12 0 5.303 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61C4.422 18.07 3.633 17.7 3.633 17.7c-1.087-.744.084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305.76-1.605-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 1.02.006 2.04.138 3 .405 2.28-1.552 3.285-1.23 3.285-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 1.096.81 2.22 0 1.606-.015 2.896-.015 3.286 0 .315.21.69.825.57C20.565 22.092 24 17.592 24 12.297c0-6.627-5.373-12-12-12"></path>
                        </svg>
                    </a>
                    <a class="text-sm text-gray-500 transition hover:text-gray-600" target="_blank" rel="noopener noreferrer" href="https://facebook.com">
                        <span class="sr-only">facebook</span>
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" class="hover:text-primary-500 fill-current text-gray-700 h-6 w-6">
                            <title>Facebook</title>
                            <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"></path>
                        </svg>
                    </a>
                    <a class="text-sm text-gray-500 transition hover:text-gray-600" target="_blank" rel="noopener noreferrer" href="https://youtube.com">
                        <span class="sr-only">youtube</span>
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" class="hover:text-primary-500 fill-current text-gray-700 h-6 w-6">
                            <title>Youtube</title>
                            <path d="M23.499 6.203a3.008 3.008 0 00-2.089-2.089c-1.87-.501-9.4-.501-9.4-.501s-7.509-.01-9.399.501a3.008 3.008 0 00-2.088 2.09A31.258 31.26 0 000 12.01a31.258 31.26 0 00.523 5.785 3.008 3.008 0 002.088 2.089c1.869.502 9.4.502 9.4.502s7.508 0 9.399-.502a3.008 3.008 0 002.089-2.09 31.258 31.26 0 00.5-5.784 31.258 31.26 0 00-.5-5.808zm-13.891 9.4V8.407l6.266 3.604z"></path>
                        </svg>
                    </a>
                    <a class="text-sm text-gray-500 transition hover:text-gray-600" target="_blank" rel="noopener noreferrer" href="https://www.linkedin.com">
                        <span class="sr-only">linkedin</span>
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" class="hover:text-primary-500 fill-current text-gray-700 h-6 w-6">
                            <title>Linkedin</title>
                            <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 01-2.063-2.065 2.064 2.064 112.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"></path>
                        </svg>
                    </a>
                    <a class="text-sm text-gray-500 transition hover:text-gray-600" target="_blank" rel="noopener noreferrer" href="https://bsky.app/">
                        <span class="sr-only">bluesky</span>
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" class="hover:text-primary-500 fill-current text-gray-700 h-6 w-6">
                            <title>Bluesky</title>
                            <path d="M12 10.8c-1.087-2.114-4.046-6.053-6.798-7.995C2.566.944 1.561 1.266.902 1.565C.139 1.908 0 3.08 0 3.768c0 .69.378 5.65.624 6.479c.815 2.736 3.713 3.66 6.383 3.364q.204-.03.415-.056q-.207.033-.415.056c-3.912.58-7.387 2.005-2.83 7.078c5.013 5.19 6.87-1.113 7.823-4.308c.953 3.195 2.05 9.271 7.733 4.308c4.267-4.308 1.172-6.498-2.74-7.078a9 9 0 0 1-.415-.056q.21.026.415.056c2.67.297 5.568-.628 6.383-3.364c.246-.828.624-5.79.624-6.478c0-.69-.139-1.861-.902-2.206c-.659-.298-1.664-.62-4.3 1.24C16.046 4.748 13.087 8.687 12 10.8"></path>
                        </svg>
                    </a>
                    <a class="text-sm text-gray-500 transition hover:text-gray-600" target="_blank" rel="noopener noreferrer" href="https://twitter.com/x">
                        <span class="sr-only">x</span>
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" class="hover:text-primary-500 fill-current text-gray-700 h-6 w-6">
                            <title>X</title>
                            <path d="M18.901 1.153h3.68l-8.04 9.19L24 22.846h-7.406l-5.8-7.584-6.638 7.584H.474l8.6-9.83L0 1.154h7.594l5.243 6.932ZM17.61 20.644h2.039L6.486 3.24H4.298Z"></path>
                        </svg>
                    </a>
                    <a class="text-sm text-gray-500 transition hover:text-gray-600" target="_blank" rel="noopener noreferrer" href="https://www.instagram.com">
                        <span class="sr-only">instagram</span>
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" class="hover:text-primary-500 fill-current text-gray-700 h-6 w-6">
                            <title>Instagram</title>
                            <path d="M12 0C8.74 0 8.333.015 7.053.072 5.775.132 4.905.333 4.14.63c-.789.306-1.459.717-2.126 1.384S.935 3.35.63 4.14C.333 4.905.131 5.775.072 7.053.012 8.333 0 8.74 0 12s.015 3.667.072 4.947c.06 1.277.261 2.148.558 2.913.306.788.717 1.459 1.384 2.126.667.666 1.336 1.079 2.126 1.384.766.296 1.636.499 2.913.558C8.333 23.988 8.74 24 12 24s3.667-.015 4.947-.072c1.277-.06 2.148-.262 2.913-.558.788-.306 1.459-.718 2.126-1.384.666-.667 1.079-1.335 1.384-2.126.296-.765.499-1.636.558-2.913.06-1.28.072-1.687.072-4.947s-.015-3.667-.072-4.947c-.06-1.277-.262-2.149-.558-2.913-.306-.789-.718-1.459-1.384-2.126C21.319 1.347 20.651.935 19.86.63c-.765-.297-1.636-.499-2.913-.558C15.667.012 15.26 0 12 0zm0 2.16c3.203 0 3.585.016 4.85.071 1.17.055 1.805.249 2.227.415.562.217.96.477 1.382.896.419.42.679.819.896 1.381.164.422.36 1.057.413 2.227.057 1.266.07 1.646.07 4.85s-.015 3.585-.074 4.85c-.061 1.17-.256 1.805-.421 2.227-.224.562-.479.96-.899 1.382-.419.419-.824.679-1.38.896-.42.164-1.065.36-2.235.413-1.274.057-1.649.07-4.859.07-3.211 0-3.586-.015-4.859-.074-1.171-.061-1.816-.256-2.236-.421-.569-.224-.96-.479-1.379-.899-.421-.419-.69-.824-.9-1.38-.165-.42-.359-1.065-.42-2.235-.045-1.26-.061-1.649-.061-4.844 0-3.196.016-3.586.061-4.861.061-1.17.255-1.814.42-2.234.21-.57.479-.96.9-1.381.419-.419.81-.689 1.379-.898.42-.166 1.051-.361 2.221-.421 1.275-.045 1.65-.06 4.859-.06l.045.03zm0 3.678c-3.405 0-6.162 2.76-6.162 6.162 0 3.405 2.76 6.162 6.162 6.162 3.405 0 6.162-2.76 6.162-6.162 0-3.405-2.76-6.162-6.162-6.162zM12 16c-2.21 0-4-1.79-4-4s1.79-4 4-4 4 1.79 4 4-1.79 4-4 4zm7.846-10.405c0 .795-.646 1.44-1.44 1.44-.795 0-1.44-.646-1.44-1.44 0-.794.646-1.439 1.44-1.439.793-.001 1.44.645 1.44 1.439z"></path>
                        </svg>
                    </a>
                    <a class="text-sm text-gray-500 transition hover:text-gray-600" target="_blank" rel="noopener noreferrer" href="https://www.threads.net">
                        <span class="sr-only">threads</span>
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" class="hover:text-primary-500 fill-current text-gray-700 h-6 w-6">
                            <title>Threads</title>
                            <path d="M12.186 24h-.007c-3.581-.024-6.334-1.205-8.184-3.509C2.35 18.44 1.5 15.586 1.472 12.01v-.017c.03-3.579.879-6.43 2.525-8.482C5.845 1.205 8.6.024 12.18 0h.014c2.746.02 5.043.725 6.826 2.098 1.677 1.29 2.858 3.13 3.509 5.467l-2.04.569c-1.104-3.96-3.898-5.984-8.304-6.015-2.91.022-5.11.936-6.54 2.717C4.307 6.504 3.616 8.914 3.589 12c.027 3.086.718 5.496 2.057 7.164 1.43 1.783 3.631 2.698 6.54 2.717 2.623-.02 4.358-.631 5.8-2.045 1.647-1.613 1.618-3.593 1.09-4.798-.31-.71-.873-1.3-1.634-1.75-.192 1.352-.622 2.446-1.284 3.272-.886 1.102-2.14 1.704-3.73 1.79-1.202.065-2.361-.218-3.259-.801-1.063-.689-1.685-1.74-1.752-2.964-.065-1.19.408-2.285 1.33-3.082.88-.76 2.119-1.207 3.583-1.291a13.853 13.853 0 0 1 3.02.142c-.126-.742-.375-1.332-.75-1.757-.513-.586-1.308-.883-2.359-.89h-.029c-.844 0-1.992.232-2.721 1.32L7.734 7.847c.98-1.454 2.568-2.256 4.478-2.256h.044c3.194.02 5.097 1.975 5.287 5.388.108.046.216.094.321.142 1.49.7 2.58 1.761 3.154 3.07.797 1.82.871 4.79-1.548 7.158-1.85 1.81-4.094 2.628-7.277 2.65Zm1.003-11.69c-.242 0-.487.007-.739.021-1.836.103-2.98.946-2.916 2.143.067 1.256 1.452 1.839 2.784 1.767 1.224-.065 2.818-.543 3.086-3.71a10.5 10.5 0 0 0-2.215-.221z"></path>
                        </svg>
                    </a>
                    <a class="text-sm text-gray-500 transition hover:text-gray-600" target="_blank" rel="noopener noreferrer" href="https://medium.com">
                        <span class="sr-only">medium</span>
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" class="hover:text-primary-500 fill-current text-gray-700 h-6 w-6">
                            <title>Medium</title>
                            <path d="M13.54 12a6.8 6.8 0 01-6.77 6.82A6.8 6.8 0 010 12a6.8 6.8 0 016.77-6.82A6.8 6.8 0 0113.54 12zM20.96 12c0 3.54-1.51 6.42-3.38 6.42-1.87 0-3.39-2.88-3.39-6.42s1.52-6.42 3.39-6.42 3.38 2.88 3.38 6.42M24 12c0 3.17-.53 5.75-1.19 5.75-.66 0-1.19-2.58-1.19-5.75s.53-5.75 1.19-5.75C23.47 6.25 24 8.83 24 12z"></path>
                        </svg>
                    </a>
                </div>
                <div class="mb-2 flex space-x-2 text-sm text-gray-500" bis_skin_checked="1">
                    <div bis_skin_checked="1">Dede Saputra</div>
                    <div bis_skin_checked="1"> • </div>
                    <div bis_skin_checked="1">© 2025</div>
                    <div bis_skin_checked="1"> • </div>
                    <a class="break-words" href="/">Dede Saputra Blog</a>
                </div>
                <div class="mb-8 text-sm text-gray-500" bis_skin_checked="1">
                    <a class="break-words" target="_blank" rel="noopener noreferrer" href="https://dedesaputra">Sudung Pak Dede</a>
                </div>
            </div>
        </footer>
        
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
