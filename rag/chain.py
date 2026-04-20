import os
import re
import anthropic
from rag import embedder

SYSTEM_PROMPT = """あなたは社内情報アシスタントです。
以下の【参考資料】のみを根拠として質問に回答してください。
資料に情報がない場合は「資料に該当情報がありません」と答えてください。
回答は日本語で簡潔に記述し、参照した資料番号を文末に [1][2] の形式で必ず明記してください。

【参考資料】
{context}
"""

_client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


def answer(query: str, history: list[dict]) -> dict:
    candidates = embedder.search(query)

    if not candidates:
        return {"answer": "資料に該当情報がありません。先にドキュメントをアップロードしてください。", "sources": []}

    context = _build_context(candidates)
    system = SYSTEM_PROMPT.format(context=context)
    messages = [*history, {"role": "user", "content": query}]

    try:
        response = _client.messages.create(
            model=os.getenv("CLAUDE_MODEL", "claude-sonnet-4-6"),
            max_tokens=1024,
            system=system,
            messages=messages,
        )
        answer_text = response.content[0].text
        used_sources = _filter_cited(answer_text, candidates)
        return {"answer": answer_text, "sources": used_sources}
    except anthropic.AuthenticationError:
        return {"answer": "APIキーが無効です。.env の ANTHROPIC_API_KEY を確認してください。", "sources": []}
    except anthropic.RateLimitError:
        return {"answer": "APIのレート制限に達しました。しばらくしてから再試行してください。", "sources": []}
    except Exception as e:
        return {"answer": f"エラーが発生しました: {e}", "sources": []}


def _build_context(sources: list[dict]) -> str:
    parts = []
    for i, s in enumerate(sources, 1):
        parts.append(f"[{i}] {s['source']} (p.{s['page']})\n{s['text']}")
    return "\n\n".join(parts)


def _filter_cited(text: str, sources: list[dict]) -> list[dict]:
    cited_indices = {int(n) for n in re.findall(r"\[(\d+)\]", text)}
    return [s for i, s in enumerate(sources, 1) if i in cited_indices]
