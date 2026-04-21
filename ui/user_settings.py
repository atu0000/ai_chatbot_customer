import streamlit as st
import streamlit_authenticator as stauth
from ui.auth import save_config, load_config


def render_user_settings(authenticator: stauth.Authenticate):
    st.title("ユーザー設定")
    st.subheader("パスワード変更")

    username = st.session_state.get("username", "")
    try:
        changed = authenticator.reset_password(
            username=username,
            location="main",
            fields={
                "Form name": "パスワード変更",
                "Current password": "現在のパスワード",
                "New password": "新しいパスワード",
                "Repeat password": "新しいパスワード（確認）",
                "Reset": "変更する",
            },
        )
        if changed:
            # パスワード変更後は config に保存
            config = load_config()
            creds = config["credentials"]
            # authenticator 内部の credentials を取得して同期
            internal = authenticator.authentication_handler.credentials
            creds["usernames"][username]["password"] = (
                internal["usernames"][username]["password"]
            )
            save_config(config)
            st.success("パスワードを変更しました。")
    except Exception as e:
        st.error(f"パスワード変更に失敗しました: {e}")
