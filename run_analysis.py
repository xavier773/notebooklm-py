import sys
sys.path.insert(0, '.')
from notebooklm.notebook import Notebook

VAULT = "/Users/x-mac/Library/Mobile Documents/iCloud~md~obsidian/Documents/Obsidian"

sources = [
    f"{VAULT}/.agents/tmp/source_1.md",
    f"{VAULT}/.agents/tmp/source_2.md",
    f"{VAULT}/.agents/tmp/source_3.md"
]

questions = [
    "Q1: 請從這三份文件（EASY-Care系統性回顧、台灣長照CMS操作手冊、interRAI CHA手冊）中，整合比較三套評估工具在以下四個維度的異同：(1) 評估面向完整性（涵蓋哪些領域）、(2) 本土適用性（台灣使用可行性）、(3) 信效度基礎、(4) 服務連結強度（評估結果如何連結到服務或給付）。請以表格呈現比較結果。",
    
    "Q2: 請列出這三份文件中提到的核心概念、評估指標或分類系統（如CMS等級、EASY-Care的三個總結性指標、interRAI的CAPs等），並說明每個概念的定義與用途。",
    
    "Q3: 根據這三份文件，目前老年需求評估工具領域存在哪些研究缺口或限制？特別關注：(a) 信度證據不足之處、(b) 跨文化驗證缺口、(c) 工具間的互操作性問題。",
    
    "Q4: 這三份文件在方法論上有哪些值得注意的設計選擇？例如評估方式（自評 vs 專業評估）、計分邏輯、模組化設計等。這些設計選擇對評估結果有何影響？",
    
    "Q5: 若要以這三套工具為基礎，為台灣獨居老人設計一套整合性需求評估工具，你會如何取捨各工具的優點？請提出具體的整合建議，包括：(a) 應保留哪些評估面向、(b) 可採用哪種計分邏輯、(c) 如何強化服務連結、(d) 需要補充哪些本土化項目。"
]

for i, q in enumerate(questions, 1):
    print(f"\n{'='*80}")
    print(f"Q{i}: {q[:80]}...")
    print(f"{'='*80}")
    
    nb = Notebook()
    for s in sources:
        nb.add_file(s)
    
    try:
        result = nb.chat(q)
        print(result)
    except Exception as e:
        print(f"Error: {e}")
    
    print(f"\n--- END Q{i} ---\n")
