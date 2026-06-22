import streamlit as st
import feedparser
import urllib.parse
import urllib.request
import re
import json
import calendar
import os
import html
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

# ─────────────────────────────────────────────
#  ページ設定
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="AI ニュース収集ダッシュボード",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
#  CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Serif+JP:wght@300;400;500;600&family=Noto+Sans+JP:wght@300;400;500&family=Cormorant+Garamond:ital,wght@0,400;0,600;1,400&display=swap');

html, body, [class*="css"] { font-family: 'Noto Sans JP', sans-serif; }

.stApp {
    background-color: #1a120b;
    background-image:
        radial-gradient(ellipse at 15% 30%, rgba(201,169,110,0.06) 0%, transparent 55%),
        radial-gradient(ellipse at 85% 70%, rgba(139,90,60,0.07) 0%, transparent 55%);
}

/* ── サイドバー ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0e0a06 0%, #1a120b 40%, #231710 100%);
    border-right: 1px solid #4a3520;
}
[data-testid="stSidebar"] * { color: #d4b896 !important; }
[data-testid="stSidebar"] hr { border-color: #2e1f14 !important; }
[data-testid="stSidebar"] .stTextInput input {
    background: rgba(201,169,110,0.06) !important;
    border: 1px solid #4a3520 !important;
    border-radius: 4px !important;
    color: #d4b896 !important;
    font-size: 0.9rem !important;
}
[data-testid="stSidebar"] .stTextInput input:focus {
    border-color: #c9a96e !important;
    box-shadow: 0 0 0 2px rgba(201,169,110,0.15) !important;
}
[data-testid="stSidebar"] .stTextInput input::placeholder { color: #6b5040 !important; }
[data-testid="stSidebar"] .stSelectbox div[data-baseweb] {
    background: rgba(201,169,110,0.06) !important;
    border-color: #4a3520 !important;
}

/* ── サイドバーナビゲーション（radio） ── */
[data-testid="stSidebar"] .stRadio > label { display: none !important; }
[data-testid="stSidebar"] [data-baseweb="radio-group"] { gap: 0 !important; }
[data-testid="stSidebar"] [data-baseweb="radio"] {
    padding: 8px 12px !important;
    border-radius: 5px !important;
    transition: background 0.2s !important;
    cursor: pointer !important;
    margin: 1px 0 !important;
}
[data-testid="stSidebar"] [data-baseweb="radio"]:hover {
    background: rgba(201,169,110,0.08) !important;
}
[data-testid="stSidebar"] [data-baseweb="radio"] > div:first-child {
    border-color: #4a3520 !important;
    min-width: 14px !important; height: 14px !important;
}
[data-testid="stSidebar"] [data-baseweb="radio"][data-checked="true"] {
    background: rgba(201,169,110,0.13) !important;
    border-left: 3px solid #c9a96e !important;
}
[data-testid="stSidebar"] [data-baseweb="radio"][data-checked="true"] > div:first-child {
    border-color: #c9a96e !important;
    background: #c9a96e !important;
}
[data-testid="stSidebar"] [data-baseweb="radio"] > div:last-child {
    font-size: 0.88rem !important;
    letter-spacing: 0.04em !important;
    color: #7a6050 !important;
}
[data-testid="stSidebar"] [data-baseweb="radio"][data-checked="true"] > div:last-child {
    color: #e8c870 !important;
    font-weight: 500 !important;
}

