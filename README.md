# AI News Gathering Dashboard

AI関連ニュース、技術記事、arXiv論文、自治体・企業のAI活用情報をまとめて収集し、Obsidian用Markdownとして整理できるデスクトップアプリです。

Python環境を別途用意しなくても、Windows用インストーラーを実行するだけで使えます。

## 主な機能

- AIニュースをGoogle News RSSから収集
- note / Zenn / Qiita / はてな / 技術ブログ / X検索 / arXiv などからAI情報を収集
- AI情報をカテゴリ別に表示
- arXivのAI論文カテゴリは、今日新しく公開・更新された論文だけを表示
- 地方自治体、企業、AIエージェント、ローカルLLM、AI画像生成、AI動画、AI音声、ゲーム開発、3D、アバター、AI論文などのカテゴリに対応
- リンク先本文を取得し、Obsidian用Markdownに変換
- カテゴリ別・テーマ別まとめMarkdownを生成
- まとめMarkdownをもとに、note向けの記事ドラフトを生成
- アプリ内で生成済みMarkdownを確認
- 文章生成は無料のローカルLLMであるOllamaの `gemma4` を優先利用
- Ollamaに接続できない場合はルールベース生成に自動退避

## インストール

Releases から最新版の `AI-News-Dashboard-Setup-*.exe` をダウンロードして実行してください。

既に旧バージョンをインストールしている場合は、同じアプリとしてアップデートされます。古いアプリ本体は新しいバージョンに置き換わります。

初回起動時にWindows Defenderの警告が表示される場合があります。個人開発の未署名アプリのためです。

1. 「詳細情報」をクリック
2. 「実行」をクリック
3. インストールウィザードに従ってインストール

## 起動方法

インストール後、以下のいずれかで起動できます。

- デスクトップショートカット
- スタートメニューの `AI News Dashboard`
- インストールフォルダ内の `AI News Dashboard.exe`

アプリ起動後、内部でStreamlitサーバーが立ち上がり、Electronウィンドウ内にダッシュボードが表示されます。

ローカルURLは以下です。

```text
http://localhost:8501
```

## 画面構成

### AI ニュース

Google News RSSからAI関連ニュースを収集します。

- 検索キーワード指定
- 日本語 / 英語ニュース切替
- TOP 5表示
- カテゴリタブ
- ページネーション
- サムネイル付きカード表示

### AI 情報

AI関連の技術情報、活用事例、開発者向け記事、arXiv論文を収集します。

主な収集対象:

- note
- Zenn
- Qiita
- はてな
- arXiv
- X / SNS検索
- 技術ブログ
- 開発ツール関連情報
- 自治体・行政DX情報
- 企業のAI活用情報
- ローカルLLM / OSS / ハードウェア情報

主なカテゴリ:

- GPT
- Gemini
- Grok
- Claude
- AIエージェント
- 地方自治体
- 企業
- AI開発ツール
- AI論文
- AI画像生成
- AI動画
- 動画編集
- AI音声
- ローカルLLM
- AI業務自動化
- AI教育・研修
- AIセキュリティ
- ゲーム開発
- アプリ開発
- 3D
- アバター
- LLM
- MCP
- ハードウェア
- オープンソース
- HuggingFace
- その他

### Obsidian 出力

収集した記事をObsidian用Markdownとして保存します。

保存時に行うこと:

- 取得済み記事をカテゴリ分類
- リンク先本文を取得
- 1記事ごとのMarkdownを作成
- カテゴリ別Markdownを作成
- テーマ別まとめMarkdownを作成
- note記事風ドラフトを作成
- 生成済みMarkdownをアプリ内で閲覧

保存先:

```text
D:\新しいフォルダー (4)\notevalt
```

フォルダ構成:

```text
notevalt
├─ 00_Inbox
├─ 01_News_Sources
├─ 02_Theme_Summaries
├─ 03_Article_Drafts
├─ 04_Published
└─ 99_Templates
```

日付ごとに以下のような階層で保存されます。

```text
01_News_Sources
└─ 2026
   └─ 06
      └─ 16
         ├─ AIエージェント
         ├─ 地方自治体
         ├─ AI論文
         └─ ...
```

## Ollamaについて

記事ドラフトや要約生成では、ローカルLLMのOllama `gemma4` を優先して使います。

Ollamaを使う場合:

```powershell
ollama pull gemma4
ollama serve
```

Ollamaが起動していない場合でも、アプリはルールベース生成に切り替えて動作します。

## 開発者向け

ソースからStreamlitとして起動する場合:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

ローカルでElectron版を起動する場合:

```powershell
npm install
npm run start
```

Windowsインストーラーを作成する場合:

```powershell
npm install
npm run dist
```

ビルド時は `resources/python-dist` 相当のPythonランタイムを `buildResources/python-dist` または既存インストール済みアプリのランタイムから取り込む構成です。

## バージョン

現在のバージョン: `1.1.0`

## 技術スタック

- Streamlit
- feedparser
- Ollama
- arXiv RSS
- Google News RSS
- Electron
- electron-builder

