import os
import streamlit as st
from rag.loader import load_document
from rag import embedder

UPLOAD_DIR = "data/uploads"
ALLOWED_TYPES = ["pdf", "csv", "txt", "docx", "xlsx"]


def render_documents():
    st.header("ドキュメント管理")
    _render_uploader()
    st.divider()
    _render_source_list()


# ── アップローダー ──────────────────────────────────────────────────

def _render_uploader():
    if "uploader_key" not in st.session_state:
        st.session_state.uploader_key = 0
    if "pending_overwrites" not in st.session_state:
        st.session_state.pending_overwrites = []

    uploaded_files = st.file_uploader(
        "ファイルを選択（PDF / CSV / TXT / Word / Excel）",
        type=ALLOWED_TYPES,
        accept_multiple_files=True,
        key=f"uploader_{st.session_state.uploader_key}",
    )

    if st.button("アップロード", disabled=not uploaded_files):
        existing = set(embedder.list_sources())
        duplicates = [f for f in uploaded_files if f.name in existing]
        new_files  = [f for f in uploaded_files if f.name not in existing]

        # 重複ファイルを確認待ちに保存
        if duplicates:
            st.session_state.pending_overwrites = duplicates
            st.session_state.pending_new_files  = new_files
        else:
            _process_files(new_files)
            _reset_uploader()

    # 上書き確認ダイアログ
    if st.session_state.pending_overwrites:
        names = ", ".join(f.name for f in st.session_state.pending_overwrites)
        st.warning(f"以下のファイルはすでに登録されています。上書きしますか？\n\n{names}")
        col1, col2 = st.columns(2)
        if col1.button("上書きする", type="primary"):
            all_files = st.session_state.pending_new_files + st.session_state.pending_overwrites
            _process_files(all_files)
            st.session_state.pending_overwrites = []
            st.session_state.pending_new_files  = []
            _reset_uploader()
        if col2.button("スキップ"):
            _process_files(st.session_state.pending_new_files)
            st.session_state.pending_overwrites = []
            st.session_state.pending_new_files  = []
            _reset_uploader()


def _process_files(files):
    for uf in files:
        save_path = os.path.join(UPLOAD_DIR, os.path.basename(uf.name))
        with open(save_path, "wb") as f:
            f.write(uf.getbuffer())
        with st.spinner(f"{uf.name} を処理中..."):
            try:
                chunks = load_document(save_path)
                if not chunks:
                    st.warning(f"{uf.name} からテキストを抽出できませんでした。")
                    continue
                embedder.add_documents(chunks)
                st.success(f"{uf.name} を登録しました（{len(chunks)} チャンク）")
            except ValueError as e:
                st.error(f"{uf.name}: {e}")
            except Exception as e:
                st.error(f"{uf.name} の処理中にエラーが発生しました: {e}")


def _reset_uploader():
    st.session_state.uploader_key += 1
    st.rerun()


# ── 登録済みドキュメント一覧 ────────────────────────────────────────

def _render_source_list():
    st.subheader("登録済みドキュメント")
    sources = embedder.list_sources_with_count()

    if not sources:
        st.caption("まだドキュメントが登録されていません")
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

        col_check, col_name, col_count, col_del = st.columns([0.5, 4, 1.5, 1])
        col_check.checkbox(
            label="",
            key=f"chk_{source}",
            label_visibility="collapsed",
            on_change=on_individual,
        )
        col_name.write(f"📄 {source}")
        col_count.caption(f"{item['chunks']} チャンク")
        if col_del.button("削除", key=f"del_{source}"):
            _delete_source(source)
            st.session_state.selected_sources.discard(source)
            st.session_state.pop(f"chk_{source}", None)
            st.rerun()

    if st.session_state.selected_sources:
        st.divider()
        n = len(st.session_state.selected_sources)
        if st.button(f"選択した {n} 件を一括削除", type="primary"):
            for source in list(st.session_state.selected_sources):
                _delete_source(source)
                st.session_state.pop(f"chk_{source}", None)
            st.session_state.selected_sources = set()
            st.session_state["chk_all"] = False
            st.success(f"{n} 件のドキュメントを削除しました")
            st.rerun()


def _delete_source(source: str):
    embedder.delete_source(source)
    upload_path = os.path.join(UPLOAD_DIR, source)
    if os.path.exists(upload_path):
        os.remove(upload_path)
