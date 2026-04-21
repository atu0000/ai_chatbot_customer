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
| 共有ドキュメント | 管理者が全ユーザー共通の資料をアップロード。全員のチャットで参照される |
| Web 取り込み | URL を入力するだけで Web ページの内容を RAG に登録 |
| RAG 回答生成 | アップロード資料（個人＋共有）のみを根拠に Claude が回答 |
| 出典表示 | 回答に使ったチャンクのファイル名・ページ／URL を表示 |
| 会話履歴 | マルチターン対応（文脈を引き継いだ回答） |
| 回答品質評価 | 👍/👎 ボタンでフィードバックを収集。管理者が統計を確認可能 |
| コスト表示 | セッションのトークン数・推定コスト（円／ドル）をリアルタイム表示 |
| 禁止ワードフィルター | 管理者が設定した禁止ワードを含む送信をブロック。情報漏洩・悪意のある入力を予防 |
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
| 排他制御 | filelock |

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

`config/auth.yaml` を開き、以下の3点を必ず設定してください。

#### ① Cookie シークレットキーを生成・設定

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

出力された文字列を `cookie.key` に設定します。

#### ② ユーザー情報を設定

```yaml
credentials:
  usernames:
    admin:
      email: admin@example.com
      name: 管理者
      password: "YourStr0ng!Pass"   # 8文字以上・大小英字・数字・記号を含む
      role: admin

cookie:
  expiry_days: 1                    # セッション有効期間（日数）
  key: "生成したランダムキーを貼り付け"
  name: rag_chatbot_auth
```

パスワードは初回起動時に自動でハッシュ化されます。

> `config/auth.yaml` は `.gitignore` に含まれており Git 管理外です。

### 5. 起動

```bash
streamlit run app.py
```

ブラウザで `http://localhost:8501` が自動的に開きます。

---

## 使い方

### 管理者（role: admin）

1. 設定したアカウントでログイン
2. **「👥 ユーザー管理」** から新規ユーザーを登録・削除・役職変更
3. **「📁 ドキュメント管理」** でアップロード先を選択
   - **個人用**: 自分のチャットのみで参照される
   - **全体共有**: 全ユーザーのチャットで参照される（社内規程・マニュアル等に使用）
4. **「💬 チャット」** で質問を入力して送信
5. **「👥 ユーザー管理 → フィードバック統計」** でユーザーの回答評価を確認
6. **「👥 ユーザー管理 → 禁止ワード設定」** で送信を禁止するワードを登録・管理

### 一般ユーザー（role: user）

1. 管理者から発行されたアカウントでログイン
2. **「⚙️ ユーザー設定」** からパスワードを変更
3. **「📁 ドキュメント管理」** からファイルをアップロード（自分専用の領域）
4. **「💬 チャット」** で質問を入力して送信（禁止ワードを含む場合はブロック）
5. 回答の下の 👍 / 👎 ボタンでフィードバックを送信

> チャットは **個人ドキュメント＋管理者がアップロードした共有ドキュメント** を参照します。他のユーザーの個人ファイルは参照されません。

---

## 役職ごとの機能一覧

| 機能 | 管理者 | ユーザー |
|------|:------:|:--------:|
| チャット・コスト表示 | ✅ | ✅ |
| 個人ドキュメント管理（ファイル・URL） | ✅ | ✅ |
| 回答品質フィードバック（👍/👎） | ✅ | ✅ |
| 共有ドキュメントのアップロード・管理 | ✅ | ✗ |
| ユーザー管理（登録・削除・役職変更） | ✅ | ✗ |
| フィードバック統計閲覧 | ✅ | ✗ |
| 禁止ワード設定（追加・削除・有効化） | ✅ | ✗ |
| ユーザー設定（パスワード変更） | ✗ | ✅ |

---

## セキュリティ対策

| 対策 | 内容 |
|------|------|
| パスワードハッシュ化 | bcrypt で自動ハッシュ化。平文は保存しない |
| SSRF 対策 | Web 取り込み時に localhost・プライベート IP・非 HTTP(S) を拒否 |
| ファイル名サニタイズ | アップロード時に危険文字を除去しディレクトリトラバーサルを防止 |
| CSV インジェクション対策 | フィードバック保存時に数式先頭文字（= + - @）を無害化 |
| 禁止ワードフィルター | 管理者が設定したワードを含む送信をブロック。個人情報等の入力・抜き取りを予防 |
| 排他ファイルロック | `auth.yaml` / `feedback.csv` / `moderation.json` を filelock で保護 |
| Cookie キー検証 | 起動時にデフォルト値・空欄なら即座にエラー停止 |
| エラー詳細の非表示 | スタックトレースをブラウザに表示しない |
| セッション有効期間 | デフォルト 1 日（`auth.yaml` で変更可能） |
| 外部アクセス遮断 | Streamlit はデフォルトで localhost のみバインド。外部公開には別途設定が必要 |

---

## プロジェクト構成

```
ai_chatbot_customer/
├── .streamlit/
│   └── config.toml             # テーマ・セキュリティ設定
├── config/
│   ├── auth.example.yaml       # 認証設定テンプレート
│   └── auth.yaml               # 認証設定（git 管理外）
├── data/
│   ├── uploads/
│   │   ├── {username}/         # ユーザー別アップロードファイル（git 管理外）
│   │   └── __shared__/         # 共有ドキュメント（管理者がアップロード）
│   ├── feedback/
│   │   └── feedback.csv        # フィードバック記録（git 管理外）
│   ├── moderation.json         # 禁止ワード設定（git 管理外）
│   └── chroma/                 # ChromaDB データ（git 管理外）
├── docs/                       # 設計ドキュメント
├── rag/
│   ├── loader.py               # ドキュメント読み込み・チャンク分割
│   ├── crawler.py              # Web ページ取得・SSRF 対策付き
│   ├── embedder.py             # ChromaDB 操作（ユーザー別・共有・キャッシュ付き）
│   ├── chain.py                # RAG パイプライン・コスト計算
│   ├── feedback.py             # フィードバック保存・CSV インジェクション対策
│   └── moderation.py           # 禁止ワード設定の読み書き・メッセージチェック
├── ui/
│   ├── auth.py                 # 認証・役職管理・Cookie キー検証
│   ├── admin.py                # 管理者画面（ユーザー管理・フィードバック・禁止ワード）
│   ├── chat.py                 # チャット画面（禁止ワードチェック・フィードバック・コスト）
│   ├── documents.py            # ドキュメント管理（個人用 / 共有の切り替え）
│   ├── styles.py               # グローバル CSS
│   └── user_settings.py        # ユーザー設定（パスワード変更）
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