/* ── サイドバーボタン（検索） ── */
[data-testid="stSidebar"] .stButton button {
    background: linear-gradient(135deg, #c9a96e 0%, #a67c52 100%) !important;
    color: #0e0a06 !important;
    border: none !important;
    border-radius: 4px !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    letter-spacing: 0.08em !important;
    width: 100% !important;
    padding: 10px !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.4) !important;
}
[data-testid="stSidebar"] .stButton button:hover {
    background: linear-gradient(135deg, #e0c080 0%, #c9a96e 100%) !important;
    box-shadow: 0 4px 14px rgba(201,169,110,0.35) !important;
    transform: translateY(-1px) !important;
}
/* チェックボックス */
[data-testid="stSidebar"] .stCheckbox label {
    font-size: 0.84rem !important;
    color: #8a7060 !important;
    gap: 8px !important;
    cursor: pointer !important;
}
[data-testid="stSidebar"] .stCheckbox [data-checked="true"] {
    background: #c9a96e !important;
    border-color: #c9a96e !important;
}

/* ── メインエリア ── */
.block-container {
    padding-top: 1rem !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
    max-width: 1200px !important;
}

/* ── ヘッダーバナー ── */
.hero-banner {
    position: relative; border-radius: 10px; overflow: hidden;
    margin-bottom: 24px; height: 160px;
    background: linear-gradient(135deg, #0e0a06 0%, #2a1a0e 40%, #1a0f08 100%);
    border: 1px solid #3a2a1a;
    box-shadow: 0 6px 30px rgba(0,0,0,0.6);
    display: flex; align-items: center;
}
.hero-banner .hero-shelf { position: absolute; right: 0; top: 0; bottom: 0; width: 55%; opacity: 0.15; }
.hero-banner .hero-text { position: relative; z-index: 2; padding: 0 36px; }
.hero-banner .hero-title {
    font-family: 'Cormorant Garamond','Noto Serif JP',serif;
    font-size: 1.85rem; font-weight: 600; color: #e8d5b0; margin: 0;
    letter-spacing: 0.08em; text-shadow: 0 2px 12px rgba(0,0,0,0.5); line-height: 1.3;
}
.hero-banner .hero-sub {
    font-size: 0.75rem; color: #7a5f3e; margin: 7px 0 0 0; letter-spacing: 0.15em; text-transform: uppercase;
}
.hero-banner .hero-ornament {
    font-size: 3.2rem; position: absolute; right: 36px; top: 50%;
    transform: translateY(-50%); opacity: 0.22; filter: sepia(1);
}

/* ── 仕切り線 ── */
.ornament-divider {
    display: flex; align-items: center; gap: 12px; margin: 6px 0 20px 0;
}
.ornament-divider .line {
    flex: 1; height: 1px;
    background: linear-gradient(90deg, transparent, #3a2a1a, #c9a96e44, #3a2a1a, transparent);
}
.ornament-divider .symbol { color: #c9a96e; font-size: 0.9rem; opacity: 0.6; }

/* ── バッジ類 ── */
.search-badge {
    background: rgba(201,169,110,0.08); border: 1px solid #3a2a1a;
    border-left: 3px solid #c9a96e; color: #c9a96e; border-radius: 4px;
    padding: 6px 16px; font-size: 0.82rem; letter-spacing: 0.06em;
    display: inline-flex; align-items: center; gap: 6px;
}
.count-text { font-size: 0.78rem; color: #5a4030; letter-spacing: 0.04em; }
.count-text strong { color: #c9a96e; }

/* ════════════════════════════════════════
   TOP 5 セクション
   ════════════════════════════════════════ */
.top5-section {
    background: linear-gradient(160deg, #241508 0%, #1e1206 50%, #241508 100%);
    border: 1px solid #6a4820; border-radius: 10px; margin-bottom: 28px; overflow: hidden;
    box-shadow: 0 4px 28px rgba(0,0,0,0.55), inset 0 1px 0 rgba(201,169,110,0.12);
}
.top5-header {
    background: linear-gradient(90deg, #2e1808, #4a2c10, #2e1808);
    border-bottom: 1px solid #6a4820;
    padding: 13px 22px; display: flex; align-items: center; justify-content: space-between;
}
.top5-header-title {
    font-family: 'Noto Serif JP',serif; font-size: 0.98rem; font-weight: 600;
    color: #e8c870; letter-spacing: 0.10em;
}
.top5-header-time { font-size: 0.68rem; color: #5a3c18; letter-spacing: 0.06em; }
.top5-item {
    display: flex; align-items: center; gap: 14px; padding: 13px 20px;
    border-bottom: 1px solid #2a1808;
    text-decoration: none !important;
    transition: background 0.22s ease; cursor: pointer;
}
.top5-item:last-child { border-bottom: none; }
.top5-item:hover { background: rgba(201,169,110,0.07); text-decoration: none !important; }
.top5-item.rank-first {
    padding: 17px 20px;
    background: linear-gradient(90deg, rgba(201,169,110,0.09) 0%, transparent 65%);
    border-bottom: 1px solid #3a2010;
}
.top5-item.rank-first:hover { background: linear-gradient(90deg, rgba(201,169,110,0.14) 0%, rgba(201,169,110,0.04) 65%); }
.rank-badge {
    min-width: 38px; height: 38px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-family: 'Cormorant Garamond',serif; font-weight: 600; flex-shrink: 0; font-size: 1.0rem;
}
.rb-1 { background: linear-gradient(135deg,#c9a020,#f0c840); color:#1a0e04; font-size:1.15rem; box-shadow:0 2px 8px rgba(201,160,32,0.4); }
.rb-2 { background: linear-gradient(135deg,#7a8a98,#a8b8c4); color:#181e22; }
.rb-3 { background: linear-gradient(135deg,#8a5228,#b87040); color:#1a0e04; }
.rb-4 { background: rgba(201,169,110,0.12); color:#c9a96e; border:1px solid #4a3520; }
.rb-5 { background: rgba(201,169,110,0.07); color:#906840; border:1px solid #342010; }
.top5-content { flex: 1; min-width: 0; }
.top5-title {
    font-family: 'Noto Serif JP',serif; font-size: 0.91rem; font-weight: 500;
    color: #dcc898; line-height: 1.5; margin: 0 0 3px 0;
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.rank-first .top5-title {
    font-size: 1.01rem; color: #f0d8a8; white-space: normal;
    display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;
}
.top5-date { font-size: 0.68rem; color: #5a3c20; letter-spacing: 0.04em; }
.score-wrap { display: flex; align-items: center; gap: 7px; flex-shrink: 0; }
.score-label { font-size: 0.63rem; color: #5a3c20; letter-spacing: 0.05em; }
.score-bar-bg { width: 64px; height: 3px; background: #2a1608; border-radius: 2px; overflow: hidden; }
.score-bar-fill { height: 100%; border-radius: 2px; background: linear-gradient(90deg,#8a5018,#d4a030); }
.rank-first .score-bar-fill { background: linear-gradient(90deg,#c09020,#f5d050); }
.score-pct { font-size: 0.66rem; color: #c9a96e; min-width: 26px; text-align: right; font-family: 'Cormorant Garamond',serif; }

/* ── ニュースカード（共通） ── */
.news-card {
    display: block; text-decoration: none !important;
    background: #3a2614; border: 1px solid #4e3420; border-radius: 8px;
    margin-bottom: 16px; overflow: hidden;
    transition: all 0.3s cubic-bezier(0.25,0.46,0.45,0.94);
    box-shadow: 0 3px 12px rgba(0,0,0,0.3); cursor: pointer; position: relative;
}
.news-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 36px rgba(0,0,0,0.45), 0 0 0 1px #c9a96e66;
    border-color: #7a5535; background: #4a3020; text-decoration: none !important;
}
.card-img-wrap {
    width: 100%; height: 140px; overflow: hidden;
    background: linear-gradient(135deg,#2a1a0a,#3a2410); position: relative;
}
.card-img-wrap img {
    width: 100%; height: 100%; object-fit: cover; opacity: 0.82;
    transition: opacity 0.3s ease, transform 0.4s ease;
    filter: sepia(0.2) contrast(0.95);
}
.news-card:hover .card-img-wrap img { opacity: 0.95; transform: scale(1.04); }
.card-img-placeholder {
    width: 100%; height: 100%; display: flex; align-items: center; justify-content: center;
    background: linear-gradient(135deg,#2a1a0a 0%,#3a2410 50%,#2a1a0a 100%);
    position: relative; overflow: hidden;
}
.card-img-placeholder::before {
    content: ''; position: absolute; inset: 0;
    background: repeating-linear-gradient(90deg, transparent, transparent 28px,
        rgba(201,169,110,0.10) 28px, rgba(201,169,110,0.10) 30px);
}
.card-img-placeholder .ph-icon { font-size:2.8rem; opacity:0.45; position:relative; z-index:1; filter:sepia(1); }
.card-img-badge {
    position: absolute; top: 8px; left: 8px;
    background: rgba(0,0,0,0.65); border: 1px solid #3a2a1a;
    color: #c9a96e; font-size: 0.68rem; padding: 2px 8px;
    border-radius: 3px; letter-spacing: 0.06em; backdrop-filter: blur(4px);
}
.card-body { padding: 16px 18px 14px; }
.card-title {
    font-family: 'Noto Serif JP',serif; font-size: 0.97rem; font-weight: 500; color: #ead9bc;
    margin: 0 0 8px 0; line-height: 1.6;
    display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;
}
.news-card:hover .card-title { color: #f5e8cc; }
.card-date { font-size: 0.73rem; color: #a07850; margin: 0 0 10px 0; }
.card-summary {
    font-size: 0.82rem; color: #b09070; line-height: 1.7; margin: 0 0 12px 0;
    display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;
}
.card-footer {
    display: flex; align-items: center; justify-content: space-between;
    padding-top: 10px; border-top: 1px solid #4e3420;
}
.card-read-btn { font-size: 0.72rem; color: #c9a96e; letter-spacing: 0.06em; opacity: 0.7; transition: opacity 0.2s; }
.news-card:hover .card-read-btn { opacity: 1; }
.card-num { font-size: 0.68rem; color: #7a5535; letter-spacing: 0.04em; font-family: 'Cormorant Garamond',serif; }

/* ════════════════════════════════════════
   AI 情報カード（ニュースカードと同じ構造）
   ════════════════════════════════════════ */
.info-card {
    display: block; text-decoration: none !important;
    background: #3a2614; border: 1px solid #4e3420; border-radius: 8px;
    margin-bottom: 16px; overflow: hidden;
    transition: all 0.3s cubic-bezier(0.25,0.46,0.45,0.94);
    box-shadow: 0 3px 12px rgba(0,0,0,0.3); cursor: pointer; position: relative;
}
.info-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 36px rgba(0,0,0,0.45), 0 0 0 1px #c9a96e66;
    border-color: #7a5535; background: #4a3020; text-decoration: none !important;
}
/* ソースヘッダー（画像エリアの代わり） */
.info-src-header {
    height: 72px; display: flex; align-items: center; justify-content: center; gap: 10px;
    overflow: hidden; position: relative;
}
.info-src-header::after {
    content: ''; position: absolute; bottom: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg, transparent, rgba(201,169,110,0.35), transparent);
}
.info-src-icon { font-size: 1.5rem; line-height: 1; }
.info-src-label {
    font-size: 0.78rem; font-weight: 600; letter-spacing: 0.12em;
    text-transform: uppercase; opacity: 0.92;
}

/* ソース統計バー */
.source-stats {
    display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 20px;
}
.source-stat-chip {
    display: inline-flex; align-items: center; gap: 5px;
    padding: 4px 12px; border-radius: 16px;
    font-size: 0.72rem; letter-spacing: 0.05em;
    border: 1px solid rgba(255,255,255,0.06);
    background: rgba(255,255,255,0.03);
    transition: opacity 0.2s;
}

/* ── ページネーション ── */
.pagination-wrap {
    display: flex; align-items: center; justify-content: center;
    gap: 10px; margin: 32px 0 8px; padding: 20px 0; border-top: 1px solid #2e1f14;
}
.page-info {
    font-family: 'Cormorant Garamond',serif; font-size: 1.05rem;
    color: #7a6050; letter-spacing: 0.1em; min-width: 120px; text-align: center;
}
.page-info strong { color: #c9a96e; }
div[data-testid="column"] .stButton button {
    background: transparent !important; border: 1px solid #3a2a1a !important;
    color: #c9a96e !important; border-radius: 4px !important;
    font-size: 0.82rem !important; letter-spacing: 0.06em !important;
    padding: 8px 20px !important; transition: all 0.2s ease !important; width: 100% !important;
}
div[data-testid="column"] .stButton button:hover {
    background: rgba(201,169,110,0.1) !important;
    border-color: #c9a96e !important;
}
div[data-testid="column"] .stButton button:disabled { opacity: 0.2 !important; }

/* ── フッター ── */
.library-footer {
    margin-top: 20px; padding: 20px 0; text-align: center;
    font-family: 'Cormorant Garamond',serif; font-size: 0.8rem;
    color: #3a2a1a; letter-spacing: 0.12em;
}
.library-footer .footer-ornament { display: block; font-size: 1.2rem; margin-bottom: 6px; opacity: 0.3; }

h1, h2, h3 { font-family: 'Noto Serif JP',serif !important; color: #ffffff !important; }

/* ── 本文 typography ── */
h2 {
    font-size: 1.22rem !important;
    font-weight: 600 !important;
    margin: 2rem 0 0.75rem 0 !important;
    padding-bottom: 0.45rem !important;
    border-bottom: 1px solid rgba(201,169,110,0.30) !important;
    letter-spacing: 0.06em !important;
}
h3 {
    color: #e8c870 !important;
    font-size: 1.02rem !important;
    font-weight: 500 !important;
    margin: 1.4rem 0 0.4rem 0 !important;
    letter-spacing: 0.04em !important;
}
.block-container .stMarkdown p {
    color: #e8e8e8 !important;
    line-height: 1.95 !important;
    font-size: 0.94rem !important;
    margin-bottom: 0.85rem !important;
}
.block-container .stMarkdown strong,
.block-container .stMarkdown b {
    color: #ffffff !important;
    font-weight: 600 !important;
}
.block-container .stMarkdown a { color: #c9a96e !important; }
.stSpinner > div { border-top-color: #c9a96e !important; }
.stAlert {
    background: rgba(201,169,110,0.06) !important; border-color: #3a2a1a !important;
    color: #d4b896 !important; border-radius: 6px !important;
}
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #0e0a06; }
::-webkit-scrollbar-thumb { background: #3a2a1a; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #c9a96e66; }

/* ── カテゴリタブ ── */
.stTabs [data-baseweb="tab-list"] {
    background: transparent !important;
    gap: 3px !important;
    border-bottom: 1px solid #3a2a1a !important;
    flex-wrap: wrap !important;
    padding-bottom: 0 !important;
}
.stTabs [data-baseweb="tab"] {
    background: rgba(201,169,110,0.05) !important;
    border: 1px solid #3a2a1a !important;
    border-bottom: none !important;
    border-radius: 6px 6px 0 0 !important;
    color: #7a6050 !important;
    font-size: 0.80rem !important;
    letter-spacing: 0.04em !important;
    padding: 7px 13px !important;
    font-family: 'Noto Sans JP', sans-serif !important;
    transition: all 0.18s ease !important;
    white-space: nowrap !important;
}
.stTabs [data-baseweb="tab"]:hover {
    background: rgba(201,169,110,0.10) !important;
    color: #c9a96e !important;
    border-color: #5a3c20 !important;
}
.stTabs [aria-selected="true"] {
    background: rgba(201,169,110,0.16) !important;
    border-color: #c9a96e !important;
    color: #e8c870 !important;
    font-weight: 500 !important;
}
.stTabs [data-baseweb="tab-highlight"] {
    background: #c9a96e !important;
    height: 2px !important;
}
.stTabs [data-baseweb="tab-panel"] { padding-top: 18px !important; }

/* ── メインカテゴリ切替（ページ送り後も選択維持） ── */
.block-container .stRadio [data-baseweb="radio-group"] {
    display: flex !important;
    flex-wrap: wrap !important;
    gap: 4px !important;
    margin-bottom: 18px !important;
}
.block-container .stRadio [data-baseweb="radio"] {
    background: rgba(201,169,110,0.05) !important;
    border: 1px solid #3a2a1a !important;
    border-radius: 6px !important;
    padding: 7px 12px !important;
    margin: 0 !important;
}
.block-container .stRadio [data-baseweb="radio"]:hover {
    background: rgba(201,169,110,0.10) !important;
    border-color: #5a3c20 !important;
}
.block-container .stRadio [data-baseweb="radio"][data-checked="true"] {
    background: rgba(201,169,110,0.16) !important;
    border-color: #c9a96e !important;
}
.block-container .stRadio [data-baseweb="radio"] > div:first-child {
    display: none !important;
}
.block-container .stRadio [data-baseweb="radio"] > div:last-child {
    color: #ffffff !important;
    font-size: 0.80rem !important;
    letter-spacing: 0.04em !important;
}
.block-container .stRadio [data-baseweb="radio"][data-checked="true"] > div:last-child {
    color: #ffffff !important;
    font-weight: 500 !important;
}

/* ── ミニカレンダー ─────────────────────────── */
[data-testid="stSidebar"] div[data-testid="column"] .stButton button {
    padding: 2px 1px !important;
    min-height: 26px !important;
    font-size: 0.74rem !important;
    letter-spacing: 0 !important;
    font-weight: 600 !important;
    line-height: 1 !important;
    box-shadow: none !important;
}

/* ── 記事要約カード ─────────────────────────── */
.report-art-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid #2e1f14;
    border-left: 3px solid #c9a96e;
    border-radius: 6px;
    padding: 12px 16px;
    margin-bottom: 10px;
    transition: border-color 0.2s;
}
.report-art-card:hover { border-color: #c9a96e; }
.report-art-card .rac-meta {
    font-size: 0.72rem; color: #5a4030;
    margin-bottom: 4px; letter-spacing: 0.05em;
}
.report-art-card .rac-title {
    font-size: 0.92rem; font-weight: 600;
    color: #c9a96e; margin-bottom: 6px;
    line-height: 1.4;
}
.report-art-card .rac-title a {
    color: #c9a96e !important; text-decoration: none !important;
}
.report-art-card .rac-title a:hover { text-decoration: underline !important; }
.report-art-card .rac-body {
    font-size: 0.83rem; color: #b09070;
    line-height: 1.75;
}

/* ── Obsidian結果カード ───────────────── */
.kw-idea-card,
.kw-idea-card *:not(a) {
    color: #ffffff !important;
}
.kw-idea-keywords-label,
.kw-section-title {
    color: #ffffff !important;
}
.kw-text,
.kw-idea-keywords,
.kw-url-list li {
    color: #ffffff !important;
}
.kw-url-list a {
    color: #c9a96e !important;
}

/* ── 全体文字色：基本白、リンクと重要部分は金 ───────────────── */
.stApp,
.stApp p,
.stApp li,
.stApp span,
.stApp div,
.stApp label,
.stApp [data-testid="stMarkdownContainer"],
.stApp [data-testid="stMarkdownContainer"] p,
.stApp [data-testid="stMarkdownContainer"] li,
.stApp [data-testid="stMarkdownContainer"] span {
    color: #ffffff !important;
}
.stApp a,
.stApp a *,
.stApp strong,
.stApp b,
.stApp h2,
.stApp h3,
.stApp h4,
.stApp [data-testid="stMarkdownContainer"] a,
.stApp [data-testid="stMarkdownContainer"] strong,
.stApp [data-testid="stMarkdownContainer"] b {
    color: #c9a96e !important;
}
.stApp h1 {
    color: #ffffff !important;
}
.stApp hr {
    border-color: rgba(201,169,110,0.35) !important;
}
.stApp details,
.stApp summary,
.stApp [data-testid="stExpander"] *,
.stApp [data-testid="stSelectbox"] *,
.stApp [data-baseweb="select"] * {
    color: #ffffff !important;
}
.stApp [data-baseweb="select"] {
    background: rgba(255,255,255,0.08) !important;
}

</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  定数
# ─────────────────────────────────────────────
CARDS_PER_PAGE = 10
FETCH_LIMIT    = 100
INFO_FAST_LIMIT = 12
INFO_DEEP_LIMIT = 30
INFO_FETCH_WORKERS = 10
SHELF_ICONS    = ["📖", "📰", "🔬", "💡", "🤖", "🧠", "📡", "⚙️", "🌐", "📊"]
DIGITAL_AGENCY_RSS_URL = "https://www.digital.go.jp/rss/news.xml"
OBSIDIAN_VAULT_DIR = Path(r"D:\新しいフォルダー (4)\notevalt")
DIGITAL_AGENCY_FOCUS_KEYWORDS = [
    "ai", "生成ai", "人工知能", "デジタル改革共創", "共創プラットフォーム",
    "地方公共団体", "地方自治体", "自治体", "行政dx", "自治体dx",
    "ガイドライン", "アナログ規制", "govtech", "スマートシティ",
]

# AI情報ページのソース設定
# ─── 除外キーワード（エンタメ・浅い入門を弾く） ───────────────────
# タイトルにこれらが含まれている記事は表示しない
EXCLUDE_TITLE_KEYWORDS: list[str] = [
    # エンタメ系 AI 画像・グラビア
    "グラビア", "aiグラビア", "ai写真集", "ai美女", "ai彼女", "ai水着",
    "aiアイドル", "aiガール", "ai妻", "aiキャラ", "ai画像集", "aiイラスト集",
    "ai漫画家", "ai漫画制作", "ai作画",
    # AI 執筆小説（技術でなく創作物）
    "ai小説", "ai執筆小説", "aiが書いた小説", "ai生成小説", "ai作家",
    "aiで小説", "aiで書いた", "ai創作", "aiで書く小説",
    "aiポエム", "aiで詩", "ai詩", "ai俳句", "ai短歌", "aiエッセイ",
    "chatgptで小説", "chatgptで詩", "chatgptでポエム",
    "小説を書いてみた", "詩を書いてみた", "ポエムを書いてみた",
    "日記を書いてみた", "ai日記", "chatgpt日記",
    # 浅い入門
    "chatgptとは", "chatgpt入門", "chatgptの始め方",
    "ai入門", "aiとは何か", "chatgptを初めて",
    "初心者向けchatgpt", "初心者向けai", "初心者でもわかるchatgpt",
    "初心者でもわかるai", "はじめてのchatgpt", "はじめての生成ai",
    "chatgptを始める", "gptの始め方", "openaiの始め方",
    "chatgpt 使ってみた", "chatgptを使ってみた",
]

# タイトル + 要約で除外するパターン（正規表現）
EXCLUDE_REGEX_PATTERNS: list[str] = [
    r'ai.*グラビア|グラビア.*ai',
    r'ai.*美女.*生成|美女.*ai.*生成',
    r'ai.*彼女|彼女.*ai.*作',
    r'chatgpt[でと].*小説.*書',
    r'ai[でと].*漫画.*描',
    # AI 小説・創作系
    r'ai[がでにより]+(書い|執筆|生成し)(た|た小説|た物語)',
    r'(小説|物語|詩)[をが]aiで(書|生成|創作)',
    r'aiが?(書いた|生成した)(小説|物語|ショートストーリー)',
    r'ai(小説|ストーリー|フィクション).{0,10}(書|読|楽し|感想)',
    r'(chatgpt|生成ai|ai).{0,12}(ポエム|詩|俳句|短歌|小説|物語|日記).{0,18}(書|作|生成|やってみた|使ってみた)',
    r'(ポエム|詩|俳句|短歌|小説|物語|日記).{0,18}(chatgpt|生成ai|ai)',
    r'(今日|最近|週末|朝|夜).{0,12}(日記|雑記|つぶやき)',
    r'(chatgpt|生成ai|ai).{0,10}(始め方|はじめ方|入門|初心者|超初心者|使ってみた|触ってみた)',
    r'(gpt|chatgpt|openai).{0,12}(アカウント作成|登録方法|ログイン方法)',
]

INFO_SOURCES = [
    # ── デジタル庁公式RSS（一次情報） ───────────
    {
        "id": "digital_agency", "label": "デジタル庁公式", "icon": "🏛️",
        "color": "#38BDF8", "bg": "rgba(56,189,248,0.15)",
        "type": "rss",
        "urls": [
            DIGITAL_AGENCY_RSS_URL,
        ],
    },
    # ── note ──────────────────────────────────
    {
        "id": "note", "label": "note", "icon": "✍️",
        "color": "#41C9B4", "bg": "rgba(65,201,180,0.15)",
        "type": "rss",
        "urls": [
            "https://note.com/hashtag/AI/rss",
            "https://note.com/hashtag/人工知能/rss",
            "https://note.com/hashtag/機械学習/rss",
            "https://note.com/hashtag/ChatGPT/rss",
            "https://note.com/hashtag/LLM/rss",
            "https://note.com/hashtag/Claude/rss",
            "https://note.com/hashtag/Gemini/rss",
            "https://note.com/hashtag/OpenAI/rss",
            "https://note.com/hashtag/Anthropic/rss",
            "https://note.com/hashtag/NotebookLM/rss",
            "https://note.com/hashtag/ローカルAI/rss",
            "https://note.com/hashtag/ローカルLLM/rss",
            "https://note.com/hashtag/LMStudio/rss",
            "https://note.com/hashtag/AI開発ツール/rss",
            "https://note.com/hashtag/AIアプリ開発/rss",
            "https://note.com/hashtag/ゲーム開発/rss",
            "https://note.com/hashtag/AIゲーム/rss",
            "https://note.com/hashtag/動画編集/rss",
            "https://note.com/hashtag/AI動画編集/rss",
            "https://note.com/hashtag/3DCG/rss",
            "https://note.com/hashtag/Blender/rss",
            "https://note.com/hashtag/UnrealEngine/rss",
            "https://note.com/hashtag/Meshy/rss",
            "https://note.com/hashtag/AIエージェント/rss",
            "https://note.com/hashtag/自治体DX/rss",
            "https://note.com/hashtag/地方自治体/rss",
            "https://note.com/hashtag/行政DX/rss",
            "https://note.com/hashtag/GovTech/rss",
            "https://note.com/hashtag/企業DX/rss",
            "https://note.com/hashtag/業務効率化/rss",
            "https://note.com/hashtag/社内AI/rss",
            "https://note.com/hashtag/AIアバター/rss",
            "https://note.com/hashtag/プログラミング/rss",
            "https://note.com/hashtag/オープンソース/rss",
            "https://note.com/hashtag/MCP/rss",
            "https://note.com/hashtag/Ollama/rss",
            "https://note.com/hashtag/AI動画/rss",
            "https://note.com/hashtag/AI音声/rss",
            "https://note.com/hashtag/Grok/rss",
            "https://note.com/hashtag/n8n/rss",
            "https://note.com/hashtag/Dify/rss",
            "https://note.com/hashtag/Docker/rss",
        ],
    },
    # ── Zenn ──────────────────────────────────
    {
        "id": "zenn", "label": "Zenn", "icon": "💻",
        "color": "#3EA8FF", "bg": "rgba(62,168,255,0.15)",
        "type": "rss",
        "urls": [
            "https://zenn.dev/topics/ai/feed",
            "https://zenn.dev/topics/llm/feed",
            "https://zenn.dev/topics/chatgpt/feed",
            "https://zenn.dev/topics/claude/feed",
            "https://zenn.dev/topics/gemini/feed",
            "https://zenn.dev/topics/openai/feed",
            "https://zenn.dev/topics/anthropic/feed",
            "https://zenn.dev/topics/cursor/feed",
            "https://zenn.dev/topics/claudecode/feed",
            "https://zenn.dev/topics/copilot/feed",
            "https://zenn.dev/topics/vscode/feed",
            "https://zenn.dev/topics/github/feed",
            "https://zenn.dev/topics/aiagent/feed",
            "https://zenn.dev/topics/gamedev/feed",
            "https://zenn.dev/topics/unrealengine/feed",
            "https://zenn.dev/topics/unity/feed",
            "https://zenn.dev/topics/blender/feed",
            "https://zenn.dev/topics/dx/feed",
            "https://zenn.dev/topics/govtech/feed",
            "https://zenn.dev/topics/business/feed",
            "https://zenn.dev/topics/localllm/feed",
            "https://zenn.dev/topics/mcp/feed",
            "https://zenn.dev/topics/ollama/feed",
            "https://zenn.dev/topics/n8n/feed",
            "https://zenn.dev/topics/huggingface/feed",
            "https://zenn.dev/topics/docker/feed",
            "https://zenn.dev/topics/dify/feed",
        ],
    },
    # ── Qiita ─────────────────────────────────
    {
        "id": "qiita", "label": "Qiita", "icon": "📝",
        "color": "#55C500", "bg": "rgba(85,197,0,0.15)",
        "type": "rss",
        "urls": [
            "https://qiita.com/tags/ai/feed",
            "https://qiita.com/tags/llm/feed",
            "https://qiita.com/tags/chatgpt/feed",
            "https://qiita.com/tags/claude/feed",
            "https://qiita.com/tags/gemini/feed",
            "https://qiita.com/tags/openai/feed",
            "https://qiita.com/tags/anthropic/feed",
            "https://qiita.com/tags/cursor/feed",
            "https://qiita.com/tags/claudecode/feed",
            "https://qiita.com/tags/copilot/feed",
            "https://qiita.com/tags/vscode/feed",
            "https://qiita.com/tags/github/feed",
            "https://qiita.com/tags/aiagent/feed",
            "https://qiita.com/tags/gamedev/feed",
            "https://qiita.com/tags/unrealengine/feed",
            "https://qiita.com/tags/unity/feed",
            "https://qiita.com/tags/blender/feed",
            "https://qiita.com/tags/dx/feed",
            "https://qiita.com/tags/govtech/feed",
            "https://qiita.com/tags/業務効率化/feed",
            "https://qiita.com/tags/localllm/feed",
            "https://qiita.com/tags/mcp/feed",
            "https://qiita.com/tags/ollama/feed",
            "https://qiita.com/tags/n8n/feed",
            "https://qiita.com/tags/huggingface/feed",
            "https://qiita.com/tags/docker/feed",
            "https://qiita.com/tags/dify/feed",
        ],
    },
    # ── はてなブックマーク ─────────────────────
    {
        "id": "hatena", "label": "はてな", "icon": "📌",
        "color": "#00A4DE", "bg": "rgba(0,164,222,0.15)",
        "type": "rss",
        "urls": [
            "https://b.hatena.ne.jp/hotentry/it.rss",
            "https://b.hatena.ne.jp/search/tag?q=AI&mode=rss",
        ],
    },
    # ── arXiv 論文 / 技術報告 ─────────────────
    {
        "id": "arxiv", "label": "arXiv", "icon": "📄",
        "color": "#B31B1B", "bg": "rgba(179,27,27,0.16)",
        "type": "rss",
        "urls": [
            "https://export.arxiv.org/rss/cs.AI",
            "https://export.arxiv.org/rss/cs.CL",
            "https://export.arxiv.org/rss/cs.CV",
            "https://export.arxiv.org/rss/cs.LG",
            "https://export.arxiv.org/rss/cs.RO",
            "https://export.arxiv.org/rss/cs.HC",
            "https://export.arxiv.org/rss/stat.ML",
            "https://export.arxiv.org/rss/eess.AS",
        ],
    },
    # ── X / SNS ───────────────────────────────
    {
        "id": "x_sns", "label": "X / SNS", "icon": "𝕏",
        "color": "#E8C870", "bg": "rgba(232,200,112,0.12)",
        "type": "google",
        "queries": [
            "Claude OR ChatGPT OR Gemini OR OpenAI OR Anthropic OR Grok twitter OR X 技術 話題",
            "MCP OR n8n OR Dify OR Ollama OR MANUS OR AIエージェント SNS 話題 技術",
            "Cursor OR NotebookLM OR Codex OR HuggingFace OR Docker AI 開発 話題",
        ],
    },
    # ── ブログ / 解説記事 ─────────────────────
    {
        "id": "blog", "label": "ブログ", "icon": "🌐",
        "color": "#C96E9A", "bg": "rgba(201,110,154,0.12)",
        "type": "google",
        "queries": [
            "Claude OR \"Claude Code\" OR Anthropic OR NotebookLM OR \"Gemini Canvas\" 解説 実装",
            "AIアバター OR ローカルAI OR オープンソース OR AIクラウドサービス 技術 解説",
            "自律型AIエージェント OR AIエージェント構築 OR LLM活用 OR RAG 実践",
            "Grok OR \"Google AI\" OR \"Notion AI\" OR \"Hugging Face\" 解説 活用",
        ],
    },
    # ── 開発ツール ────────────────────────────
    {
        "id": "devtools", "label": "開発ツール", "icon": "🛠️",
        "color": "#F4A261", "bg": "rgba(244,162,97,0.13)",
        "type": "google",
        "queries": [
            "Cursor OR Codex OR \"Github Copilot\" OR \"VS Code\" AI 開発 実装",
            "\"Claude Code\" OR Antigravity OR \"Google Antigravity\" OR \"open claw\" AI コーディング",
            "AIアプリ開発 OR AIゲーム開発 OR Vibe Coding OR バイブコーディング 実装",
            "MCP OR n8n OR Dify OR \"Hugging Face\" OR Ollama 構築 ツール 解説",
            "Docker OR nanobanana OR \"Notion AI\" OR \"GitHub Actions\" AI 環境構築",
            "\"Google Antigravity\" OR \"Gemini Code Assist\" OR \"Google AI Studio\" 開発 解説",
        ],
    },
    # ── ローカルLLM ───────────────────────────
    {
        "id": "local_llm", "label": "ローカルLLM", "icon": "🖥️",
        "color": "#60A5FA", "bg": "rgba(96,165,250,0.13)",
        "type": "google",
        "queries": [
            "ローカルLLM OR ローカルAI OR Ollama OR LM Studio 構築 解説",
            "Open WebUI OR llama.cpp OR GGUF OR vLLM OR llama-cpp-python 日本語",
            "自宅サーバー AI OR ローカルRAG OR 社内LLM オンプレ 構築",
            "ローカルLLM GPU OR NPU OR Mac mini OR RTX AI 環境",
        ],
    },
    # ── AIエージェント / ビジネス ──────────────
    {
        "id": "agent_biz", "label": "エージェント", "icon": "🤖",
        "color": "#A78BFA", "bg": "rgba(167,139,250,0.13)",
        "type": "google",
        "queries": [
            "AIエージェント OR 自律型AIエージェント OR MANUS OR n8n 構築 実践",
            "\"Gemini Canvas\" OR NotebookLM OR AIクラウドサービス OR オープンソースAI 活用",
            "AIエージェント ビジネス活用 OR 自律型AI 実装 OR LLMエージェント 構築",
        ],
    },
    # ── 自治体 / 行政DX ───────────────────────
    {
        "id": "local_gov", "label": "自治体", "icon": "🏛️",
        "color": "#38BDF8", "bg": "rgba(56,189,248,0.13)",
        "type": "google",
        "queries": [
            "地方自治体 生成AI OR AI活用 OR ChatGPT 導入 OR ガイドライン",
            "自治体DX OR 行政DX OR GovTech OR スマートシティ AI 活用 事例",
            "デジタル庁 デジタル改革共創プラットフォーム OR デジタル改革共創 PF AI 自治体",
            "自治体 窓口 AI OR チャットボット OR 議事録生成 OR 業務効率化",
            "地方公共団体 生成AI OR LGWAN AI OR 自治体 情報システム AI",
        ],
    },
    # ── 企業AI活用 / 業務DX ──────────────────
    {
        "id": "enterprise_ai", "label": "企業AI", "icon": "🏢",
        "color": "#34D399", "bg": "rgba(52,211,153,0.13)",
        "type": "google",
        "queries": [
            "企業 生成AI 活用事例 OR 導入事例 OR 業務効率化",
            "社内AI OR AIエージェント 企業導入 OR RAG 社内ナレッジ",
            "コンタクトセンター AI OR 営業 AI OR マーケティング AI 活用 事例",
            "バックオフィス AI OR 経理 AI OR 人事 AI OR 法務 AI 生成AI",
            "製造業 AI OR 小売 AI OR 金融 AI OR 物流 AI DX 事例",
        ],
    },
    # ── 生成AI（動画・音声・音楽） ────────────
    {
        "id": "generative", "label": "生成AI", "icon": "🎬",
        "color": "#FB923C", "bg": "rgba(251,146,60,0.13)",
        "type": "google",
        "queries": [
            "AI動画生成 OR Remotion OR Sora OR \"Runway\" OR \"Pika\" 技術 解説",
            "AI動画編集 OR Remotion OR Premiere Pro AI OR DaVinci Resolve AI OR CapCut AI 活用",
            "AI音声生成 OR AI作曲 OR \"音楽生成AI\" OR \"TTS\" OR \"Eleven Labs\" 実装",
            "Grok OR \"Google Veo\" OR \"Gemini\" 動画 OR 音声 生成 AI 技術",
            "\"AI動画\" OR \"AI音楽\" OR AIコンテンツ生成 ツール 解説 実践",
        ],
    },
    # ── AI制作：ゲーム / アプリ / 3D / アバター ──
    {
        "id": "creative_dev", "label": "制作開発", "icon": "🎮",
        "color": "#F472B6", "bg": "rgba(244,114,182,0.13)",
        "type": "google",
        "queries": [
            "AIゲーム開発 OR ゲーム開発 AI OR Unity AI OR Unreal Engine AI 実装",
            "AIアプリ開発 OR 生成AIアプリ OR Streamlit OR Next.js AI アプリ 実装",
            "Meshy OR Blender AI OR Unreal Engine AI OR 3D生成AI OR text to 3D",
            "AIアバター OR VRM OR Live2D AI OR Character Creator AI OR アバター生成",
        ],
    },
    # ── ハードウェア / インフラ ───────────────
    {
        "id": "hardware", "label": "ハードウェア", "icon": "⚙️",
        "color": "#94A3B8", "bg": "rgba(148,163,184,0.13)",
        "type": "google",
        "queries": [
            "AI ハードウェア OR GPU OR NPU OR \"AI チップ\" OR NVIDIA 最新 技術",
            "\"ローカル環境構築\" OR Docker OR \"自宅サーバー\" AI 実装 解説",
            "\"AI PC\" OR \"AI アクセラレータ\" OR \"エッジAI\" OR \"量子コンピュータ\" 技術",
        ],
    },
]


# ─────────────────────────────────────────────
#  ヘルパー関数
# ─────────────────────────────────────────────

def build_rss_url(q: str, l: str = "ja", c: str = "JP") -> str:
    return f"https://news.google.com/rss/search?q={urllib.parse.quote(q)}&hl={l}&gl={c}&ceid={c}:{l.upper()}"


def parse_date(entry) -> str:
    if hasattr(entry, "published_parsed") and entry.published_parsed:
        try:
            dt = datetime(*entry.published_parsed[:6])
            return dt.strftime("%Y年%m月%d日  %H:%M")
        except Exception:
            pass
    return "日付不明"


def _entry_date_key(entry) -> str:
    parsed = getattr(entry, "published_parsed", None) or getattr(entry, "updated_parsed", None)
    if parsed:
        try:
            return datetime(*parsed[:6]).strftime("%Y-%m-%d")
        except Exception:
            pass
    for key in ["published", "updated"]:
        raw = str(getattr(entry, key, "") or entry.get(key, ""))
        m = re.search(r"\d{4}-\d{2}-\d{2}", raw)
        if m:
            return m.group(0)
    return ""


def _is_today_entry(entry) -> bool:
    return _entry_date_key(entry) == datetime.now().strftime("%Y-%m-%d")


def get_timestamp(entry) -> float:
    pp = getattr(entry, "published_parsed", None)
    if pp:
        try:
            return float(calendar.timegm(pp))
        except Exception:
            pass
    return 0.0


def get_summary(entry) -> str:
    raw   = getattr(entry, "summary", "") or getattr(entry, "description", "")
    clean = re.sub(r"<[^>]+>", "", raw)
    return re.sub(r"\s+", " ", clean).strip() or "要約はありません。"


def get_image(entry):
    if hasattr(entry, "media_thumbnail") and entry.media_thumbnail:
        return entry.media_thumbnail[0].get("url")
    if hasattr(entry, "media_content") and entry.media_content:
        u = entry.media_content[0].get("url", "")
        if u.startswith("http"):
            return u
    if hasattr(entry, "enclosures") and entry.enclosures:
        for enc in entry.enclosures:
            u = enc.get("href") or enc.get("url", "")
            if u.startswith("http") and any(u.lower().endswith(x) for x in [".jpg",".jpeg",".png",".webp"]):
                return u
    return None


# ─────────────────────────────────────────────
#  ニュースページ用フェッチ
# ─────────────────────────────────────────────

@st.cache_data(ttl=21600, show_spinner=False)
def fetch_news_articles(q: str, l: str, c: str) -> list[dict]:
    url  = build_rss_url(q, l, c)
    feed = feedparser.parse(url)
    out  = []
    for entry in feed.entries[:FETCH_LIMIT]:
        out.append({
            "title":   entry.get("title", "タイトルなし"),
            "link":    entry.get("link", "#"),
            "date":    parse_date(entry),
            "summary": get_summary(entry),
            "image":   get_image(entry),
        })
    seen = {a["link"] for a in out}
    digital_feed = feedparser.parse(DIGITAL_AGENCY_RSS_URL)
    for entry in digital_feed.entries[:50]:
        title = entry.get("title", "タイトルなし")
        summary = get_summary(entry)
        text = (title + " " + summary).lower()
        link = entry.get("link", "#")
        if link in seen:
            continue
        if not any(kw in text for kw in DIGITAL_AGENCY_FOCUS_KEYWORDS):
            continue
        seen.add(link)
        out.append({
            "title":   f"【デジタル庁公式】{title}",
            "link":    link,
            "date":    parse_date(entry),
            "summary": summary,
            "image":   None,
        })
    return out


# ─────────────────────────────────────────────
#  AI情報ページ用フェッチ
# ─────────────────────────────────────────────

def _fetch_rss_url_uncached(url: str, sid: str, slabel: str, scolor: str, sbg: str, sicon: str, limit: int = INFO_FAST_LIMIT) -> list[dict]:
    try:
        feed = feedparser.parse(url)
        out  = []
        entries = feed.entries[:80] if sid == "arxiv" else feed.entries[:limit]
        for entry in entries:
            if sid == "arxiv" and not _is_today_entry(entry):
                continue
            out.append({
                "title":        entry.get("title", "タイトルなし"),
                "link":         entry.get("link", "#"),
                "date":         parse_date(entry),
                "ts":           get_timestamp(entry),
                "summary":      get_summary(entry),
                "author":       getattr(entry, "author", ""),
                "source_id":    sid,
                "source_label": slabel,
                "source_color": scolor,
                "source_bg":    sbg,
                "source_icon":  sicon,
            })
            if len(out) >= limit:
                break
        return out
    except Exception:
        return []


@st.cache_data(ttl=7200, show_spinner=False)
def _fetch_rss_url_fresh(url: str, sid: str, slabel: str, scolor: str, sbg: str, sicon: str, limit: int = INFO_FAST_LIMIT) -> list[dict]:
    return _fetch_rss_url_uncached(url, sid, slabel, scolor, sbg, sicon, limit)


@st.cache_data(ttl=21600, show_spinner=False)
def _fetch_rss_url_mid(url: str, sid: str, slabel: str, scolor: str, sbg: str, sicon: str, limit: int = INFO_FAST_LIMIT) -> list[dict]:
    return _fetch_rss_url_uncached(url, sid, slabel, scolor, sbg, sicon, limit)


@st.cache_data(ttl=43200, show_spinner=False)
def _fetch_rss_url_slow(url: str, sid: str, slabel: str, scolor: str, sbg: str, sicon: str, limit: int = INFO_FAST_LIMIT) -> list[dict]:
    return _fetch_rss_url_uncached(url, sid, slabel, scolor, sbg, sicon, limit)


def _source_cache_tier(source_id: str, url: str) -> str:
    if source_id == "arxiv" or "export.arxiv.org" in url:
        return "fresh"
    if source_id == "digital_agency" or "digital.go.jp" in url:
        return "slow"
    if source_id in {"x_sns", "blog", "devtools", "agent_biz", "local_gov", "enterprise_ai", "generative", "creative_dev", "hardware"}:
        return "fresh"
    return "mid"


def _fetch_rss_url(url: str, sid: str, slabel: str, scolor: str, sbg: str, sicon: str, limit: int = INFO_FAST_LIMIT) -> list[dict]:
    tier = _source_cache_tier(sid, url)
    if tier == "slow":
        return _fetch_rss_url_slow(url, sid, slabel, scolor, sbg, sicon, limit)
    if tier == "fresh":
        return _fetch_rss_url_fresh(url, sid, slabel, scolor, sbg, sicon, limit)
    return _fetch_rss_url_mid(url, sid, slabel, scolor, sbg, sicon, limit)


def clear_info_rss_cache() -> None:
    for fn in [_fetch_rss_url_fresh, _fetch_rss_url_mid, _fetch_rss_url_slow]:
        try:
            fn.clear()
        except Exception:
            pass


# ─── カテゴリ定義（AI情報ページのタブ） ──────────────────────────
CATEGORY_KEYWORDS: dict[str, list[str]] = {
    "GPT": [
        "gpt", "chatgpt", "openai", "gpt-4", "gpt-5", "gpt4", "gpt5",
        "o1", "o3", "o4", "dall-e", "whisper", "codex",
    ],
    "Gemini": [
        "gemini", "google gemini", "gemini pro", "gemini ultra", "gemini flash",
        "gemini 2", "gemini canvas", "google ai studio", "notebooklm",
        "notebook lm", "google deepmind", "bard", "google ai",
    ],
    "Grok": [
        "grok", "xai", "x.ai", "grok 2", "grok 3", "grok-2", "grok-3",
        "elon musk ai", "x ai",
    ],
    "Claude": [
        "claude", "anthropic", "claude code", "claude 3", "claude 4",
        "mcp", "model context protocol",
    ],
    "AIエージェント": [
        "aiエージェント", "ai agent", "エージェント ai", "自律型ai", "自律エージェント",
        "マルチエージェント", "multi-agent", "agentic", "autonomous agent",
        "langchain", "langgraph", "autogpt", "auto-gpt", "crewai", "crew ai",
        "manus", "n8n", "dify", "make.com", "zapier ai",
        "エージェント開発", "エージェント構築", "ai workflow", "aiワークフロー",
    ],
    "地方自治体": [
        "地方自治体", "自治体", "地方公共団体", "行政", "行政dx", "自治体dx",
        "デジタル庁", "デジタル改革共創プラットフォーム", "デジタル改革共創",
        "共創プラットフォーム", "デジタル庁公式", "govtech", "ガブテック", "スマートシティ",
        "lgwan", "自治体ai", "行政ai", "生成aiガイドライン",
        "aiガイドライン", "自治体チャットボット", "窓口ai", "議事録生成",
        "公務員 ai", "行政サービス", "住民サービス", "自治体業務",
        "ai活用自治体", "地方創生 ai", "防災 ai", "教育委員会 ai",
    ],
    "企業": [
        "企業", "法人", "会社", "社内ai", "企業ai", "企業dx", "dx",
        "業務効率化", "業務改善", "生産性向上", "ai導入", "生成ai導入",
        "ai活用事例", "生成ai活用事例", "導入事例", "事例",
        "社内chatgpt", "社内gpt", "社内llm", "rag", "社内ナレッジ",
        "ナレッジマネジメント", "バックオフィス", "コンタクトセンター",
        "カスタマーサポート", "営業ai", "マーケティングai", "人事ai",
        "経理ai", "法務ai", "製造業 ai", "金融 ai", "小売 ai",
        "物流 ai", "aiエージェント 企業", "aiワークフロー",
    ],
    "AI開発ツール": [
        "ai開発ツール", "ai ide", "aiコーディング", "ai coding", "コーディングai",
        "vibe coding", "バイブコーディング", "cursor", "cursor ai",
        "github copilot", "copilot", "claude code", "claude cli",
        "codex", "openai codex", "gemini code assist", "google code assist",
        "antigravity", "google antigravity", "open claw", "openclaw",
        "codeium", "windsurf", "replit agent", "bolt.new", "lovable",
    ],
    "AI論文": [
        "arxiv", "論文", "paper", "survey", "サーベイ", "technical report",
        "研究", "研究報告", "ベンチマーク", "benchmark", "dataset", "データセット",
        "evaluation", "評価", "手法", "提案手法", "実験", "preprint",
        "machine learning", "deep learning", "natural language processing",
        "computer vision", "large language model", "llm", "rag",
        "agent", "agents", "ai agent", "tool use", "mcp", "model context protocol",
        "local llm", "open-source", "open source", "github", "code",
        "inference", "推論", "推論高速化", "optimization", "quantization", "量子化",
        "memory", "long-term memory", "長期記憶", "knowledge graph", "retrieval",
        "multimodal", "マルチモーダル", "speech", "音声", "robotics", "hci",
        "safety", "alignment", "governance", "自治体", "行政", "業務効率化",
        "gpu", "npu", "edge ai", "survey paper",
    ],
    "AI作曲": [
        "ai作曲", "ai音楽", "音楽生成", "ai music", "suno", "udio",
        "music ai", "musicgen", "ai song", "ai歌", "ai作詞",
    ],
    "AI画像生成": [
        "ai画像生成", "画像生成ai", "画像生成", "ai画像", "image generation",
        "text to image", "midjourney", "stable diffusion", "stablediffusion",
        "flux", "dall-e", "dalle", "firefly", "adobe firefly",
        "ideogram", "leonardo ai", "comfyui", "controlnet", "sdxl",
        "imagefx", "nano banana", "画像編集ai", "生成ai 画像",
    ],
    "AI動画": [
        "ai動画", "動画生成", "remotion", "sora", "runway", "pika",
        "veo", "kling", "haiper", "video ai", "ai video", "動画ai",
        "ai映像", "テキストto動画",
    ],
    "動画編集": [
        "動画編集", "ai動画編集", "remotion", "premiere pro ai", "adobe firefly",
        "after effects ai", "davinci resolve ai", "capcut ai", "vrew",
        "descript", "runway edit", "字幕生成", "自動字幕", "ショート動画 ai",
    ],
    "AI音声": [
        "ai音声", "音声生成", "tts", "eleven labs", "elevenlabs",
        "voicevox", "音声ai", "voice ai", "text to speech",
        "音声クローン", "ai voicing", "ai読み上げ",
    ],
    "ローカルLLM": [
        "ローカルllm", "ローカルai", "ローカル環境", "ollama", "docker",
        "localllm", "local llm", "環境構築", "自宅サーバー",
        "ローカル構築", "lm studio", "lmstudio", "open webui",
        "koboldcpp", "llama.cpp", "llama-cpp", "gguf", "vllm",
        "mlx", "jan ai", "anythingllm", "local rag", "ローカルrag",
        "オンプレllm", "社内llm", "プライベートllm",
    ],
    "AI業務自動化": [
        "業務自動化", "ai自動化", "rpa", "rpa代替", "n8n", "dify",
        "make.com", "zapier", "ワークフロー自動化", "業務フロー",
        "定型業務", "バックオフィス", "メール自動化", "議事録生成",
        "社内業務", "業務効率化",
    ],
    "AI教育・研修": [
        "ai教育", "生成ai研修", "ai研修", "社内研修", "リスキリング",
        "aiリテラシー", "プロンプト研修", "教育ai", "職員研修",
        "研修プログラム", "人材育成", "学校 ai", "大学 ai",
    ],
    "AIセキュリティ": [
        "aiセキュリティ", "生成ai セキュリティ", "情報漏洩", "情報漏えい",
        "プロンプトインジェクション", "prompt injection", "データ保護",
        "個人情報保護", "機密情報", "ガバナンス", "リスク管理",
        "シャドーai", "shadow ai", "ゼロトラスト",
    ],
    "ゲーム開発": [
        "ゲーム開発", "aiゲーム", "aiゲーム開発", "game dev", "gamedev",
        "unity", "unreal engine", "ue5", "godot", "roblox", "fortnite uefn",
        "npc ai", "ゲームai", "procedural generation", "プロシージャル生成",
        "ゲームアセット", "ゲーム制作", "indie game ai",
    ],
    "アプリ開発": [
        "アプリ開発", "aiアプリ", "aiアプリ開発", "生成aiアプリ",
        "webアプリ", "streamlit", "gradio", "next.js", "react",
        "fastapi", "langchain app", "ragアプリ", "チャットボット開発",
        "saas ai", "業務アプリ ai", "プロトタイプ開発",
    ],
    "3D": [
        "3d", "3dcg", "3d生成", "text to 3d", "meshy", "tripo",
        "luma ai", "spline", "blender", "blender ai", "unreal engine",
        "ue5", "unity 3d", "gaussian splatting", "nerf", "3dモデル",
        "3dアセット", "3d avatar", "3dアバター",
    ],
    "アバター": [
        "アバター", "aiアバター", "avatar ai", "vrm", "vroid", "live2d",
        "character creator", "キャラクター生成", "aiキャラクター",
        "バーチャルヒューマン", "vtuber ai", "デジタルヒューマン",
        "heygen avatar", "d-id", "synthesia", "音声クローン",
    ],
    "LLM": [
        "llm", "大規模言語モデル", "language model", "llama", "mistral",
        "phi", "falcon", "rag", "retrieval augmented", "ファインチューニング",
        "fine-tuning", "fine tuning", "プロンプトエンジニアリング",
        "prompt engineering", "hugging face", "huggingface",
        "transformer", "オープンソースllm", "open source llm",
        "基盤モデル", "foundation model",
    ],
    "MCP": [
        "mcp", "model context protocol", "mcp server", "mcp client",
        "mcp tool", "mcp連携", "mcp活用", "mcp設定", "mcp実装",
    ],
    "ハードウェア": [
        "nvidia", "gpu", "h100", "h200", "b200", "a100", "cuda",
        "tpu", "aiチップ", "ai chip", "半導体", "npu",
        "amd", "intel arc", "apple silicon", "ai hardware",
        "データセンター ai", "ai server", "aiサーバー",
        "raspberry pi", "ラズベリーパイ", "ラズパイ",
        "mac mini", "mac studio", "mini pc", "ミニpc", "ミニパソコン",
        "小型pc", "小型サーバー",
    ],
    "オープンソース": [
        "オープンソース", "open source", "oss", "github", "オープンソースai",
        "open source ai", "公開モデル", "コミュニティ開発", "apache license",
        "mit license", "オープンモデル", "公式リポジトリ", "fork", "プルリク",
    ],
    "HuggingFace": [
        "hugging face", "huggingface", "hf", "🤗",
        "transformers", "diffusers", "hugging face hub",
        "spaces", "safetensors", "gguf", "モデルハブ",
        "huggingface spaces", "huggingface model",
    ],
    "その他": [],  # catch-all
}

# カテゴリ名 → セッションキー用の安全な文字列
CAT_KEYS: dict[str, str] = {
    "GPT":          "gpt",
    "Gemini":       "gemini",
    "Grok":         "grok",
    "Claude":       "claude",
    "AIエージェント": "agent",
    "地方自治体":  "local_gov",
    "企業":        "enterprise",
    "AI開発ツール": "devtools",
    "AI論文":       "paper",
    "AI作曲":       "music",
    "AI画像生成":   "image_gen",
    "AI動画":       "video",
    "動画編集":     "video_edit",
    "AI音声":       "voice",
    "ローカルLLM":  "local_llm",
    "AI業務自動化": "automation",
    "AI教育・研修": "education",
    "AIセキュリティ": "security",
    "ゲーム開発":   "game_dev",
    "アプリ開発":   "app_dev",
    "3D":           "3d",
    "アバター":     "avatar",
    "LLM":          "llm",
    "MCP":          "mcp",
    "ハードウェア":  "hardware",
    "オープンソース": "oss",
    "HuggingFace":  "hf",
    "その他":       "other",
}

def _is_arxiv_article(article: dict) -> bool:
    source_id = str(article.get("source_id", "")).lower()
    source_label = str(article.get("source_label", "")).lower()
    url = _article_url(article).lower()
    return source_id == "arxiv" or "arxiv" in source_label or "arxiv.org" in url


def filter_by_category(articles: list[dict], category: str) -> list[dict]:
    """カテゴリキーワードでフィルタリング。その他は他カテゴリ非該当の全記事"""
    if category == "AI論文":
        return [a for a in articles if _is_arxiv_article(a)]

    if category == "その他":
        specific = [c for c in CATEGORY_KEYWORDS if c != "その他"]
        def not_matched(art: dict) -> bool:
            if _is_arxiv_article(art):
                return False
            t = (art["title"] + " " + art["summary"]).lower()
            return not any(any(kw in t for kw in CATEGORY_KEYWORDS[c]) for c in specific)
        return [a for a in articles if not_matched(a)]

    keywords = CATEGORY_KEYWORDS.get(category, [])
    if not keywords:
        return articles
    return [
        a for a in articles
        if any(kw in (a["title"] + " " + a["summary"]).lower() for kw in keywords)
    ]


# ─────────────────────────────────────────────
#  キーワード分析アーカイブ
# ─────────────────────────────────────────────

_base = Path(os.environ.get("APP_DATA_DIR", str(Path(__file__).parent)))
ARCHIVE_DIR = _base / "archives"
ARCHIVE_DIR.mkdir(exist_ok=True)


def _archive_path(date_str: str) -> Path:
    return ARCHIVE_DIR / f"{date_str}.json"


def load_analysis(date_str: str) -> dict | None:
    p = _archive_path(date_str)
    if p.exists():
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


def save_analysis(date_str: str, data: dict) -> None:
    with open(_archive_path(date_str), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def list_archives() -> list[str]:
    return sorted([p.stem for p in ARCHIVE_DIR.glob("*.json")], reverse=True)


def render_archive_calendar(archives: list[str], viewing_date: str, today_str: str) -> str:
    archive_set = set(archives)
    try:
        current = datetime.strptime(viewing_date, "%Y-%m-%d")
    except ValueError:
        current = datetime.now()
    month_key = st.session_state.get("kw_calendar_month", current.strftime("%Y-%m"))
    try:
        year, month = [int(x) for x in month_key.split("-")]
    except ValueError:
        year, month = current.year, current.month

    cal_head_l, cal_head_c, cal_head_r = st.columns([1, 2, 1])
    prev_year, prev_month = (year - 1, 12) if month == 1 else (year, month - 1)
    next_year, next_month = (year + 1, 1) if month == 12 else (year, month + 1)
    with cal_head_l:
        if st.button("‹", key="kw_cal_prev", use_container_width=True):
            st.session_state["kw_calendar_month"] = f"{prev_year:04d}-{prev_month:02d}"
            st.rerun()
    with cal_head_c:
        st.markdown(
            f'<div style="text-align:center;color:#ffffff;font-weight:700;padding:7px 0;">{year}年{month:02d}月</div>',
            unsafe_allow_html=True,
        )
    with cal_head_r:
        if st.button("›", key="kw_cal_next", use_container_width=True):
            st.session_state["kw_calendar_month"] = f"{next_year:04d}-{next_month:02d}"
            st.rerun()

    week_labels = ["月", "火", "水", "木", "金", "土", "日"]
    header_cols = st.columns(7)
    for i, label in enumerate(week_labels):
        header_cols[i].markdown(
            f'<div style="text-align:center;color:#c9a96e;font-size:0.75rem;">{label}</div>',
            unsafe_allow_html=True,
        )

    for week_idx, week in enumerate(calendar.monthcalendar(year, month)):
        cols = st.columns(7)
        for day_idx, day in enumerate(week):
            with cols[day_idx]:
                if day == 0:
                    st.markdown("&nbsp;", unsafe_allow_html=True)
                    continue
                date_str = f"{year:04d}-{month:02d}-{day:02d}"
                has_archive = date_str in archive_set
                label = f"📌 {day}" if date_str == viewing_date else str(day)
                if has_archive:
                    if st.button(label, key=f"kw_cal_{date_str}", use_container_width=True):
                        st.session_state["kw_viewing_date"] = date_str
                        st.session_state["kw_calendar_month"] = f"{year:04d}-{month:02d}"
                        st.rerun()
                else:
                    color = "#7a5535" if date_str == today_str else "#4a3520"
                    st.markdown(
                        f'<div style="text-align:center;color:{color};padding:0.45rem 0;border:1px solid #2e1f14;border-radius:5px;opacity:0.55;">{day}</div>',
                        unsafe_allow_html=True,
                    )
    return st.session_state.get("kw_viewing_date", viewing_date)


# ─────────────────────────────────────────────
#  Obsidian 出力
# ─────────────────────────────────────────────

OBSIDIAN_DIRS = [
    "00_Inbox",
    "01_News_Sources",
    "02_Theme_Summaries",
    "03_Article_Drafts",
    "04_Published",
    "05_fact",
    "06_hypothesis",
    "07_trend",
    "08_article",
    "09_AI_Note",
    "10_arXiv",
    "11_Logs",
    "99_Templates",
]

# 段階的に検証できるよう、Obsidian出力は現在この段階まで実行する。
# 1: 本文取得・除外判定・01_News_Sources保存・11_Logs保存
# 7: fact/hypothesis/trend/AI Note/article/arXiv/閲覧まで実行
OBSIDIAN_EXPORT_STAGE = 7

OBSIDIAN_CATEGORY_KEYWORDS: dict[str, list[str]] = {
    "AIエージェント": [
        "aiエージェント", "agentic", "autonomous agent", "自律型ai", "manus",
        "langchain", "langgraph", "crewai", "dify", "n8n", "mcp", "ワークフロー",
    ],
    "AIコーディング": [
        "claude code", "codex", "cursor", "github copilot", "copilot",
        "antigravity", "openclaw", "windsurf", "aiコーディング", "vibe coding",
        "gemini code assist", "プログラミング", "開発支援",
    ],
    "AI検索": [
        "ai検索", "search ai", "perplexity", "genspark", "felo", "検索ai",
        "リサーチai", "deep research", "情報収集", "検索エンジン",
    ],
    "AI論文": [
        "arxiv", "論文", "paper", "survey", "サーベイ", "technical report",
        "preprint", "研究", "研究報告", "提案手法", "実験結果",
        "benchmark", "ベンチマーク", "dataset", "データセット",
        "evaluation", "評価", "large language model", "machine learning",
        "agent", "ai agent", "tool use", "mcp", "model context protocol",
        "local llm", "open-source", "open source", "github", "code",
        "inference", "推論", "推論高速化", "optimization", "quantization", "量子化",
        "memory", "long-term memory", "長期記憶", "knowledge graph", "retrieval", "rag",
        "multimodal", "マルチモーダル", "speech", "音声", "robotics", "hci",
        "safety", "alignment", "governance", "自治体", "行政", "業務効率化",
        "gpu", "npu", "edge ai", "survey paper",
    ],
    "AI画像生成": [
        "画像生成", "ai画像", "image generation", "midjourney", "stable diffusion",
        "flux", "dall-e", "firefly", "ideogram", "leonardo ai",
    ],
    "AI動画生成": [
        "ai動画", "動画生成", "sora", "runway", "pika", "veo", "kling",
        "remotion", "video ai", "動画編集", "ai動画編集",
    ],
    "AI音声・会話AI": [
        "ai音声", "音声生成", "tts", "stt", "elevenlabs", "voicevox",
        "音声クローン", "会話ai", "チャットボット", "音声対話", "voice ai",
    ],
    "AIアバター": [
        "aiアバター", "アバター", "vrm", "vroid", "live2d", "heygen",
        "d-id", "synthesia", "digital human", "デジタルヒューマン", "vtuber",
    ],
    "地方自治体": [
        "地方自治体", "自治体", "地方公共団体", "行政dx", "自治体dx",
        "デジタル庁", "デジタル改革共創プラットフォーム", "デジタル改革共創",
        "共創プラットフォーム", "govtech", "ガブテック", "lgwan",
        "住民サービス", "行政サービス", "公務員", "自治体ai",
        "生成aiガイドライン", "aiガイドライン", "窓口ai", "議事録生成",
    ],
    "ローカルAI・OSS": [
        "ローカルllm", "ローカルai", "ollama", "lm studio", "open webui",
        "llama.cpp", "gguf", "vllm", "oss", "オープンソース", "github",
        "huggingface", "hugging face", "ローカルrag",
    ],
    "AI業務自動化": [
        "業務自動化", "自動化", "workflow automation", "ai自動化",
        "rpa", "rpa代替", "n8n", "dify", "make.com", "zapier",
        "業務フロー", "ワークフロー", "バックオフィス", "議事録", "メール自動化",
        "社内業務", "定型業務", "業務効率化", "自動処理",
    ],
    "AI教育・研修": [
        "ai教育", "生成ai研修", "ai研修", "社内研修", "リスキリング",
        "aiリテラシー", "プロンプト研修", "教育ai", "学校", "大学",
        "授業", "教材", "研修プログラム", "人材育成", "職員研修",
    ],
    "AIセキュリティ": [
        "aiセキュリティ", "セキュリティ", "情報漏洩", "情報漏えい",
        "プロンプトインジェクション", "prompt injection", "データ保護",
        "個人情報保護", "機密情報", "ガバナンス", "リスク管理",
        "シャドーai", "shadow ai", "ゼロトラスト", "脆弱性",
    ],
    "ゲーム開発": [
        "ゲーム開発", "aiゲーム", "aiゲーム開発", "game dev", "gamedev",
        "unity", "unreal engine", "ue5", "godot", "roblox",
        "npc ai", "ai npc", "プロシージャル生成", "procedural",
        "ゲーム制作", "ゲームai", "3dゲーム", "メタバース",
    ],
    "AIビジネス活用": [
        "企業", "社内ai", "業務効率化", "導入事例", "活用事例", "dx",
        "営業", "マーケティング", "人事", "経理", "法務", "コンタクトセンター",
    ],
    "AI法規制・著作権": [
        "著作権", "法規制", "規制", "ai act", "eu ai act", "ガイドライン",
        "個人情報", "プライバシー", "セキュリティ", "コンプライアンス",
        "利用規約", "知的財産",
    ],
    "AIモデル・ベンチマーク": [
        "llm", "gpt", "claude", "gemini", "grok", "llama", "mistral",
        "ベンチマーク", "benchmark", "評価", "モデル", "新モデル",
        "性能", "推論", "rag", "fine-tuning", "ファインチューニング",
    ],
    "AIツール紹介": [
        "ツール", "aiツール", "使い方", "比較", "料金", "無料", "導入",
        "レビュー", "おすすめ", "サービス", "アプリ", "プラットフォーム",
    ],
}

OBSIDIAN_CATEGORY_ORDER = list(OBSIDIAN_CATEGORY_KEYWORDS.keys())

OBSIDIAN_CATEGORY_DESCRIPTIONS: dict[str, str] = {
    "AIエージェント": "AIエージェントに関するニュース・事例・ツールを集約するページ。",
    "AIコーディング": "AIを使った開発支援、コーディングエージェント、開発ワークフローを集約するページ。",
    "AI検索": "AI検索、リサーチAI、情報収集ワークフローを集約するページ。",
    "AI論文": "arXivのAI関連論文、技術報告、サーベイ論文、ベンチマーク情報を集約するページ。",
    "AI画像生成": "画像生成AI、デザイン生成、画像制作ワークフローを集約するページ。",
    "AI動画生成": "AI動画生成、動画編集、映像制作ワークフローを集約するページ。",
    "AI音声・会話AI": "音声生成、会話AI、チャットボット、音声インターフェースを集約するページ。",
    "AIアバター": "AIアバター、デジタルヒューマン、VRM/Live2D活用を集約するページ。",
    "地方自治体": "地方自治体、行政DX、デジタル庁、住民サービスに関するAI活用を集約するページ。",
    "ローカルAI・OSS": "ローカルLLM、OSS、セルフホストAI、社内LLMを集約するページ。",
    "AI業務自動化": "AIエージェント、RPA代替、n8n/Difyなどを使った業務自動化を集約するページ。",
    "AI教育・研修": "AIリテラシー、社内研修、自治体職員研修、教育現場でのAI活用を集約するページ。",
    "AIセキュリティ": "AI利用時の情報漏洩、プロンプトインジェクション、ガバナンス、リスク管理を集約するページ。",
    "ゲーム開発": "AIを使ったゲーム開発、NPC、Unity/Unreal Engine、アセット制作を集約するページ。",
    "AIビジネス活用": "企業・自治体・業務効率化に関するAI活用事例を集約するページ。",
    "AI法規制・著作権": "AIの法規制、著作権、ガイドライン、リスク管理を集約するページ。",
    "AIモデル・ベンチマーク": "AIモデル、性能評価、ベンチマーク、新モデル情報を集約するページ。",
    "AIツール紹介": "AIツールの使い方、比較、料金、導入判断材料を集約するページ。",
}


def _safe_filename(name: str, max_len: int = 80) -> str:
    cleaned = re.sub(r'[\\/:*?"<>|#\[\]\n\r\t]', "_", name).strip(" ._")
    cleaned = re.sub(r"\s+", " ", cleaned)
    return (cleaned[:max_len].rstrip(" ._") or "untitled")


def _md_escape(text: str) -> str:
    return re.sub(r"\s+", " ", str(text or "")).strip()


def _md_block_text(text: str, max_len: int = 6000) -> str:
    cleaned = str(text or "").replace("\r\n", "\n").replace("\r", "\n")
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    cleaned = "\n".join(re.sub(r"[ \t]+", " ", line).strip() for line in cleaned.splitlines())
    return cleaned.strip()[:max_len]


def _article_url(article: dict) -> str:
    return article.get("link") or article.get("url") or "#"


def _article_source(article: dict) -> str:
    return article.get("source_label") or article.get("source_id") or "Google News"


def _article_date(article: dict) -> str:
    return article.get("date") or "日付不明"


def _article_full_text(article: dict) -> str:
    return _md_block_text(article.get("full_text") or article.get("summary") or "")


def _article_content_status(article: dict) -> str:
    return article.get("content_status") or ("本文取得済み" if article.get("full_text") else "RSS要約のみ")


def _article_type(article: dict) -> str:
    source = _article_source(article).lower()
    url = _article_url(article).lower()
    title = article.get("title", "").lower()
    if "github" in source or "github.com" in url:
        return "GitHub"
    if "x / sns" in source or "twitter" in url or "x.com" in url:
        return "X"
    if "note" in source or "note.com" in url:
        return "note"
    if "arxiv" in url or "論文" in title or "paper" in title:
        return "論文"
    if "公式" in source or "digital.go.jp" in url:
        return "公式発表"
    return "ニュース"


def _strip_html_to_text(raw_html: str) -> str:
    text = raw_html
    text = re.sub(r"(?is)<(script|style|noscript|svg|form|header|footer|nav|aside).*?</\1>", " ", text)
    text = re.sub(r"(?is)<br\s*/?>", "\n", text)
    text = re.sub(r"(?is)</p\s*>", "\n", text)
    text = re.sub(r"(?is)</h[1-6]\s*>", "\n", text)
    text = re.sub(r"(?is)<li[^>]*>", "\n- ", text)
    text = re.sub(r"(?is)<[^>]+>", " ", text)
    text = html.unescape(text)
    lines = []
    for line in text.splitlines():
        line = re.sub(r"\s+", " ", line).strip()
        if not line:
            continue
        if len(line) < 8 and not line.startswith("- "):
            continue
        if any(skip in line.lower() for skip in ["cookie", "javascript", "広告", "ログイン", "会員登録", "subscribe"]):
            continue
        lines.append(line)
    return "\n".join(lines)


def _extract_article_text_from_html(raw_html: str) -> str:
    candidates: list[str] = []
    for pattern in [
        r"(?is)<article\b[^>]*>(.*?)</article>",
        r'(?is)<main\b[^>]*>(.*?)</main>',
        r'(?is)<div\b[^>]+(?:class|id)=["\'][^"\']*(?:article|entry|post|content|note|body|main)[^"\']*["\'][^>]*>(.*?)</div>',
    ]:
        candidates.extend(re.findall(pattern, raw_html))
    candidates.append(raw_html)
    best = ""
    for candidate in candidates:
        text = _strip_html_to_text(candidate)
        if len(text) > len(best):
            best = text
    return best[:12000].strip()


@st.cache_data(ttl=21600, show_spinner=False)
def fetch_article_body(url: str) -> dict:
    if not url or url == "#":
        return {"text": "", "status": "URLなし"}
    try:
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                              "(KHTML, like Gecko) Chrome/125.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "ja,en-US;q=0.8,en;q=0.6",
            },
        )
        with urllib.request.urlopen(req, timeout=8) as response:
            content_type = response.headers.get("Content-Type", "")
            if "text/html" not in content_type and "application/xhtml" not in content_type:
                return {"text": "", "status": f"HTML以外: {content_type or '不明'}"}
            raw = response.read(1_500_000)
        raw_html = raw.decode("utf-8", errors="ignore")
        text = _extract_article_text_from_html(raw_html)
        if len(text) < 180:
            return {"text": text, "status": "本文短め・要確認"}
        return {"text": text, "status": "本文取得済み"}
    except Exception as exc:
        return {"text": "", "status": f"本文取得失敗: {type(exc).__name__}"}


def _new_obsidian_log() -> dict[str, list[dict]]:
    return {
        "summary": [],
        "body_fetch_failed": [],
        "excluded_articles": [],
        "unclassified_articles": [],
        "generation_errors": [],
        "ollama_errors": [],
        "generated_files": [],
    }


def _log_event(logs: dict | None, section: str, **kwargs) -> None:
    if logs is None:
        return
    logs.setdefault(section, []).append({
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        **kwargs,
    })


def _quality_exclusion_reason(article: dict, deep: bool = False) -> str:
    title = article.get("title", "").lower()
    summary = article.get("summary", "").lower()
    url = _article_url(article).lower()
    source = _article_source(article).lower()
    combined = title + " " + summary
    if deep and ("note.com" in url or "note" in source):
        body = fetch_article_body(_article_url(article)).get("text", "")
        combined = f"{combined} {body[:3500].lower()}"

    for kw in EXCLUDE_TITLE_KEYWORDS:
        if kw in title:
            return f"除外タイトルキーワード: {kw}"

    for pattern in EXCLUDE_REGEX_PATTERNS:
        if re.search(pattern, combined):
            return f"除外パターン一致: {pattern}"

    weak_personal_markers = [
        "今日は", "最近思う", "ふと思った", "日記", "雑記", "ただのメモ",
        "書いてみました", "作ってみました", "使ってみました",
        "小説", "物語", "ポエム", "詩", "俳句", "短歌",
    ]
    practical_markers = [
        "導入", "活用事例", "業務", "自治体", "企業", "開発", "実装",
        "比較", "検証", "料金", "ガイドライン", "セキュリティ", "api",
        "github", "oss", "ローカルllm", "n8n", "dify", "rag",
    ]
    if any(marker in combined for marker in weak_personal_markers):
        if not any(marker in combined for marker in practical_markers):
            return "日記・ポエム・小説生成・薄い体験談と判断"

    beginner_markers = [
        "初心者", "超初心者", "入門", "始め方", "はじめ方",
        "アカウント作成", "登録方法", "ログイン方法",
    ]
    if any(marker in combined for marker in beginner_markers):
        if not any(marker in combined for marker in ["企業", "自治体", "研修", "教育", "ガイドライン", "セキュリティ", "導入"]):
            return "初心者向けすぎる入門記事と判断"

    if len(_md_escape(article.get("summary", ""))) < 35 and not _is_arxiv_article(article):
        return "要約が短く内容が薄い記事と判断"

    return ""


def enrich_articles_with_body(articles: list[dict], progress_cb=None, logs: dict | None = None) -> list[dict]:
    enriched: list[dict] = []
    total = max(1, len(articles))
    for idx, article in enumerate(articles, 1):
        if progress_cb:
            progress_cb(idx, total, f"本文取得中: {idx}/{total}")
        url = _article_url(article)
        body = fetch_article_body(url)
        full_text = body.get("text", "")
        enriched.append({
            **article,
            "full_text": full_text,
            "content_status": body.get("status", ""),
        })
        status = body.get("status", "")
        if not full_text or status.startswith("本文取得失敗") or status in {"URLなし"} or status.startswith("HTML以外"):
            _log_event(
                logs,
                "body_fetch_failed",
                title=article.get("title", ""),
                url=url,
                source=_article_source(article),
                reason=status or "本文なし",
            )
    return enriched


def _post_body_exclusion_reason(article: dict) -> str:
    if _is_arxiv_article(article) or _is_primary_source(article):
        return ""
    full_text = _md_block_text(article.get("full_text", ""), 1000)
    summary = _md_escape(article.get("summary", ""))
    status = _article_content_status(article)
    if not full_text and len(summary) < 140:
        return f"本文取得不可かつ判断材料が少なすぎる: {status}"
    if status.startswith("本文取得失敗") and len(summary) < 220:
        return f"本文取得失敗で参考情報不足: {status}"
    if status.startswith("HTML以外") and len(summary) < 220:
        return f"HTML本文を取得できず参考情報不足: {status}"
    return ""


def _obsidian_tag_metadata(article: dict, main_category: str, themes: list[str]) -> dict[str, list[str]]:
    text = _article_text_for_classification(article).lower()
    vendor_terms = {
        "OpenAI": ["openai", "chatgpt", "gpt", "codex"],
        "Anthropic": ["anthropic", "claude"],
        "Google": ["google", "gemini", "deepmind", "notebooklm", "antigravity"],
        "xAI": ["xai", "grok"],
        "Microsoft": ["microsoft", "copilot", "azure"],
        "Meta": ["meta", "llama"],
        "NVIDIA": ["nvidia", "gpu", "cuda"],
        "HuggingFace": ["huggingface", "hugging face"],
        "Ollama": ["ollama"],
        "Runway": ["runway"],
        "Suno": ["suno"],
        "Udio": ["udio"],
        "ElevenLabs": ["elevenlabs", "eleven labs"],
        "Blender": ["blender"],
        "Unreal Engine": ["unreal engine", "ue5"],
        "Unity": ["unity"],
        "Meshy": ["meshy"],
    }
    vendors = [name for name, kws in vendor_terms.items() if any(kw in text for kw in kws)]
    technologies = [main_category, *themes]
    applications = [cat for cat in ["企業", "地方自治体", "AI業務自動化", "ゲーム開発", "アプリ開発", "AI教育・研修"] if cat in themes or cat == main_category]
    keyword_candidates = [
        "Codex", "Claude Code", "MCP", "RAG", "ローカルLLM", "AIエージェント",
        "AIコーディング", "AI画像生成", "AI動画", "AI音声", "アバター",
        "量子化", "推論高速化", "Knowledge Graph", "GPU", "NPU",
    ]
    keywords = [kw for kw in keyword_candidates if kw.lower() in text or kw in main_category or kw in themes]
    return {
        "vendor": list(dict.fromkeys(vendors)) or ["未特定"],
        "technology": list(dict.fromkeys([t for t in technologies if t]))[:6],
        "application": list(dict.fromkeys(applications)) or ["未特定"],
        "keywords": list(dict.fromkeys(keywords))[:8],
    }


def _yaml_list(values: list[str]) -> str:
    return "[" + ", ".join(str(v).replace("[", "").replace("]", "") for v in values if v) + "]"


def _is_primary_source(article: dict) -> bool:
    source = _article_source(article)
    url = _article_url(article).lower()
    return "公式" in source or any(domain in url for domain in [
        "digital.go.jp", "openai.com", "anthropic.com", "googleblog.com",
        "developers.googleblog.com", "microsoft.com", "github.com",
    ])


def _importance_label(article: dict) -> str:
    score = score_article(article, 0)
    if _is_primary_source(article) or score >= 50:
        return "高"
    if score >= 30:
        return "中"
    return "低"


def _article_text_for_classification(article: dict) -> str:
    return " ".join([
        str(article.get("title", "")),
        str(article.get("summary", "")),
        str(article.get("full_text", ""))[:4000],
        str(_article_source(article)),
        str(_article_url(article)),
    ]).lower()


def _obsidian_category_scores(article: dict) -> dict[str, int]:
    text = _article_text_for_classification(article)
    scores: dict[str, int] = {}
    for category, keywords in OBSIDIAN_CATEGORY_KEYWORDS.items():
        if category == "AI論文" and not _is_arxiv_article(article):
            scores[category] = 0
            continue
        score = 0
        for keyword in keywords:
            kw = keyword.lower()
            if kw in text:
                score += 3 if len(kw) >= 5 else 2
        if category == "地方自治体" and any(k in text for k in ["自治体", "地方自治体", "デジタル庁", "行政dx", "住民サービス"]):
            score += 6
        if category == "AI業務自動化" and any(k in text for k in ["業務自動化", "rpa", "n8n", "dify", "業務フロー", "定型業務"]):
            score += 6
        if category == "AI教育・研修" and any(k in text for k in ["ai研修", "生成ai研修", "リスキリング", "aiリテラシー", "職員研修"]):
            score += 5
        if category == "AIセキュリティ" and any(k in text for k in ["セキュリティ", "情報漏洩", "プロンプトインジェクション", "ガバナンス", "リスク管理"]):
            score += 6
        if category == "AI論文" and any(k in text for k in ["arxiv", "論文", "paper", "survey", "サーベイ", "benchmark", "dataset"]):
            score += 7
        if category == "ゲーム開発" and any(k in text for k in ["ゲーム開発", "aiゲーム", "unity", "unreal engine", "godot", "npc"]):
            score += 5
        if category == "AIビジネス活用" and any(k in text for k in ["企業", "導入事例", "活用事例", "社内ai", "業務効率化"]):
            score += 4
        if category == "ローカルAI・OSS" and any(k in text for k in ["ローカルllm", "ollama", "oss", "open source", "オープンソース", "github"]):
            score += 4
        if category == "AIモデル・ベンチマーク" and any(k in text for k in ["gpt", "claude", "gemini", "llm", "ベンチマーク"]):
            score += 2
        scores[category] = score
    return scores


def _classify_obsidian_article(article: dict, limit: int = 5) -> tuple[str, list[str]]:
    scores = _obsidian_category_scores(article)
    ranked = sorted(
        OBSIDIAN_CATEGORY_ORDER,
        key=lambda cat: (scores.get(cat, 0), -OBSIDIAN_CATEGORY_ORDER.index(cat)),
        reverse=True,
    )
    positive = [cat for cat in ranked if scores.get(cat, 0) > 0]
    main_category = positive[0] if positive else "AIビジネス活用"
    related = positive[:limit]
    if main_category not in related:
        related.insert(0, main_category)
    return main_category, related[:limit]


def _related_themes(article: dict, limit: int = 5) -> list[str]:
    _main, themes = _classify_obsidian_article(article, limit)
    return themes


def _target_readers(themes: list[str]) -> str:
    readers = ["AI情報収集者"]
    if any(t in themes for t in ["AIビジネス活用", "AIエージェント", "AIコーディング", "ローカルAI・OSS", "AIツール紹介"]):
        readers.insert(0, "ビジネスマン")
    text = " ".join(themes)
    if "自治体" in text or "AIビジネス活用" in themes:
        readers.insert(0, "自治体担当者")
    return " / ".join(dict.fromkeys(readers))


def _seo_candidates(themes: list[str]) -> list[str]:
    defaults = {
        "AIエージェント": ["AIエージェント 活用事例", "AIエージェント 業務効率化"],
        "AIコーディング": ["AIコーディング 使い方", "生成AI 開発支援"],
        "AI検索": ["AI検索 比較", "AI情報収集 方法"],
        "AI論文": ["AI論文 最新", "arXiv AI サーベイ", "LLM ベンチマーク"],
        "AI画像生成": ["画像生成AI ビジネス活用", "画像生成AI 著作権"],
        "AI動画生成": ["AI動画生成 ツール", "AI動画編集 仕事活用"],
        "AI音声・会話AI": ["音声AI 活用事例", "会話AI 業務効率化"],
        "AIアバター": ["AIアバター 活用", "デジタルヒューマン 事例"],
        "地方自治体": ["自治体 AI活用", "デジタル庁 生成AI", "自治体DX 生成AI"],
        "ローカルAI・OSS": ["ローカルLLM 使い方", "OSS生成AI 企業導入"],
        "AI業務自動化": ["AI業務自動化", "n8n AI活用", "Dify 業務効率化"],
        "AI教育・研修": ["生成AI研修", "AIリテラシー教育", "自治体 AI研修"],
        "AIセキュリティ": ["生成AI セキュリティ", "プロンプトインジェクション 対策", "シャドーAI リスク"],
        "ゲーム開発": ["AIゲーム開発", "Unity AI活用", "Unreal Engine 生成AI"],
        "AIビジネス活用": ["生成AI 企業活用", "自治体 AI活用"],
        "AI法規制・著作権": ["生成AI 著作権", "AI法規制 最新"],
        "AIモデル・ベンチマーク": ["AIモデル 比較", "LLM ベンチマーク"],
        "AIツール紹介": ["AIツール おすすめ", "生成AIツール 比較"],
    }
    out: list[str] = []
    for theme in themes[:3]:
        out.extend(defaults.get(theme, []))
    return list(dict.fromkeys(out))[:6] or ["生成AI 最新トレンド", "AI活用事例", "AI情報収集"]


def ensure_obsidian_vault(base_dir: Path = OBSIDIAN_VAULT_DIR) -> dict:
    base_dir.mkdir(parents=True, exist_ok=True)
    for folder in OBSIDIAN_DIRS:
        (base_dir / folder).mkdir(parents=True, exist_ok=True)

    templates = {
        "news_item_template.md": """---
type: news_item
main_category:
related_themes:
source:
url:
created:
source_type:
content_status:
importance:
target_reader:
article_status: source_note
---

# {{title}}

## 基本情報
- 日付：
- URL：
- 出典：
- 取得日：
- メインカテゴリ：
- 関連テーマ：
- 種別：
- 重要度：
- 本文取得状況：
- 想定読者：

## 要約

{{summary}}

## 何が起きたか

事実ベースで記述。発表・公開・導入・仕様変更など、起きたことを短く整理する。

## なぜ重要か

企業、自治体、個人開発者、情報収集者にとっての意味を書く。

## 記事に使えそうな観点

- 〇〇という切り口で記事化できる
- 〇〇と比較できる

## 読者にとって役立つポイント

- 仕事でどう使えるか：
- 自治体でどう関係するか：
- 注意点・リスク：

## 一次情報・確認メモ

- 公式発表：
- 数値・料金・条件：
- 未確認事項：

## 本文抜粋

リンク先から取得した本文をここに保存する。
""",
        "theme_summary_template.md": """---
type: theme_summary
theme:
updated:
status: active
target_reader:
---

# {{theme}}

## 概要

このテーマに関するニュース・事例・ツールを集約するページ。

## 最近の流れ

- 
- 
- 

## 関連ニュース

### YYYY-MM-DD ニュース名
- 何が起きたか
- なぜ重要か
- 関連：
- 本文取得状況：
- ソースMarkdown：

## 共通して見える変化

- 
- 
- 

## ビジネス・自治体で見るべきポイント

- 企業：
- 自治体：
- 個人・情報発信者：

## 記事化できる切り口

- 
- 
- 

## 注意点・未確認事項

- 
- 

## note記事ドラフト用メモ

- 想定読者：
- 記事の主張：
- 導入で使う出来事：
- まとめで伝える考察：

## 参考リンク
""",
        "article_template.md": """---
type: article_draft
status: draft
theme:
created:
target_reader:
seo_keywords:
---

# {{title}}

## 導入

最近、〇〇に関する動きが相次いでいます。
そこから見えてくるのは、〇〇という変化です。
この記事では、その背景とビジネス・自治体で見るべきポイントを整理します。

## 何が起きているのか

事実ベースで説明する。感想表現は使わない。

## なぜ注目されているのか

背景、読者の関心、業務上の意味を書く。

## これまでとの違い

従来のやり方や過去の流れと比較する。

## ビジネス・自治体で見るべきポイント

企業、自治体、個人開発者、情報収集者の視点で整理する。

## まとめ

今回の話は、単なる新ツール紹介ではありません。
〇〇という流れを示しています。

今後は〇〇が重要になりそうです。

## 使用したソースMarkdown

## 参考リンク
""",
        "fact_template.md": """---
type: fact
source:
url:
created:
category:
---

# {{title}}

## 確認できる事実

- 誰が：
- いつ：
- 何を：
- 何が変わったか：
- 関連する機能・技術・製品：

## 根拠

- ソースMarkdown：
- URL：

## 禁止事項

このファイルには推測、感想、考察を書かない。
""",
        "hypothesis_template.md": """---
type: hypothesis
created:
theme:
status: working
---

# {{theme}} 仮説

## 仮説

〇〇の可能性がある。

## 根拠となるfact

- 

## 追加で確認したいこと

- 

## 注意

断定しない。必ず「可能性がある」「考えられる」などの推測表現を使う。
""",
        "trend_template.md": """---
type: trend
theme:
updated:
status: active
---

# {{theme}} トレンド

## 長期トレンド

## 追記ログ

### YYYY-MM-DD

- 

## 関連fact

- 

## 関連まとめ

- 
""",
        "arxiv_template.md": """---
type: arxiv_paper
created:
category: AI論文
source: arXiv
url:
---

# {{title}}

## 基本情報

- 公開日：
- URL：
- arXivカテゴリ：
- 関連テーマ：

## 要約

## 技術的に何が新しいか

## 実務・企業・自治体で応用できそうな点

## 注意点・未確認事項

## 本文抜粋
""",
        "ai_note_template.md": """---
type: ai_note
created:
status: draft
---

# AI Note 原稿

## 使用した素材

## 原稿

## 参考ソース
""",
        "log_template.md": """---
type: obsidian_export_log
created:
---

# Obsidian出力ログ

## 本文取得失敗URL

## 除外した記事

## 分類不能記事

## 生成エラー

## Ollamaエラー
""",
    }
    for filename, body in templates.items():
        path = base_dir / "99_Templates" / filename
        if not path.exists():
            path.write_text(body, encoding="utf-8")

    published_path = base_dir / "04_Published" / "note投稿済み.md"
    if not published_path.exists():
        published_path.write_text("# note投稿済み\n\n投稿済み記事のURLや振り返りを記録します。\n", encoding="utf-8")

    return {"base_dir": str(base_dir), "folders": OBSIDIAN_DIRS}


def _categorized_articles(articles: list[dict]) -> dict[str, list[dict]]:
    grouped: dict[str, list[dict]] = {cat: [] for cat in OBSIDIAN_CATEGORY_ORDER}
    for art in articles:
        main_category, _themes = _classify_obsidian_article(art)
        grouped.setdefault(main_category, []).append(art)
    return {cat: vals for cat, vals in grouped.items() if vals}


def _article_angle_lines(article: dict, themes: list[str]) -> list[str]:
    main = themes[0] if themes else "AIビジネス活用"
    lines = [
        f"{main}の最新動向として、企業・自治体の導入判断や情報収集の材料になる",
        "既存業務への影響、導入時のリスク、運用設計の観点で比較できる",
    ]
    if "AIビジネス活用" in themes:
        lines.insert(0, "企業や自治体がAI活用を検討する際の具体事例として整理できる")
    if "AI法規制・著作権" in themes:
        lines.append("ガイドライン、著作権、個人情報保護の注意点とあわせて記事化できる")
    if "ローカルAI・OSS" in themes:
        lines.append("クラウドAIとの違い、社内利用、コスト、データ管理の観点で比較できる")
    return list(dict.fromkeys(lines))[:4]


def _summarize_article_text(article: dict, max_chars: int = 420) -> str:
    text = _article_full_text(article)
    if not text:
        return _md_escape(article.get("summary", ""))
    sentences = re.split(r"(?<=[。.!?！？])\s+", text.replace("\n", " "))
    picked: list[str] = []
    total = 0
    for sentence in sentences:
        sentence = _md_escape(sentence)
        if len(sentence) < 18:
            continue
        picked.append(sentence)
        total += len(sentence)
        if total >= max_chars:
            break
    return " ".join(picked)[:max_chars].strip() or _md_escape(article.get("summary", ""))


@st.cache_data(ttl=21600, show_spinner=False)
def _ollama_article_analysis(title: str, url: str, category: str, text: str) -> dict:
    clipped = _md_block_text(text, 8000)
    if not clipped:
        return {}
    prompt = f"""あなたはAIニュースをnote記事化するための編集者です。
以下の本文を読み、JSONのみで返してください。

条件:
- summary: 本文全体の要約。冒頭のコピペではなく、何についての記事かを200〜450字で整理する
- what_happened: 何が起きたか。発表、導入、失敗、手順、主張など事実関係を250〜600字で具体的に書く
- why_important: なぜ重要か。企業、自治体、AI情報収集者、実務への影響を300〜700字で丁寧に書く
- 感想表現は禁止
- 本文にない断定はしない

タイトル: {title}
URL: {url}
カテゴリ: {category}

本文:
{clipped}

返す形式:
{{"summary":"...","what_happened":"...","why_important":"..."}}
"""
    raw = _ollama_generate(prompt, "gemma4")
    if not raw:
        return {}
    raw = re.sub(r"```(?:json)?", "", raw).strip("`").strip()
    m = re.search(r"\{[\s\S]*\}", raw)
    if not m:
        return {}
    try:
        data = json.loads(m.group())
    except Exception:
        return {}
    return {
        "summary": _md_block_text(data.get("summary", ""), 900),
        "what_happened": _md_block_text(data.get("what_happened", ""), 1200),
        "why_important": _md_block_text(data.get("why_important", ""), 1400),
    }


def _article_analysis(article: dict, main_category: str) -> dict:
    text = _article_full_text(article)
    title = _md_escape(article.get("title", "タイトルなし"))
    url = _article_url(article)
    analysis = _ollama_article_analysis(title, url, main_category, text)
    if analysis.get("summary") and analysis.get("what_happened") and analysis.get("why_important"):
        return analysis
    fallback_summary = _summarize_article_text(article, 520)
    fallback_what = (
        f"{title}について、リンク先本文では次の内容が扱われています。"
        f"{fallback_summary}"
    )
    fallback_why = (
        f"{main_category}の動向として、この記事は単なる情報紹介ではなく、実務でAIを使う際の判断材料になります。"
        "企業や自治体では、導入効果だけでなく、運用ルール、情報管理、既存業務との接続、利用者への説明まで確認する必要があります。"
        "そのため、本文で扱われている事実をもとに、何が変わりつつあるのか、どの現場に関係するのかを整理しておく価値があります。"
    )
    return {
        "summary": fallback_summary,
        "what_happened": fallback_what,
        "why_important": fallback_why,
    }


def _what_happened_text(article: dict) -> str:
    title = _md_escape(article.get("title", "この記事"))
    summary = _summarize_article_text(article, 520)
    if summary:
        return summary
    return f"{title} に関する情報が公開・報道されています。"


def _news_item_block(article: dict, idx: int, collected_date: str) -> str:
    title = _md_escape(article.get("title", "タイトルなし"))
    full_text = _article_full_text(article)
    url = _article_url(article)
    source = _md_escape(_article_source(article))
    date = _md_escape(_article_date(article))
    main_category, themes = _classify_obsidian_article(article)
    theme_text = " / ".join(themes)
    meta = _obsidian_tag_metadata(article, main_category, themes)
    source_type = _article_type(article)
    importance = _importance_label(article)
    readers = _target_readers(themes)
    analysis = _article_analysis(article, main_category)
    angles = "\n".join(f"- {line}" for line in _article_angle_lines(article, themes))
    return f"""---
type: news_item
created: {collected_date}
main_category: {main_category}
vendor: {_yaml_list(meta['vendor'])}
technology: {_yaml_list(meta['technology'])}
application: {_yaml_list(meta['application'])}
keywords: {_yaml_list(meta['keywords'])}
url: {url}
source: {source}
content_status: {_article_content_status(article)}
---

# {title}

## 基本情報
- 日付：{date}
- URL：{url}
- 出典：{source}
- 取得日：{collected_date}
- メインカテゴリ：{main_category}
- 関連テーマ：{theme_text}
- 種別：{source_type}
- 重要度：{importance}
- 本文取得状況：{_article_content_status(article)}
- 想定読者：{readers}
- vendor：{" / ".join(meta['vendor'])}
- technology：{" / ".join(meta['technology'])}
- application：{" / ".join(meta['application'])}
- keywords：{" / ".join(meta['keywords'])}

## 要約

{analysis.get('summary', '')}

## 何が起きたか

{analysis.get('what_happened', '')}

## なぜ重要か

{analysis.get('why_important', '')}

## 記事に使えそうな観点

{angles}

## 読者にとって役立つポイント

- 仕事でどう使えるか：{main_category}の動きを、業務効率化・情報収集・制作・開発のどこに使えるか検討する材料になります。
- 自治体でどう関係するか：住民サービス、職員業務、ガイドライン、情報管理に関係する場合は追加調査の候補になります。
- 注意点・リスク：公式情報、利用条件、個人情報、著作権、セキュリティ面を確認する必要があります。

## 一次情報・確認メモ

- 公式発表：{url if _is_primary_source(article) else '未確認'}
- 数値・料金・条件：未確認
- 未確認事項：本文取得状況、公開元、対象ユーザー、利用条件を確認する

## 本文抜粋

{full_text[:3500] if full_text else 'リンク先本文を取得できなかったため、RSS要約のみ保存しています。'}
"""


def _news_item_inline_block(article: dict, idx: int) -> str:
    title = _md_escape(article.get("title", "タイトルなし"))
    summary = _summarize_article_text(article, 260)
    url = _article_url(article)
    source = _md_escape(_article_source(article))
    date = _md_escape(_article_date(article))
    main_category, themes_list = _classify_obsidian_article(article)
    themes = " / ".join(themes_list)
    return f"""### {idx}. {title}

- 日付：{date}
- URL：{url}
- 出典：{source}
- メインカテゴリ：{main_category}
- 関連テーマ：{themes}
- 本文取得状況：{_article_content_status(article)}

{summary}
"""


def _write_category_sources(base_dir: Path, grouped: dict[str, list[dict]], today: str) -> list[Path]:
    # 01_News_Sources は「1記事1Markdown」を原則にするため、カテゴリ別indexは作らない。
    return []


def _write_individual_news_items(base_dir: Path, grouped: dict[str, list[dict]], today: str) -> tuple[list[Path], dict[str, list[Path]], dict[str, Path]]:
    written: list[Path] = []
    by_category: dict[str, list[Path]] = {}
    by_url: dict[str, Path] = {}
    seen_urls: set[str] = set()
    day_root = _flat_date_folder(base_dir / "01_News_Sources", today)
    for category, articles in grouped.items():
        category_dir = day_root / _safe_filename(category)
        category_dir.mkdir(parents=True, exist_ok=True)
        for article in articles[:20]:
            url = _article_url(article)
            if url in seen_urls:
                continue
            seen_urls.add(url)
            title = _safe_filename(article.get("title", "ニュース"), 70)
            path = category_dir / f"{title}.md"
            path.write_text(_news_item_block(article, 1, today), encoding="utf-8")
            written.append(path)
            by_category.setdefault(category, []).append(path)
            by_url[url] = path
    return written, by_category, by_url


def _relative_obsidian_path(path: Path, base_dir: Path = OBSIDIAN_VAULT_DIR) -> str:
    try:
        return path.relative_to(base_dir).as_posix()
    except ValueError:
        return path.as_posix()


def _source_markdown_line(path: Path, base_dir: Path) -> str:
    rel = _relative_obsidian_path(path, base_dir)
    return f"[[{rel}]]"


def _date_folder(parent: Path, date_text: str) -> Path:
    parts = date_text.split("-")
    if len(parts) == 3:
        return parent / parts[0] / parts[1] / parts[2]
    return parent / _safe_filename(date_text)


def _flat_date_folder(parent: Path, date_text: str) -> Path:
    return parent / _safe_filename(date_text)


def _build_theme_summary(category: str, articles: list[dict], today: str, source_paths: list[Path], base_dir: Path) -> str:
    top_articles = articles[:8]
    description = OBSIDIAN_CATEGORY_DESCRIPTIONS.get(
        category,
        f"{category} に関するニュース・事例・ツールを集約するページ。",
    )
    usable, reference, exclude = [], [], []
    for article in top_articles:
        status = _article_content_status(article)
        score = score_article(article, 0)
        if article.get("full_text") and score >= 25:
            usable.append(article)
        elif article.get("full_text") or _is_primary_source(article) or _is_arxiv_article(article):
            reference.append(article)
        else:
            exclude.append(article)

    def source_list(items: list[dict], label: str) -> str:
        if not items:
            return "- なし"
        rows = []
        for i, article in enumerate(items[:8]):
            source_md = source_paths[i] if i < len(source_paths) else None
            rows.append(
                f"- {label}: {_md_escape(article.get('title', 'タイトルなし'))}\n"
                f"  - 理由：{_summarize_article_text(article, 180)}\n"
                f"  - 本文取得状況：{_article_content_status(article)}\n"
                f"  - ソースMarkdown：{_source_markdown_line(source_md, base_dir) if source_md else '未作成'}"
            )
        return "\n".join(rows)

    related_blocks = []
    for i, article in enumerate(top_articles[:6]):
        source_md = source_paths[i] if i < len(source_paths) else None
        related_blocks.append(f"""### {_md_escape(_article_date(article))} {_md_escape(article.get('title', 'タイトルなし'))}
- {_summarize_article_text(article, 360)}
- 出典：{_md_escape(_article_source(article))}
- URL：{_article_url(article)}
- 関連：{" / ".join(_related_themes(article))}
- 本文取得状況：{_article_content_status(article)}
- ソースMarkdown：{_source_markdown_line(source_md, base_dir) if source_md else '未作成'}
""")
    related_news = "\n\n".join(related_blocks)
    trend_hint = f"{category}に関する同種の動きが複数確認できる場合、07_trend/{_safe_filename(category)}.md の更新候補です。"
    x_posts = "\n".join(f"- {category}: {_summarize_article_text(a, 110)}" for a in usable[:4]) or "- まだ投稿候補は少ない"
    note_judgement = "記事化候補あり" if usable else ("参考情報として保留" if reference else "除外寄り")
    seo = "\n".join(f"- {kw}" for kw in _seo_candidates([category]))
    source_lines = "\n".join(
        f"- {_source_markdown_line(path, base_dir)}"
        for path in source_paths[:20]
    )
    return f"""---
type: theme_summary
theme: {category}
updated: {today}
---

# {category}

## 概要

{description}

## このテーマで起きていること

{related_news or '関連ニュースはまだありません。'}

## 共通して見える流れ

- {category}に関する情報が複数出ている場合、単発ニュースではなく運用・導入・制作フローの変化として見る。
- 本文取得済みのソースを優先し、タイトルや冒頭だけで判断しない。
- 企業・自治体・開発者・情報発信者のどの読者に役立つかを分けて整理する。

## ソース分類

### 1. 記事化に使えるソース

{source_list(usable, '採用')}

### 2. 参考程度のソース

{source_list(reference, '参考')}

### 3. 除外した方がよいソース

{source_list(exclude, '除外候補')}

## 記事化できる切り口

- {category} の最新動向を、企業や自治体が何を見るべきかという観点で整理する
- 導入事例、公式発表、ツール紹介を比較して、実務で使う前の判断材料にする
- 技術の新規性だけでなく、業務フロー・ガイドライン・運用設計への影響を見る

## X投稿ネタ候補

{x_posts}

## note記事化判定

- 判定：{note_judgement}
- 理由：本文取得済みで、複数ソースから共通する変化が見えるほど記事化しやすい。

## trend更新候補

{trend_hint}

## SEO候補

{seo}

## ソースMarkdown

{source_lines or '- まだありません'}

## 参考リンク

{chr(10).join(f'- [{_md_escape(a.get("title", "タイトルなし"))}]({_article_url(a)})' for a in top_articles)}
"""


def _write_theme_summaries(base_dir: Path, grouped: dict[str, list[dict]], today: str, source_map: dict[str, list[Path]]) -> list[Path]:
    written: list[Path] = []
    day_root = _flat_date_folder(base_dir / "02_Theme_Summaries", today)
    day_root.mkdir(parents=True, exist_ok=True)
    ranked = sorted(
        grouped.items(),
        key=lambda item: len(item[1]),
        reverse=True,
    )
    for category, articles in ranked:
        path = day_root / f"{_safe_filename(category)}.md"
        path.write_text(_build_theme_summary(category, articles, today, source_map.get(category, []), base_dir), encoding="utf-8")
        written.append(path)
    return written


def _extract_summary_bullets(summary_text: str, limit: int = 6) -> list[str]:
    bullets: list[str] = []
    for line in summary_text.splitlines():
        stripped = line.strip()
        if stripped.startswith("- ") and "ソースMarkdown" not in stripped and "URL：" not in stripped:
            content = stripped[2:].strip()
            if content and content not in bullets:
                bullets.append(content)
        if len(bullets) >= limit:
            break
    return bullets


def _draft_title_for_category(category: str) -> str:
    titles = {
        "地方自治体": "自治体の生成AI活用は実証から運用設計の段階へ",
        "AI業務自動化": "AI業務自動化はツール導入から業務設計の時代へ",
        "AIセキュリティ": "生成AI活用で見落とせないセキュリティとガバナンス",
        "ローカルAI・OSS": "ローカルAIとOSSが企業利用で注目される理由",
        "AIエージェント": "AIエージェントは会話するAIから動くAIへ進んでいる",
        "AIコーディング": "AIコーディングは補助ツールから開発プロセスへ広がっている",
        "AI論文": "arXivのAI論文から見える次の技術トレンド",
        "ゲーム開発": "AIゲーム開発は制作補助から開発工程の再設計へ",
    }
    return titles.get(category, f"{category}の最新動向とビジネスで見るべきポイント")


def _enforce_draft_length(body: str, max_chars: int = 10000) -> str:
    """互換用。原稿は途中で切らず、そのまま返す。"""
    return body.strip()


def _draft_has_complete_ending(body: str, required_header: str) -> bool:
    text = body.strip()
    if required_header not in text:
        return False
    if "## まとめ" not in text and "## 結論" not in text:
        return False
    tail = text[-300:]
    if tail.endswith(("、", "，", "・", "です", "ます", "する", "れる", "ため", "ので")):
        return False
    return True


def _complete_ollama_draft(
    body: str,
    original_prompt: str,
    required_header: str,
    required_tail: str,
    max_rounds: int = 3,
) -> str:
    completed = body.strip()
    for _ in range(max_rounds):
        if _draft_has_complete_ending(completed, required_header):
            return completed
        continuation_prompt = f"""以下の原稿は途中で終わっている可能性があります。
すでに書いた内容を繰り返さず、直前から自然に続きを書いてください。

必ず守ること:
- 途中で切らず、最後まで完結させる
- 必ず「## まとめ」を書く
- 必ず末尾に「{required_header}」を入れる
- 参考ソースやソースMarkdownは、以下の指定内容をそのまま載せる
- 事実、背景、比較、実務上の意味を丁寧に書く
- 「思いました」「感じました」は使わない

元の指示:
{original_prompt[:5000]}

指定する末尾:
{required_tail}

現在の原稿末尾:
{completed[-4500:]}
"""
        cont = _ollama_generate(continuation_prompt, "gemma4", num_predict=4200)
        if not cont:
            break
        completed = f"{completed.rstrip()}\n\n{cont.strip()}"
    if required_header not in completed:
        completed = f"{completed.rstrip()}\n\n{required_tail.strip()}"
    return completed.strip()


def _ollama_generate(prompt: str, model: str = "gemma4", num_predict: int = 3600) -> str:
    try:
        payload = json.dumps({
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.35, "num_predict": num_predict},
        }).encode("utf-8")
        req = urllib.request.Request(
            "http://localhost:11434/api/generate",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=240) as response:
            data = json.loads(response.read().decode("utf-8", errors="ignore"))
        return str(data.get("response", "")).strip()
    except Exception:
        return ""


def _build_llm_draft_prompt(category: str, summary_text: str, source_lines: str) -> str:
    clipped_summary = summary_text[:7000]
    return f"""あなたはnote向けのビジネス記事を書く編集者です。
以下の素材Markdownをもとに、日本語の記事ドラフトを作ってください。

条件:
- 全体で3000字以上10000字以下
- 10000字を超えそうな場合でも、途中で切らず、内容を自然に整理して最後まで書ききる
- わかりやすく具体的に、丁寧に略さず書く
- タイトル、導入、見出し、本文、まとめを自然に整える
- note向けだがビジネス寄り
- 煽りすぎない
- 本文では「思いました」「感じました」などの感想表現は禁止
- 事実、背景、比較、ビジネス・自治体での意味を中心に書く
- 専門用語は必要に応じて短く説明する
- 箇条書きは多用しない
- 末尾に「## 使用したソースMarkdown」を入れ、以下のソース一覧をそのまま載せる
- 途中で終わらせず、必ず「まとめ」と「使用したソースMarkdown」まで書いて完結させる

テーマ: {category}

ソース一覧:
{source_lines}

素材Markdown:
{clipped_summary}
"""


def _read_joined(paths: list[Path], max_chars: int = 12000) -> str:
    chunks = []
    for path in paths:
        try:
            chunks.append(f"\n\n# SOURCE: {_relative_obsidian_path(path)}\n" + path.read_text(encoding="utf-8")[:3000])
        except Exception:
            continue
        if sum(len(c) for c in chunks) >= max_chars:
            break
    return "\n".join(chunks)[:max_chars]


def _build_rule_based_draft(category: str, summary_path: Path, source_paths: list[Path], today: str, base_dir: Path) -> str:
    summary_text = summary_path.read_text(encoding="utf-8") if summary_path.exists() else ""
    bullets = _extract_summary_bullets(summary_text, 8)
    key_points = bullets[:4] or [f"{category} に関するニュースや事例が増えています。"]
    source_lines = "\n".join(
        f"- {_source_markdown_line(path, base_dir)}"
        for path in [summary_path, *source_paths[:12]]
    )
    intro_topic = key_points[0].rstrip("。")
    body_points = "\n\n".join(f"{point}。" if not point.endswith(("。", "」", "）")) else point for point in key_points[:3])
    comparison = {
        "AIエージェント": "これまではチャット型AIに質問して回答を得る使い方が中心でした。今後は、外部ツールや業務システムと連携し、一定の目的に沿って処理を進める設計が重要になります。",
        "AIコーディング": "従来の補完ツールはコード入力の支援が中心でした。現在は、要件整理、実装、テスト、修正までを一連の開発プロセスとして扱う流れが強まっています。",
        "AI論文": "これまでは論文情報を研究者や専門職だけが追うことが多い領域でした。現在は、LLM、AIエージェント、画像生成、ローカルAIなどの進化が速く、arXivの論文やサーベイが実務の技術選定にも影響しやすくなっています。",
        "地方自治体": "これまでは個別業務の効率化や実証実験として語られることが多かった領域です。現在は、住民サービス、職員業務、ガイドライン、デジタル庁の一次情報を含めて、自治体全体の運用設計として見る必要があります。",
        "ローカルAI・OSS": "クラウドAIだけに依存する形から、データ管理やコスト、社内ルールに合わせてローカル環境やOSSを使い分ける段階に移っています。",
        "AI業務自動化": "これまでは単発の効率化ツールやRPAとして扱われることが多かった領域です。現在は、生成AI、ワークフロー自動化、社内データ連携を組み合わせて、業務プロセス全体を再設計する流れが強まっています。",
        "AI教育・研修": "これまではAIツールの使い方を学ぶ研修が中心でした。現在は、職種別・業務別に何を任せ、どこに注意するかまで含めた実践的なAIリテラシー教育が求められています。",
        "AIセキュリティ": "これまではAI活用の利便性が注目されがちでした。現在は、機密情報の扱い、プロンプトインジェクション、シャドーAI、ガバナンスを含めて、安全に使うための設計が重要になっています。",
        "ゲーム開発": "これまでは画像やテキスト生成を制作補助として使う例が中心でした。現在は、NPCの振る舞い、プロシージャル生成、UnityやUnreal Engineの制作フローまで含めて、開発工程そのものにAIを組み込む流れが出ています。",
        "AIビジネス活用": "話題性のあるツールを試す段階から、業務フロー、費用対効果、ガイドライン、教育体制まで含めて導入を考える段階に変わっています。",
    }.get(category, "これまでは新機能や新ツールの紹介として受け止められることが多かった領域です。今後は、実務に組み込んだときの成果、制約、運用方法まで含めて見る必要があります。")
    title = _draft_title_for_category(category)
    draft = f"""---
type: article_draft
status: draft
created: {today}
theme: {category}
target_reader: ビジネスマン / 自治体担当者 / AI情報収集者
seo_keywords: {', '.join(_seo_candidates([category]))}
---

# {title}

## 導入

{intro_topic}。

この動きから見えてくるのは、生成AIが単なる便利ツールではなく、仕事の進め方や情報収集の方法に組み込まれ始めているという変化です。この記事では、{category}をめぐる最近の動きを整理し、企業や自治体がどのように捉えるべきかを見ていきます。

## 何が起きているのか

直近では、{category}に関するニュース、ツール、事例が複数出ています。主な動きは次のとおりです。

{body_points}

これらは個別のニュースに見えますが、共通しているのは、AIを試す段階から、実際の業務や制作、開発、情報整理に組み込む段階へ移っている点です。

## なぜ注目されているのか

企業や自治体にとって、AI活用は「何ができるか」だけでは判断しにくくなっています。重要なのは、既存業務のどこに入れると効果が出るのか、どのデータを扱うのか、誰が運用するのか、リスクをどう管理するのかという点です。

特に、情報収集、文書作成、開発支援、住民サービス、社内ナレッジ共有のような領域では、AIの導入効果が見えやすい一方で、ルール整備や検証も欠かせません。

## これまでとの違い

{comparison}

## ビジネス・自治体で見るべきポイント

企業は、業務効率化だけでなく、品質管理、情報共有、顧客対応、教育コストまで含めて見る必要があります。自治体では、職員業務の負担軽減、住民向けサービス、説明責任、個人情報保護の観点が重要になります。

個人や情報発信者にとっては、単にツール名を紹介するよりも、どの業務に使えるのか、導入時に何を確認すべきか、既存のやり方と何が違うのかを整理することで、読者にとって役立つ記事になります。

## 導入前に確認すべき論点

実務でAIを扱うときは、最初に目的を絞ることが重要です。何となく便利そうだから使うのではなく、情報収集を速くしたいのか、資料作成を効率化したいのか、問い合わせ対応を改善したいのか、開発や制作の工程を短縮したいのかを分けて考える必要があります。

次に確認したいのは、扱う情報の種類です。社外に出せない情報、個人情報、契約情報、未公開情報を扱う場合は、利用するAIサービスや運用ルールを慎重に選ぶ必要があります。特に自治体や企業では、便利さだけでなく説明責任と安全性が求められます。

最後に、成果の測り方を決めておくことも大切です。作業時間がどれだけ減ったのか、品質が安定したのか、担当者の負担が下がったのか、住民や顧客への対応が改善したのかを見なければ、導入効果を説明しにくくなります。

## まとめ

今回の話は、単なる新ツール紹介ではありません。
{category}が、実務の中で使い方を検討する段階に入っていることを示しています。

今後は、AIをどう使うかだけでなく、どの業務に組み込み、どのルールで運用し、どの成果を測るかが重要になります。読者が見ておくべきなのは、新しいツール名だけではなく、導入事例、公式発表、運用ルール、現場での使われ方です。

## 使用したソースMarkdown

{source_lines}
"""
    return _enforce_draft_length(draft)


def _build_article_draft_from_summary(category: str, summary_path: Path, source_paths: list[Path], today: str, base_dir: Path, use_ollama: bool = True, extra_sources: list[Path] | None = None) -> str:
    extra_sources = extra_sources or []
    fallback = _build_rule_based_draft(category, summary_path, source_paths, today, base_dir)
    if not use_ollama:
        return fallback
    source_lines = "\n".join(
        f"- {_source_markdown_line(path, base_dir)}"
        for path in [summary_path, *source_paths[:12]]
    )
    summary_text = (summary_path.read_text(encoding="utf-8") if summary_path.exists() else "") + _read_joined(extra_sources, 10000)
    prompt = _build_llm_draft_prompt(category, summary_text, source_lines)
    generated = _ollama_generate(prompt, "gemma4", num_predict=7200)
    if not generated or len(generated) < 2500:
        return fallback
    source_tail = f"## 使用したソースMarkdown\n\n{source_lines}"
    completed = _complete_ollama_draft(generated, prompt, "## 使用したソースMarkdown", source_tail)
    return _enforce_draft_length(completed)


def _write_article_drafts_from_summaries(base_dir: Path, summary_files: list[Path], source_map: dict[str, list[Path]], today: str, use_ollama: bool = True, fact_map: dict[str, list[Path]] | None = None, hypothesis_files: list[Path] | None = None, ai_note_files: list[Path] | None = None) -> list[Path]:
    written: list[Path] = []
    day_root = _flat_date_folder(base_dir / "03_Article_Drafts", today)
    day_root.mkdir(parents=True, exist_ok=True)
    for idx, summary_path in enumerate(summary_files[:10], 1):
        category = summary_path.stem
        title = _safe_filename(f"{category}の最新動向とビジネスで見るべきポイント", 60)
        path = day_root / f"{idx:02d}_{title}.md"
        trend_path = base_dir / "07_trend" / f"{_safe_filename(category)}.md"
        extra = []
        extra.extend((fact_map or {}).get(category, [])[:8])
        extra.extend(hypothesis_files or [])
        extra.extend(ai_note_files or [])
        if trend_path.exists():
            extra.append(trend_path)
        path.write_text(
            _build_article_draft_from_summary(category, summary_path, source_map.get(category, []), today, base_dir, use_ollama, extra_sources=extra),
            encoding="utf-8",
        )
        written.append(path)
    return written


def _ollama_fact_extract(article: dict, main_category: str, logs: dict | None = None) -> dict:
    text = _article_full_text(article)
    if not text:
        return {}
    prompt = f"""以下の記事本文から、確認できる事実だけを抽出してください。
JSONのみで返してください。

禁止:
- 推測、感想、考察を書かない
- 本文にない内容を補わない
- 「重要」「注目」など評価語を使わない

返すJSON:
{{"who":"誰が", "when":"いつ", "what":"何を発表・公開・実施したか", "change":"何が変わったか", "product":"関連する機能・技術・製品", "facts":["本文から確認できる事実1","本文から確認できる事実2"]}}

タイトル: {_md_escape(article.get('title', ''))}
URL: {_article_url(article)}
カテゴリ: {main_category}
本文:
{text[:7000]}
"""
    raw = _ollama_generate(prompt, "gemma4", num_predict=1800)
    if not raw:
        _log_event(logs, "ollama_errors", step="fact抽出", title=article.get("title", ""), url=_article_url(article), reason="Ollama応答なし")
        return {}
    raw = re.sub(r"```(?:json)?", "", raw).strip("`").strip()
    m = re.search(r"\{[\s\S]*\}", raw)
    if not m:
        _log_event(logs, "generation_errors", step="fact抽出JSON解析", title=article.get("title", ""), url=_article_url(article), reason="JSONなし")
        return {}
    try:
        data = json.loads(m.group())
    except Exception as exc:
        _log_event(logs, "generation_errors", step="fact抽出JSON解析", title=article.get("title", ""), url=_article_url(article), reason=type(exc).__name__)
        return {}
    return data if isinstance(data, dict) else {}


def _fact_markdown(article: dict, today: str, source_path: Path | None, base_dir: Path, logs: dict | None = None) -> str:
    main_category, themes = _classify_obsidian_article(article)
    meta = _obsidian_tag_metadata(article, main_category, themes)
    data = _ollama_fact_extract(article, main_category, logs)
    title = _md_escape(article.get("title", "タイトルなし"))
    source_line = _source_markdown_line(source_path, base_dir) if source_path else "未作成"
    facts = data.get("facts") if isinstance(data.get("facts"), list) else []
    if not facts:
        facts = [
            f"出典「{_article_source(article)}」で「{title}」という情報が公開されています。",
            f"URLは {_article_url(article)} です。",
            f"カテゴリは {main_category} と判定されています。",
        ]
    fact_lines = "\n".join(f"- {_md_escape(fact)}" for fact in facts[:8])
    return f"""---
type: fact
source: {_md_escape(_article_source(article))}
url: {_article_url(article)}
created: {today}
category: {main_category}
vendor: {_yaml_list(meta['vendor'])}
technology: {_yaml_list(meta['technology'])}
application: {_yaml_list(meta['application'])}
keywords: {_yaml_list(meta['keywords'])}
---

# {title}

## 確認できる事実

- 誰が：{_md_escape(data.get('who') or _article_source(article))}
- いつ：{_md_escape(data.get('when') or _article_date(article))}
- 何を：{_md_escape(data.get('what') or title)}
- 何が変わったか：{_md_escape(data.get('change') or '本文から明確に確認できる変更点は追加確認が必要です')}
- 関連する機能・技術・製品：{_md_escape(data.get('product') or '未特定')}
- vendor：{" / ".join(meta['vendor'])}
- technology：{" / ".join(meta['technology'])}
- application：{" / ".join(meta['application'])}
- keywords：{" / ".join(meta['keywords'])}

## 本文から確認できる事実

{fact_lines}

## 根拠

- ソースMarkdown：{source_line}
- URL：{_article_url(article)}
- 出典：{_md_escape(_article_source(article))}
- 本文取得状況：{_article_content_status(article)}

## 禁止事項

このファイルには推測、感想、考察を書かない。
"""


def _write_fact_files(base_dir: Path, articles: list[dict], today: str, source_by_url: dict[str, Path], logs: dict | None = None) -> tuple[list[Path], dict[str, list[Path]]]:
    written: list[Path] = []
    by_category: dict[str, list[Path]] = {}
    day_root = _flat_date_folder(base_dir / "05_fact", today)
    day_root.mkdir(parents=True, exist_ok=True)
    seen: set[str] = set()
    for article in articles[:100]:
        url = _article_url(article)
        if url in seen:
            continue
        seen.add(url)
        category, _themes = _classify_obsidian_article(article)
        category_dir = day_root / _safe_filename(category)
        category_dir.mkdir(parents=True, exist_ok=True)
        title = _safe_filename(article.get("title", "fact"), 70)
        path = category_dir / f"{title}.md"
        path.write_text(_fact_markdown(article, today, source_by_url.get(url), base_dir, logs), encoding="utf-8")
        written.append(path)
        by_category.setdefault(category, []).append(path)
    return written, by_category


def _write_hypothesis_files(base_dir: Path, fact_map: dict[str, list[Path]], today: str) -> list[Path]:
    written: list[Path] = []
    day_root = _flat_date_folder(base_dir / "06_hypothesis", today)
    day_root.mkdir(parents=True, exist_ok=True)
    for category, paths in sorted(fact_map.items(), key=lambda x: len(x[1]), reverse=True)[:12]:
        fact_lines = "\n".join(f"- {_source_markdown_line(path, base_dir)}" for path in paths[:10])
        path = day_root / f"{_safe_filename(category)}_hypothesis.md"
        path.write_text(f"""---
type: hypothesis
created: {today}
theme: {category}
status: working
---

# {category} 仮説

## 仮説

{category}に関する複数の事実から、今後この領域の導入・検証・情報発信が増える可能性がある。

企業や自治体では、単発のニュースとして見るだけでなく、業務フロー、ガイドライン、費用対効果、運用体制と結びつけて検討する必要が出てくると考えられる。

## 根拠となるfact

{fact_lines or '- まだfactがありません'}

## 追加で確認したいこと

- 公式発表や一次情報があるか
- 実際の導入事例や利用条件が確認できるか
- 企業・自治体で使う場合の制約やリスクがあるか

## 注意

このファイルはfactをもとにした仮説です。断定は禁止し、「可能性がある」「考えられる」という前提で扱います。
""", encoding="utf-8")
        written.append(path)
    return written


def _append_trend_files(base_dir: Path, grouped: dict[str, list[dict]], today: str, fact_map: dict[str, list[Path]], summary_files: list[Path]) -> list[Path]:
    written: list[Path] = []
    trend_root = base_dir / "07_trend"
    trend_root.mkdir(parents=True, exist_ok=True)
    log_root = _flat_date_folder(base_dir / "11_Logs", today) / "trend_updates"
    log_root.mkdir(parents=True, exist_ok=True)
    summary_map = {path.stem: path for path in summary_files}
    for category, articles in sorted(grouped.items(), key=lambda x: len(x[1]), reverse=True)[:14]:
        path = trend_root / f"{_safe_filename(category)}.md"
        if path.exists():
            current = path.read_text(encoding="utf-8")
        else:
            current = f"""---
type: trend
theme: {category}
updated: {today}
status: active
---

# {category} トレンド

## 長期トレンド

{OBSIDIAN_CATEGORY_DESCRIPTIONS.get(category, category + 'に関する長期トレンドを保存するページ。')}
"""
        article_lines = "\n".join(f"- {_md_escape(a.get('title', 'タイトルなし'))}（{_article_source(a)}）" for a in articles[:6])
        fact_lines = "\n".join(f"- {_source_markdown_line(p, base_dir)}" for p in fact_map.get(category, [])[:8])
        summary_line = f"- {_source_markdown_line(summary_map[category], base_dir)}" if category in summary_map else "- 未作成"
        observation_count = current.count("### 観測") + current.count("#### 今日確認した動き") + len(articles)
        trend_level = "主要トレンド" if observation_count >= 10 else ("継続トレンド" if observation_count >= 3 else "新規/観測中")
        prompt = f"""既存のトレンドMarkdownと今日の材料を読み、テーマごとの長期トレンドとして整理し直してください。

条件:
- 単純追記は禁止
- 既存トレンドを補強 / 修正 / 新規トレンド / ノイズ のどれかを判断する
- 同じ傾向が3回以上なら継続トレンド、10回以上なら主要トレンドとして扱う
- Markdownで返す
- 根拠factリンクと関連まとめリンクを残す

テーマ: {category}
トレンド状態: {trend_level}

既存trend:
{current[:8000]}

今日確認した動き:
{article_lines}

関連fact:
{fact_lines}

関連まとめ:
{summary_line}
"""
        updated = _ollama_generate(prompt, "gemma4", num_predict=4200)
        if not updated:
            updated = f"""{current.rstrip()}

## {today} 更新

### 判断

既存トレンドを補強する可能性がある。

### 今日確認した動き

{article_lines or '- なし'}

### 関連fact

{fact_lines or '- なし'}

### 関連まとめ

{summary_line}
"""
        path.write_text(updated.strip(), encoding="utf-8")
        log_path = log_root / f"{today}_{_safe_filename(category)}_trend_update.md"
        log_path.write_text(f"""---
type: trend_update
created: {today}
theme: {category}
trend_level: {trend_level}
---

# {category} trend更新判断ログ

## 判断

- 判定：{trend_level}
- 観測数目安：{observation_count}
- 更新方針：既存トレンドを読み込み、今日の材料で補強・修正・新規・ノイズを判定して再整理

## 今日確認した動き

{article_lines or '- なし'}

## 関連fact

{fact_lines or '- なし'}

## 関連まとめ

{summary_line}
""", encoding="utf-8")
        written.append(path)
    return written


def _write_candidate_articles(base_dir: Path, draft_files: list[Path], today: str) -> list[Path]:
    written: list[Path] = []
    day_root = base_dir / "08_article"
    day_root.mkdir(parents=True, exist_ok=True)
    for idx, draft_path in enumerate(draft_files[:8], 1):
        try:
            text = draft_path.read_text(encoding="utf-8")
        except Exception:
            continue
        title = _safe_filename(draft_path.stem, 70)
        path = day_root / f"{today}_{idx:02d}_{title}.md"
        path.write_text(text.replace("status: draft", "status: candidate"), encoding="utf-8")
        written.append(path)
    return written


def _write_arxiv_files(base_dir: Path, articles: list[dict], today: str, logs: dict | None = None) -> list[Path]:
    written: list[Path] = []
    day_root = _flat_date_folder(base_dir / "10_arXiv", today)
    day_root.mkdir(parents=True, exist_ok=True)
    for idx, article in enumerate([a for a in articles if _is_arxiv_article(a)][:40], 1):
        title = _md_escape(article.get("title", "arXiv paper"))
        category, themes = _classify_obsidian_article(article)
        analysis = _article_analysis(article, "AI論文")
        path = day_root / f"{idx:02d}_{_safe_filename(title, 80)}.md"
        path.write_text(f"""---
type: arxiv_paper
created: {today}
category: AI論文
source: arXiv
url: {_article_url(article)}
---

# {title}

## 基本情報

- 公開日：{_article_date(article)}
- URL：{_article_url(article)}
- arXivカテゴリ：{_md_escape(article.get('source_label') or 'arXiv')}
- 関連テーマ：{' / '.join(themes)}
- 本文取得状況：{_article_content_status(article)}

## 要約

{analysis.get('summary') or _summarize_article_text(article, 500)}

## 技術的に何が新しいか

{analysis.get('what_happened') or '本文から確認できる技術的な新規性は追加確認が必要です。'}

## 実務・企業・自治体で応用できそうな点

{analysis.get('why_important') or '実務応用の可能性は、関連分野と公開コード、評価条件を確認して判断する必要があります。'}

## 注意点・未確認事項

- 査読前のプレプリントである可能性があります。
- 実装コード、ライセンス、データセット、評価条件は一次情報で確認してください。
- 今日新しく公開・更新されたarXiv項目のみを対象にしています。

## 本文抜粋

{_article_full_text(article)[:3500] or _md_escape(article.get('summary', ''))}
""", encoding="utf-8")
        written.append(path)
    return written


def _build_ai_note_source(base_dir: Path, today: str, summary_files: list[Path], fact_files: list[Path], arxiv_files: list[Path]) -> str:
    lines = ["---", "type: ai_note_source", f"created: {today}", "---", "", f"# {today} AI Note ソース", ""]
    lines.append("## テーマ別まとめ")
    lines.extend(f"- {_source_markdown_line(path, base_dir)}" for path in summary_files[:12])
    lines.append("\n## fact")
    lines.extend(f"- {_source_markdown_line(path, base_dir)}" for path in fact_files[:20])
    lines.append("\n## arXiv")
    lines.extend(f"- {_source_markdown_line(path, base_dir)}" for path in arxiv_files[:12])
    lines.append("\n## 関連trend")
    trend_root = base_dir / "07_trend"
    if trend_root.exists():
        lines.extend(f"- {_source_markdown_line(path, base_dir)}" for path in sorted(trend_root.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True)[:12])
    return "\n".join(lines)


def _build_ai_note_article(source_text: str, today: str, logs: dict | None = None) -> str:
    prompt = f"""以下のAIニュース素材をもとに、note向けのビジネス寄り記事を1本作成してください。

条件:
- AI Noteキーワードは作らない
- 1500字以上6000字以下
- 途中で切らず最後まで書く
- 以下の見出しを必ず含める
  - 今日の注目テーマ
  - 今日起きたこと
  - 今日見えた変化
  - X投稿ネタ候補
  - note記事ネタ候補
  - 関連trend
  - 使用ソース一覧
- 本文では感想表現を使わず、事実、背景、比較、ビジネス・自治体での意味を中心に書く

日付: {today}
素材:
{source_text[:9000]}
"""
    generated = _ollama_generate(prompt, "gemma4", num_predict=7200)
    if not generated:
        _log_event(logs, "ollama_errors", step="AI Note原稿生成", reason="Ollama応答なし")
        generated = f"""# {today} のAIニュースから見る実務活用の流れ

## 導入

今日のAI関連情報では、技術開発、企業活用、自治体活用、AI論文など複数の動きが確認できます。個別のニュースを追うだけでは流れが見えにくいため、素材をまとめて見ることで、仕事や行政でどのような変化が起きているのかを整理できます。

## 本文

AI活用は、単なるツール紹介から、業務フローや情報管理、開発体制、教育、セキュリティを含む運用設計へ広がっています。企業では業務効率化や社内ナレッジ活用、自治体では住民サービスや職員業務の改善が主な論点になります。

## まとめ

今後は新しいツール名だけでなく、どの現場で使えるのか、どの情報を扱うのか、どのルールで運用するのかを見ることが重要になります。

## 使用したソース

{source_text[:2500]}
"""
    tail = "## 使用ソース一覧\n\n" + source_text[:4000]
    return _complete_ollama_draft(generated, prompt, "## 使用ソース一覧", tail)


def _write_ai_note_files(base_dir: Path, today: str, summary_files: list[Path], fact_files: list[Path], arxiv_files: list[Path], logs: dict | None = None) -> list[Path]:
    written: list[Path] = []
    day_root = _flat_date_folder(base_dir / "09_AI_Note", today)
    day_root.mkdir(parents=True, exist_ok=True)
    source_text = _build_ai_note_source(base_dir, today, summary_files, fact_files, arxiv_files)
    source_path = day_root / f"AI_Note_Source_{today}.md"
    draft_path = day_root / f"AI_Note_{today}.md"
    source_path.write_text(source_text, encoding="utf-8")
    draft_path.write_text(_build_ai_note_article(source_text, today, logs), encoding="utf-8")
    written.extend([source_path, draft_path])
    return written


def _write_export_log(base_dir: Path, today: str, logs: dict) -> Path:
    day_root = _flat_date_folder(base_dir / "11_Logs", today)
    day_root.mkdir(parents=True, exist_ok=True)
    path = day_root / f"{datetime.now().strftime('%H%M%S')}_obsidian_export_log.md"
    def section(title: str, key: str) -> str:
        items = logs.get(key, [])
        if not items:
            return f"## {title}\n\n- なし\n"
        body = []
        for item in items:
            body.append("\n".join(f"- {k}: {v}" for k, v in item.items()))
        return f"## {title}\n\n" + "\n\n".join(body) + "\n"
    path.write_text(f"""---
type: obsidian_export_log
created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
---

# Obsidian出力ログ {today}

{section('実行サマリー', 'summary')}
{section('本文取得失敗URL', 'body_fetch_failed')}
{section('除外した記事', 'excluded_articles')}
{section('分類不能記事', 'unclassified_articles')}
{section('生成エラー', 'generation_errors')}
{section('Ollamaエラー', 'ollama_errors')}
{section('生成されたファイル一覧', 'generated_files')}
""", encoding="utf-8")
    return path


def export_obsidian_pipeline(base_dir: Path = OBSIDIAN_VAULT_DIR, use_ollama: bool = True, progress_cb=None) -> dict:
    def update(percent: int, message: str):
        if progress_cb:
            progress_cb(percent, message)

    logs = _new_obsidian_log()
    update(3, "Obsidianフォルダを確認中…")
    ensure_obsidian_vault(base_dir)
    today = datetime.now().strftime("%Y-%m-%d")
    update(8, "AIニュースを収集中…")
    news_articles = fetch_news_articles("生成AI OR AI OR 人工知能", "ja", "JP")
    filtered_news: list[dict] = []
    for article in news_articles:
        reason = _quality_exclusion_reason(article, deep=False)
        if reason:
            _log_event(
                logs,
                "excluded_articles",
                title=article.get("title", ""),
                url=_article_url(article),
                source=_article_source(article),
                reason=reason,
            )
        else:
            filtered_news.append(article)
    update(18, "AI情報を収集中…")
    info_articles = get_info_articles_for_obsidian([src["id"] for src in INFO_SOURCES], logs=logs)
    combined_articles = filtered_news + info_articles

    def body_progress(idx: int, total: int, message: str):
        pct = 22 + int((idx / max(1, total)) * 28)
        update(min(50, pct), f"{message} / リンク先本文を確認しています")

    all_articles = enrich_articles_with_body(combined_articles, progress_cb=body_progress, logs=logs)
    accepted_articles: list[dict] = []
    for article in all_articles:
        reason = _post_body_exclusion_reason(article)
        if reason:
            _log_event(
                logs,
                "excluded_articles",
                title=article.get("title", ""),
                url=_article_url(article),
                source=_article_source(article),
                reason=reason,
            )
        else:
            accepted_articles.append(article)
    all_articles = accepted_articles
    update(53, "カテゴリ分類中…")
    grouped = _categorized_articles(all_articles)
    for article in all_articles:
        category, _themes = _classify_obsidian_article(article)
        if not category:
            _log_event(logs, "unclassified_articles", title=article.get("title", ""), url=_article_url(article), reason="カテゴリ未判定")

    update(58, "Inbox Markdownを作成中…")
    inbox_path = base_dir / "00_Inbox" / "未整理ニュース.md"
    inbox_body = [
        "---",
        "type: inbox",
        f"updated: {today}",
        "---",
        "",
        "# 未整理ニュース",
        "",
        f"最終更新: {today}",
        "",
    ]
    inbox_body.extend(_news_item_inline_block(a, i) for i, a in enumerate(all_articles[:80], 1))
    inbox_path.write_text("\n".join(inbox_body), encoding="utf-8")

    update(64, "カテゴリ別Markdownを作成中…")
    source_files = _write_category_sources(base_dir, grouped, today)
    update(70, "ニュース個別Markdownを作成中…")
    item_files, source_map, source_by_url = _write_individual_news_items(base_dir, grouped, today)
    for path in [*source_files, *item_files]:
        _log_event(logs, "generated_files", type="news_source", path=_relative_obsidian_path(path, base_dir))

    if OBSIDIAN_EXPORT_STAGE <= 1:
        update(95, "第1段階ログを保存中…")
        _log_event(
            logs,
            "summary",
            stage="第1段階",
            collected=len(combined_articles),
            accepted=len(all_articles),
            excluded=len(logs.get("excluded_articles", [])),
            body_fetch_failed=len(logs.get("body_fetch_failed", [])),
            generated_files=len(source_files) + len(item_files),
        )
        log_path = _write_export_log(base_dir, today, logs)
        _log_event(logs, "generated_files", type="log", path=_relative_obsidian_path(log_path, base_dir))
        log_path.write_text(log_path.read_text(encoding="utf-8"), encoding="utf-8")
        update(100, "第1段階のObsidian出力が完了しました。")
        return {
            "base_dir": str(base_dir),
            "stage": OBSIDIAN_EXPORT_STAGE,
            "news_count": len(filtered_news),
            "info_count": len(info_articles),
            "body_fetched_count": sum(1 for a in all_articles if a.get("full_text")),
            "category_count": len(grouped),
            "source_files": len(source_files),
            "item_files": len(item_files),
            "fact_files": 0,
            "hypothesis_files": 0,
            "summary_files": 0,
            "trend_files": 0,
            "draft_files": 0,
            "article_files": 0,
            "arxiv_files": 0,
            "ai_note_files": 0,
            "log_files": 1,
            "excluded_count": len(logs.get("excluded_articles", [])),
            "body_failed_count": len(logs.get("body_fetch_failed", [])),
            "draft_method": "第1段階: 本文取得・除外判定・ニュース保存・ログ保存",
            "inbox": str(inbox_path),
            "log": str(log_path),
        }

    update(74, "fact Markdownを作成中…")
    fact_files, fact_map = _write_fact_files(base_dir, all_articles, today, source_by_url, logs)
    update(78, "仮説Markdownを作成中…")
    hypothesis_files = _write_hypothesis_files(base_dir, fact_map, today)
    update(81, "テーマ別まとめMarkdownを作成中…")
    summary_files = _write_theme_summaries(base_dir, grouped, today, source_map)
    update(85, "長期トレンドを更新中…")
    trend_files = _append_trend_files(base_dir, grouped, today, fact_map, summary_files)
    update(89, "今日のarXiv論文を保存中…")
    arxiv_files = _write_arxiv_files(base_dir, all_articles, today, logs)
    update(92, "AI Note原稿とソースを保存中…")
    ai_note_files = _write_ai_note_files(base_dir, today, summary_files, fact_files, arxiv_files, logs)
    update(95, "note記事ドラフトを生成中…")
    draft_files = _write_article_drafts_from_summaries(base_dir, summary_files, source_map, today, use_ollama, fact_map=fact_map, hypothesis_files=hypothesis_files, ai_note_files=ai_note_files)
    update(97, "完成候補記事を保存中…")
    article_files = _write_candidate_articles(base_dir, draft_files, today)
    update(99, "処理ログを保存中…")
    for typ, paths in [
        ("fact", fact_files),
        ("hypothesis", hypothesis_files),
        ("theme_summary", summary_files),
        ("trend", trend_files),
        ("arxiv", arxiv_files),
        ("ai_note", ai_note_files),
        ("article_draft", draft_files),
        ("article", article_files),
    ]:
        for path in paths:
            _log_event(logs, "generated_files", type=typ, path=_relative_obsidian_path(path, base_dir))
    _log_event(
        logs,
        "summary",
        stage="第7段階",
        collected=len(combined_articles),
        accepted=len(all_articles),
        excluded=len(logs.get("excluded_articles", [])),
        body_fetch_failed=len(logs.get("body_fetch_failed", [])),
        generated_files=len(logs.get("generated_files", [])),
    )
    log_path = _write_export_log(base_dir, today, logs)
    update(100, "Obsidian出力が完了しました。")

    return {
        "base_dir": str(base_dir),
        "news_count": len(filtered_news),
        "info_count": len(info_articles),
        "body_fetched_count": sum(1 for a in all_articles if a.get("full_text")),
        "category_count": len(grouped),
        "source_files": len(source_files),
        "item_files": len(item_files),
        "fact_files": len(fact_files),
        "hypothesis_files": len(hypothesis_files),
        "summary_files": len(summary_files),
        "trend_files": len(trend_files),
        "draft_files": len(draft_files),
        "article_files": len(article_files),
        "arxiv_files": len(arxiv_files),
        "ai_note_files": len(ai_note_files),
        "log_files": 1,
        "excluded_count": len(logs.get("excluded_articles", [])),
        "body_failed_count": len(logs.get("body_fetch_failed", [])),
        "draft_method": "Ollama gemma4（未接続時のみルール生成へ自動退避）",
        "inbox": str(inbox_path),
        "log": str(log_path),
    }


def _obsidian_date_options(base_dir: Path = OBSIDIAN_VAULT_DIR) -> list[str]:
    roots = [
        base_dir / "09_AI_Note",
        base_dir / "10_arXiv",
        base_dir / "11_Logs",
        base_dir / "08_article",
        base_dir / "06_hypothesis",
        base_dir / "05_fact",
        base_dir / "03_Article_Drafts",
        base_dir / "02_Theme_Summaries",
        base_dir / "01_News_Sources",
    ]
    dates: set[str] = set()
    for root in roots:
        if not root.exists():
            continue
        for day_dir in root.iterdir():
            if day_dir.is_dir() and re.fullmatch(r"\d{4}-\d{2}-\d{2}", day_dir.name):
                dates.add(day_dir.name)
        for year_dir in root.iterdir():
            if not year_dir.is_dir() or not re.fullmatch(r"\d{4}", year_dir.name):
                continue
            for month_dir in year_dir.iterdir():
                if not month_dir.is_dir() or not re.fullmatch(r"\d{2}", month_dir.name):
                    continue
                for day_dir in month_dir.iterdir():
                    if day_dir.is_dir() and re.fullmatch(r"\d{2}", day_dir.name):
                        dates.add(f"{year_dir.name}-{month_dir.name}-{day_dir.name}")
    return sorted(dates, reverse=True)


def _obsidian_files_for_view(base_dir: Path, section: str, date_text: str) -> list[Path]:
    section_dirs = {
        "AI Note": "09_AI_Note",
        "arXiv": "10_arXiv",
        "ログ": "11_Logs",
        "完成候補記事": "08_article",
        "トレンド": "07_trend",
        "仮説": "06_hypothesis",
        "fact": "05_fact",
        "記事ドラフト": "03_Article_Drafts",
        "テーマ別まとめ": "02_Theme_Summaries",
        "ニュースソース": "01_News_Sources",
        "Inbox": "00_Inbox",
    }
    folder = section_dirs.get(section, "03_Article_Drafts")
    if section == "Inbox":
        path = base_dir / folder / "未整理ニュース.md"
        return [path] if path.exists() else []
    if section in {"トレンド", "完成候補記事"}:
        root = base_dir / folder
        return sorted(root.rglob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True) if root.exists() else []
    if section in {"AI Note", "arXiv", "ログ", "仮説", "fact", "ニュースソース", "テーマ別まとめ", "記事ドラフト"}:
        root = _flat_date_folder(base_dir / folder, date_text)
    else:
        root = _date_folder(base_dir / folder, date_text)
    if not root.exists():
        return []
    return sorted(root.rglob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True)


def _read_markdown_preview(path: Path, max_chars: int = 14000) -> str:
    try:
        text = path.read_text(encoding="utf-8")
    except Exception as exc:
        return f"読み込みに失敗しました: {exc}"
    return text[:max_chars].rstrip()


def is_quality_article(article: dict, deep: bool = False) -> bool:
    """エンタメ系・浅い入門記事をフィルタリング"""
    return not _quality_exclusion_reason(article, deep=deep)


def get_info_articles(selected_ids: list[str], deep: bool = False) -> list[dict]:
    all_art, seen = [], set()
    fetch_limit = INFO_DEEP_LIMIT if deep else INFO_FAST_LIMIT
    tasks = []
    for src in INFO_SOURCES:
        if src["id"] not in selected_ids:
            continue
        kw = dict(sid=src["id"], slabel=src["label"],
                  scolor=src["color"], sbg=src["bg"], sicon=src["icon"])

        # URL リスト構築（RSS直接 or Google News RSS）
        if src["type"] == "rss":
            urls = src.get("urls", [])
        elif src["type"] == "google":
            qs   = src.get("queries") or ([src["query"]] if src.get("query") else [])
            urls = [build_rss_url(q, "ja", "JP") for q in qs]
        else:
            urls = []

        for url in urls:
            tasks.append((url, kw))

    with ThreadPoolExecutor(max_workers=INFO_FETCH_WORKERS) as executor:
        future_map = {
            executor.submit(_fetch_rss_url, url, limit=fetch_limit, **kw): url
            for url, kw in tasks
        }
        for future in as_completed(future_map):
            try:
                articles = future.result()
            except Exception:
                continue
            for art in articles:
                link = art.get("link")
                if link not in seen and is_quality_article(art, deep=deep):
                    seen.add(link)
                    all_art.append(art)

    all_art.sort(key=lambda x: x.get("ts", 0), reverse=True)
    return all_art


def get_info_articles_for_obsidian(selected_ids: list[str], logs: dict | None = None) -> list[dict]:
    all_art, seen = [], set()
    fetch_limit = INFO_DEEP_LIMIT
    tasks = []
    for src in INFO_SOURCES:
        if src["id"] not in selected_ids:
            continue
        kw = dict(sid=src["id"], slabel=src["label"],
                  scolor=src["color"], sbg=src["bg"], sicon=src["icon"])
        if src["type"] == "rss":
            urls = src.get("urls", [])
        elif src["type"] == "google":
            qs = src.get("queries") or ([src["query"]] if src.get("query") else [])
            urls = [build_rss_url(q, "ja", "JP") for q in qs]
        else:
            urls = []
        for url in urls:
            tasks.append((url, kw))

    with ThreadPoolExecutor(max_workers=INFO_FETCH_WORKERS) as executor:
        future_map = {
            executor.submit(_fetch_rss_url, url, limit=fetch_limit, **kw): url
            for url, kw in tasks
        }
        for future in as_completed(future_map):
            try:
                articles = future.result()
            except Exception as exc:
                _log_event(logs, "generation_errors", step="AI情報RSS取得", reason=type(exc).__name__)
                continue
            for art in articles:
                link = art.get("link")
                if not link or link in seen:
                    continue
                reason = _quality_exclusion_reason(art, deep=True)
                if reason:
                    _log_event(
                        logs,
                        "excluded_articles",
                        title=art.get("title", ""),
                        url=link,
                        source=_article_source(art),
                        reason=reason,
                    )
                    continue
                seen.add(link)
                all_art.append(art)

    all_art.sort(key=lambda x: x.get("ts", 0), reverse=True)
    return all_art


# ─────────────────────────────────────────────
#  注目度スコアリング（ニュースページTOP5用）
# ─────────────────────────────────────────────

HOT_KEYWORDS: dict[str, float] = {
    "agi": 28, "汎用人工知能": 28,
    "gpt-5": 26, "gpt5": 26, "o3": 20, "o4": 20,
    "claude 4": 24, "claude4": 24, "gemini 2": 22,
    "openai": 15, "chatgpt": 14, "claude": 13, "gemini": 13,
    "gpt-4o": 13, "gpt-4": 12, "llama": 12, "mistral": 11, "grok": 11,
    "sora": 14, "nvidia": 13, "h100": 12,
    "microsoft": 9, "google deepmind": 13, "anthropic": 14,
    "regulation": 12, "規制": 12, "禁止": 12, "eu ai act": 15,
    "breakthrough": 14, "画期的": 14, "革新": 12, "世界初": 14,
    "new model": 11, "新モデル": 11, "released": 9, "リリース": 9,
    "robot": 10, "robotics": 12, "humanoid": 14, "ヒューマノイド": 14,
    "autonomous": 11, "自律": 11, "自動運転": 12,
    "billion": 10, "兆円": 13, "億円": 10,
    "safety": 8, "alignment": 12,
    "research": 6, "論文": 6, "arxiv": 12, "survey": 10, "サーベイ": 10,
    "benchmark": 10, "evaluation": 9, "dataset": 8, "technical report": 8,
    "agent": 9, "tool use": 9, "mcp": 12, "rag": 10, "knowledge graph": 9,
    "long-term memory": 11, "長期記憶": 11, "quantization": 12, "量子化": 12,
    "inference": 9, "推論高速化": 12, "optimization": 8,
    "multimodal": 10, "マルチモーダル": 10,
    "自治体": 11, "地方自治体": 13, "デジタル庁": 13, "自治体dx": 12,
    "行政dx": 12, "govtech": 11, "スマートシティ": 10,
    "企業": 8, "社内ai": 12, "企業dx": 10, "業務効率化": 10,
    "導入事例": 10, "活用事例": 10, "社内llm": 12,
    "ローカルllm": 15, "ollama": 13, "lm studio": 12, "open webui": 11,
    "gguf": 10, "llama.cpp": 11, "ローカルrag": 12,
    "cursor": 10, "claude code": 12, "codex": 10, "ai開発ツール": 10,
    "ゲーム開発": 10, "aiゲーム": 11, "アプリ開発": 10,
    "画像生成": 10, "ai画像生成": 11, "midjourney": 10, "stable diffusion": 10,
    "flux": 9, "dall-e": 9, "firefly": 8, "comfyui": 9,
    "動画編集": 9, "ai動画編集": 11,
    "meshy": 11, "blender": 10, "unreal engine": 10, "3d生成": 11,
    "アバター": 10, "vrm": 9, "live2d": 9,
}


def score_article(article: dict, idx: int) -> float:
    text  = (article["title"] + " " + article["summary"]).lower()
    score = sum(pts for kw, pts in HOT_KEYWORDS.items() if kw in text)
    score += max(0.0, 28 - idx * 0.45)
    score += len(re.findall(r'\d+(?:\.\d+)?[%億兆]', article["title"])) * 2.5
    return score


def get_top5(articles: list[dict]) -> list[dict]:
    scored = sorted(
        [{**a, "_score": score_article(a, i)} for i, a in enumerate(articles)],
        key=lambda x: x["_score"], reverse=True,
    )[:5]
    max_s = scored[0]["_score"] if scored else 1.0
    for item in scored:
        item["_pct"] = min(100, int(item["_score"] / max_s * 100))
    return scored


# ─────────────────────────────────────────────
#  TOP5 フラグメント（12時間ごと自動更新）
# ─────────────────────────────────────────────

RANK_CSS   = ["rb-1", "rb-2", "rb-3", "rb-4", "rb-5"]
RANK_LABEL = ["1st",  "2nd",  "3rd",  "4th",  "5th"]

_TOP5_INTERVAL = 21600  # 6時間


def _build_top5_html(top5: list[dict]) -> str:
    rows_html = ""
    for rank, item in enumerate(top5):
        item_cls = "top5-item rank-first" if rank == 0 else "top5-item"
        rows_html += f"""
<a href="{item['link']}" target="_blank" class="{item_cls}">
  <div class="rank-badge {RANK_CSS[rank]}">{RANK_LABEL[rank]}</div>
  <div class="top5-content">
    <div class="top5-title">{item['title']}</div>
    <div class="top5-date">🕰 &nbsp;{item['date']}</div>
  </div>
  <div class="score-wrap">
    <span class="score-label">注目度</span>
    <div class="score-bar-bg"><div class="score-bar-fill" style="width:{item['_pct']}%"></div></div>
    <span class="score-pct">{item['_pct']}%</span>
  </div>
</a>"""
    return rows_html


@st.fragment(run_every=_TOP5_INTERVAL)
def render_top5(q: str, l: str, c: str) -> None:
    arts = fetch_news_articles(q, l, c)
    if not arts:
        return
    top5        = get_top5(arts)
    updated_str = datetime.now().strftime("%H:%M 更新")
    st.markdown(f"""
<div class="top5-section">
  <div class="top5-header">
    <div class="top5-header-title">✦ &nbsp;今注目すべき AI ニュース&nbsp; TOP 5&nbsp; ✦</div>
    <div class="top5-header-time">🕐 &nbsp;{updated_str}</div>
  </div>
  {_build_top5_html(top5)}
</div>
""", unsafe_allow_html=True)


@st.fragment(run_every=_TOP5_INTERVAL)
def render_top5_info() -> None:
    arts = get_info_articles([src["id"] for src in INFO_SOURCES])
    if not arts:
        return
    top5        = get_top5(arts)
    updated_str = datetime.now().strftime("%H:%M 更新")
    st.markdown(f"""
<div class="top5-section">
  <div class="top5-header">
    <div class="top5-header-title">✦ &nbsp;今注目すべき AI 情報&nbsp; TOP 5&nbsp; ✦</div>
    <div class="top5-header-time">🕐 &nbsp;{updated_str}</div>
  </div>
  {_build_top5_html(top5)}
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  コンテンツ自動更新フラグメント（6時間）
# ─────────────────────────────────────────────

_CONTENT_INTERVAL = 21600  # 6時間


@st.fragment(run_every=_CONTENT_INTERVAL)
def render_news_content(q: str, l: str, c: str) -> None:
    with st.spinner("館内を検索しています…"):
        articles = fetch_news_articles(q, l, c)

    if not articles:
        st.warning("記事が見つかりませんでした。別のキーワードをお試しください。")
        return

    n_cat_names  = list(CATEGORY_KEYWORDS.keys())
    n_cat_counts = {cat: len(filter_by_category(articles, cat)) for cat in n_cat_names}
    if st.session_state.get("active_news_category") not in n_cat_names:
        st.session_state.active_news_category = n_cat_names[0]

    category = st.radio(
        "ニュースカテゴリ",
        options=n_cat_names,
        format_func=lambda cat: f"{cat}  {n_cat_counts[cat]}件",
        horizontal=True,
        label_visibility="collapsed",
        key="active_news_category",
    )

    cat_key  = CAT_KEYS[category]
    page_key = f"news_page_{cat_key}"
    if page_key not in st.session_state:
        st.session_state[page_key] = 0

    filtered = filter_by_category(articles, category)

    if not filtered:
        st.markdown(
            '<p style="color:#5a4030; font-size:0.85rem; padding:12px 0;">該当する記事はありません。</p>',
            unsafe_allow_html=True,
        )
        return

    total_c       = len(filtered)
    total_pages_c = max(1, (total_c + CARDS_PER_PAGE - 1) // CARDS_PER_PAGE)
    ipage         = min(st.session_state[page_key], total_pages_c - 1)
    st.session_state[page_key] = ipage
    istart        = ipage * CARDS_PER_PAGE
    iend          = istart + CARDS_PER_PAGE

    st.markdown(
        f'<p class="count-text">全 <strong>{total_c}</strong> 件 &nbsp;｜&nbsp; '
        f'<strong>{istart+1}</strong>–<strong>{min(iend, total_c)}</strong> 件を表示</p>',
        unsafe_allow_html=True,
    )

    left_col, right_col = st.columns(2, gap="medium")
    for i, article in enumerate(filtered[istart:iend]):
        col  = left_col if i % 2 == 0 else right_col
        img  = article["image"]
        num  = istart + i + 1
        icon = SHELF_ICONS[(istart + i) % len(SHELF_ICONS)]
        img_html = (
            f'<div class="card-img-wrap">'
            f'<img src="{img}" alt="" loading="lazy" '
            f'onerror="this.parentElement.innerHTML=\'<div class=\\"card-img-placeholder\\"><div class=\\"ph-icon\\">{icon}</div></div>\'">'
            f'<span class="card-img-badge">AI NEWS</span></div>'
            if img else
            f'<div class="card-img-wrap"><div class="card-img-placeholder"><div class="ph-icon">{icon}</div></div>'
            f'<span class="card-img-badge">AI NEWS</span></div>'
        )
        col.markdown(f"""
<a href="{article['link']}" target="_blank" class="news-card">
  {img_html}
  <div class="card-body">
    <p class="card-title">{article['title']}</p>
    <p class="card-date">🕰 &nbsp;{article['date']}</p>
    <p class="card-summary">{article['summary']}</p>
    <div class="card-footer">
      <span class="card-read-btn">↗ 元記事を開く</span>
      <span class="card-num">No. {num:03d}</span>
    </div>
  </div>
</a>
""", unsafe_allow_html=True)

    render_divider()
    pag_l, pag_c, pag_r = st.columns([2, 3, 2])
    with pag_l:
        if st.button("◀　前のページ", key=f"news_prev_{cat_key}",
                     disabled=(ipage == 0), use_container_width=True):
            st.session_state[page_key] -= 1
            st.rerun()
    with pag_c:
        st.markdown(
            f'<div class="pagination-wrap"><span class="page-info">'
            f'<strong>{ipage+1}</strong> / {total_pages_c}</span></div>',
            unsafe_allow_html=True,
        )
    with pag_r:
        if st.button("次のページ　▶", key=f"news_next_{cat_key}",
                     disabled=(ipage >= total_pages_c - 1), use_container_width=True):
            st.session_state[page_key] += 1
            st.rerun()


@st.fragment(run_every=_CONTENT_INTERVAL)
def render_info_content(selected_ids: list) -> None:
    with st.spinner("各ソースから情報を収集しています…"):
        info_articles = get_info_articles(selected_ids)

    if not info_articles:
        st.warning("記事が見つかりませんでした。しばらく経ってから再取得してください。")
        return

    cat_names  = list(CATEGORY_KEYWORDS.keys())
    cat_counts = {cat: len(filter_by_category(info_articles, cat)) for cat in cat_names}
    if st.session_state.get("active_info_category") not in cat_names:
        st.session_state.active_info_category = cat_names[0]

    category = st.radio(
        "情報カテゴリ",
        options=cat_names,
        format_func=lambda cat: f"{cat}  {cat_counts[cat]}件",
        horizontal=True,
        label_visibility="collapsed",
        key="active_info_category",
    )

    cat_key  = CAT_KEYS[category]
    page_key = f"info_page_{cat_key}"
    if page_key not in st.session_state:
        st.session_state[page_key] = 0

    filtered = filter_by_category(info_articles, category)

    if not filtered:
        st.markdown(
            '<p style="color:#5a4030; font-size:0.85rem; padding:12px 0;">該当する記事はありません。</p>',
            unsafe_allow_html=True,
        )
        return

    total_c       = len(filtered)
    total_pages_c = max(1, (total_c + CARDS_PER_PAGE - 1) // CARDS_PER_PAGE)
    ipage         = min(st.session_state[page_key], total_pages_c - 1)
    st.session_state[page_key] = ipage
    istart        = ipage * CARDS_PER_PAGE
    iend          = istart + CARDS_PER_PAGE

    st.markdown(
        f'<p class="count-text">全 <strong>{total_c}</strong> 件 &nbsp;｜&nbsp; '
        f'<strong>{istart+1}</strong>–<strong>{min(iend, total_c)}</strong> 件を表示</p>',
        unsafe_allow_html=True,
    )

    lcol, rcol = st.columns(2, gap="medium")
    for i, art in enumerate(filtered[istart:iend]):
        col = lcol if i % 2 == 0 else rcol
        num = istart + i + 1
        author_part = f'✍ {art["author"]} &nbsp;｜&nbsp; ' if art.get("author") else ""
        col.markdown(f"""
<a href="{art['link']}" target="_blank" class="info-card">
  <div class="info-src-header"
       style="background:{art['source_bg']};">
    <span class="info-src-icon">{art['source_icon']}</span>
    <span class="info-src-label" style="color:{art['source_color']};">{art['source_label']}</span>
  </div>
  <div class="card-body">
    <p class="card-title">{art['title']}</p>
    <p class="card-date">{author_part}🕰 &nbsp;{art['date']}</p>
    <p class="card-summary">{art['summary']}</p>
    <div class="card-footer">
      <span class="card-read-btn">↗ 記事を開く</span>
      <span class="card-num">No. {num:03d}</span>
    </div>
  </div>
</a>
""", unsafe_allow_html=True)

    render_divider()
    p_l, p_c, p_r = st.columns([2, 3, 2])
    with p_l:
        if st.button("◀　前のページ", key=f"prev_{cat_key}",
                     disabled=(ipage == 0), use_container_width=True):
            st.session_state[page_key] -= 1
            st.rerun()
    with p_c:
        st.markdown(
            f'<div class="pagination-wrap"><span class="page-info">'
            f'<strong>{ipage+1}</strong> / {total_pages_c}</span></div>',
            unsafe_allow_html=True,
        )
    with p_r:
        if st.button("次のページ　▶", key=f"next_{cat_key}",
                     disabled=(ipage >= total_pages_c - 1), use_container_width=True):
            st.session_state[page_key] += 1
            st.rerun()


# ─────────────────────────────────────────────
#  共通：ヘッダーバナー描画
# ─────────────────────────────────────────────

def render_hero(title: str, subtitle: str, ornament: str) -> None:
    books_svg = "".join([
        f'<rect x="{10+i*22}" y="{15+(i%5)*12}" width="{14+(i%3)*4}" '
        f'height="{130-(i%4)*15}" rx="2" fill="#c9a96e" opacity="{0.12+(i%4)*0.04}"/>'
        for i in range(25)
    ])
    st.markdown(f"""
<div class="hero-banner">
  <svg class="hero-shelf" viewBox="0 0 600 180" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="xMaxYMid slice">
    {books_svg}
    <line x1="0" y1="155" x2="600" y2="155" stroke="#c9a96e" stroke-width="1.5" opacity="0.15"/>
  </svg>
  <div class="hero-text">
    <div class="hero-title">{title}</div>
    <div class="hero-sub">{subtitle}</div>
  </div>
  <div class="hero-ornament">{ornament}</div>
</div>
""", unsafe_allow_html=True)


def render_divider() -> None:
    st.markdown(
        '<div class="ornament-divider"><div class="line"></div>'
        '<div class="symbol">✦</div><div class="line"></div></div>',
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────
#  サイドバー
# ─────────────────────────────────────────────
with st.sidebar:
    # ロゴ
    st.markdown("""
<div style="text-align:center; padding:18px 0 10px; border-bottom:1px solid #2e1f14; margin-bottom:16px;">
  <svg width="52" height="44" viewBox="0 0 52 44" fill="none" xmlns="http://www.w3.org/2000/svg">
    <rect x="2"  y="6"  width="7"  height="32" rx="1.5" fill="#c9a96e" opacity="0.85"/>
    <rect x="11" y="10" width="5"  height="28" rx="1.5" fill="#a67c52" opacity="0.9"/>
    <rect x="18" y="4"  width="9"  height="34" rx="1.5" fill="#c9a96e" opacity="0.7"/>
    <rect x="29" y="8"  width="6"  height="30" rx="1.5" fill="#8a5c38" opacity="0.9"/>
    <rect x="37" y="12" width="8"  height="26" rx="1.5" fill="#c9a96e" opacity="0.8"/>
    <rect x="47" y="7"  width="3"  height="31" rx="1.5" fill="#a67c52" opacity="0.75"/>
    <line x1="0" y1="38.5" x2="52" y2="38.5" stroke="#c9a96e" stroke-width="1.5" opacity="0.4"/>
  </svg>
  <div style="font-family:'Cormorant Garamond',serif; font-size:1.1rem; color:#c9a96e; letter-spacing:0.15em; margin-top:6px;">THE LIBRARY</div>
  <div style="font-size:0.68rem; color:#4a3520; letter-spacing:0.12em; margin-top:2px;">AI NEWS ARCHIVE</div>
</div>
""", unsafe_allow_html=True)

    # ── ナビゲーション ──
    st.markdown('<p style="font-size:0.72rem; color:#4a3520; letter-spacing:0.10em; margin:0 0 6px 4px;">NAVIGATION</p>', unsafe_allow_html=True)
    nav_choice = st.radio(
        "nav",
        options=["📰  AI ニュース", "💡  AI 情報", "🗂  Obsidian 出力"],
        key="nav_radio",
        label_visibility="collapsed",
    )
    nav_page = (
        "news"         if "ニュース" in nav_choice else
        "obsidian"     if "Obsidian" in nav_choice else
        "info"
    )

    st.markdown('<hr style="border-color:#2e1f14; margin:14px 0;">', unsafe_allow_html=True)

    # ── 条件分岐：ページ別設定 ──
    if nav_page == "news":
        st.markdown('<p style="font-size:0.78rem; color:#5a4030; letter-spacing:0.08em; margin-bottom:6px;">— 検索キーワード</p>', unsafe_allow_html=True)
        search_query = st.text_input(
            "検索キーワード", value="生成AI OR AI OR 人工知能",
            placeholder="例：機械学習、ChatGPT ...",
            label_visibility="collapsed", key="news_query_input",
        )
        st.markdown('<p style="font-size:0.78rem; color:#5a4030; letter-spacing:0.08em; margin:12px 0 6px;">— 言語設定</p>', unsafe_allow_html=True)
        lang_opt = st.selectbox(
            "言語設定", options=["日本語 (ja/JP)", "English (en/US)", "English (en/GB)"],
            label_visibility="collapsed", key="news_lang_select",
        )
        lang_map  = {"日本語 (ja/JP)": ("ja","JP"), "English (en/US)": ("en","US"), "English (en/GB)": ("en","GB")}
        lang, country = lang_map[lang_opt]
        st.markdown("<br>", unsafe_allow_html=True)
        search_btn = st.button("📚　記事を検索する", use_container_width=True)
    else:
        selected_sources = [src["id"] for src in INFO_SOURCES]  # 全ソース有効
        search_btn  = False
        lang, country = "ja", "JP"
        search_query  = ""
        if nav_page == "info":
            st.markdown("""
<div style="font-size:0.72rem; color:#4a3520; line-height:1.9; letter-spacing:0.05em;">
  <div style="color:#7a5535; margin-bottom:6px;">📡 収集ソース</div>
  note / Zenn / Qiita / はてな<br>
  arXiv / X・SNS / ブログ / 開発ツール<br>
  エージェント / 生成AI / HW<br><br>
  <div style="color:#7a5535; margin-bottom:4px;">🗂 カテゴリ</div>
  GPT / Gemini / Grok / Claude<br>
  AIエージェント / 地方自治体 / 企業<br>
  AI開発ツール / AI論文 / ゲーム開発 / アプリ開発<br>
  AI作曲 / AI画像生成 / AI動画 / 動画編集 / AI音声<br>
  ローカルLLM / AI業務自動化 / AI教育・研修 / AIセキュリティ<br>
  3D / アバター<br>
  LLM / MCP<br>
  ハードウェア / オープンソース / HuggingFace<br>
  その他
</div>
""", unsafe_allow_html=True)
        elif nav_page == "obsidian":
            st.markdown(f"""
<div style="font-size:0.72rem; color:#4a3520; line-height:1.9; letter-spacing:0.05em;">
  <div style="color:#7a5535; margin-bottom:6px;">🗂 Obsidian 出力</div>
  収集記事をカテゴリ別・テーマ別に整理し、<br>
  note記事ドラフトまでMarkdown保存します。<br><br>
  保存先<br>
  <span style="color:#c9a96e;">{OBSIDIAN_VAULT_DIR}</span>
</div>
""", unsafe_allow_html=True)

    # 館内案内
    st.markdown("""
<div style="margin-top:20px; padding-top:16px; border-top:1px solid #2e1f14;
     font-size:0.70rem; color:#3a2a1a; line-height:2.1; letter-spacing:0.06em;">
  <div style="color:#5a4030; margin-bottom:4px;">ℹ️ 館内案内</div>
  データソース｜Google News / RSS<br>
  取得上限 ｜100件<br>
  表示件数 ｜10件 / ページ<br>
  TOP5更新 ｜12時間ごと自動
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  セッション管理
# ─────────────────────────────────────────────
if "query"              not in st.session_state: st.session_state.query              = "生成AI OR AI OR 人工知能"
if "lang"               not in st.session_state: st.session_state.lang               = "ja"
if "country"            not in st.session_state: st.session_state.country            = "JP"
if "page"               not in st.session_state: st.session_state.page               = 0
if "info_page"          not in st.session_state: st.session_state.info_page          = 0
if "prev_nav"           not in st.session_state: st.session_state.prev_nav           = "news"
if "kw_viewing_date"    not in st.session_state: st.session_state.kw_viewing_date    = datetime.now().strftime("%Y-%m-%d")
if "kw_calendar_month"  not in st.session_state: st.session_state.kw_calendar_month  = datetime.now().strftime("%Y-%m")

# ページ切り替え時にページ番号リセット
if nav_page != st.session_state.prev_nav:
    for _k in list(st.session_state.keys()):
        if _k.startswith("news_page_") or _k.startswith("info_page_"):
            st.session_state[_k] = 0
    st.session_state.prev_nav = nav_page

if nav_page == "news" and search_btn:
    changed = (search_query != st.session_state.query
               or lang    != st.session_state.lang
               or country != st.session_state.country)
    if changed:
        for _k in list(st.session_state.keys()):
            if _k.startswith("news_page_"):
                st.session_state[_k] = 0
    st.session_state.query   = search_query
    st.session_state.lang    = lang
    st.session_state.country = country

cur_q = st.session_state.query
cur_l = st.session_state.lang
cur_c = st.session_state.country


# ═══════════════════════════════════════════════
#  メインコンテンツ：AI ニュースページ
# ═══════════════════════════════════════════════
if nav_page == "news":

    render_hero("AI ニュース収集ダッシュボード", "Intelligence · Curated · Daily", "📰")

    col_badge, col_refresh = st.columns([5, 1])
    with col_badge:
        st.markdown(f'<div class="search-badge">🔎 &nbsp;{cur_q}</div>', unsafe_allow_html=True)
    with col_refresh:
        if st.button("🔄 再取得", key="news_refresh"):
            st.cache_data.clear()
            for _k in list(st.session_state.keys()):
                if _k.startswith("news_page_"):
                    st.session_state[_k] = 0
            st.rerun()

    render_divider()

    # TOP5（自動更新フラグメント）
    render_top5(cur_q, cur_l, cur_c)
    render_divider()

    # 記事一覧（6時間ごと自動更新フラグメント）
    render_news_content(cur_q, cur_l, cur_c)


# ═══════════════════════════════════════════════
#  メインコンテンツ：AI 情報ページ
# ═══════════════════════════════════════════════
elif nav_page == "info":

    render_hero("AI 情報アーカイブ", "GPT · Claude · ローカルLLM · 開発 · 3D · アバター", "💡")

    col_badge2, col_refresh2, col_deep2 = st.columns([4, 1, 1])
    with col_badge2:
        st.markdown('<div class="search-badge">📡 &nbsp;全ソースから収集中</div>', unsafe_allow_html=True)
    with col_refresh2:
        if st.button("🔄 軽く更新", key="info_refresh"):
            try:
                clear_info_rss_cache()
            except Exception:
                st.cache_data.clear()
            st.rerun()
    with col_deep2:
        if st.button("🧭 深く更新", key="info_deep_refresh"):
            with st.spinner("本文確認用に深く更新中…"):
                try:
                    clear_info_rss_cache()
                    fetch_article_body.clear()
                except Exception:
                    st.cache_data.clear()
                _ = get_info_articles([src["id"] for src in INFO_SOURCES], deep=True)
            st.success("深い更新が完了しました。Obsidian出力に使えます。")

    render_divider()

    # TOP5（自動更新フラグメント）
    render_top5_info()
    render_divider()

    # 記事一覧（6時間ごと自動更新フラグメント）
    render_info_content(selected_sources)


# ═══════════════════════════════════════════════
#  メインコンテンツ：Obsidian 出力ページ
# ═══════════════════════════════════════════════
elif nav_page == "obsidian":

    render_hero("Obsidian 出力", "Collect · Categorize · Summarize · Draft", "🗂")

    st.markdown(f'<div class="search-badge">📁 &nbsp;{OBSIDIAN_VAULT_DIR}</div>', unsafe_allow_html=True)
    render_divider()

    st.markdown("""
<div style="color:#ffffff; line-height:1.9; font-size:0.92rem;">
  <p>AIニュース・AI情報をObsidian用Markdownに変換します。</p>
  <p>カテゴリ別ニュース、テーマ別まとめ、note記事ドラフト、テンプレートを指定フォルダに保存します。</p>
</div>
""", unsafe_allow_html=True)

    st.markdown("""
<div style="color:#ffffff; line-height:1.8; font-size:0.86rem;">
  文章生成・分類・要約はOllama gemma4を優先します。Ollamaに接続できない場合のみ、ルールベース生成で補完します。
</div>
""", unsafe_allow_html=True)

    col_setup, col_export = st.columns([1, 1])
    with col_setup:
        if st.button("フォルダとテンプレートを作成", key="obs_setup", use_container_width=True):
            try:
                result = ensure_obsidian_vault(OBSIDIAN_VAULT_DIR)
                st.success(f"作成しました: {result['base_dir']}")
            except Exception as e:
                st.error(f"作成に失敗しました: {e}")

    with col_export:
        if st.button("今日の素材をObsidianに出力", key="obs_export", use_container_width=True):
            progress_bar = st.progress(0)
            progress_text = st.empty()

            def update_obs_progress(percent: int, message: str):
                progress_bar.progress(max(0, min(100, percent)))
                progress_text.markdown(f"<div class='kw-text'>進捗 {percent}%｜{message}</div>", unsafe_allow_html=True)

            update_obs_progress(2, "準備中…")
            with st.spinner("ニュース収集・分類・Markdown生成中…"):
                try:
                    result = export_obsidian_pipeline(OBSIDIAN_VAULT_DIR, progress_cb=update_obs_progress)
                    st.success("Obsidian出力が完了しました。")
                    st.markdown(f"""
<div class="kw-idea-card">
  <div class="kw-idea-body">
    <div class="kw-section-title">出力先</div>
    <div class="kw-text">{result['base_dir']}</div>
    <div class="kw-section-title">収集件数</div>
    <div class="kw-text">AIニュース {result['news_count']} 件 / AI情報 {result['info_count']} 件</div>
    <div class="kw-section-title">生成ファイル</div>
    <div class="kw-text">カテゴリ別 {result['source_files']} 件 / ニュース個別 {result['item_files']} 件 / fact {result['fact_files']} 件 / 仮説 {result['hypothesis_files']} 件 / テーマ別 {result['summary_files']} 件 / トレンド {result['trend_files']} 件 / 記事ドラフト {result['draft_files']} 件 / 完成候補 {result['article_files']} 件 / AI Note {result['ai_note_files']} 件 / arXiv {result['arxiv_files']} 件 / ログ {result['log_files']} 件</div>
    <div class="kw-section-title">処理ログ</div>
    <div class="kw-text">本文取得失敗 {result['body_failed_count']} 件 / 除外 {result['excluded_count']} 件<br>{result['log']}</div>
    <div class="kw-section-title">ドラフト生成</div>
    <div class="kw-text">{result['draft_method']}</div>
  </div>
</div>
""", unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"出力に失敗しました: {e}")

    render_divider()

    st.markdown("""
<div style="color:#ffffff; line-height:1.9; font-size:0.86rem;">
  <strong>生成される構成</strong><br>
  00_Inbox / 01_News_Sources / 02_Theme_Summaries / 03_Article_Drafts / 04_Published / 05_fact / 06_hypothesis / 07_trend / 08_article / 09_AI_Note / 10_arXiv / 11_Logs / 99_Templates
</div>
""", unsafe_allow_html=True)

    render_divider()

    st.markdown("""
<div style="color:#ffffff; line-height:1.9; font-size:0.92rem;">
  <strong>アプリ内で読む</strong><br>
  生成済みのMarkdownをここで確認できます。
</div>
""", unsafe_allow_html=True)

    date_options = _obsidian_date_options(OBSIDIAN_VAULT_DIR)
    if date_options:
        default_date = datetime.now().strftime("%Y-%m-%d")
        default_index = date_options.index(default_date) if default_date in date_options else 0
        read_col1, read_col2 = st.columns([1, 1])
        with read_col1:
            read_section = st.selectbox(
                "読む種類",
                ["AI Note", "完成候補記事", "記事ドラフト", "テーマ別まとめ", "fact", "仮説", "トレンド", "arXiv", "ログ", "ニュースソース", "Inbox"],
                key="obs_read_section",
            )
        with read_col2:
            read_date = st.selectbox(
                "日付",
                date_options,
                index=default_index,
                key="obs_read_date",
            )

        md_files = _obsidian_files_for_view(OBSIDIAN_VAULT_DIR, read_section, read_date)
        if md_files:
            labels = [
                _relative_obsidian_path(path, OBSIDIAN_VAULT_DIR)
                for path in md_files
            ]
            selected_label = st.selectbox("Markdownファイル", labels, key="obs_read_file")
            selected_path = md_files[labels.index(selected_label)]
            st.markdown(f'<div class="search-badge">📄 &nbsp;{html.escape(selected_label)}</div>', unsafe_allow_html=True)
            with st.expander("Markdown原文を表示", expanded=False):
                st.code(_read_markdown_preview(selected_path), language="markdown")
            st.markdown(_read_markdown_preview(selected_path), unsafe_allow_html=False)
        else:
            st.info("この条件のMarkdownはまだありません。")
    else:
        st.info("まだ出力済みMarkdownがありません。先に「今日の素材をObsidianに出力」を押してください。")


# ─────────────────────────────────────────────
#  フッター（共通）
# ─────────────────────────────────────────────
st.markdown("""
<div class="library-footer">
  <span class="footer-ornament">— ✦ —</span>
  AI News Gathering Dashboard &nbsp;｜&nbsp; Powered by Google News RSS &amp; Streamlit
</div>
""", unsafe_allow_html=True)
