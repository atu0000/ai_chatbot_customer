import streamlit as st
from rag.chain import answer
from rag import embedder
from rag import feedback as fb


def render_chat():
    st.title("社内RAGチャットボット")

    username = st.session_state.get("username", "")

    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "sources_map" not in st.session_state:
        st.session_state.sources_map = {}
    if "feedback_done" not in st.session_state:
        st.session_state.feedback_done = set()

    if not embedder.list_sources(username):
        st.info("サイドバーからドキュメントをアップロードすると、その内容をもとに回答します。")

    for i, msg in enumerate(st.session_state.messages):
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            if msg["role"] == "assistant":
                sources = st.session_state.sources_map.get(i, [])
                _render_sources(sources)
                _render_feedback(i, msg, username)

    if prompt := st.chat_input("質問を入力してください"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        with st.chat_message("assistant"):
            with st.spinner("回答を生成中..."):
                result = answer(prompt, _get_history(), username=username)
            st.write(result["answer"])
            _render_sources(result["sources"])

        idx = len(st.session_state.messages)
        st.session_state.messages.append({"role": "assistant", "content": result["answer"]})
        st.session_state.sources_map[idx] = result["sources"]

    if st.session_state.messages:
        st.divider()
        if st.button("🔄 会話をリセット"):
            st.session_state.messages = []
            st.session_state.sources_map = {}
            st.session_state.feedback_done = set()
            st.rerun()


def _render_feedback(msg_idx: int, msg: dict, username: str):
    if msg_idx in st.session_state.feedback_done:
        st.caption("✅ フィードバックを送信しました")
        return

    # 直前のユーザー発言を取得
    question = ""
    if msg_idx > 0:
        prev = st.session_state.messages[msg_idx - 1]
        if prev["role"] == "user":
            question = prev["content"]

    col_good, col_bad, _ = st.columns([1, 1, 8])
    if col_good.button("👍", key=f"good_{msg_idx}"):
        fb.save(username, question, msg["content"], "good")
        st.session_state.feedback_done.add(msg_idx)
        st.rerun()
    if col_bad.button("👎", key=f"bad_{msg_idx}"):
        fb.save(username, question, msg["content"], "bad")
        st.session_state.feedback_done.add(msg_idx)
        st.rerun()


def _render_sources(sources: list[dict]):
    if not sources:
        return
    with st.expander("📎 出典を見る"):
        for i, s in enumerate(sources, 1):
            st.markdown(f"**[{i}] {s['source']} (p.{s['page']})**")
            st.caption(s["text"])
            if i < len(sources):
                st.divider()


def _get_history() -> list[dict]:
    return [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
