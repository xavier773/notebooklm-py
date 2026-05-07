from __future__ import annotations

import os
from pathlib import Path
from typing import Iterator

import anthropic

from .document import Document

MODEL = "claude-haiku-4-5-20251001"
SYSTEM = (
    "You are a research assistant. Answer questions using only the provided documents. "
    "Cite the document name when referencing specific information. "
    "If the answer cannot be found in the documents, say so clearly."
)

_KEY_FILE = Path.home() / ".claude" / "notebooklm_key"


def _resolve_api_key() -> str:
    # Claude Code sets ANTHROPIC_API_KEY="" in subprocesses — key file takes priority.
    key_file_key = _KEY_FILE.read_text().strip() if _KEY_FILE.exists() else ""
    if key_file_key:
        return key_file_key
    env_key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if env_key:
        return env_key
    raise RuntimeError(
        f"No Anthropic API key found.\n"
        f"Create {_KEY_FILE} with your API key (one line):\n"
        f"  echo 'sk-ant-...' > {_KEY_FILE} && chmod 600 {_KEY_FILE}"
    )


class Notebook:
    def __init__(self, model: str = MODEL):
        self.model = model
        self.documents: list[Document] = []
        self._client = anthropic.Anthropic(api_key=_resolve_api_key())
        self._history: list[dict] = []

    # ── documents ──────────────────────────────────────────────────────────

    def add_file(self, path: str | Path) -> "Notebook":
        self.documents.append(Document.from_file(path))
        return self

    def add_text(self, text: str, name: str = "inline") -> "Notebook":
        self.documents.append(Document.from_text(text, name))
        return self

    def clear_documents(self) -> "Notebook":
        self.documents.clear()
        self._history.clear()
        return self

    # ── chat ───────────────────────────────────────────────────────────────

    def chat(self, question: str) -> str:
        """Single-turn Q&A, returns the full response text."""
        return "".join(self.stream(question))

    def stream(self, question: str) -> Iterator[str]:
        """Stream the response token by token."""
        if not self.documents:
            raise ValueError("Add at least one document before asking questions.")

        context = "\n\n".join(d.as_context_block() for d in self.documents)
        system_with_docs = f"{SYSTEM}\n\n<documents>\n{context}\n</documents>"

        self._history.append({"role": "user", "content": question})

        full_text = ""
        with self._client.messages.stream(
            model=self.model,
            max_tokens=4096,
            system=[
                {
                    "type": "text",
                    "text": system_with_docs,
                    "cache_control": {"type": "ephemeral"},
                }
            ],
            messages=self._history,
        ) as s:
            for chunk in s.text_stream:
                full_text += chunk
                yield chunk

        self._history.append({"role": "assistant", "content": full_text})

    def reset_history(self) -> "Notebook":
        self._history.clear()
        return self
