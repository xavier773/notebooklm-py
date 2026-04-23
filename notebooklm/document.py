from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Document:
    name: str
    content: str
    source: str = ""

    @classmethod
    def from_file(cls, path: str | Path) -> "Document":
        p = Path(path)
        if p.suffix.lower() == ".pdf":
            return cls._from_pdf(p)
        return cls(name=p.name, content=p.read_text(encoding="utf-8"), source=str(p))

    @classmethod
    def from_text(cls, text: str, name: str = "inline") -> "Document":
        return cls(name=name, content=text, source="inline")

    @classmethod
    def _from_pdf(cls, path: Path) -> "Document":
        try:
            from pypdf import PdfReader
        except ImportError as e:
            raise ImportError("Install pypdf: pip install pypdf") from e

        reader = PdfReader(str(path))
        pages = [page.extract_text() or "" for page in reader.pages]
        content = "\n\n".join(pages)
        return cls(name=path.name, content=content, source=str(path))

    def as_context_block(self) -> str:
        return f"<document name=\"{self.name}\">\n{self.content}\n</document>"
