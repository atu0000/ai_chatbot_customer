# 社内RAGチャットボット

社内ドキュメントをアップロードするだけで、その内容をもとに自然言語で回答する業務向けチャットボットです。
**Claude Code を活用して設計・実装**したポートフォリオ成果物です。

---

## 主な機能

| 機能 | 説明 |
|------|------|
| ユーザー認証 | ログイン／ログアウト。未認証ユーザーはアクセス不可 |
| 役職管理 | 管理者 / ユーザーの2役職。メニューを自動切り替え |
| ユーザー管理 | 管理者がアプリ上でアカウント登録・削除・役職変更 |
| マルチユーザー | ユーザーごとにドキュメントと会話履歴を完全分離 |
| ドキュメント登録 | PDF / CSV / TXT / Word / Excel をアップロード |
| Web 取り込み | URL を入力するだけで Web ページの内容を RAG に登録 |
| RAG 回答生成 | アップロード資料のみを根拠に Claude が回答 |
| 出典表示 | 回答に使ったチャンクのファイル名・ページ／URL を表示 |
| 会話履歴 | マルチターン対応（文脈を引き継いだ回答） |
| 回答品質評価 | 👍/👎 ボタンでフィードバックを収集。管理者が統計を確認可能 |
| 永続化 | アプリ再起動後もドキュメントを保持 |

---

## 技術スタック

| レイヤー | 採用技術 |
|----------|----------|
| UI | Streamlit |
| 認証 | streamlit-authenticator |
| LLM | Anthropic Claude API（claude-sonnet-4-6） |
| Embedding | sentence-transformers（multilingual） |
| ベクトル DB | ChromaDB（ローカル永続化・ユーザー別コレクション） |
| ドキュメント解析 | PyMuPDF / pandas / python-docx / openpyxl |
| Web 取り込み | requests / BeautifulSoup4 |

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

### 4. 認証設定ファイルを作成

```bash
cp config/auth.example.yaml config/auth.yaml
```

`config/auth.yaml` を開き、ユーザー情報と Cookie シークレットキーを編集します。

```yaml
credentials:
  usernames:
    admin:
      email: admin@example.com
      name: 管理者
      password: admin123        # 初回起動時に自動ハッシュ化されます
      role: admin
    user1:
      email: user1@example.com
      name: ユーザー1
      password: user1pass
      role: user

cookie:
  expiry_days: 30
  key: supersecretkey_change_this   # 必ず変更してください
  name: rag_chatbot_auth
```

> `config/auth.yaml` は `.gitignore` に含まれており Git 管理外です。

### 5. 起動

```bash
streamlit run app.py
```

ブラウザで `http://localhost:8501` が自動的に開きます。

---

## 使い方

### 管理者（role: admin）

1. `admin` アカウントでログイン
2. サイドバー **「ユーザー管理」** から新規ユーザーを登録・削除・役職変更
3. サイドバーからドキュメントをアップロード、または URL を入力して Web ページを取り込む
4. チャット欄に質問を入力して送信
5. **「ユーザー管理 → フィードバック統計」** でユーザーの回答評価を確認

### 一般ユーザー（role: user）

1. 発行されたアカウントでログイン
2. **「ユーザー設定」** からパスワードを変更可能
3. サイドバーからドキュメントをアップロード、または URL を入力して Web ページを取り込む（自分専用の領域）
4. チャット欄に質問を入力して送信
5. 回答の下の 👍 / 👎 ボタンでフィードバックを送信

> ドキュメントは **ユーザーごとに完全分離**されています。他のユーザーのファイルは参照されません。

---

## 役職ごとの機能一覧

| 機能 | 管理者 | ユーザー |
|------|:------:|:--------:|
| チャット | ✅ | ✅ |
| ドキュメント管理（ファイル・URL） | ✅ | ✅ |
| 回答品質フィードバック（👍/👎） | ✅ | ✅ |
| ユーザー管理（登録・削除・役職変更） | ✅ | ✗ |
| フィードバック統計閲覧 | ✅ | ✗ |
| ユーザー設定（パスワード変更） | ✗ | ✅ |

---

## プロジェクト構成

```
ai_chatbot_customer/
├── .streamlit/
│   └── config.toml             # テーマ設定
├── config/
│   ├── auth.example.yaml       # 認証設定テンプレート
│   └── auth.yaml               # 認証設定（git 管理外）
├── data/
│   ├── uploads/
│   │   └── {username}/         # ユーザー別アップロードファイル（git 管理外）
│   ├── feedback/
│   │   └── feedback.csv        # フィードバック記録（git 管理外）
│   └── chroma/                 # ChromaDB データ（git 管理外）
├── docs/                       # 設計ドキュメント
│   ├── 01_要件定義.md
│   ├── 02_基本設計.md
│   ├── 03_詳細設計.md
│   └── 04_実装計画.md
├── rag/
│   ├── loader.py               # ドキュメント読み込み・チャンク分割
│   ├── crawler.py              # Web ページ取得・チャンク分割
│   ├── embedder.py             # ChromaDB 操作（ユーザー別コレクション）
│   ├── chain.py                # RAG パイプライン・Claude API 呼び出し
│   └── feedback.py             # フィードバック保存・読み込み
├── ui/
│   ├── auth.py                 # 認証・役職管理
│   ├── admin.py                # 管理者画面（ユーザー管理・フィードバック統計）
│   ├── chat.py                 # チャット画面（👍/👎 ボタン含む）
│   ├── documents.py            # ドキュメント管理画面（ファイル・URL）
│   └── user_settings.py        # ユーザー設定画面（パスワード変更）
├── app.py                      # エントリーポイント
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
