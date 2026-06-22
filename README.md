# AI News Dashboard

AIニュース、技術記事、note、ブログ、arXiv論文を収集し、Obsidianで記事化しやすいMarkdown素材へ整理するローカル専用ダッシュボードです。

## 主な機能

- AIニュースをGoogle News RSSから収集
- AI情報をnote、Zenn、Qiita、技術ブログ、公式情報、arXivから収集
- AI情報は初心者向けすぎる記事、日記、ポエム、小説生成だけの記事、内容の薄い宣伝記事を除外
- arXivは今日新しく公開されたAI関連論文のみをAI論文カテゴリに表示
- Obsidian出力時にリンク先本文を取得し、冒頭抜粋ではなく本文内容をもとに要約
- Ollama `gemma4` で分類、要約、fact、hypothesis、trend、AI Note、記事ドラフトを生成
- 外部有料API、Gemini API、Anthropic APIは不要
- 生成済みMarkdownをアプリ内で閲覧可能

## 起動方法

インストール後、以下のいずれかで起動できます。

- デスクトップショートカットをダブルクリック
- スタートメニューから `AI News Dashboard` を起動
- 開発用フォルダでは `run_app.bat` をダブルクリック

起動後、ブラウザで次のURLが開きます。

```text
http://localhost:8501
```

## 画面

- `AI ニュース`: AI関連ニュースを収集、検索、カテゴリ表示します。
- `AI 情報`: note、技術ブログ、arXivなどからAI活用・開発情報を収集します。
- `Obsidian 出力`: 収集済み素材をObsidian Vault向けMarkdownとして保存し、生成結果をアプリ内で確認できます。

## Obsidian Vault

保存先は次のフォルダです。

```text
D:\新しいフォルダー (4)\notevalt
```

想定フォルダ構成:

```text
00_Inbox
01_News_Sources
02_Theme_Summaries
03_Article_Drafts
04_Published
05_fact
06_hypothesis
07_trend
08_article
09_AI_Note
10_arXiv
11_Logs
99_Templates
```

日付管理するフォルダ:

- `01_News_Sources`
- `05_fact`
- `06_hypothesis`
- `09_AI_Note`
- `10_arXiv`
- `11_Logs`

テーマ単位で育てるフォルダ:

- `07_trend`

記事タイトル単位で保存するフォルダ:

- `08_article`

## Obsidian出力で生成されるもの

- `01_News_Sources`: 1記事1Markdownのニュース本文・要約
- `02_Theme_Summaries`: その日に見つかった記事化候補テーマの整理
- `05_fact`: 事実だけを抽出したMarkdown
- `06_hypothesis`: factを根拠にした仮説Markdown
- `07_trend`: テーマごとの長期トレンド更新
- `09_AI_Note`: 今日の注目テーマ、起きたこと、見えた変化、投稿ネタ候補
- `10_arXiv`: 今日新規公開されたAI関連論文
- `11_Logs`: 本文取得失敗、除外理由、Ollamaエラー、生成ファイル一覧
- `03_Article_Drafts` / `08_article`: note向けの記事下書き・完成候補

## Ollama

文章生成、分類、要約、記事生成はローカルのOllama `gemma4` を使います。

```powershell
ollama pull gemma4
ollama serve
```

Ollamaに接続できない場合、一部処理はルールベースで補完しますが、記事生成や高品質要約には `gemma4` の利用を推奨します。

## 開発者向け

手動で起動する場合:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

## 技術スタック

- Streamlit
- feedparser
- requests / BeautifulSoup
- Ollama gemma4
- PyInstaller
- Electron / electron-builder
