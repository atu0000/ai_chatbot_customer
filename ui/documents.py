import os
import streamlit as st
from rag.loader import load_document
from rag import embedder

UPLOAD_DIR = "data/uploads"
ALLOWED_TYPES = ["pdf", "csv", "txt", "docx", "xlsx"]


def render_documents():
    st.header("ドキュメント管理")

    uploaded_files = st.file_uploader(
        "ファイルを選択（PDF / CSV / TXT / Word / Excel）",
        type=ALLOWED_TYPES,
        accept_multiple_files=True,
    )

    if st.button("アップロード", disabled=not uploaded_files):
        for uf in uploaded_files:
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

    st.divider()
    st.subheader("登録済みドキュメント")
    sources = embedder.list_sources()

    if not sources:
        st.caption("まだドキュメントが登録されていません")
        return

    for source in sources:
        col1, col2 = st.columns([4, 1])
        col1.write(f"📄 {source}")
        if col2.button("削除", key=f"del_{source}"):
            embedder.delete_source(source)
            upload_path = os.path.join(UPLOAD_DIR, source)
            if os.path.exists(upload_path):
                os.remove(upload_path)
            st.success(f"{source} を削除しました")
            st.rerun()
