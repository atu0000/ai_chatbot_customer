import streamlit as st
from rag.chain import answer
from rag import embedder
from rag import feedback as fb
from rag import moderation


def render_chat():
    username = st.session_state.get("username", "")

    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "sources_map" not in st.session_state:
        st.session_state.sources_map = {}
    if "feedback_done" not in st.session_state:
        st.session_state.feedback_done = set()
    if "total_cost_usd" not in st.session_state:
        st.session_state.total_cost_usd = 0.0
    if "total_input_tokens" not in st.session_state:
        st.session_state.total_input_tokens = 0
    if "total_output_tokens" not in st.session_state:
        st.session_state.total_output_tokens = 0

    # サイドバー：リセットボタン + コスト表示
    with st.sidebar:
        st.divider()
        if st.button("🔄 会話をリセット", use_container_width=True, disabled=not st.session_state.messages):
            st.session_state.messages = []
            st.session_state.sources_map = {}
            st.session_state.feedback_done = set()
            st.session_state.total_cost_usd = 0.0
            st.session_state.total_input_tokens = 0
            st.session_state.total_output_tokens = 0
            st.rerun()

        if st.session_state.total_input_tokens > 0:
            st.divider()
            st.caption("📊 このセッションの使用量")
            st.caption(f"入力: {st.session_state.total_input_tokens:,} トークン")
            st.caption(f"出力: {st.session_state.total_output_tokens:,} トークン")
            cost_jpy = st.session_state.total_cost_usd * 150
            st.caption(f"推定コスト: ¥{cost_jpy:.2f}（${st.session_state.total_cost_usd:.4f}）")

    st.title("💬 チャット")

    if not embedder.has_any_sources(username):
        st.info("📁 ドキュメント管理からファイルをアップロードすると、その内容をもとに回答します。")
        return

    for i, msg in enumerate(st.session_state.messages):
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            if msg["role"] == "assistant":
                sources = st.session_state.sources_map.get(i, [])
                _render_sources(sources)
                _render_feedback(i, msg, username)

    if prompt := st.chat_input("質問を入力してください"):
        blocked_word = moderation.check_message(prompt)
        if blocked_word:
            st.warning(f"禁止ワードが含まれているため送信できません。（検出ワード: `{blocked_word}`）")
        else:
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.write(prompt)

            with st.chat_message("assistant"):
                with st.spinner("回答を生成中..."):
                    result = answer(prompt, _get_history(), username=username)
                st.write(result["answer"])
                _render_sources(result["sources"])

            # コスト累積
            if result.get("usage"):
                st.session_state.total_cost_usd     += result["usage"]["cost_usd"]
                st.session_state.total_input_tokens  += result["usage"]["input_tokens"]
                st.session_state.total_output_tokens += result["usage"]["output_tokens"]

            idx = len(st.session_state.messages)
            st.session_state.messages.append({"role": "assistant", "content": result["answer"]})
            st.session_state.sources_map[idx] = result["sources"]


def _render_feedback(msg_idx: int, msg: dict, username: str):
    if msg_idx in st.session_state.feedback_done:
        st.caption("✅ フィードバックありがとうございます")
        return

    question = ""
    if msg_idx > 0:
        prev = st.session_state.messages[msg_idx - 1]
        if prev["role"] == "user":
            question = prev["content"]

    st.caption("この回答は役に立ちましたか？")
    col_good, col_bad, _ = st.columns([1.4, 1.4, 7])
    if col_good.button("👍 役立った", key=f"good_{msg_idx}", use_container_width=True):
        fb.save(username, question, msg["content"], "good")
        st.session_state.feedback_done.add(msg_idx)
        st.rerun()
    if col_bad.button("👎 改善が必要", key=f"bad_{msg_idx}", use_container_width=True):
        fb.save(username, question, msg["content"], "bad")
        st.session_state.feedback_done.add(msg_idx)
        st.rerun()


def _render_sources(sources: list[dict]):
    if not sources:
        return
    with st.expander("📎 出典を見る"):
        for i, s in enumerate(sources, 1):
            st.markdown(f"**[{i}] {s['source']}** — p.{s['page']}")
            st.caption(s["text"])
            if i < len(sources):
                st.divider()


def _get_history() -> list[dict]:
    return [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
