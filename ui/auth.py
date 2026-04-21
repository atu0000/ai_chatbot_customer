import re
import yaml
import streamlit as st
import streamlit_authenticator as stauth
from streamlit_authenticator.utilities.validator import Validator
from pathlib import Path


class JapaneseValidator(Validator):
    """パスワードバリデーションメッセージを日本語化したバリデーター。"""

    def diagnose_password(self, password: str) -> str:
        min_length = 8
        max_length = 20
        errors = []
        if not min_length <= len(password) <= max_length:
            errors.append(f"{min_length}〜{max_length}文字にしてください \n\n")
        if not re.search(r"[a-z]", password):
            errors.append("小文字（a〜z）を1文字以上含めてください \n\n")
        if not re.search(r"[A-Z]", password):
            errors.append("大文字（A〜Z）を1文字以上含めてください \n\n")
        if not re.search(r"\d", password):
            errors.append("数字（0〜9）を1文字以上含めてください \n\n")
        if not re.search(r"[!@#$%^&*()_+\-=\[\]{};:\'\"\\|,.<>\/?`~]", password):
            errors.append("記号（!@#$%^&* など）を1文字以上含めてください \n\n")
        return "**パスワードの要件:** \n\n" + "".join(errors)

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
        validator=JapaneseValidator(),
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
    """サイドバーにログインユーザー情報とログアウトボタンを表示する。"""
    name = st.session_state.get("name", "")
    role = get_current_role()
    role_label = "管理者" if role == "admin" else "ユーザー"
    badge_color = "#F59E0B" if role == "admin" else "#10B981"
    st.sidebar.markdown(
        f"""
        <div style="padding:0.6rem 0;">
            <div style="font-size:0.85rem; color:#94A3B8;">ログイン中</div>
            <div style="font-size:1rem; font-weight:600;">{name}</div>
            <span style="
                background:{badge_color};
                color:white;
                font-size:0.72rem;
                font-weight:600;
                padding:2px 8px;
                border-radius:99px;
            ">{role_label}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    authenticator.logout(button_name="ログアウト", location="sidebar")
