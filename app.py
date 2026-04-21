import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

os.makedirs("data/uploads", exist_ok=True)
os.makedirs("data/chroma", exist_ok=True)

st.set_page_config(
    page_title="社内RAGチャットボット",
    page_icon="🤖",
    layout="wide",
)

from ui.styles import inject
inject()

if not os.getenv("ANTHROPIC_API_KEY"):
    st.error("ANTHROPIC_API_KEY が設定されていません。.env ファイルを確認してください。")
    st.stop()

from ui.auth import build_authenticator, require_login, render_logout, get_current_role
from ui.documents import render_documents
from ui.chat import render_chat
from ui.admin import render_admin
from ui.user_settings import render_user_settings

# ── ログイン画面 ─────────────────────────────────────────────────────
authenticator = build_authenticator()

if not st.session_state.get("authentication_status"):
    st.markdown("""
    <div style="text-align:center; padding: 3rem 0 1.5rem;">
        <div style="font-size:3rem;">🤖</div>
        <div style="font-size:1.8rem; font-weight:700; color:#1E293B; margin:0.4rem 0 0.2rem;">社内RAGチャットボット</div>
        <div style="font-size:0.95rem; color:#64748B;">社内ドキュメントをもとに質問に回答します</div>
    </div>
    """, unsafe_allow_html=True)
    _, col, _ = st.columns([1, 2, 1])
    with col:
        require_login(authenticator)
    st.stop()

require_login(authenticator)

role = get_current_role()

# ── サイドバー ─────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🤖 RAGチャットボット")
    st.divider()
    render_logout(authenticator)
    st.divider()

    if role == "admin":
        page = st.radio(
            "メニュー",
            ["💬 チャット", "📁 ドキュメント管理", "👥 ユーザー管理"],
            label_visibility="collapsed",
        )
    else:
        page = st.radio(
            "メニュー",
            ["💬 チャット", "📁 ドキュメント管理", "⚙️ ユーザー設定"],
            label_visibility="collapsed",
        )

# ── メインエリア ───────────────────────────────────────────────────────
if page == "💬 チャット":
    render_chat()
elif page == "📁 ドキュメント管理":
    render_documents()
elif page == "👥 ユーザー管理" and role == "admin":
    render_admin()
elif page == "⚙️ ユーザー設定":
    render_user_settings(authenticator)
