import json
import re
from pathlib import Path
from filelock import FileLock

_CONFIG_PATH = Path("data/moderation.json")
_LOCK_PATH = Path("data/moderation.json.lock")

_DEFAULT: dict = {"enabled": True, "blocked_words": []}


def load_config() -> dict:
    if not _CONFIG_PATH.exists():
        return dict(_DEFAULT)
    with FileLock(str(_LOCK_PATH)):
        with open(_CONFIG_PATH, encoding="utf-8") as f:
            return json.load(f)


def save_config(config: dict) -> None:
    _CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with FileLock(str(_LOCK_PATH)):
        with open(_CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)


def check_message(text: str) -> str | None:
    """禁止ワードが含まれていればそのワードを返す。含まれていなければ None。"""
    config = load_config()
    if not config.get("enabled", True):
        return None
    for word in config.get("blocked_words", []):
        if word and re.search(re.escape(word), text, re.IGNORECASE):
            return word
    return None
