from __future__ import annotations

import json
import re
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Document:
    name: str
    content: str
    source: str = ""

    # ── 公開建構方法 ───────────────────────────────────────────────────────

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
    def from_youtube(cls, url: str, lang: str = "zh-Hant,zh,en") -> "Document":
        """Extract transcript from a YouTube video using yt-dlp.

        Falls back to video description + chapters when no subtitles are available.
        Requires yt-dlp: brew install yt-dlp
        """
        _require_ytdlp()

        # ── 取得影片 metadata ─────────────────────────────────────────────
        meta_proc = subprocess.run(
            ["yt-dlp", "--dump-json", "--no-playlist", url],
            capture_output=True,
            text=True,
        )
        meta: dict = {}
        if meta_proc.returncode == 0:
            try:
                meta = json.loads(meta_proc.stdout)
            except json.JSONDecodeError:
                pass

        title = meta.get("title") or "YouTube Video"
        channel = meta.get("channel") or meta.get("uploader") or ""
        upload_date = meta.get("upload_date") or ""
        description = (meta.get("description") or "")[:1500]
        chapters: list[dict] = meta.get("chapters") or []

        # ── 下載字幕 ──────────────────────────────────────────────────────
        transcript: str | None = None
        with tempfile.TemporaryDirectory() as tmpdir:
            subprocess.run(
                [
                    "yt-dlp",
                    "--write-auto-sub", "--write-sub",
                    "--sub-lang", lang,
                    "--sub-format", "vtt",
                    "--skip-download",
                    "--no-playlist",
                    "--output", f"{tmpdir}/sub.%(ext)s",
                    url,
                ],
                capture_output=True,
                text=True,
            )
            vtt_files = sorted(Path(tmpdir).glob("*.vtt"))
            if vtt_files:
                transcript = cls._parse_vtt(vtt_files[0].read_text(encoding="utf-8"))

        # ── 組合文件內容 ──────────────────────────────────────────────────
        header = (
            f"# {title}\n\n"
            f"**頻道**：{channel}  \n"
            f"**日期**：{upload_date}  \n"
            f"**來源**：{url}\n\n"
        )

        if transcript:
            body = f"## 字幕逐字稿\n\n{transcript}"
        else:
            chapter_text = ""
            if chapters:
                chapter_text = "## 章節\n\n" + "\n".join(
                    f"- {c.get('title', '')} "
                    f"({int(c.get('start_time', 0))}s–{int(c.get('end_time', 0))}s)"
                    for c in chapters
                ) + "\n\n"
            body = (
                chapter_text
                + f"## 影片描述\n\n{description}\n\n"
                + "[字幕不可用，以上為頻道描述，僅供參考]"
            )

        return cls(name=title, content=header + body, source=url)

    # ── 私有方法 ──────────────────────────────────────────────────────────

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

    @staticmethod
    def _parse_vtt(vtt_text: str) -> str:
        """Parse VTT subtitle file into clean, deduplicated plain text."""
        text_lines: list[str] = []
        prev = ""
        for line in vtt_text.splitlines():
            line = line.strip()
            if (
                not line
                or line.startswith("WEBVTT")
                or "-->" in line
                or line.startswith(("Kind:", "Language:", "NOTE", "STYLE"))
                or re.match(r"^\d+$", line)  # bare sequence numbers
            ):
                continue
            # strip inline tags: <00:00:00.000>, <c>, </c>, <i>, etc.
            line = re.sub(r"<[^>]+>", "", line).strip()
            if not line or line == prev:
                continue
            text_lines.append(line)
            prev = line
        return " ".join(text_lines)

    def as_context_block(self) -> str:
        return f'<document name="{self.name}">\n{self.content}\n</document>'


# ── 工具函式 ──────────────────────────────────────────────────────────────

def _require_ytdlp() -> None:
    if subprocess.run(["which", "yt-dlp"], capture_output=True).returncode != 0:
        raise RuntimeError(
            "yt-dlp 未安裝。請執行：brew install yt-dlp  或  pip install yt-dlp"
        )
