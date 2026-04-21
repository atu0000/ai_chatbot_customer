import ipaddress
import os
import re
import socket
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from dotenv import load_dotenv

load_dotenv()

CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 500))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 50))
_TIMEOUT = 15
_HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; RAGBot/1.0)"}
_SKIP_TAGS = {"script", "style", "noscript", "header", "footer", "nav", "aside"}


def _validate_url(url: str) -> None:
    """SSRF 対策: 内部アドレス・非 HTTP(S) スキームを拒否する。"""
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise ValueError(f"http / https 以外のスキームは使用できません: {parsed.scheme}")

    hostname = parsed.hostname
    if not hostname:
        raise ValueError("ホスト名が指定されていません。")

    # localhost 系を拒否
    if hostname in ("localhost", "127.0.0.1", "::1"):
        raise ValueError("ローカルホストへのアクセスは許可されていません。")

    # DNS 解決してプライベート IP を拒否
    try:
        ip = socket.getaddrinfo(hostname, None)[0][4][0]
        addr = ipaddress.ip_address(ip)
        if addr.is_private or addr.is_loopback or addr.is_link_local or addr.is_reserved:
            raise ValueError("プライベートネットワークへのアクセスは許可されていません。")
    except socket.gaierror:
        raise ValueError(f"ホスト名を解決できませんでした: {hostname}")


def fetch(url: str) -> list[dict]:
    """URL からテキストを取得してチャンクのリストを返す。"""
    _validate_url(url)

    resp = requests.get(url, headers=_HEADERS, timeout=_TIMEOUT, allow_redirects=True, max_redirects=5)
    resp.raise_for_status()
    resp.encoding = resp.apparent_encoding

    soup = BeautifulSoup(resp.text, "lxml")
    for tag in soup(_SKIP_TAGS):
        tag.decompose()

    body = soup.find("main") or soup.find("body") or soup
    raw = body.get_text(separator="\n")
    text = _clean(raw)

    if not text:
        raise ValueError("ページからテキストを抽出できませんでした。")

    source = _url_to_label(url)
    chunks = []
    for chunk_text in _split(text):
        if chunk_text.strip():
            chunks.append({"text": chunk_text.strip(), "source": source, "page": url})
    return chunks


def _clean(text: str) -> str:
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


def _split(text: str) -> list[str]:
    chunks = []
    start = 0
    while start < len(text):
        chunks.append(text[start:start + CHUNK_SIZE])
        start += CHUNK_SIZE - CHUNK_OVERLAP
    return chunks


def _url_to_label(url: str) -> str:
    """URL を短いラベル文字列に変換する（ソース名として利用）。"""
    parsed = urlparse(url)
    label = parsed.netloc + parsed.path.rstrip("/")
    return label[:80] if len(label) > 80 else label
