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

from ui.documents import render_documents
from ui.chat import render_chat

with st.sidebar:
    render_documents()

render_chat()
