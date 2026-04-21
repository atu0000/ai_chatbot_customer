import streamlit as st
from rag.chain import answer
from rag import embedder


def render_chat():
    st.title("社内RAGチャットボット")

    username = st.session_state.get("username", "")

    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "sources_map" not in st.session_state:
        st.session_state.sources_map = {}

    if not embedder.list_sources(username):
        st.info("サイドバーからドキュメントをアップロードすると、その内容をもとに回答します。")

    for i, msg in enumerate(st.session_state.messages):
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            if msg["role"] == "assistant":
                sources = st.session_state.sources_map.get(i, [])
                _render_sources(sources)

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
