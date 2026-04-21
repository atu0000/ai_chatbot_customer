import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

os.makedirs("data/uploads", exist_ok=True)
os.makedirs("data/chroma", exist_ok=True)

st.set_page_config(page_title="社内RAGチャットボット", layout="wide")

if not os.getenv("ANTHROPIC_API_KEY"):
    st.error("ANTHROPIC_API_KEY が設定されていません。.env ファイルを確認してください。")
    st.stop()

from ui.auth import build_authenticator, require_login, render_logout, get_current_role
from ui.documents import render_documents
from ui.chat import render_chat
from ui.admin import render_admin
from ui.user_settings import render_user_settings

authenticator = build_authenticator()
require_login(authenticator)

role = get_current_role()

# ── サイドバー ─────────────────────────────────────────────────────────
with st.sidebar:
    render_logout(authenticator)
    st.divider()

    if role == "admin":
        page = st.radio(
            "メニュー",
            ["チャット", "ドキュメント管理", "ユーザー管理"],
            label_visibility="collapsed",
        )
    else:
        page = st.radio(
            "メニュー",
            ["チャット", "ドキュメント管理", "ユーザー設定"],
            label_visibility="collapsed",
        )

    if page == "ドキュメント管理":
        st.divider()
        render_documents()

# ── メインエリア ───────────────────────────────────────────────────────
if page == "チャット":
    render_chat()
elif page == "ドキュメント管理":
    st.title("ドキュメント管理")
    st.info("サイドバーからファイルをアップロード・管理してください。")
elif page == "ユーザー管理" and role == "admin":
    render_admin()
elif page == "ユーザー設定":
    render_user_settings(authenticator)
