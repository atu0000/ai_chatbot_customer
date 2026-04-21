import streamlit as st


def inject():
    st.markdown("""
    <style>
    /* ── Streamlit デフォルト要素を非表示 ── */
    #MainMenu, footer, header { visibility: hidden; }

    /* ── メインコンテナ ── */
    .main .block-container {
        padding-top: 1.8rem;
        padding-bottom: 2rem;
        max-width: 860px;
    }

    /* ── サイドバー ── */
    section[data-testid="stSidebar"] {
        background: #1E293B;
    }
    section[data-testid="stSidebar"] * {
        color: #E2E8F0 !important;
    }
    section[data-testid="stSidebar"] .stButton button {
        background: #334155;
        border: 1px solid #475569;
        color: #E2E8F0 !important;
        border-radius: 8px;
        width: 100%;
    }
    section[data-testid="stSidebar"] .stButton button:hover {
        background: #2563EB;
        border-color: #2563EB;
    }
    /* サイドバー radio ナビ */
    section[data-testid="stSidebar"] .stRadio label {
        font-size: 0.95rem;
        padding: 0.3rem 0;
    }

    /* ── ボタン（メインエリア） ── */
    .stButton button {
        border-radius: 8px;
        font-weight: 500;
        transition: all 0.15s ease;
    }
    .stButton button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(37,99,235,0.2);
    }

    /* ── チャット メッセージ ── */
    .stChatMessage {
        border-radius: 12px;
        margin-bottom: 0.5rem;
    }

    /* ── メトリクスカード ── */
    [data-testid="metric-container"] {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 1rem 1.2rem;
    }

    /* ── expander ── */
    .streamlit-expanderHeader {
        border-radius: 8px;
        font-size: 0.9rem;
    }

    /* ── info / success / error ── */
    .stAlert {
        border-radius: 10px;
    }

    /* ── ログイン画面 ── */
    .login-wrapper {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        min-height: 60vh;
    }
    .login-card {
        background: white;
        border: 1px solid #E2E8F0;
        border-radius: 16px;
        padding: 2.5rem 2rem;
        box-shadow: 0 4px 24px rgba(0,0,0,0.06);
        width: 100%;
        max-width: 420px;
        margin: 0 auto;
    }
    .login-title {
        text-align: center;
        font-size: 1.8rem;
        font-weight: 700;
        color: #1E293B;
        margin-bottom: 0.3rem;
    }
    .login-subtitle {
        text-align: center;
        font-size: 0.95rem;
        color: #64748B;
        margin-bottom: 1.5rem;
    }

    /* ── タブ ── */
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0;
        font-weight: 500;
    }

    /* ── divider ── */
    hr {
        border-color: #E2E8F0;
    }
    </style>
    """, unsafe_allow_html=True)
