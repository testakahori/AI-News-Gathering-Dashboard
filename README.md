# 📚 AI ニュース収集ダッシュボード

> Google News RSS・note・Zenn・Qiita などからAI関連情報をリアルタイム収集し、  
> ダークテーマの美しいダッシュボードで表示するデスクトップアプリです。

![Streamlit](https://img.shields.io/badge/Streamlit-1.54.0-FF4B4B?style=flat&logo=streamlit)
![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=flat&logo=python)
![Platform](https://img.shields.io/badge/Platform-Windows-0078D4?style=flat&logo=windows)

---

## 📥 ダウンロード・インストール

**Python不要。インストーラーをダブルクリックするだけで使えます。**

1. [**Releases**](../../releases/latest) を開く
2. `AI-News-Dashboard-Setup.exe` をダウンロード
3. ダブルクリック → インストールウィザードに従う
4. 完了後「アプリを起動する」にチェックを入れてFinish

> **⚠️ Windows Defenderの警告について**
> 初回起動時に「WindowsによってPCが保護されました」と表示される場合があります。
> 「詳細情報」→「実行」をクリックしてください。（署名なしの個人開発アプリのため）
>
> 🛡️ **VirusTotal スキャン結果: [0 / 67 — 全社クリア](https://www.virustotal.com/gui/file/bed0c12ebadac28aea34b240a2cae467031cd105d10332f507aca6e4699fb3c2/detection)**
> 67社のセキュリティエンジンすべてで脅威なしと判定されています。

---

## 🖥️ 起動方法

インストール後は以下のいずれかで起動できます：

- **デスクトップのショートカット**をダブルクリック
- スタートメニューから「AI ニュース収集ダッシュボード」を検索

起動すると自動でブラウザが開き、ダッシュボードが表示されます。  
アドレスは `http://localhost:8501` です。

---

## 🗺️ 画面の説明

サイドバーのメニューで3つのページを切り替えられます。

### 📰 AIニュース

Google News RSSからAI関連ニュースをリアルタイム収集して表示します。

| 機能 | 詳細 |
|------|------|
| 検索キーワード | 任意のキーワードで記事を絞り込み |
| 言語切替 | 日本語（ja/JP）・英語（en/US, en/GB）に対応 |
| TOP 5 | スコアリングで注目記事をランキング表示（5分ごと自動更新） |
| ページネーション | 10件ずつ表示、最大100件取得 |
| カードUI | サムネイル画像付き・クリックで元記事を開く |

**🔄 再取得ボタン**でキャッシュをクリアして最新情報を取得できます。

---

### 🤖 AI情報

開発者・研究者向けの技術情報を10ソースから収集します。

**収集ソース：**  
note / Zenn / Qiita / はてなブログ / X(Twitter) / 各種技術ブログ

**カテゴリタブ：**

| タブ | 内容 |
|------|------|
| GPT | OpenAI・ChatGPT関連 |
| Claude | Anthropic・Claude関連 |
| AI作曲 | Suno / Udio など音楽生成AI |
| AI動画 | Sora / Runway など動画生成AI |
| AI音声 | ElevenLabs など音声合成AI |
| ローカル環境 | Ollama・LM Studioなどローカル実行 |
| その他 | 上記以外のAI関連情報 |

---

### 📋 日報

毎日深夜0時に自動で生成されるAIニュースの日報です。

**サイドバーのミニカレンダー**で過去の日報を閲覧できます。  
日報が存在する日付はボタン表示、存在しない日はグレーで表示されます。

**日報の構成：**

```
## 今日のAI概況      ← その日の全体的な流れ
## 主な動き          ← トピックごとの解説 + 元記事要約カード
## 今日の注目        ← 最重要トピックの深掘り
## 編集後記          ← 一日の振り返り
```

#### 生成方式の切り替え

| 方式 | 品質 | 必要なもの |
|------|------|-----------|
| アルゴリズム生成 | ★★★　無料 | 何も不要 |
| Claude API生成 | ★★★★★ 高精度 | Anthropic APIキー |

Claude APIを使うには、サイドバーの「Anthropic APIキー」欄に `sk-ant-` から始まるキーを入力してください。  
APIキーは [Anthropic Console](https://console.anthropic.com/) から取得できます。

**「🔄 再生成」ボタン**でいつでも最新の記事をもとに日報を作り直せます。

---

## 📁 データの保存場所

インストールフォルダ内に自動作成されます（デフォルト: `C:\Program Files\AI-News-Dashboard\`）

```
AI-News-Dashboard\
├── AI-News-Dashboard.exe
├── daily_reports\    ← 日報データ（JSON）
└── archives\         ← アーカイブ
```

日報データはアンインストールしても残ります。

---

## 🛠️ ソースから起動する（開発者向け）

```bash
# Python 3.10以上が必要
pip install -r requirements.txt
streamlit run app.py
```

---

## 🔧 技術スタック

- [Streamlit](https://streamlit.io/) — UIフレームワーク
- [feedparser](https://feedparser.readthedocs.io/) — RSS取得・解析
- [Anthropic API](https://www.anthropic.com/) — 日報のAI生成（任意）
- Google News RSS — ニュースソース
- PyInstaller + Inno Setup — Windows実行ファイル化

---

## 📝 著作権

© 2026 testakahori. All Rights Reserved.
