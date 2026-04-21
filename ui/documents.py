import os
import re
import streamlit as st
from rag.loader import load_document
from rag import embedder
from rag import crawler
from rag.embedder import SHARED_USER
from ui.auth import get_current_role

ALLOWED_TYPES = ["pdf", "csv", "txt", "docx", "xlsx"]


def _sanitize_filename(name: str) -> str:
    """ディレクトリトラバーサル対策: ベース名のみ取り出し、危険な文字を除去する。"""
    base = os.path.basename(name)
    # 英数字・日本語・ハイフン・アンダースコア・ドット以外を _ に置換
    safe = re.sub(r"[^\w\u3000-\u9fff\u30a0-\u30ff\u3040-\u309f\-.]", "_", base)
    # 先頭のドットを除去（隠しファイル防止）
    safe = safe.lstrip(".")
    return safe or "uploaded_file"


def _upload_dir(username: str) -> str:
    path = os.path.join("data/uploads", username)
    os.makedirs(path, exist_ok=True)
    return path


def render_documents():
    st.title("📁 ドキュメント管理")

    username = st.session_state.get("username", "")
    role = get_current_role()

    # 管理者は個人用 / 全体共有を切り替えられる
    if role == "admin":
        scope = st.radio(
            "アップロード先",
            ["個人用（自分のみ参照）", "全体共有（全ユーザーが参照）"],
            horizontal=True,
        )
        target_user = SHARED_USER if scope == "全体共有（全ユーザーが参照）" else username
        if target_user == SHARED_USER:
            st.info("ここにアップロードしたドキュメントはすべてのユーザーのチャットで参照されます。")
    else:
        target_user = username

    tab_file, tab_url, tab_list = st.tabs(["📄 ファイルアップロード", "🌐 URLから取り込む", "📋 登録済み一覧"])

    with tab_file:
        _render_uploader(target_user)

    with tab_url:
        _render_url_fetcher(target_user)

    with tab_list:
        _render_source_list(target_user)


# ── ファイルアップロード ─────────────────────────────────────────────

def _render_uploader(username: str):
    st.subheader("ファイルをアップロード")
    st.caption("PDF / CSV / TXT / Word / Excel に対応しています。")

    if "uploader_key" not in st.session_state:
        st.session_state.uploader_key = 0
    if "pending_overwrites" not in st.session_state:
        st.session_state.pending_overwrites = []

    uploaded_files = st.file_uploader(
        "ファイルを選択",
        type=ALLOWED_TYPES,
        accept_multiple_files=True,
        key=f"uploader_{st.session_state.uploader_key}",
        label_visibility="collapsed",
    )

    if st.button("アップロード", disabled=not uploaded_files, type="primary"):
        existing = set(embedder.list_sources(username))
        duplicates = [f for f in uploaded_files if f.name in existing]
        new_files  = [f for f in uploaded_files if f.name not in existing]

        if duplicates:
            st.session_state.pending_overwrites = duplicates
            st.session_state.pending_new_files  = new_files
        else:
            _process_files(new_files, username)
            _reset_uploader()

    if st.session_state.pending_overwrites:
        names = ", ".join(f.name for f in st.session_state.pending_overwrites)
        st.warning(f"以下のファイルはすでに登録されています。上書きしますか？\n\n`{names}`")
        col1, col2 = st.columns(2)
        if col1.button("上書きする", type="primary"):
            all_files = st.session_state.pending_new_files + st.session_state.pending_overwrites
            _process_files(all_files, username)
            st.session_state.pending_overwrites = []
            st.session_state.pending_new_files  = []
            _reset_uploader()
        if col2.button("スキップ"):
            _process_files(st.session_state.pending_new_files, username)
            st.session_state.pending_overwrites = []
            st.session_state.pending_new_files  = []
            _reset_uploader()


