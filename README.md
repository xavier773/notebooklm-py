# notebooklm-py

本地版 NotebookLM — 使用 Claude API 對文件進行問答。

## 安裝

```bash
pip install -e .
```

需要設定 API 金鑰：

```bash
export ANTHROPIC_API_KEY=your_key_here
```

## 使用方式

### 互動式問答

```bash
notebooklm chat report.pdf notes.md
```

### 單次問答

```bash
notebooklm ask "這份文件的主要結論是什麼？" --file report.pdf
```

### Python API

```python
from notebooklm import Notebook

nb = Notebook()
nb.add_file("report.pdf")
nb.add_file("notes.md")

# 單次問答
answer = nb.chat("這份文件談到了什麼？")
print(answer)

# 串流輸出
for chunk in nb.stream("請摘要重點"):
    print(chunk, end="", flush=True)
```

## 支援格式

- `.txt` — 純文字
- `.md` — Markdown
- `.pdf` — PDF（需安裝 `pypdf`）

## 特色

- 多文件同時載入，交叉問答
- 對話歷史記憶（多輪對話）
- 使用 Claude 的 prompt caching 降低費用
- 串流輸出
