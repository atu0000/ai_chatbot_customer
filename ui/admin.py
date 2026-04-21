import bcrypt
import streamlit as st
from ui.auth import load_config, save_config
from rag import feedback as fb


def render_admin():
    st.title("管理者パネル")
    tab_list, tab_register, tab_feedback = st.tabs(["ユーザー一覧", "ユーザー登録", "フィードバック統計"])

    with tab_list:
        _render_user_list()

    with tab_register:
        _render_register_form()

    with tab_feedback:
        _render_feedback_stats()


def _render_feedback_stats():
    st.subheader("回答品質フィードバック")
    records = fb.load_all()

    if not records:
        st.info("まだフィードバックがありません。")
        return

    total = len(records)
    good = sum(1 for r in records if r["rating"] == "good")
    bad = total - good

    col1, col2, col3 = st.columns(3)
    col1.metric("総フィードバック数", total)
    col2.metric("👍 良い回答", good)
    col3.metric("👎 改善が必要", bad)

    if total > 0:
        rate = round(good / total * 100, 1)
        st.progress(good / total, text=f"満足度: {rate}%")

    st.divider()
    st.subheader("フィードバック一覧")

    filter_rating = st.selectbox("絞り込み", ["すべて", "👍 良い回答", "👎 改善が必要"])
    filtered = records
    if filter_rating == "👍 良い回答":
        filtered = [r for r in records if r["rating"] == "good"]
    elif filter_rating == "👎 改善が必要":
        filtered = [r for r in records if r["rating"] == "bad"]

    for r in reversed(filtered):
        label = "👍" if r["rating"] == "good" else "👎"
        with st.expander(f"{label} {r['timestamp']} — {r['username']} — {r['question'][:40]}"):
            st.markdown(f"**質問:** {r['question']}")
            st.markdown(f"**回答:** {r['answer']}")
            st.caption(f"ユーザー: {r['username']} ／ 日時: {r['timestamp']}")


def _render_user_list():
    config = load_config()
    users = config["credentials"]["usernames"]

    if not users:
        st.info("登録済みユーザーがいません。")
        return

    current_user = st.session_state.get("username", "")

    for username, info in list(users.items()):
        role = info.get("role", "user")
        role_label = "管理者" if role == "admin" else "ユーザー"
        col_name, col_email, col_role, col_actions = st.columns([2, 3, 1.5, 2])

        col_name.write(f"**{info.get('name', '')}** (`{username}`)")
        col_email.caption(info.get("email", ""))
        col_role.caption(role_label)

        with col_actions:
            action_col, del_col = st.columns(2)
            new_role = "user" if role == "admin" else "admin"
            new_role_label = "ユーザーに変更" if role == "admin" else "管理者に変更"
            if action_col.button(new_role_label, key=f"role_{username}", use_container_width=True):
                config["credentials"]["usernames"][username]["role"] = new_role
                save_config(config)
                st.success(f"{info.get('name')} の役職を変更しました。")
                st.rerun()

            if username != current_user:
                if del_col.button("削除", key=f"del_{username}", type="primary", use_container_width=True):
                    del config["credentials"]["usernames"][username]
                    save_config(config)
                    st.success(f"{info.get('name')} を削除しました。")
                    st.rerun()
            else:
                del_col.caption("(自分)")

        st.divider()


def _render_register_form():
    st.subheader("新規ユーザー登録")

    with st.form("register_form", clear_on_submit=True):
        username = st.text_input("ユーザー名 *", placeholder="半角英数字")
        name = st.text_input("表示名 *", placeholder="山田 太郎")
        email = st.text_input("メールアドレス *", placeholder="user@example.com")
        password = st.text_input("パスワード *", type="password")
        password_confirm = st.text_input("パスワード（確認）*", type="password")
        role = st.selectbox("役職 *", options=["user", "admin"], format_func=lambda r: "ユーザー" if r == "user" else "管理者")
        submitted = st.form_submit_button("登録", type="primary")

    if not submitted:
        return

    # バリデーション
    errors = []
    if not username:
        errors.append("ユーザー名を入力してください。")
    if not name:
        errors.append("表示名を入力してください。")
    if not email:
        errors.append("メールアドレスを入力してください。")
    if not password:
        errors.append("パスワードを入力してください。")
    elif len(password) < 8:
        errors.append("パスワードは8文字以上で入力してください。")
    elif password != password_confirm:
        errors.append("パスワードが一致しません。")

    if errors:
        for e in errors:
            st.error(e)
        return

    config = load_config()
    if username in config["credentials"]["usernames"]:
        st.error(f"ユーザー名 '{username}' はすでに使用されています。")
        return

    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    config["credentials"]["usernames"][username] = {
        "email": email,
        "name": name,
        "password": hashed,
        "role": role,
    }
    save_config(config)
    role_label = "管理者" if role == "admin" else "ユーザー"
    st.success(f"{name}（{role_label}）を登録しました。")
