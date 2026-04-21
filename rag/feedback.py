import csv
import os
from datetime import datetime

FEEDBACK_PATH = "data/feedback/feedback.csv"
_FIELDS = ["timestamp", "username", "question", "answer", "rating"]


def _ensure_file():
    os.makedirs(os.path.dirname(FEEDBACK_PATH), exist_ok=True)
    if not os.path.exists(FEEDBACK_PATH):
        with open(FEEDBACK_PATH, "w", newline="", encoding="utf-8") as f:
            csv.DictWriter(f, fieldnames=_FIELDS).writeheader()


def save(username: str, question: str, answer: str, rating: str) -> None:
    """rating: 'good' or 'bad'"""
    _ensure_file()
    with open(FEEDBACK_PATH, "a", newline="", encoding="utf-8") as f:
        csv.DictWriter(f, fieldnames=_FIELDS).writerow({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "username": username,
            "question": question,
            "answer": answer,
            "rating": rating,
        })


def load_all() -> list[dict]:
    _ensure_file()
    with open(FEEDBACK_PATH, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))