def _process_files(files, username: str):
    upload_dir = _upload_dir(username)
    for uf in files:
        save_path = os.path.join(upload_dir, _sanitize_filename(uf.name))
        with open(save_path, "wb") as f:
            f.write(uf.getbuffer())
        with st.spinner(f"{uf.name} を処理中..."):
            try:
                chunks = load_document(save_path)
                if not chunks:
                    st.warning(f"{uf.name} からテキストを抽出できませんでした。")
                    continue
                embedder.add_documents(chunks, username)
                st.success(f"✅ {uf.name} を登録しました（{len(chunks)} チャンク）")
            except ValueError as e:
                st.error(f"{uf.name}: {e}")
            except Exception as e:
                st.error(f"{uf.name} の処理中にエラーが発生しました: {e}")


def _reset_uploader():
    st.session_state.uploader_key += 1
    st.rerun()


# ── URL 取り込み ────────────────────────────────────────────────────

def _render_url_fetcher(username: str):
    st.subheader("Web ページを取り込む")
    st.caption("URL を入力すると、ページのテキストを RAG に登録します。JavaScript で動的に生成されるページには対応していません。")

    url = st.text_input("URL", placeholder="https://example.com/page", label_visibility="collapsed")
    if st.button("取り込む", disabled=not url, type="primary"):
        label = crawler._url_to_label(url)
        existing = set(embedder.list_sources(username))
        if label in existing:
            st.warning(f"「{label}」はすでに登録されています。一覧から削除してから再登録してください。")
            return
        with st.spinner(f"{url} を取得中..."):
            try:
                chunks = crawler.fetch(url)
                embedder.add_documents(chunks, username)
                st.success(f"✅ 「{label}」を登録しました（{len(chunks)} チャンク）")
            except Exception as e:
                st.error(f"取り込みに失敗しました: {e}")


# ── 登録済みドキュメント一覧 ─────────────────────────────────────────

def _render_source_list(username: str):
    st.subheader("登録済みドキュメント")
    sources = embedder.list_sources_with_count(username)

    if not sources:
        st.info("まだドキュメントが登録されていません。")
        return

    if "selected_sources" not in st.session_state:
        st.session_state.selected_sources = set()
    if "chk_all" not in st.session_state:
        st.session_state["chk_all"] = False

    all_names = [s["source"] for s in sources]
    for name in all_names:
        if f"chk_{name}" not in st.session_state:
            st.session_state[f"chk_{name}"] = False

    def on_select_all():
        checked = st.session_state["chk_all"]
        st.session_state.selected_sources = set(all_names) if checked else set()
        for name in all_names:
            st.session_state[f"chk_{name}"] = checked

    st.checkbox("すべて選択", key="chk_all", on_change=on_select_all)

    for item in sources:
        source = item["source"]

        def on_individual(s=source):
            if st.session_state[f"chk_{s}"]:
                st.session_state.selected_sources.add(s)
            else:
                st.session_state.selected_sources.discard(s)
            st.session_state["chk_all"] = all(
                st.session_state.get(f"chk_{n}", False) for n in all_names
            )

        col_check, col_name, col_count, col_del = st.columns([0.5, 5, 1.5, 1])
        col_check.checkbox(
            label="",
            key=f"chk_{source}",
            label_visibility="collapsed",
            on_change=on_individual,
        )
        col_name.write(f"📄 {source}")
        col_count.caption(f"{item['chunks']} チャンク")
        if col_del.button("削除", key=f"del_{source}"):
            _delete_source(source, username)
            st.session_state.selected_sources.discard(source)
            st.session_state.pop(f"chk_{source}", None)
            st.rerun()

    if st.session_state.selected_sources:
        st.divider()
        n = len(st.session_state.selected_sources)
        if st.button(f"選択した {n} 件を一括削除", type="primary"):
            for source in list(st.session_state.selected_sources):
                _delete_source(source, username)
                st.session_state.pop(f"chk_{source}", None)
            st.session_state.selected_sources = set()
            st.session_state["chk_all"] = False
            st.success(f"{n} 件のドキュメントを削除しました")
            st.rerun()


def _delete_source(source: str, username: str):
    embedder.delete_source(source, username)
    upload_path = os.path.join(_upload_dir(username), source)
    if os.path.exists(upload_path):
        os.remove(upload_path)
