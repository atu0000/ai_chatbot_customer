import yaml
import streamlit as st
import streamlit_authenticator as stauth
from pathlib import Path

CONFIG_PATH = Path("config/auth.yaml")


def load_config() -> dict:
    with open(CONFIG_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f)


def save_config(config: dict) -> None:
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        yaml.dump(config, f, allow_unicode=True, default_flow_style=False)


def build_authenticator() -> stauth.Authenticate:
    if not CONFIG_PATH.exists():
        st.error(f"認証設定ファイルが見つかりません: {CONFIG_PATH}\n`config/auth.example.yaml` をコピーして設定してください。")
        st.stop()

    config = load_config()
    authenticator = stauth.Authenticate(
        config["credentials"],
        config["cookie"]["name"],
        config["cookie"]["key"],
        config["cookie"]["expiry_days"],
        auto_hash=True,
    )
    # auto_hash でパスワードがハッシュ化された場合は保存
    save_config(config)
    return authenticator


def require_login(authenticator: stauth.Authenticate) -> None:
    """未認証ならログイン画面を表示してアプリを停止する。"""
    authenticator.login(
        location="main",
        max_login_attempts=5,
        fields={
            "Form name": "ログイン",
            "Username": "ユーザー名",
            "Password": "パスワード",
            "Login": "ログイン",
        },
    )

    status = st.session_state.get("authentication_status")

    if status is False:
        st.error("ユーザー名またはパスワードが正しくありません")
        st.stop()
    elif status is None:
        st.stop()


def get_current_role() -> str:
    """ログイン中ユーザーの role を返す（未設定なら 'user'）。"""
    username = st.session_state.get("username", "")
    if not username:
        return "user"
    config = load_config()
    user = config["credentials"]["usernames"].get(username, {})
    return user.get("role", "user")


def render_logout(authenticator: stauth.Authenticate) -> None:
    """サイドバーにログインユーザー名とログアウトボタンを表示する。"""
    name = st.session_state.get("name", "")
    role = get_current_role()
    role_label = "管理者" if role == "admin" else "ユーザー"
    st.sidebar.markdown(f"**{name}** ({role_label})")
    authenticator.logout(button_name="ログアウト", location="sidebar")
