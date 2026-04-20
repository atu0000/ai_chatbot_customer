# 社内RAGチャットボット

社内ドキュメントをアップロードするだけで、その内容をもとに自然言語で回答する業務向けチャットボットです。
**Claude Code を活用して設計・実装**したポートフォリオ成果物です。

---

## 主な機能

| 機能 | 説明 |
|------|------|
| ドキュメント登録 | PDF / CSV / TXT / Word / Excel をアップロード |
| RAG 回答生成 | アップロード資料のみを根拠に Claude が回答 |
| 出典表示 | 回答に使ったチャンクのファイル名・ページを表示 |
| 会話履歴 | マルチターン対応（文脈を引き継いだ回答） |
| 永続化 | アプリ再起動後もドキュメントを保持 |

---

## 技術スタック

| レイヤー | 採用技術 |
|----------|----------|
| UI | Streamlit |
| LLM | Anthropic Claude API（claude-sonnet-4-6） |
| Embedding | sentence-transformers（multilingual） |
| ベクトル DB | ChromaDB（ローカル永続化） |
| ドキュメント解析 | PyMuPDF / pandas / python-docx / openpyxl |

---

## セットアップ

### 1. リポジトリをクローン

```bash
git clone https://github.com/atu0000/ai_chatbot_customer.git
cd ai_chatbot_customer
```

### 2. 仮想環境を作成・有効化

**Windows**
```bash
py -m venv .venv
.venv\Scripts\activate
pip install -r requirements_windows.txt
```

**Mac / Linux**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements_mac.txt
```

### 3. 環境変数を設定

```bash
cp .env.example .env
```

`.env` を開き `ANTHROPIC_API_KEY` に取得済みの API キーを入力します。

```
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxx
```

> API キーは [Anthropic Console](https://console.anthropic.com/) から取得できます。

### 4. 起動

```bash
streamlit run app.py
```

ブラウザで `http://localhost:8501` が自動的に開きます。

---

## 使い方

1. **サイドバー**からドキュメント（PDF・Word・Excel 等）をアップロード
2. **チャット欄**に質問を入力して送信
3. 回答の下にある **「出典を見る」** で根拠テキストを確認

---

## プロジェクト構成

```
ai_chatbot_customer/
├── .streamlit/
│   └── config.toml        # テーマ設定
├── data/
│   ├── uploads/           # アップロードされたファイル（git 管理外）
│   └── chroma/            # ChromaDB データ（git 管理外）
├── docs/                  # 設計ドキュメント
│   ├── 01_要件定義.md
│   ├── 02_基本設計.md
│   ├── 03_詳細設計.md
│   └── 04_実装計画.md
├── rag/
│   ├── loader.py          # ドキュメント読み込み・チャンク分割
│   ├── embedder.py        # ChromaDB 操作
│   └── chain.py           # RAG パイプライン・Claude API 呼び出し
├── ui/
│   ├── chat.py            # チャット画面
│   └── documents.py       # ドキュメント管理画面
├── app.py                 # エントリーポイント
├── requirements_windows.txt
├── requirements_mac.txt
└── .env.example
```

---

## 設計ドキュメント

詳細な設計は `docs/` フォルダを参照してください。

- [01_要件定義](docs/01_要件定義.md)
- [02_基本設計](docs/02_基本設計.md)
- [03_詳細設計](docs/03_詳細設計.md)
- [04_実装計画](docs/04_実装計画.md)
