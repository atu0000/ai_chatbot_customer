import bcrypt
import streamlit as st
from ui.auth import load_config, save_config


def render_user_settings():
    st.title("⚙️ ユーザー設定")
    st.subheader("パスワード変更")

    username = st.session_state.get("username", "")

    with st.form("change_password_form", clear_on_submit=True):
        current = st.text_input("現在のパスワード", type="password")
        new_pw  = st.text_input("新しいパスワード", type="password")
        confirm = st.text_input("新しいパスワード（確認）", type="password")
        submitted = st.form_submit_button("変更する", type="primary")

    if not submitted:
        return

    config = load_config()
    stored_hash = config["credentials"]["usernames"].get(username, {}).get("password", "")

    # 現在のパスワードを検証
    if not stored_hash or not bcrypt.checkpw(current.encode(), stored_hash.encode()):
        st.error("現在のパスワードが正しくありません。")
        return

    # 新しいパスワードのバリデーション
    errors = []
    if len(new_pw) < 8:
        errors.append("パスワードは8文字以上で入力してください。")
    if new_pw != confirm:
        errors.append("新しいパスワードが一致しません。")
    if new_pw == current:
        errors.append("現在のパスワードと同じパスワードは使用できません。")
    if errors:
        for e in errors:
            st.error(e)
        return

    new_hash = bcrypt.hashpw(new_pw.encode(), bcrypt.gensalt()).decode()
    config["credentials"]["usernames"][username]["password"] = new_hash
    save_config(config)
    st.success("パスワードを変更しました。")
